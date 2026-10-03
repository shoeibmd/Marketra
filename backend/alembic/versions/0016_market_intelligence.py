"""market regime snapshots and anomaly records

Revision ID: 0016_market_intelligence
Revises: 0015_multi_portfolio_intelligence
Create Date: 2026-03-30 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0016_market_intelligence"
down_revision: Union[str, None] = "0015_multi_portfolio_intelligence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Market Regime Snapshots Table
    op.create_table(
        "market_regime_snapshots",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("regime_classification", sa.String(length=30), nullable=False),
        sa.Column("nifty50_return_pct", sa.Numeric(precision=18, scale=2), server_default="0.00", nullable=False),
        sa.Column("market_breadth_ratio", sa.Numeric(precision=18, scale=2), server_default="1.00", nullable=False),
        sa.Column("realized_volatility_pct", sa.Numeric(precision=18, scale=2), server_default="15.00", nullable=False),
        sa.Column("data_quality_status", sa.String(length=30), server_default="AVAILABLE", nullable=False),
        sa.Column("metrics_json", sa.JSON(), nullable=False),
    )
    op.create_index("ix_market_regime_timestamp", "market_regime_snapshots", ["timestamp"])
    op.create_index("ix_market_regime_class", "market_regime_snapshots", ["regime_classification"])

    # 2. Market Anomaly Records Table
    op.create_table(
        "market_anomaly_records",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("anomaly_type", sa.String(length=50), nullable=False),
        sa.Column("symbol", sa.String(length=30), nullable=True),
        sa.Column("sector", sa.String(length=100), nullable=True),
        sa.Column("observed_value", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("baseline_value", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("deviation_pct", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("data_quality_status", sa.String(length=30), server_default="AVAILABLE", nullable=False),
    )
    op.create_index("ix_market_anomaly_timestamp", "market_anomaly_records", ["timestamp"])
    op.create_index("ix_market_anomaly_type", "market_anomaly_records", ["anomaly_type"])
    op.create_index("ix_market_anomaly_symbol", "market_anomaly_records", ["symbol"])
    op.create_index("ix_market_anomaly_sector", "market_anomaly_records", ["sector"])


def downgrade() -> None:
    op.drop_table("market_anomaly_records")
    op.drop_table("market_regime_snapshots")
