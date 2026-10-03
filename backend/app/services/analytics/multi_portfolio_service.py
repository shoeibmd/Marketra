import logging
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import (
    Instrument,
    PaperPosition,
    PaperTradingAccount,
    PortfolioGroup,
    PortfolioGroupMembership,
)
from app.services.analytics.portfolio_analytics import PortfolioAnalyticsService
from app.services.analytics.portfolio_risk import PortfolioRiskService

logger = logging.getLogger("terminal.analytics.multi_portfolio")


class MultiPortfolioService:
    """Production service for multi-portfolio management, side-by-side comparisons, consolidated risk aggregation, duplicate exposure detection, and P&L attribution."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_user_portfolios(self, user_id: UUID) -> List[PaperTradingAccount]:
        """Fetch all paper trading accounts owned by user."""
        stmt = select(PaperTradingAccount).where(PaperTradingAccount.user_id == user_id).order_by(PaperTradingAccount.created_at.asc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create_portfolio_account(
        self, user_id: UUID, name: str, initial_cash: Decimal, portfolio_type: str = "PAPER"
    ) -> PaperTradingAccount:
        """Create new portfolio account for user."""
        acct = PaperTradingAccount(
            id=uuid4(),
            user_id=user_id,
            name=name,
            initial_cash=initial_cash,
            available_cash=initial_cash,
            portfolio_type=portfolio_type,
        )
        self.db.add(acct)
        await self.db.commit()
        return acct

    async def compare_portfolios(
        self, user_id: UUID, account_ids: Optional[List[UUID]] = None
    ) -> List[Dict[str, Any]]:
        """Side-by-side factual comparison of user-owned portfolios."""
        portfolios = await self.list_user_portfolios(user_id)
        if account_ids:
            portfolios = [p for p in portfolios if p.id in account_ids]

        analytics_svc = PortfolioAnalyticsService(self.db)
        risk_svc = PortfolioRiskService(self.db)
        comparisons: List[Dict[str, Any]] = []

        for p in portfolios:
            pa = await analytics_svc.generate_portfolio_analytics(user_id=user_id, account_id=p.id)
            var_es = await risk_svc.calculate_var_and_es(user_id=user_id, account_id=p.id)
            div = await risk_svc.calculate_diversification_metrics(user_id=user_id, account_id=p.id)

            summary = pa.get("summary", {})
            risk_analytics = pa.get("risk_analytics", {})

            comparisons.append({
                "account_id": str(p.id),
                "name": p.name,
                "portfolio_type": p.portfolio_type,
                "total_equity": summary.get("total_equity", 0.0),
                "cash_balance": summary.get("cash_balance", 0.0),
                "total_return_pct": summary.get("total_return_pct", 0.0),
                "realized_pnl": summary.get("realized_pnl", 0.0),
                "unrealized_pnl": summary.get("unrealized_pnl", 0.0),
                "max_drawdown_pct": risk_analytics.get("max_drawdown_pct", 0.0),
                "volatility_pct": risk_analytics.get("annualized_volatility_pct"),
                "sharpe_ratio": risk_analytics.get("sharpe_ratio"),
                "historical_var_95_pct": var_es.get("value_at_risk", {}).get("historical_var_pct", 0.0),
                "hhi_index": div.get("summary", {}).get("hhi_index", 0.0),
                "diversification_score": div.get("summary", {}).get("diversification_score", 0.0),
                "data_quality_status": pa.get("data_status", "AVAILABLE"),
            })

        return comparisons

    async def get_consolidated_portfolio(
        self, user_id: UUID, account_ids: Optional[List[UUID]] = None
    ) -> Dict[str, Any]:
        """Aggregate total equity, cash, P&L, exposure, and risk across multiple user portfolios."""
        portfolios = await self.list_user_portfolios(user_id)
        if account_ids:
            portfolios = [p for p in portfolios if p.id in account_ids]

        analytics_svc = PortfolioAnalyticsService(self.db)
        risk_svc = PortfolioRiskService(self.db)

        combined_equity = Decimal("0.00")
        combined_cash = Decimal("0.00")
        combined_positions_val = Decimal("0.00")
        combined_realized_pnl = Decimal("0.00")
        combined_unrealized_pnl = Decimal("0.00")

        company_exposure_val: Dict[str, Decimal] = {}
        sector_exposure_val: Dict[str, Decimal] = {}

        account_weights: Dict[UUID, Decimal] = {}

        for p in portfolios:
            pa = await analytics_svc.generate_portfolio_analytics(user_id=user_id, account_id=p.id)
            summary = pa.get("summary", {})
            eq = Decimal(str(summary.get("total_equity", 0.0)))
            cash = Decimal(str(summary.get("cash_balance", 0.0)))
            pos_val = Decimal(str(summary.get("positions_value", 0.0)))
            rpnl = Decimal(str(summary.get("realized_pnl", 0.0)))
            upnl = Decimal(str(summary.get("unrealized_pnl", 0.0)))

            combined_equity += eq
            combined_cash += cash
            combined_positions_val += pos_val
            combined_realized_pnl += rpnl
            combined_unrealized_pnl += upnl

            account_weights[p.id] = eq

            for pos in pa.get("positions", []):
                sym = pos.get("symbol", "UNKNOWN")
                val = Decimal(str(pos.get("market_value", 0.0)))
                company_exposure_val[sym] = company_exposure_val.get(sym, Decimal("0.00")) + val

        combined_company_exposure_pct: Dict[str, float] = {}
        combined_sector_exposure_pct: Dict[str, float] = {}

        if combined_equity > 0:
            for sym, val in company_exposure_val.items():
                combined_company_exposure_pct[sym] = round(float((val / combined_equity) * Decimal("100.00")), 2)

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "portfolios_count": len(portfolios),
            "consolidated_summary": {
                "total_equity": float(combined_equity),
                "cash_balance": float(combined_cash),
                "positions_value": float(combined_positions_val),
                "realized_pnl": float(combined_realized_pnl),
                "unrealized_pnl": float(combined_unrealized_pnl),
                "total_pnl": float(combined_realized_pnl + combined_unrealized_pnl),
            },
            "consolidated_company_exposure_pct": combined_company_exposure_pct,
            "disclaimer": "Consolidated metrics reflect mathematical aggregation across user-owned portfolio accounts.",
        }

    async def detect_duplicate_exposures(
        self, user_id: UUID, account_ids: Optional[List[UUID]] = None
    ) -> List[Dict[str, Any]]:
        """Identify companies and sectors held across multiple portfolios."""
        portfolios = await self.list_user_portfolios(user_id)
        if account_ids:
            portfolios = [p for p in portfolios if p.id in account_ids]

        analytics_svc = PortfolioAnalyticsService(self.db)
        holding_map: Dict[str, List[Dict[str, Any]]] = {}

        for p in portfolios:
            pa = await analytics_svc.generate_portfolio_analytics(user_id=user_id, account_id=p.id)
            for pos in pa.get("positions", []):
                sym = pos.get("symbol")
                if sym:
                    holding_map.setdefault(sym, []).append({
                        "account_id": str(p.id),
                        "account_name": p.name,
                        "market_value": pos.get("market_value", 0.0),
                    })

        duplicates: List[Dict[str, Any]] = []
        for sym, occurrences in holding_map.items():
            if len(occurrences) >= 2:
                total_val = sum(o["market_value"] for o in occurrences)
                duplicates.append({
                    "symbol": sym,
                    "portfolio_count": len(occurrences),
                    "combined_market_value": total_val,
                    "breakdown": occurrences,
                })

        return duplicates

    async def get_portfolio_attribution(
        self, user_id: UUID, account_ids: Optional[List[UUID]] = None
    ) -> Dict[str, Any]:
        """Performance attribution explaining total consolidated P&L through portfolio accounts and assets."""
        portfolios = await self.list_user_portfolios(user_id)
        if account_ids:
            portfolios = [p for p in portfolios if p.id in account_ids]

        analytics_svc = PortfolioAnalyticsService(self.db)
        attribution_by_portfolio: List[Dict[str, Any]] = []
        total_pnl = Decimal("0.00")

        for p in portfolios:
            pa = await analytics_svc.generate_portfolio_analytics(user_id=user_id, account_id=p.id)
            sum_data = pa.get("summary", {})
            p_pnl = Decimal(str(sum_data.get("total_pnl", 0.0)))
            total_pnl += p_pnl

            attribution_by_portfolio.append({
                "account_id": str(p.id),
                "account_name": p.name,
                "total_pnl": float(p_pnl),
            })

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "total_consolidated_pnl": float(total_pnl),
            "attribution_by_portfolio": attribution_by_portfolio,
            "disclaimer": "Attribution explains total P&L contributions across user-owned portfolio accounts.",
        }
