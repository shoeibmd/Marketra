import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.websockets import manager as ws_manager
from app.models.domain import (
    Notification,
    PortfolioBriefing,
    PortfolioBriefingPreference,
    PortfolioChangeEvent,
)
from app.schemas.ai import ResearchQueryParsed
from app.services.analytics.portfolio_analytics import PortfolioAnalyticsService
from app.services.analytics.portfolio_change_detection import PortfolioChangeDetectionService
from app.services.analytics.portfolio_risk import PortfolioRiskService
from app.services.analytics.portfolio_risk_monitoring import PortfolioRiskMonitoringService
from app.services.rag.retrieval_engine import RAGRetrievalEngine

logger = logging.getLogger("terminal.analytics.briefings")


class PortfolioBriefingService:
    """Production service generating scheduled, source-grounded portfolio briefings with citations and real-time alerts."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_or_create_briefing_preference(self, user_id: UUID) -> PortfolioBriefingPreference:
        """Fetch or initialize user briefing preferences."""
        stmt = select(PortfolioBriefingPreference).where(PortfolioBriefingPreference.user_id == user_id)
        res = await self.db.execute(stmt)
        pref = res.scalar_one_or_none()
        if not pref:
            pref = PortfolioBriefingPreference(
                user_id=user_id,
                daily_briefing_enabled=True,
                weekly_briefing_enabled=True,
                pre_market_briefing_enabled=True,
                intraday_briefing_enabled=True,
                preferred_delivery_time="08:30",
                minimum_significance="MATERIAL",
                sections_config_json={
                    "include_summary": True,
                    "include_changes": True,
                    "include_risk": True,
                    "include_news": True,
                    "include_benchmark": True,
                },
            )
            self.db.add(pref)
            await self.db.flush()
        return pref

    async def generate_briefing(
        self,
        user_id: UUID,
        briefing_type: str = "DAILY",
        account_id: Optional[UUID] = None,
    ) -> PortfolioBriefing:
        """Generate structured, source-grounded portfolio briefing."""
        now = datetime.now(UTC)
        period_days = 7 if briefing_type == "WEEKLY" else 1
        period_start = now - timedelta(days=period_days)

        analytics_svc = PortfolioAnalyticsService(self.db)
        risk_svc = PortfolioRiskService(self.db)
        change_svc = PortfolioChangeDetectionService(self.db)

        # Detect changes
        changes = await change_svc.detect_and_record_changes(user_id=user_id, account_id=account_id)

        # RAG evidence retrieval
        query_parsed = ResearchQueryParsed(
            query=f"Portfolio {briefing_type} Briefing Analysis",
            date_range_days=period_days,
        )
        evidence = await RAGRetrievalEngine.retrieve_evidence(query_parsed, self.db, user_id=user_id)

        portfolio_analytics = await analytics_svc.generate_portfolio_analytics(user_id=user_id, account_id=account_id)
        var_es = await risk_svc.calculate_var_and_es(user_id=user_id, account_id=account_id)

        summary = portfolio_analytics.get("summary", {})
        risk_analytics = portfolio_analytics.get("risk_analytics", {})
        data_status = portfolio_analytics.get("data_status", "AVAILABLE")

        briefing_status = "COMPLETED" if data_status == "AVAILABLE" else "PARTIAL"

        content_json = {
            "portfolio_summary": {
                "total_equity": summary.get("total_equity", 0.0),
                "cash_balance": summary.get("cash_balance", 0.0),
                "total_return_pct": summary.get("total_return_pct", 0.0),
                "realized_pnl": summary.get("realized_pnl", 0.0),
                "unrealized_pnl": summary.get("unrealized_pnl", 0.0),
            },
            "what_changed": [
                {
                    "change_type": c.change_type,
                    "significance": c.significance,
                    "description": c.description,
                }
                for c in changes
            ],
            "risk_changes": {
                "current_drawdown_pct": risk_analytics.get("max_drawdown_pct", 0.0),
                "volatility_pct": risk_analytics.get("annualized_volatility_pct"),
                "historical_var_95_pct": var_es.get("value_at_risk", {}).get("historical_var_pct", 0.0),
                "expected_shortfall_95_pct": var_es.get("expected_shortfall", {}).get("cvar_expected_shortfall_pct", 0.0),
            },
            "news_and_events": evidence.get("financial_events", [])[:5],
            "benchmark_comparison": portfolio_analytics.get("benchmark_comparison", {}),
            "important_alerts": evidence.get("portfolio_analytics", {}).get("active_risk_alerts", []),
            "data_quality": {
                "overall_status": data_status,
                "observation_count": var_es.get("observation_count", 0),
            },
            "disclaimer": "Portfolio briefings are factual, descriptive analytical summaries. Content does not constitute investment recommendations.",
        }

        briefing_title = f"{briefing_type.capitalize()} Portfolio Briefing — {now.strftime('%b %d, %Y')}"

        briefing = PortfolioBriefing(
            id=uuid4(),
            user_id=user_id,
            account_id=account_id,
            briefing_type=briefing_type.upper(),
            status=briefing_status,
            significance="MATERIAL",
            summary_title=briefing_title,
            content_json=content_json,
            sources_json=[
                {"type": "PORTFOLIO_SNAPSHOT", "description": "Internal transaction and position ledger"},
                {"type": "OHLCV_PRICE_BARS", "description": "Daily market quote history"},
            ],
            data_quality_status=data_status,
            generated_at=now,
            period_start=period_start,
            period_end=now,
            is_read=False,
        )
        self.db.add(briefing)

        # Persist Notification Center item
        notif = Notification(
            user_id=user_id,
            notification_type="portfolio_briefing_ready",
            title=briefing_title,
            summary=f"Your {briefing_type.lower()} briefing is ready with total return of {summary.get('total_return_pct', 0.0)}%.",
            importance="INFO",
        )
        self.db.add(notif)

        await self.db.commit()

        # Broadcast WebSocket event
        await ws_manager.broadcast({
            "type": "portfolio_briefing_ready",
            "data": {
                "briefing_id": str(briefing.id),
                "user_id": str(user_id),
                "briefing_type": briefing.briefing_type,
                "summary_title": briefing_title,
                "data_quality": data_status,
                "generated_at": now.isoformat(),
            },
        })

        return briefing
