"""event market observations

Revision ID: 0007_event_market_observations
Revises: 0006_watchlists_and_notifications
Create Date: 2026-03-30 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0007_event_market_observations"
down_revision: Union[str, None] = "0006_watchlists_and_notifications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "event_market_observations",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("event_id", sa.Uuid(as_uuid=True), sa.ForeignKey("financial_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("instrument_id", sa.Uuid(as_uuid=True), sa.ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("session_classification", sa.String(length=30), nullable=False),
        sa.Column("baseline_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("baseline_price", sa.Float(), nullable=True),
        sa.Column("price_at_event", sa.Float(), nullable=True),
        sa.Column("return_1d_pct", sa.Float(), nullable=True),
        sa.Column("return_3d_pct", sa.Float(), nullable=True),
        sa.Column("return_5d_pct", sa.Float(), nullable=True),
        sa.Column("return_10d_pct", sa.Float(), nullable=True),
        sa.Column("return_20d_pct", sa.Float(), nullable=True),
        sa.Column("volume_before", sa.Float(), nullable=True),
        sa.Column("volume_after", sa.Float(), nullable=True),
        sa.Column("volume_change_pct", sa.Float(), nullable=True),
        sa.Column("calculation_method", sa.String(length=100), server_default="PREVIOUS_CLOSE_BASELINE", nullable=False),
        sa.Column("data_status", sa.String(length=30), server_default="AVAILABLE", nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("event_id", "instrument_id", name="uq_event_instrument_observation"),
    )
    op.create_index("ix_event_market_obs_event_id", "event_market_observations", ["event_id"])
    op.create_index("ix_event_market_obs_instrument_id", "event_market_observations", ["instrument_id"])
    op.create_index("ix_event_market_obs_event_timestamp", "event_market_observations", ["event_timestamp"])
    op.create_index("ix_event_market_obs_session", "event_market_observations", ["session_classification"])
    op.create_index("ix_event_market_obs_data_status", "event_market_observations", ["data_status"])


def downgrade() -> None:
    op.drop_index("ix_event_market_obs_data_status", table_name="event_market_observations")
    op.drop_index("ix_event_market_obs_session", table_name="event_market_observations")
    op.drop_index("ix_event_market_obs_event_timestamp", table_name="event_market_observations")
    op.drop_index("ix_event_market_obs_instrument_id", table_name="event_market_observations")
    op.drop_index("ix_event_market_obs_event_id", table_name="event_market_observations")
    op.drop_table("event_market_observations")
