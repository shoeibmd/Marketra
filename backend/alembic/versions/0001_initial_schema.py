"""Initial baseline domain schema migration

Revision ID: 0001_initial_schema
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table(
        'workspaces',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('layout_config', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workspaces_user_id'), 'workspaces', ['user_id'], unique=False)

    op.create_table(
        'exchanges',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('country', sa.String(length=50), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exchanges_code'), 'exchanges', ['code'], unique=True)

    op.create_table(
        'instruments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('exchange_id', sa.Uuid(), nullable=True),
        sa.Column('symbol', sa.String(length=30), nullable=False),
        sa.Column('exchange_code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('isin', sa.String(length=12), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('instrument_type', sa.String(length=30), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['exchange_id'], ['exchanges.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_instruments_symbol'), 'instruments', ['symbol'], unique=False)
    op.create_index(op.f('ix_instruments_exchange_code'), 'instruments', ['exchange_code'], unique=False)
    op.create_index('ix_instruments_symbol_exchange', 'instruments', ['symbol', 'exchange_code'], unique=True)

    op.create_table(
        'provider_symbols',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('instrument_id', sa.Uuid(), nullable=False),
        sa.Column('provider_name', sa.String(length=50), nullable=False),
        sa.Column('provider_symbol', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_provider_symbols_provider_symbol', 'provider_symbols', ['provider_name', 'provider_symbol'], unique=True)

    op.create_table(
        'quotes',
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('instrument_id', sa.Uuid(), nullable=False),
        sa.Column('bid_price', sa.Float(), nullable=False),
        sa.Column('bid_size', sa.Float(), nullable=False),
        sa.Column('ask_price', sa.Float(), nullable=False),
        sa.Column('ask_size', sa.Float(), nullable=False),
        sa.Column('last_price', sa.Float(), nullable=False),
        sa.Column('last_size', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('timestamp', 'instrument_id')
    )

    op.create_table(
        'ohlcv',
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('instrument_id', sa.Uuid(), nullable=False),
        sa.Column('interval', sa.String(length=10), nullable=False),
        sa.Column('open', sa.Float(), nullable=False),
        sa.Column('high', sa.Float(), nullable=False),
        sa.Column('low', sa.Float(), nullable=False),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('timestamp', 'instrument_id', 'interval')
    )

    op.create_table(
        'fundamentals',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('instrument_id', sa.Uuid(), nullable=False),
        sa.Column('market_cap', sa.Float(), nullable=True),
        sa.Column('pe_ratio', sa.Float(), nullable=True),
        sa.Column('pb_ratio', sa.Float(), nullable=True),
        sa.Column('dividend_yield', sa.Float(), nullable=True),
        sa.Column('eps', sa.Float(), nullable=True),
        sa.Column('beta', sa.Float(), nullable=True),
        sa.Column('high_52_week', sa.Float(), nullable=True),
        sa.Column('low_52_week', sa.Float(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('instrument_id')
    )

    op.create_table(
        'news_articles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('instrument_id', sa.Uuid(), nullable=True),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=1024), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'ai_documents',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('instrument_id', sa.Uuid(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'ai_document_chunks',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('document_id', sa.Uuid(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['ai_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('ai_document_chunks')
    op.drop_table('ai_documents')
    op.drop_table('news_articles')
    op.drop_table('fundamentals')
    op.drop_table('ohlcv')
    op.drop_table('quotes')
    op.drop_table('provider_symbols')
    op.drop_table('instruments')
    op.drop_table('exchanges')
    op.drop_table('workspaces')
    op.drop_table('users')
