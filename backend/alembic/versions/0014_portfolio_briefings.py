"""portfolio briefings, preferences, and change events

Revision ID: 0014_portfolio_briefings
Revises: 0013_portfolio_risk_alerts
Create Date: 2026-03-30 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0014_portfolio_briefings"
down_revision: Union[str, None] = "0013_portfolio_risk_alerts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Briefing Preferences Table
    op.create_table(
        "portfolio_briefing_preferences",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("daily_briefing_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("weekly_briefing_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("pre_market_briefing_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("intraday_briefing_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("preferred_delivery_time", sa.String(length=10), server_default="08:30", nullable=False),
        sa.Column("minimum_significance", sa.String(length=20), server_default="MATERIAL", nullable=False),
        sa.Column("sections_config_json", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_portfolio_briefing_pref_user_id", "portfolio_briefing_preferences", ["user_id"])

    # 2. Portfolio Briefings Table
    op.create_table(
        "portfolio_briefings",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("account_id", sa.Uuid(as_uuid=True), sa.ForeignKey("paper_trading_accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("briefing_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="COMPLETED", nullable=False),
        sa.Column("significance", sa.String(length=20), server_default="MATERIAL", nullable=False),
        sa.Column("summary_title", sa.String(length=255), nullable=False),
        sa.Column("content_json", sa.JSON(), nullable=False),
        sa.Column("sources_json", sa.JSON(), nullable=False),
        sa.Column("data_quality_status", sa.String(length=30), server_default="AVAILABLE", nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default="false", nullable=False),
    )
    op.create_index("ix_portfolio_briefings_user_id", "portfolio_briefings", ["user_id"])
    op.create_index("ix_portfolio_briefings_account_id", "portfolio_briefings", ["account_id"])
    op.create_index("ix_portfolio_briefings_type", "portfolio_briefings", ["briefing_type"])
    op.create_index("ix_portfolio_briefings_status", "portfolio_briefings", ["status"])
    op.create_index("ix_portfolio_briefings_generated_at", "portfolio_briefings", ["generated_at"])
    op.create_index("ix_portfolio_briefings_is_read", "portfolio_briefings", ["is_read"])

    # 3. Portfolio Change Events Table
    op.create_table(
        "portfolio_change_events",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("account_id", sa.Uuid(as_uuid=True), sa.ForeignKey("paper_trading_accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("change_type", sa.String(length=50), nullable=False),
        sa.Column("significance", sa.String(length=20), server_default="MATERIAL", nullable=False),
        sa.Column("previous_value", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("current_value", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("absolute_change", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("percentage_change", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("affected_symbols_json", sa.JSON(), nullable=False),
        sa.Column("affected_sectors_json", sa.JSON(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("data_quality_status", sa.String(length=30), server_default="AVAILABLE", nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_portfolio_changes_user_id", "portfolio_change_events", ["user_id"])
    op.create_index("ix_portfolio_changes_account_id", "portfolio_change_events", ["account_id"])
    op.create_index("ix_portfolio_changes_type", "portfolio_change_events", ["change_type"])
    op.create_index("ix_portfolio_changes_significance", "portfolio_change_events", ["significance"])
    op.create_index("ix_portfolio_changes_detected_at", "portfolio_change_events", ["detected_at"])


def downgrade() -> None:
    op.drop_table("portfolio_change_events")
    op.drop_table("portfolio_briefings")
    op.drop_table("portfolio_briefing_preferences")
