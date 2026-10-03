from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.ai import router as ai_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.brokers import router as brokers_router
from app.api.v1.events import router as events_router
from app.api.v1.fundamentals import router as fundamentals_router
from app.api.v1.health import router as health_router
from app.api.v1.instruments import router as instruments_router
from app.api.v1.market import router as market_router
from app.api.v1.news import router as news_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.paper import router as paper_router
from app.api.v1.market_intelligence import router as market_intelligence_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.portfolio_analytics import router as portfolio_analytics_router
from app.api.v1.portfolio_risk import router as portfolio_risk_router
from app.api.v1.portfolio_risk_alerts import router as portfolio_risk_alerts_router
from app.api.v1.multi_portfolio import router as multi_portfolio_router
from app.api.v1.portfolio_briefings import router as portfolio_briefings_router
from app.api.v1.portfolio_risk_command_center import router as portfolio_risk_command_center_router
from app.api.v1.reconciliation import router as reconciliation_router
from app.api.v1.risk import router as risk_router
from app.api.v1.trading import router as trading_router
from app.api.v1.watchlists import router as watchlists_router
from app.api.v1.workspaces import router as workspaces_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(instruments_router)
api_v1_router.include_router(market_router)
api_v1_router.include_router(market_intelligence_router)
api_v1_router.include_router(fundamentals_router)
api_v1_router.include_router(news_router)
api_v1_router.include_router(events_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(watchlists_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(paper_router)
api_v1_router.include_router(trading_router)
api_v1_router.include_router(brokers_router)
api_v1_router.include_router(risk_router)
api_v1_router.include_router(reconciliation_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(portfolio_router)
api_v1_router.include_router(portfolio_analytics_router)
api_v1_router.include_router(portfolio_risk_router)
api_v1_router.include_router(portfolio_risk_alerts_router)
api_v1_router.include_router(multi_portfolio_router)
api_v1_router.include_router(portfolio_briefings_router)
api_v1_router.include_router(portfolio_risk_command_center_router)
api_v1_router.include_router(workspaces_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(health_router)

__all__ = ["api_v1_router"]
