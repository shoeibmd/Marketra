"""multi portfolio groups and memberships

Revision ID: 0015_multi_portfolio_intelligence
Revises: 0014_portfolio_briefings
Create Date: 2026-03-30 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0015_multi_portfolio_intelligence"
down_revision: Union[str, None] = "0014_portfolio_briefings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Portfolio Groups Table
    op.create_table(
        "portfolio_groups",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_portfolio_groups_user_id", "portfolio_groups", ["user_id"])

    # 2. Portfolio Group Memberships Table
    op.create_table(
        "portfolio_group_memberships",
        sa.Column("group_id", sa.Uuid(as_uuid=True), sa.ForeignKey("portfolio_groups.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("account_id", sa.Uuid(as_uuid=True), sa.ForeignKey("paper_trading_accounts.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("portfolio_group_memberships")
    op.drop_table("portfolio_groups")
