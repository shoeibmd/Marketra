import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import LiveTradingActivationLog, TradingAuditLog, User
from app.services.risk.risk_engine import RiskEngine

logger = logging.getLogger("terminal.activation_service")


class LiveTradingActivationService:
    """Service for managing administrative two-stage live trading activation and emergency kill switch controls."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def update_live_activation_stage(
        self,
        admin_user: User,
        stage: str,
        enable: bool,
        reason: str,
        source_ip: str | None = None,
    ) -> dict[str, Any]:
        """Update live trading activation Stage A or Stage B with admin authorization and audit logging."""
        if admin_user.role != "admin" and not admin_user.is_superuser:
            raise ValueError("USER_NOT_AUTHORIZED: Administrator permission is required to manage live trading activation")

        risk_engine = RiskEngine(self.db)
        prev_state = {
            "live_trading_enabled": risk_engine.live_trading_enabled,
            "trading_kill_switch": risk_engine.trading_kill_switch,
        }

        stage_clean = stage.upper().strip()
        if stage_clean == "STAGE_A":
            RiskEngine._STAGE_A_LIVE_ENABLED = enable
            action = "ENABLE_LIVE_TRADING_STAGE_A" if enable else "DISABLE_LIVE_TRADING_STAGE_A"
        elif stage_clean == "STAGE_B":
            RiskEngine._STAGE_B_KILL_SWITCH = not enable  # Stage B enable means kill switch deactivated
            action = "DEACTIVATE_KILL_SWITCH_STAGE_B" if enable else "ACTIVATE_KILL_SWITCH_STAGE_B"
        else:
            raise ValueError(f"INVALID_STAGE: Supported stages are STAGE_A and STAGE_B (got '{stage}')")

        updated_risk_engine = RiskEngine(self.db)
        new_state = {
            "live_trading_enabled": updated_risk_engine.live_trading_enabled,
            "trading_kill_switch": updated_risk_engine.trading_kill_switch,
        }

        # Log to LiveTradingActivationLog
        log = LiveTradingActivationLog(
            id=uuid.uuid4(),
            admin_user_id=admin_user.id,
            action=action,
            stage=stage_clean,
            previous_state_json=prev_state,
            new_state_json=new_state,
            reason=reason,
            source_ip=source_ip,
        )
        self.db.add(log)

        # Log to TradingAuditLog
        audit = TradingAuditLog(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            action=action,
            execution_mode="LIVE",
            details_json={
                "stage": stage_clean,
                "reason": reason,
                "previous_state": prev_state,
                "new_state": new_state,
            },
        )
        self.db.add(audit)

        await self.db.commit()
        logger.info(f"Admin {admin_user.email} updated {stage_clean} ({action}). Reason: {reason}")

        return {
            "status": "SUCCESS",
            "action": action,
            "stage": stage_clean,
            "previous_state": prev_state,
            "current_state": new_state,
            "effective_live_trading_active": updated_risk_engine.live_trading_enabled and not updated_risk_engine.trading_kill_switch,
        }
