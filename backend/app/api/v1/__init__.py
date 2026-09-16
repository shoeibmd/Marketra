from fastapi import APIRouter

from app.api.v1.ai import router as ai_router
from app.api.v1.auth import router as auth_router
from app.api.v1.fundamentals import router as fundamentals_router
from app.api.v1.health import router as health_router
from app.api.v1.instruments import router as instruments_router
from app.api.v1.market import router as market_router
from app.api.v1.news import router as news_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.workspaces import router as workspaces_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(instruments_router)
api_v1_router.include_router(market_router)
api_v1_router.include_router(fundamentals_router)
api_v1_router.include_router(news_router)
api_v1_router.include_router(portfolio_router)
api_v1_router.include_router(workspaces_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(health_router)

__all__ = ["api_v1_router"]
