import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.websockets import manager as ws_manager
from app.models.domain import (
    FinancialEvent,
    PaperPortfolioSnapshot,
    PortfolioChangeEvent,
    PortfolioRiskAlert,
    PortfolioRiskSnapshot,
)
from app.services.analytics.portfolio_analytics import PortfolioAnalyticsService
from app.services.analytics.portfolio_risk import PortfolioRiskService

logger = logging.getLogger("terminal.analytics.change_detection")


class PortfolioChangeDetectionService:
    """Service monitoring portfolio snapshots, risk metrics, concentration, and disclosures for material changes."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def detect_and_record_changes(
        self, user_id: UUID, account_id: Optional[UUID] = None
    ) -> List[PortfolioChangeEvent]:
        """Detect and persist significant portfolio changes between current state and historical snapshots."""
        analytics_svc = PortfolioAnalyticsService(self.db)
        risk_svc = PortfolioRiskService(self.db)

        current_analytics = await analytics_svc.generate_portfolio_analytics(user_id=user_id, account_id=account_id)
        current_risk = await risk_svc.calculate_var_and_es(user_id=user_id, account_id=account_id)
        current_div = await risk_svc.calculate_diversification_metrics(user_id=user_id, account_id=account_id)

        # Fetch previous risk snapshot for delta comparison
        stmt_prev_snap = (
            select(PortfolioRiskSnapshot)
            .where(PortfolioRiskSnapshot.user_id == user_id)
            .order_by(PortfolioRiskSnapshot.timestamp.desc())
            .offset(1)
            .limit(1)
        )
        res_prev_snap = await self.db.execute(stmt_prev_snap)
        prev_snap = res_prev_snap.scalar_one_or_none()

        now = datetime.now(UTC)
        recorded_changes: List[PortfolioChangeEvent] = []

        curr_equity = Decimal(str(current_analytics.get("summary", {}).get("total_equity", 0.0)))
        curr_drawdown = Decimal(str(current_analytics.get("risk_analytics", {}).get("max_drawdown_pct", 0.0)))
        curr_max_company_conc = Decimal(str(current_analytics.get("risk_analytics", {}).get("max_position_concentration_pct", 0.0)))

        if prev_snap:
            prev_equity = prev_snap.portfolio_value
            prev_drawdown = prev_snap.drawdown_pct

            # 1. VALUE CHANGE DETECTION
            if prev_equity > 0:
                abs_equity_diff = curr_equity - prev_equity
                pct_equity_diff = (abs_equity_diff / prev_equity) * Decimal("100.00")

                if abs(pct_equity_diff) >= Decimal("2.00"):
                    sig = "HIGH_IMPORTANCE" if abs(pct_equity_diff) >= Decimal("5.00") else "MATERIAL"
                    change_ev = PortfolioChangeEvent(
                        id=uuid4(),
                        user_id=user_id,
                        account_id=account_id,
                        change_type="PORTFOLIO_VALUE_CHANGE",
                        significance=sig,
                        previous_value=prev_equity,
                        current_value=curr_equity,
                        absolute_change=abs_equity_diff,
                        percentage_change=round(pct_equity_diff, 2),
                        affected_symbols_json=[],
                        affected_sectors_json=[],
                        description=f"Portfolio value changed by {pct_equity_diff:.2f}% (₹{abs_equity_diff:,.2f}) since previous snapshot.",
                        data_quality_status=current_analytics.get("data_status", "AVAILABLE"),
                        detected_at=now,
                    )
                    self.db.add(change_ev)
                    recorded_changes.append(change_ev)

            # 2. DRAWDOWN CHANGE DETECTION
            dd_diff = curr_drawdown - prev_drawdown
            if dd_diff >= Decimal("1.00"):
                sig = "HIGH_IMPORTANCE" if dd_diff >= Decimal("3.00") else "MATERIAL"
                change_ev = PortfolioChangeEvent(
                    id=uuid4(),
                    user_id=user_id,
                    account_id=account_id,
                    change_type="DRAWDOWN_INCREASE",
                    significance=sig,
                    previous_value=prev_drawdown,
                    current_value=curr_drawdown,
                    absolute_change=dd_diff,
                    percentage_change=round(dd_diff, 2),
                    affected_symbols_json=[],
                    affected_sectors_json=[],
                    description=f"Portfolio max drawdown increased from {prev_drawdown}% to {curr_drawdown}%.",
                    data_quality_status=current_analytics.get("data_status", "AVAILABLE"),
                    detected_at=now,
                )
                self.db.add(change_ev)
                recorded_changes.append(change_ev)

        # 3. RECENT DISCLOSURES / FINANCIAL EVENTS FOR HOLDINGS
        positions = current_analytics.get("positions", [])
        symbols = [p["symbol"] for p in positions if "symbol" in p]
        if symbols:
            one_day_ago = now - timedelta(days=1)
            stmt_events = (
                select(FinancialEvent)
                .where(FinancialEvent.event_date >= one_day_ago, FinancialEvent.importance.in_(["HIGH", "CRITICAL"]))
                .limit(5)
            )
            res_events = await self.db.execute(stmt_events)
            recent_events = res_events.scalars().all()

            for ev in recent_events:
                change_ev = PortfolioChangeEvent(
                    id=uuid4(),
                    user_id=user_id,
                    account_id=account_id,
                    change_type="NEW_HOLDING_DISCLOSURE",
                    significance="MATERIAL",
                    previous_value=None,
                    current_value=None,
                    absolute_change=None,
                    percentage_change=None,
                    affected_symbols_json=[ev.primary_company_id] if ev.primary_company_id else [],
                    affected_sectors_json=[ev.sector] if ev.sector else [],
                    description=f"New {ev.importance} disclosure: {ev.event_title}",
                    data_quality_status="AVAILABLE",
                    detected_at=now,
                )
                self.db.add(change_ev)
                recorded_changes.append(change_ev)

        await self.db.commit()

        # Broadcast WebSocket events for each detected change
        for c in recorded_changes:
            await ws_manager.broadcast({
                "type": "portfolio_change_detected",
                "data": {
                    "change_id": str(c.id),
                    "user_id": str(user_id),
                    "change_type": c.change_type,
                    "significance": c.significance,
                    "description": c.description,
                    "detected_at": c.detected_at.isoformat(),
                },
            })

        return recorded_changes
