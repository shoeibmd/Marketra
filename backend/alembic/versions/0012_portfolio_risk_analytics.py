"""portfolio risk analytics snapshots

Revision ID: 0012_portfolio_risk_analytics
Revises: 0011_portfolio_intelligence
Create Date: 2026-03-30 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0012_portfolio_risk_analytics"
down_revision: Union[str, None] = "0011_portfolio_intelligence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "portfolio_risk_snapshots",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("account_id", sa.Uuid(as_uuid=True), sa.ForeignKey("paper_trading_accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("portfolio_value", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("volatility_pct", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("var_95_pct", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("expected_shortfall_95_pct", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("drawdown_pct", sa.Numeric(precision=18, scale=2), server_default="0.00", nullable=False),
        sa.Column("sector_concentration_json", sa.JSON(), nullable=False),
        sa.Column("company_concentration_json", sa.JSON(), nullable=False),
        sa.Column("diversification_metrics_json", sa.JSON(), nullable=False),
        sa.Column("risk_contribution_json", sa.JSON(), nullable=False),
        sa.Column("methodology_metadata_json", sa.JSON(), nullable=False),
        sa.Column("data_quality_status", sa.String(length=30), server_default="AVAILABLE", nullable=False),
    )
    op.create_index("ix_portfolio_risk_user_id", "portfolio_risk_snapshots", ["user_id"])
    op.create_index("ix_portfolio_risk_account_id", "portfolio_risk_snapshots", ["account_id"])
    op.create_index("ix_portfolio_risk_timestamp", "portfolio_risk_snapshots", ["timestamp"])
    op.create_index("ix_portfolio_risk_data_quality", "portfolio_risk_snapshots", ["data_quality_status"])


def downgrade() -> None:
    op.drop_table("portfolio_risk_snapshots")
