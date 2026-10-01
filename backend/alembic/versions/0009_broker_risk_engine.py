"""broker integration and risk engine

Revision ID: 0009_broker_risk_engine
Revises: 0008_paper_trading
Create Date: 2026-03-30 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0009_broker_risk_engine"
down_revision: Union[str, None] = "0008_paper_trading"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. broker_accounts
    op.create_table(
        "broker_accounts",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider_name", sa.String(length=50), server_default="MOCK_LIVE_BROKER", nullable=False),
        sa.Column("account_number", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="NOT_CONFIGURED", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_broker_accounts_user_id", "broker_accounts", ["user_id"])
    op.create_index("ix_broker_accounts_provider", "broker_accounts", ["provider_name"])
    op.create_index("ix_broker_accounts_status", "broker_accounts", ["status"])

    # 2. broker_order_mappings
    op.create_table(
        "broker_order_mappings",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("client_order_id", sa.String(length=100), nullable=False, unique=True),
        sa.Column("broker_order_id", sa.String(length=100), nullable=True),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("instrument_id", sa.Uuid(as_uuid=True), sa.ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("execution_mode", sa.String(length=20), server_default="PAPER", nullable=False),
        sa.Column("side", sa.String(length=10), nullable=False),
        sa.Column("order_type", sa.String(length=20), server_default="MARKET", nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("filled_quantity", sa.Numeric(precision=18, scale=4), server_default="0", nullable=False),
        sa.Column("requested_price", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("avg_executed_price", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("status", sa.String(length=30), server_default="CREATED", nullable=False),
        sa.Column("rejection_reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_broker_order_mappings_client_id", "broker_order_mappings", ["client_order_id"])
    op.create_index("ix_broker_order_mappings_broker_id", "broker_order_mappings", ["broker_order_id"])
    op.create_index("ix_broker_order_mappings_user_id", "broker_order_mappings", ["user_id"])
    op.create_index("ix_broker_order_mappings_mode", "broker_order_mappings", ["execution_mode"])
    op.create_index("ix_broker_order_mappings_status", "broker_order_mappings", ["status"])

    # 3. risk_limits
    op.create_table(
        "risk_limits",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("max_order_quantity", sa.Numeric(precision=18, scale=4), server_default="10000", nullable=False),
        sa.Column("max_order_value", sa.Numeric(precision=18, scale=2), server_default="250000.00", nullable=False),
        sa.Column("max_portfolio_exposure_pct", sa.Numeric(precision=5, scale=2), server_default="80.00", nullable=False),
        sa.Column("daily_loss_limit", sa.Numeric(precision=18, scale=2), server_default="50000.00", nullable=False),
        sa.Column("max_open_orders", sa.Integer(), server_default="20", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_risk_limits_user_id", "risk_limits", ["user_id"])

    # 4. risk_decisions
    op.create_table(
        "risk_decisions",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_order_id", sa.String(length=100), nullable=False),
        sa.Column("rule_name", sa.String(length=50), nullable=False),
        sa.Column("input_value", sa.String(length=100), nullable=False),
        sa.Column("threshold_value", sa.String(length=100), nullable=False),
        sa.Column("decision", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_risk_decisions_user_id", "risk_decisions", ["user_id"])
    op.create_index("ix_risk_decisions_client_id", "risk_decisions", ["client_order_id"])
    op.create_index("ix_risk_decisions_decision", "risk_decisions", ["decision"])

    # 5. trading_audit_logs
    op.create_table(
        "trading_audit_logs",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("execution_mode", sa.String(length=20), server_default="PAPER", nullable=False),
        sa.Column("client_order_id", sa.String(length=100), nullable=True),
        sa.Column("details_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_trading_audit_user_id", "trading_audit_logs", ["user_id"])
    op.create_index("ix_trading_audit_action", "trading_audit_logs", ["action"])

    # 6. reconciliation_records
    op.create_table(
        "reconciliation_records",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_order_id", sa.String(length=100), nullable=False),
        sa.Column("broker_order_id", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("discrepancy_details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_reconcil_user_id", "reconciliation_records", ["user_id"])
    op.create_index("ix_reconcil_client_id", "reconciliation_records", ["client_order_id"])


def downgrade() -> None:
    op.drop_table("reconciliation_records")
    op.drop_table("trading_audit_logs")
    op.drop_table("risk_decisions")
    op.drop_table("risk_limits")
    op.drop_table("broker_order_mappings")
    op.drop_table("broker_accounts")
