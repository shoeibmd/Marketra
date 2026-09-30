"""Add watchlists, watchlist_companies, alert_preferences, and notifications tables

Revision ID: 0006_watchlists_and_notifications
Revises: 0005_financial_events_and_relationships
Create Date: 2025-01-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0006_watchlists_and_notifications'
down_revision: Union[str, None] = '0005_financial_events_and_relationships'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'watchlists',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, server_default='My Watchlist'),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_watchlists_user_id'), 'watchlists', ['user_id'], unique=False)

    op.create_table(
        'watchlist_companies',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('watchlist_id', sa.Uuid(), nullable=False),
        sa.Column('instrument_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['watchlist_id'], ['watchlists.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('watchlist_id', 'instrument_id', name='uq_watchlist_instrument')
    )
    op.create_index(op.f('ix_watchlist_companies_watchlist_id'), 'watchlist_companies', ['watchlist_id'], unique=False)
    op.create_index(op.f('ix_watchlist_companies_instrument_id'), 'watchlist_companies', ['instrument_id'], unique=False)

    op.create_table(
        'alert_preferences',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('minimum_importance', sa.String(length=20), nullable=False, server_default='HIGH'),
        sa.Column('event_types_json', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('filter_setting', sa.String(length=50), nullable=False, server_default='ALL_IMPORTANT_NEWS'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_alert_preferences_user_id'), 'alert_preferences', ['user_id'], unique=True)

    op.create_table(
        'notifications',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('event_id', sa.Uuid(), nullable=True),
        sa.Column('notification_type', sa.String(length=50), nullable=False, server_default='watchlist_alert'),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('importance', sa.String(length=20), nullable=False, server_default='HIGH'),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['financial_events.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'event_id', name='uq_user_event_notification')
    )
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)
    op.create_index(op.f('ix_notifications_event_id'), 'notifications', ['event_id'], unique=False)
    op.create_index(op.f('ix_notifications_is_read'), 'notifications', ['is_read'], unique=False)
    op.create_index(op.f('ix_notifications_created_at'), 'notifications', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_notifications_created_at'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_is_read'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_event_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_table('notifications')

    op.drop_index(op.f('ix_alert_preferences_user_id'), table_name='alert_preferences')
    op.drop_table('alert_preferences')

    op.drop_index(op.f('ix_watchlist_companies_instrument_id'), table_name='watchlist_companies')
    op.drop_index(op.f('ix_watchlist_companies_watchlist_id'), table_name='watchlist_companies')
    op.drop_table('watchlist_companies')

    op.drop_index(op.f('ix_watchlists_user_id'), table_name='watchlists')
    op.drop_table('watchlists')
