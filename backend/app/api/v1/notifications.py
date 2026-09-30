import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.models.domain import Notification, User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[dict[str, Any]])
async def list_user_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List notifications for current user with optional unread filter and pagination."""
    stmt = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))

    stmt = stmt.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
    res = await db.execute(stmt)
    notifications = res.scalars().all()

    return [
        {
            "id": str(n.id),
            "event_id": str(n.event_id) if n.event_id else None,
            "title": n.title,
            "summary": n.summary,
            "importance": n.importance,
            "event_type": n.event_type,
            "matched_symbol": n.matched_symbol,
            "trigger_reason": n.trigger_reason,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        }
        for n in notifications
    ]


@router.get("/unread-count", response_model=dict[str, Any])
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get count of unread notifications for current user."""
    stmt = select(func.count()).select_from(Notification).where(
        Notification.user_id == current_user.id,
        Notification.is_read.is_(False),
    )
    res = await db.execute(stmt)
    count = res.scalar() or 0
    return {"unread_count": count}


@router.post("/{notification_id}/read", response_model=dict[str, Any])
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Mark a notification as read (with strict user IDOR protection)."""
    try:
        n_uuid = uuid.UUID(notification_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid notification ID format")

    stmt = select(Notification).where(Notification.id == n_uuid)
    res = await db.execute(stmt)
    n = res.scalar_one_or_none()

    if not n or n.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found or unauthorized")

    n.is_read = True
    db.add(n)
    await db.commit()

    return {"status": "success", "id": str(n.id), "is_read": True}


@router.post("/read-all", response_model=dict[str, Any])
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Mark all unread notifications as read for current user."""
    stmt = (
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    res = await db.execute(stmt)
    await db.commit()

    return {"status": "success", "updated_count": res.rowcount}
