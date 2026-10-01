from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.models.domain import ReconciliationRecord, User
from app.services.trading.reconciliation_service import ReconciliationService

router = APIRouter(prefix="/reconciliation", tags=["Order Reconciliation"])


@router.get("", response_model=list[dict[str, Any]])
async def list_reconciliation_records(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List reconciliation records for current user (enforces strict user IDOR protection)."""
    stmt = (
        select(ReconciliationRecord)
        .where(ReconciliationRecord.user_id == current_user.id)
        .order_by(ReconciliationRecord.created_at.desc())
    )
    res = await db.execute(stmt)
    records = res.scalars().all()

    return [
        {
            "id": str(r.id),
            "client_order_id": r.client_order_id,
            "broker_order_id": r.broker_order_id,
            "status": r.status,
            "discrepancy_details": r.discrepancy_details,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]


@router.post("/{client_order_id}/reconcile", response_model=dict[str, Any])
async def reconcile_order(
    client_order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Trigger on-demand order state reconciliation with broker adapter."""
    service = ReconciliationService(db)
    rec = await service.reconcile_order(current_user, client_order_id)

    return {
        "id": str(rec.id),
        "client_order_id": rec.client_order_id,
        "broker_order_id": rec.broker_order_id,
        "status": rec.status,
        "discrepancy_details": rec.discrepancy_details,
        "created_at": rec.created_at.isoformat(),
    }
