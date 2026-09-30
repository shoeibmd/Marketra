"""Add news intelligence fields to news_articles table

Revision ID: 0002_news_intelligence_fields
Revises: 0001_initial_schema
Create Date: 2025-01-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0002_news_intelligence_fields'
down_revision: Union[str, None] = '0001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('news_articles', sa.Column('source_name', sa.String(length=100), nullable=False, server_default='Unknown Source'))
    op.add_column('news_articles', sa.Column('source_url', sa.String(length=1024), nullable=True))
    op.add_column('news_articles', sa.Column('discovered_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.add_column('news_articles', sa.Column('company', sa.String(length=255), nullable=True))
    op.add_column('news_articles', sa.Column('symbol', sa.String(length=30), nullable=True))
    op.add_column('news_articles', sa.Column('exchange', sa.String(length=20), nullable=True))
    op.add_column('news_articles', sa.Column('category', sa.String(length=50), nullable=False, server_default='general'))
    op.add_column('news_articles', sa.Column('raw_metadata', sa.JSON(), nullable=False, server_default='{}'))
    op.add_column('news_articles', sa.Column('content_hash', sa.String(length=64), nullable=True))
    op.add_column('news_articles', sa.Column('processing_status', sa.String(length=30), nullable=False, server_default='raw'))

    op.create_index(op.f('ix_news_articles_symbol'), 'news_articles', ['symbol'], unique=False)
    op.create_index(op.f('ix_news_articles_exchange'), 'news_articles', ['exchange'], unique=False)
    op.create_index(op.f('ix_news_articles_category'), 'news_articles', ['category'], unique=False)
    op.create_index(op.f('ix_news_articles_content_hash'), 'news_articles', ['content_hash'], unique=True)
    op.create_index(op.f('ix_news_articles_processing_status'), 'news_articles', ['processing_status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_news_articles_processing_status'), table_name='news_articles')
    op.drop_index(op.f('ix_news_articles_content_hash'), table_name='news_articles')
    op.drop_index(op.f('ix_news_articles_category'), table_name='news_articles')
    op.drop_index(op.f('ix_news_articles_exchange'), table_name='news_articles')
    op.drop_index(op.f('ix_news_articles_symbol'), table_name='news_articles')

    op.drop_column('news_articles', 'processing_status')
    op.drop_column('news_articles', 'content_hash')
    op.drop_column('news_articles', 'raw_metadata')
    op.drop_column('news_articles', 'category')
    op.drop_column('news_articles', 'exchange')
    op.drop_column('news_articles', 'symbol')
    op.drop_column('news_articles', 'company')
    op.drop_column('news_articles', 'discovered_at')
    op.drop_column('news_articles', 'source_url')
    op.drop_column('news_articles', 'source_name')
