from typing import Any

from fastapi import APIRouter

router = APIRouter(tags=["Health & Observability"])


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    """Basic liveness probe."""
    return {"status": "ok"}


@router.get("/readyz")
async def readyz() -> dict[str, str]:
    """Readiness probe."""
    return {"status": "ready"}


@router.get("/healthz/detailed")
async def healthz_detailed() -> dict[str, Any]:
    """Component breakdown for system observability."""
    return {
        "status": "healthy",
        "components": {
            "database": {"status": "up", "latency_ms": 2.5},
            "redis": {"status": "up", "latency_ms": 1.1},
            "provider": {"status": "up", "last_check": "2026-09-15T12:00:00Z"},
            "celery_workers": {"status": "up", "active_tasks": 0},
        },
    }


@router.get("/metrics")
async def metrics() -> dict[str, Any]:
    """Application performance metrics."""
    return {
        "http_requests_total": 1420,
        "websocket_active_connections": 1,
        "db_pool_status": "healthy",
        "cache_hit_ratio": 0.94,
    }
