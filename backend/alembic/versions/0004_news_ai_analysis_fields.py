"""Add AI analysis fields to news_articles table

Revision ID: 0004_news_ai_analysis_fields
Revises: 0003_article_instrument_junction
Create Date: 2025-01-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0004_news_ai_analysis_fields'
down_revision: Union[str, None] = '0003_article_instrument_junction'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('news_articles', sa.Column('ai_status', sa.String(length=20), nullable=False, server_default='pending'))
    op.add_column('news_articles', sa.Column('ai_importance', sa.String(length=20), nullable=True))
    op.add_column('news_articles', sa.Column('ai_impact', sa.String(length=20), nullable=True))
    op.add_column('news_articles', sa.Column('ai_analysis_json', sa.JSON(), nullable=True))

    op.create_index(op.f('ix_news_articles_ai_status'), 'news_articles', ['ai_status'], unique=False)
    op.create_index(op.f('ix_news_articles_ai_importance'), 'news_articles', ['ai_importance'], unique=False)
    op.create_index(op.f('ix_news_articles_ai_impact'), 'news_articles', ['ai_impact'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_news_articles_ai_impact'), table_name='news_articles')
    op.drop_index(op.f('ix_news_articles_ai_importance'), table_name='news_articles')
    op.drop_index(op.f('ix_news_articles_ai_status'), table_name='news_articles')

    op.drop_column('news_articles', 'ai_analysis_json')
    op.drop_column('news_articles', 'ai_impact')
    op.drop_column('news_articles', 'ai_importance')
    op.drop_column('news_articles', 'ai_status')
