import hashlib
import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.websockets import manager as ws_manager
from app.models.domain import (
    Notification,
    PortfolioRiskAlert,
    PortfolioRiskAlertPreference,
    PortfolioRiskAlertState,
)
from app.services.analytics.portfolio_analytics import PortfolioAnalyticsService
from app.services.analytics.portfolio_risk import PortfolioRiskService

logger = logging.getLogger("terminal.analytics.monitoring")


class PortfolioRiskMonitoringService:
    """Service evaluating user portfolio risk conditions, managing alert states, cooldowns, and recovery notifications."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_or_create_alert_preference(self, user_id: UUID) -> PortfolioRiskAlertPreference:
        """Fetch or initialize user risk alert preferences with safe defaults."""
        stmt = select(PortfolioRiskAlertPreference).where(PortfolioRiskAlertPreference.user_id == user_id)
        res = await self.db.execute(stmt)
        pref = res.scalar_one_or_none()
        if not pref:
            pref = PortfolioRiskAlertPreference(
                user_id=user_id,
                drawdown_threshold_pct=Decimal("5.00"),
                daily_loss_threshold_pct=Decimal("3.00"),
                daily_loss_threshold_amount=Decimal("50000.00"),
                var_threshold_pct=Decimal("5.00"),
                expected_shortfall_threshold_pct=Decimal("7.50"),
                company_concentration_threshold_pct=Decimal("25.00"),
                sector_concentration_threshold_pct=Decimal("40.00"),
                correlation_threshold=Decimal("0.75"),
                volatility_threshold_pct=Decimal("20.00"),
                cooldown_minutes=60,
                enabled_alerts_json=[
                    "PORTFOLIO_DRAWDOWN",
                    "PORTFOLIO_DAILY_LOSS",
                    "PORTFOLIO_VOLATILITY",
                    "PORTFOLIO_VAR",
                    "PORTFOLIO_EXPECTED_SHORTFALL",
                    "PORTFOLIO_COMPANY_CONCENTRATION",
                    "PORTFOLIO_SECTOR_CONCENTRATION",
                    "PORTFOLIO_CORRELATION",
                ],
            )
            self.db.add(pref)
            await self.db.flush()
        return pref

    async def evaluate_user_portfolio_risk(self, user_id: UUID, account_id: Optional[UUID] = None) -> List[PortfolioRiskAlert]:
        """Evaluate authorized user portfolio against configured risk conditions."""
        pref = await self.get_or_create_alert_preference(user_id)
        enabled_types = pref.enabled_alerts_json if isinstance(pref.enabled_alerts_json, list) else []

        analytics_svc = PortfolioAnalyticsService(self.db)
        risk_svc = PortfolioRiskService(self.db)

        portfolio_analytics = await analytics_svc.generate_portfolio_analytics(user_id=user_id, account_id=account_id)
        var_es_analytics = await risk_svc.calculate_var_and_es(user_id=user_id, account_id=account_id)
        div_analytics = await risk_svc.calculate_diversification_metrics(user_id=user_id, account_id=account_id)
        corr_analytics = await risk_svc.calculate_correlation_matrix(user_id=user_id, account_id=account_id)

        now = datetime.now(UTC)
        triggered_alerts: List[PortfolioRiskAlert] = []

        # 1. DRAWDOWN EVALUATION
        if "PORTFOLIO_DRAWDOWN" in enabled_types:
            dd_pct = Decimal(str(portfolio_analytics.get("risk_analytics", {}).get("max_drawdown_pct", 0.0)))
            thresh = Decimal(str(pref.drawdown_threshold_pct))
            await self._process_alert_condition(
                user_id=user_id,
                account_id=account_id,
                alert_type="PORTFOLIO_DRAWDOWN",
                metric_key="max_drawdown",
                metric_name="Max Portfolio Drawdown",
                current_value=dd_pct,
                threshold_value=thresh,
                unit="PCT",
                is_condition_met=(dd_pct >= thresh and dd_pct > Decimal("0.00")),
                severity="CRITICAL" if dd_pct >= (thresh * Decimal("2.00")) else "WARNING",
                explanation=f"Portfolio max drawdown reached {dd_pct}%, exceeding configured threshold of {thresh}%.",
                affected_symbols=[],
                affected_sectors=[],
                data_quality=portfolio_analytics.get("data_status", "AVAILABLE"),
                cooldown_minutes=pref.cooldown_minutes,
                now=now,
                out_alerts=triggered_alerts,
            )

        # 2. COMPANY CONCENTRATION EVALUATION
        if "PORTFOLIO_COMPANY_CONCENTRATION" in enabled_types:
            max_company_conc = Decimal(str(portfolio_analytics.get("risk_analytics", {}).get("max_position_concentration_pct", 0.0)))
            thresh = Decimal(str(pref.company_concentration_threshold_pct))
            company_conc_map = div_analytics.get("concentration", {}).get("company_concentration_pct", {})
            top_company = max(company_conc_map.keys(), key=lambda k: company_conc_map[k]) if company_conc_map else None

            await self._process_alert_condition(
                user_id=user_id,
                account_id=account_id,
                alert_type="PORTFOLIO_COMPANY_CONCENTRATION",
                metric_key="max_company_concentration",
                metric_name="Company Concentration",
                current_value=max_company_conc,
                threshold_value=thresh,
                unit="PCT",
                is_condition_met=(max_company_conc >= thresh and max_company_conc > Decimal("0.00")),
                severity="WARNING",
                explanation=f"Holding concentration in {top_company or 'single asset'} reached {max_company_conc}%, exceeding configured threshold of {thresh}%.",
                affected_symbols=[top_company] if top_company else [],
                affected_sectors=[],
                data_quality=div_analytics.get("data_quality_status", "AVAILABLE"),
                cooldown_minutes=pref.cooldown_minutes,
                now=now,
                out_alerts=triggered_alerts,
            )

        # 3. SECTOR CONCENTRATION EVALUATION
        if "PORTFOLIO_SECTOR_CONCENTRATION" in enabled_types:
            sector_conc_map = div_analytics.get("concentration", {}).get("sector_concentration_pct", {})
            max_sector = max(sector_conc_map.keys(), key=lambda k: sector_conc_map[k]) if sector_conc_map else None
            max_sector_conc = Decimal(str(sector_conc_map[max_sector])) if max_sector else Decimal("0.00")
            thresh = Decimal(str(pref.sector_concentration_threshold_pct))

            await self._process_alert_condition(
                user_id=user_id,
                account_id=account_id,
                alert_type="PORTFOLIO_SECTOR_CONCENTRATION",
                metric_key="max_sector_concentration",
                metric_name="Sector Concentration",
                current_value=max_sector_conc,
                threshold_value=thresh,
                unit="PCT",
                is_condition_met=(max_sector_conc >= thresh and max_sector_conc > Decimal("0.00")),
                severity="WARNING",
                explanation=f"Sector allocation in {max_sector or 'single sector'} reached {max_sector_conc}%, exceeding configured threshold of {thresh}%.",
                affected_symbols=[],
                affected_sectors=[max_sector] if max_sector else [],
                data_quality=div_analytics.get("data_quality_status", "AVAILABLE"),
                cooldown_minutes=pref.cooldown_minutes,
                now=now,
                out_alerts=triggered_alerts,
            )

        # 4. VaR EVALUATION
        if "PORTFOLIO_VAR" in enabled_types and var_es_analytics.get("data_quality_status") == "AVAILABLE":
            var_pct = Decimal(str(var_es_analytics.get("value_at_risk", {}).get("historical_var_pct", 0.0)))
            thresh = Decimal(str(pref.var_threshold_pct))

            await self._process_alert_condition(
                user_id=user_id,
                account_id=account_id,
                alert_type="PORTFOLIO_VAR",
                metric_key="historical_var_95",
                metric_name="Historical 95% VaR",
                current_value=var_pct,
                threshold_value=thresh,
                unit="PCT",
                is_condition_met=(var_pct >= thresh and var_pct > Decimal("0.00")),
                severity="CRITICAL" if var_pct >= (thresh * Decimal("1.50")) else "WARNING",
                explanation=f"Historical 95% Value at Risk reached {var_pct}%, exceeding configured threshold of {thresh}%.",
                affected_symbols=[],
                affected_sectors=[],
                data_quality="AVAILABLE",
                cooldown_minutes=pref.cooldown_minutes,
                now=now,
                out_alerts=triggered_alerts,
            )

        # 5. CORRELATION EVALUATION
        if "PORTFOLIO_CORRELATION" in enabled_types and corr_analytics.get("data_quality_status") == "AVAILABLE":
            pairs = corr_analytics.get("highly_correlated_pairs", [])
            max_corr_pair = max(pairs, key=lambda x: x["correlation"]) if pairs else None
            max_corr = Decimal(str(max_corr_pair["correlation"])) if max_corr_pair else Decimal("0.00")
            thresh = Decimal(str(pref.correlation_threshold))

            await self._process_alert_condition(
                user_id=user_id,
                account_id=account_id,
                alert_type="PORTFOLIO_CORRELATION",
                metric_key="max_holding_correlation",
                metric_name="Holding Return Correlation",
                current_value=max_corr,
                threshold_value=thresh,
                unit="SCORE",
                is_condition_met=(max_corr >= thresh and max_corr > Decimal("0.00")),
                severity="INFO",
                explanation=f"Return correlation between {max_corr_pair['symbol_1'] if max_corr_pair else 'assets'} and {max_corr_pair['symbol_2'] if max_corr_pair else 'assets'} reached {max_corr}, exceeding threshold of {thresh}.",
                affected_symbols=[max_corr_pair["symbol_1"], max_corr_pair["symbol_2"]] if max_corr_pair else [],
                affected_sectors=[],
                data_quality="AVAILABLE",
                cooldown_minutes=pref.cooldown_minutes,
                now=now,
                out_alerts=triggered_alerts,
            )

        await self.db.commit()
        return triggered_alerts

    async def _process_alert_condition(
        self,
        user_id: UUID,
        account_id: Optional[UUID],
        alert_type: str,
        metric_key: str,
        metric_name: str,
        current_value: Decimal,
        threshold_value: Decimal,
        unit: str,
        is_condition_met: bool,
        severity: str,
        explanation: str,
        affected_symbols: List[str],
        affected_sectors: List[str],
        data_quality: str,
        cooldown_minutes: int,
        now: datetime,
        out_alerts: List[PortfolioRiskAlert],
    ) -> None:
        """Process alert state machine, fingerprint deduplication, cooldown suppression, and recovery detection."""
        fingerprint_raw = f"{user_id}:{alert_type}:{metric_key}"
        fingerprint = hashlib.sha256(fingerprint_raw.encode("utf-8")).hexdigest()

        stmt = select(PortfolioRiskAlertState).where(
            PortfolioRiskAlertState.user_id == user_id,
            PortfolioRiskAlertState.fingerprint == fingerprint,
        )
        res = await self.db.execute(stmt)
        state_obj = res.scalar_one_or_none()

        if not state_obj:
            state_obj = PortfolioRiskAlertState(
                user_id=user_id,
                alert_type=alert_type,
                fingerprint=fingerprint,
                state="NORMAL",
            )
            self.db.add(state_obj)

        if is_condition_met:
            # Check cooldown
            if state_obj.state == "COOLDOWN" and state_obj.cooldown_expires_at and now < state_obj.cooldown_expires_at:
                logger.info("Risk alert %s suppressed under cooldown until %s", alert_type, state_obj.cooldown_expires_at)
                return

            # Trigger alert
            alert = PortfolioRiskAlert(
                id=uuid4(),
                user_id=user_id,
                account_id=account_id,
                alert_type=alert_type,
                severity=severity,
                metric_name=metric_name,
                current_value=current_value,
                threshold_value=threshold_value,
                unit=unit,
                status="TRIGGERED",
                fingerprint=fingerprint,
                data_quality_status=data_quality,
                affected_symbols_json=affected_symbols,
                affected_sectors_json=affected_sectors,
                explanation=explanation,
                triggered_at=now,
            )
            self.db.add(alert)
            await self.db.flush()

            # Persist Notification Center item
            notif = Notification(
                user_id=user_id,
                notification_type="portfolio_risk_alert",
                title=f"Risk Alert: {metric_name} Exceeded",
                summary=explanation,
                importance=severity,
            )
            self.db.add(notif)

            # Update state machine
            state_obj.state = "COOLDOWN"
            state_obj.last_triggered_at = now
            state_obj.last_value = current_value
            state_obj.cooldown_expires_at = now + timedelta(minutes=cooldown_minutes)

            out_alerts.append(alert)

            # Broadcast WebSocket real-time event
            await ws_manager.broadcast({
                "type": "portfolio_risk_alert",
                "data": {
                    "alert_id": str(alert.id),
                    "user_id": str(user_id),
                    "alert_type": alert_type,
                    "severity": severity,
                    "metric_name": metric_name,
                    "current_value": float(current_value),
                    "threshold_value": float(threshold_value),
                    "explanation": explanation,
                    "affected_symbols": affected_symbols,
                    "affected_sectors": affected_sectors,
                    "triggered_at": now.isoformat(),
                },
            })

        else:
            # Condition is NOT met. Check for RECOVERY transition.
            if state_obj.state in ("TRIGGERED", "COOLDOWN"):
                recovery_explanation = f"Portfolio risk recovered: {metric_name} returned to {current_value}% (below threshold of {threshold_value}%)."

                recovery_alert = PortfolioRiskAlert(
                    id=uuid4(),
                    user_id=user_id,
                    account_id=account_id,
                    alert_type="PORTFOLIO_RISK_RECOVERED",
                    severity="INFO",
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold_value=threshold_value,
                    unit=unit,
                    status="RECOVERED",
                    fingerprint=fingerprint,
                    data_quality_status=data_quality,
                    affected_symbols_json=affected_symbols,
                    affected_sectors_json=affected_sectors,
                    explanation=recovery_explanation,
                    triggered_at=now,
                    recovered_at=now,
                )
                self.db.add(recovery_alert)
                await self.db.flush()

                state_obj.state = "NORMAL"
                state_obj.cooldown_expires_at = None
                state_obj.last_value = current_value

                # Broadcast WebSocket recovery event
                await ws_manager.broadcast({
                    "type": "portfolio_risk_recovered",
                    "data": {
                        "alert_id": str(recovery_alert.id),
                        "user_id": str(user_id),
                        "alert_type": "PORTFOLIO_RISK_RECOVERED",
                        "original_alert_type": alert_type,
                        "metric_name": metric_name,
                        "current_value": float(current_value),
                        "threshold_value": float(threshold_value),
                        "explanation": recovery_explanation,
                        "recovered_at": now.isoformat(),
                    },
                })
