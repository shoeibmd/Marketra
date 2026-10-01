from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.brokers.adapter import MockLiveBrokerAdapter, PaperBrokerAdapter
from app.services.risk.risk_engine import RiskEngine

router = APIRouter(prefix="/brokers", tags=["Broker Architecture & Health"])


@router.get("", response_model=list[dict[str, Any]])
async def list_registered_brokers(
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List registered broker adapters and current configuration state. Never exposes credentials!"""
    paper_adapter = PaperBrokerAdapter(db)
    risk_engine = RiskEngine(db)
    mock_adapter = MockLiveBrokerAdapter(is_configured=risk_engine.broker_configured)

    paper_health = await paper_adapter.health_check()
    mock_health = await mock_adapter.health_check()

    return [paper_health, mock_health]


@router.get("/{broker_name}/health", response_model=dict[str, Any])
async def get_broker_health(
    broker_name: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get health status of a specific broker adapter."""
    b_name = broker_name.upper().strip()
    risk_engine = RiskEngine(db)

    if b_name == "PAPER_BROKER":
        adapter = PaperBrokerAdapter(db)
        return await adapter.health_check()
    elif b_name == "MOCK_LIVE_BROKER":
        adapter_mock = MockLiveBrokerAdapter(is_configured=risk_engine.broker_configured)
        return await adapter_mock.health_check()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Broker '{broker_name}' not found. Registered brokers: PAPER_BROKER, MOCK_LIVE_BROKER",
        )
