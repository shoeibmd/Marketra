from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_service import get_current_user
from app.db.session import get_db
from app.models.domain import User
from app.services.trading.activation_service import LiveTradingActivationService

router = APIRouter(prefix="/admin", tags=["Admin Live Activation Controls"])


class LiveActivationRequest(BaseModel):
    stage: str = Field(..., pattern="^(STAGE_A|STAGE_B)$")
    enable: bool = Field(...)
    reason: str = Field(..., min_length=5)


@router.post("/live-trading/activate", response_model=dict[str, Any])
async def activate_live_trading_stage(
    req: LiveActivationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Administrator-only endpoint to control Stage A and Stage B live activation state."""
    service = LiveTradingActivationService(db)
    try:
        res = await service.update_live_activation_stage(
            admin_user=current_user,
            stage=req.stage,
            enable=req.enable,
            reason=req.reason,
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
