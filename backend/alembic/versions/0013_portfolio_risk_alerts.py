"""portfolio risk alerts and preferences

Revision ID: 0013_portfolio_risk_alerts
Revises: 0012_portfolio_risk_analytics
Create Date: 2026-03-30 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0013_portfolio_risk_alerts"
down_revision: Union[str, None] = "0012_portfolio_risk_analytics"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Preferences Table
    op.create_table(
        "portfolio_risk_alert_preferences",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("drawdown_threshold_pct", sa.Numeric(precision=5, scale=2), server_default="5.00", nullable=False),
        sa.Column("daily_loss_threshold_pct", sa.Numeric(precision=5, scale=2), server_default="3.00", nullable=False),
        sa.Column("daily_loss_threshold_amount", sa.Numeric(precision=18, scale=2), server_default="50000.00", nullable=False),
        sa.Column("var_threshold_pct", sa.Numeric(precision=5, scale=2), server_default="5.00", nullable=False),
        sa.Column("expected_shortfall_threshold_pct", sa.Numeric(precision=5, scale=2), server_default="7.50", nullable=False),
        sa.Column("company_concentration_threshold_pct", sa.Numeric(precision=5, scale=2), server_default="25.00", nullable=False),
        sa.Column("sector_concentration_threshold_pct", sa.Numeric(precision=5, scale=2), server_default="40.00", nullable=False),
        sa.Column("correlation_threshold", sa.Numeric(precision=5, scale=2), server_default="0.75", nullable=False),
        sa.Column("volatility_threshold_pct", sa.Numeric(precision=5, scale=2), server_default="20.00", nullable=False),
        sa.Column("cooldown_minutes", sa.Integer(), server_default="60", nullable=False),
        sa.Column("enabled_alerts_json", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_portfolio_risk_pref_user_id", "portfolio_risk_alert_preferences", ["user_id"])

    # 2. Risk Alerts Table
    op.create_table(
        "portfolio_risk_alerts",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("account_id", sa.Uuid(as_uuid=True), sa.ForeignKey("paper_trading_accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("alert_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), server_default="WARNING", nullable=False),
        sa.Column("metric_name", sa.String(length=100), nullable=False),
        sa.Column("current_value", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("threshold_value", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("unit", sa.String(length=20), server_default="PCT", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="TRIGGERED", nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("data_quality_status", sa.String(length=30), server_default="AVAILABLE", nullable=False),
        sa.Column("affected_symbols_json", sa.JSON(), nullable=False),
        sa.Column("affected_sectors_json", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("recovered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_read", sa.Boolean(), server_default="false", nullable=False),
    )
    op.create_index("ix_portfolio_risk_alerts_user_id", "portfolio_risk_alerts", ["user_id"])
    op.create_index("ix_portfolio_risk_alerts_account_id", "portfolio_risk_alerts", ["account_id"])
    op.create_index("ix_portfolio_risk_alerts_alert_type", "portfolio_risk_alerts", ["alert_type"])
    op.create_index("ix_portfolio_risk_alerts_status", "portfolio_risk_alerts", ["status"])
    op.create_index("ix_portfolio_risk_alerts_fingerprint", "portfolio_risk_alerts", ["fingerprint"])
    op.create_index("ix_portfolio_risk_alerts_triggered_at", "portfolio_risk_alerts", ["triggered_at"])
    op.create_index("ix_portfolio_risk_alerts_is_read", "portfolio_risk_alerts", ["is_read"])

    # 3. Risk Alert States Table
    op.create_table(
        "portfolio_risk_alert_states",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alert_type", sa.String(length=50), nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("state", sa.String(length=20), server_default="NORMAL", nullable=False),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_value", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("cooldown_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "fingerprint", name="uq_user_risk_alert_fingerprint"),
    )
    op.create_index("ix_portfolio_risk_states_user_id", "portfolio_risk_alert_states", ["user_id"])
    op.create_index("ix_portfolio_risk_states_alert_type", "portfolio_risk_alert_states", ["alert_type"])
    op.create_index("ix_portfolio_risk_states_fingerprint", "portfolio_risk_alert_states", ["fingerprint"])


def downgrade() -> None:
    op.drop_table("portfolio_risk_alert_states")
    op.drop_table("portfolio_risk_alerts")
    op.drop_table("portfolio_risk_alert_preferences")
