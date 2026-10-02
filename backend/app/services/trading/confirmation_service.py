import hashlib
import json
import logging
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import OrderConfirmation, User

logger = logging.getLogger("terminal.confirmation_service")


def compute_order_snapshot_hash(order_params: dict[str, Any]) -> str:
    """Compute deterministic SHA-256 hash of immutable order parameters."""
    raw_qty = order_params.get("quantity")
    try:
        qty_str = str(Decimal(str(raw_qty))) if raw_qty is not None else "0"
    except Exception:
        qty_str = str(raw_qty)

    raw_price = order_params.get("requested_price")
    try:
        price_str = str(Decimal(str(raw_price))) if raw_price is not None else ""
    except Exception:
        price_str = str(raw_price) if raw_price is not None else ""

    normalized = {
        "symbol": str(order_params.get("symbol", "")).upper().strip(),
        "side": str(order_params.get("side", "")).upper().strip(),
        "quantity": qty_str,
        "order_type": str(order_params.get("order_type", "MARKET")).upper().strip(),
        "requested_price": price_str,
        "execution_mode": str(order_params.get("execution_mode", "PAPER")).upper().strip(),
    }
    encoded = json.dumps(normalized, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class ConfirmationService:
    """Service for time-limited, parameter-bound order confirmations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_confirmation(
        self,
        user: User,
        client_order_id: str,
        order_params: dict[str, Any],
        ttl_minutes: int = 5,
    ) -> OrderConfirmation:
        """Create time-bound order confirmation with snapshot parameter hash."""
        token = f"CONF_{uuid.uuid4().hex}"
        snap_hash = compute_order_snapshot_hash(order_params)
        expires_at = datetime.now(UTC) + timedelta(minutes=ttl_minutes)

        confirmation = OrderConfirmation(
            id=uuid.uuid4(),
            confirmation_token=token,
            client_order_id=client_order_id,
            user_id=user.id,
            snapshot_hash=snap_hash,
            order_params_json=order_params,
            is_used=False,
            is_invalidated=False,
            expires_at=expires_at,
        )
        self.db.add(confirmation)
        await self.db.commit()
        await self.db.refresh(confirmation)
        return confirmation

    async def validate_and_consume_confirmation(
        self,
        user: User,
        confirmation_token: str,
        current_order_params: dict[str, Any],
    ) -> tuple[bool, str]:
        """Validate confirmation token, snapshot parameter hash, expiration, and mark as single-use."""
        stmt = select(OrderConfirmation).where(OrderConfirmation.confirmation_token == confirmation_token)
        res = await self.db.execute(stmt)
        conf = res.scalar_one_or_none()

        if not conf or conf.user_id != user.id:
            return False, "CONFIRMATION_NOT_FOUND: Confirmation token not found or unauthorized"

        if conf.is_used:
            return False, "CONFIRMATION_ALREADY_USED: Confirmation token has already been consumed"

        if conf.is_invalidated:
            return False, "CONFIRMATION_INVALIDATED: Confirmation token was previously invalidated"

        now_utc = datetime.now(UTC)
        exp_utc = conf.expires_at if conf.expires_at.tzinfo else conf.expires_at.replace(tzinfo=UTC)
        if exp_utc < now_utc:
            conf.is_invalidated = True
            await self.db.commit()
            return False, "CONFIRMATION_EXPIRED: Order confirmation token has expired (5-minute limit exceeded)"

        # Parameter snapshot hash comparison
        current_hash = compute_order_snapshot_hash(current_order_params)
        if current_hash != conf.snapshot_hash:
            conf.is_invalidated = True
            await self.db.commit()
            return False, "CONFIRMATION_PARAMETER_MISMATCH: Order parameters changed after confirmation was generated"

        # Consume token
        conf.is_used = True
        await self.db.commit()
        return True, "CONFIRMATION_VALIDATED"
