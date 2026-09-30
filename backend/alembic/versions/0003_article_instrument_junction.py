"""Add article_instruments junction table and sector column to instruments

Revision ID: 0003_article_instrument_junction
Revises: 0002_news_intelligence_fields
Create Date: 2025-01-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0003_article_instrument_junction'
down_revision: Union[str, None] = '0002_news_intelligence_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('instruments', sa.Column('sector', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_instruments_sector'), 'instruments', ['sector'], unique=False)

    op.create_table(
        'article_instruments',
        sa.Column('article_id', sa.Uuid(), nullable=False),
        sa.Column('instrument_id', sa.Uuid(), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['article_id'], ['news_articles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('article_id', 'instrument_id')
    )
    op.create_index(op.f('ix_article_instruments_sector'), 'article_instruments', ['sector'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_article_instruments_sector'), table_name='article_instruments')
    op.drop_table('article_instruments')
    op.drop_index(op.f('ix_instruments_sector'), table_name='instruments')
    op.drop_column('instruments', 'sector')
