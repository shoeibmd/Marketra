"""controlled live trading and order confirmation

Revision ID: 0010_controlled_live_trading
Revises: 0009_broker_risk_engine
Create Date: 2026-03-30 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0010_controlled_live_trading"
down_revision: Union[str, None] = "0009_broker_risk_engine"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. live_trading_activation_logs
    op.create_table(
        "live_trading_activation_logs",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("admin_user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("stage", sa.String(length=20), nullable=False),
        sa.Column("previous_state_json", sa.JSON(), nullable=False),
        sa.Column("new_state_json", sa.JSON(), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("source_ip", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_activation_logs_admin_id", "live_trading_activation_logs", ["admin_user_id"])
    op.create_index("ix_activation_logs_action", "live_trading_activation_logs", ["action"])

    # 2. order_confirmations
    op.create_table(
        "order_confirmations",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("confirmation_token", sa.String(length=100), nullable=False, unique=True),
        sa.Column("client_order_id", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("order_params_json", sa.JSON(), nullable=False),
        sa.Column("is_used", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_invalidated", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_order_confirmations_token", "order_confirmations", ["confirmation_token"])
    op.create_index("ix_order_confirmations_client_id", "order_confirmations", ["client_order_id"])
    op.create_index("ix_order_confirmations_user_id", "order_confirmations", ["user_id"])


def downgrade() -> None:
    op.drop_table("order_confirmations")
    op.drop_table("live_trading_activation_logs")
