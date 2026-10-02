import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import (
    AlertPreference,
    EventCompanyRelationship,
    FinancialEvent,
    Notification,
    Watchlist,
    WatchlistCompany,
)

logger = logging.getLogger("terminal.alert_engine")


class SmartAlertEngine:
    """Evaluates financial events against user watchlists and alert preferences."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def evaluate_event_alerts(
        self,
        event: FinancialEvent,
        event_relationships: list[EventCompanyRelationship],
    ) -> list[Notification]:
        """Match event and related companies to active user watchlists & trigger alerts."""
        if not event or not event.id:
            return []

        # 1. Collect all company instrument_ids involved in event
        related_instrument_ids = {rel.instrument_id for rel in event_relationships if rel.instrument_id}
        if event.primary_company_id:
            related_instrument_ids.add(event.primary_company_id)

        if not related_instrument_ids:
            return []

        # 2. Find all watchlists containing any of these instruments
        wl_stmt = (
            select(Watchlist.user_id, WatchlistCompany.instrument_id)
            .join(WatchlistCompany, WatchlistCompany.watchlist_id == Watchlist.id)
            .where(WatchlistCompany.instrument_id.in_(related_instrument_ids))
        )
        wl_res = await self.db.execute(wl_stmt)
        matched_pairs = wl_res.all()  # [(user_id, instrument_id)]

        if not matched_pairs:
            return []

        user_matched_instruments: dict[uuid.UUID, set[uuid.UUID]] = {}
        for user_id, inst_id in matched_pairs:
            user_matched_instruments.setdefault(user_id, set()).add(inst_id)

        triggered_notifications: list[Notification] = []

        # 3. Evaluate each user's preferences & deduplicate
        for user_id, inst_ids in user_matched_instruments.items():
            pref_stmt = select(AlertPreference).where(AlertPreference.user_id == user_id)
            pref_res = await self.db.execute(pref_stmt)
            pref = pref_res.scalar_one_or_none()

            filter_setting = pref.filter_setting if pref else "ALL_IMPORTANT_NEWS"

            # Check threshold
            if filter_setting == "HIGH_CRITICAL_ONLY" and event.importance not in ["HIGH", "CRITICAL"]:
                continue

            # Check duplicate alert for (user_id, event_id)
            dup_stmt = select(Notification).where(
                Notification.user_id == user_id,
                Notification.event_id == event.id,
            )
            dup_res = await self.db.execute(dup_stmt)
            if dup_res.scalar_one_or_none():
                continue

            notification = Notification(
                id=uuid.uuid4(),
                user_id=user_id,
                event_id=event.id,
                notification_type="watchlist_alert",
                title=f"Smart Alert: {event.event_title}",
                summary=event.event_summary or "",
                importance=event.importance,
                is_read=False,
            )
            self.db.add(notification)
            triggered_notifications.append(notification)

        if triggered_notifications:
            await self.db.commit()
            logger.info(f"Smart Alert Engine created {len(triggered_notifications)} notifications for event {event.id}")

        return triggered_notifications
