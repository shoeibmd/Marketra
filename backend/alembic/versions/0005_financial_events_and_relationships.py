"""Add financial_events and event_company_relationships tables

Revision ID: 0005_financial_events_and_relationships
Revises: 0004_news_ai_analysis_fields
Create Date: 2025-01-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0005_financial_events_and_relationships'
down_revision: Union[str, None] = '0004_news_ai_analysis_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'financial_events',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('news_id', sa.Uuid(), nullable=True),
        sa.Column('cluster_id', sa.String(length=64), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False, server_default='OTHER'),
        sa.Column('event_title', sa.String(length=512), nullable=False),
        sa.Column('event_summary', sa.Text(), nullable=False),
        sa.Column('event_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('primary_company_id', sa.Uuid(), nullable=True),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('importance', sa.String(length=20), nullable=False, server_default='MEDIUM'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.90'),
        sa.Column('source_name', sa.String(length=100), nullable=False, server_default='Exchange Disclosure'),
        sa.Column('source_url', sa.String(length=1024), nullable=True),
        sa.Column('verified_facts', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('ai_analysis_json', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('potential_impact', sa.String(length=20), nullable=False, server_default='NEUTRAL'),
        sa.Column('uncertainties', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['news_id'], ['news_articles.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['primary_company_id'], ['instruments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_financial_events_news_id'), 'financial_events', ['news_id'], unique=False)
    op.create_index(op.f('ix_financial_events_cluster_id'), 'financial_events', ['cluster_id'], unique=False)
    op.create_index(op.f('ix_financial_events_event_type'), 'financial_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_financial_events_event_date'), 'financial_events', ['event_date'], unique=False)
    op.create_index(op.f('ix_financial_events_primary_company_id'), 'financial_events', ['primary_company_id'], unique=False)
    op.create_index(op.f('ix_financial_events_sector'), 'financial_events', ['sector'], unique=False)
    op.create_index(op.f('ix_financial_events_importance'), 'financial_events', ['importance'], unique=False)

    op.create_table(
        'event_company_relationships',
        sa.Column('event_id', sa.Uuid(), nullable=False),
        sa.Column('instrument_id', sa.Uuid(), nullable=False),
        sa.Column('role', sa.String(length=30), nullable=False, server_default='PRIMARY_SUBJECT'),
        sa.Column('relationship_note', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['event_id'], ['financial_events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('event_id', 'instrument_id')
    )
    op.create_index(op.f('ix_event_company_relationships_role'), 'event_company_relationships', ['role'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_event_company_relationships_role'), table_name='event_company_relationships')
    op.drop_table('event_company_relationships')

    op.drop_index(op.f('ix_financial_events_importance'), table_name='financial_events')
    op.drop_index(op.f('ix_financial_events_sector'), table_name='financial_events')
    op.drop_index(op.f('ix_financial_events_primary_company_id'), table_name='financial_events')
    op.drop_index(op.f('ix_financial_events_event_date'), table_name='financial_events')
    op.drop_index(op.f('ix_financial_events_event_type'), table_name='financial_events')
    op.drop_index(op.f('ix_financial_events_cluster_id'), table_name='financial_events')
    op.drop_index(op.f('ix_financial_events_news_id'), table_name='financial_events')
    op.drop_table('financial_events')
