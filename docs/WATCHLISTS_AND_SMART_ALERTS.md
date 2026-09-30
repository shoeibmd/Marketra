# Personal Watchlists & Smart Alerts Engine

## Overview
Phase 12 introduces user-personalized multi-watchlists, configurable alert preferences, and the **Smart Alert Engine**. Financial events and news are continuously matched against each user's watchlists and related company role mappings to produce targeted, deduplicated alerts without noise.

---

## Key Features

1. **Personalized Multi-Watchlists**:
   - Create and organize custom watchlists (e.g., "Core Portfolio", "IT Giants", "High Growth").
   - Add/remove companies by symbol or ISIN.
   - Enforces strict IDOR user authorization checks on all CRUD routes.

2. **Smart Alert Engine**:
   - Evaluates incoming financial events against user watchlists and company relationship networks.
   - Triggers alerts for directly watched symbols as well as second-degree impact companies (e.g. key suppliers, customers, competitors).
   - Prevents duplicate alerts per `(user_id, event_id)` pair.

3. **Configurable Alert Preferences**:
   - Set minimum importance threshold (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
   - Filter by specific event categories or custom notification rules.

4. **Realtime WebSocket Alerts & Notification Center**:
   - Broadcasts `watchlist_alert` WebSocket events to connected sessions.
   - Frontend notification bell and drawer with unread counter and quick "Mark Read" actions.

---

## API Endpoints

### Watchlists (`/api/v1/watchlists`)
- `GET /` — List user watchlists (auto-creates default "My Watchlist" if none exists).
- `POST /` — Create custom watchlist.
- `GET /{watchlist_id}` — Get watchlist details & companies (strict IDOR check).
- `POST /{watchlist_id}/companies` — Add instrument to watchlist by symbol or ISIN.
- `DELETE /{watchlist_id}/companies/{symbol}` — Remove company from watchlist.
- `GET /preferences/me` — Get user alert preferences.
- `PUT /preferences/me` — Update user alert preferences.

### Notifications (`/api/v1/notifications`)
- `GET /` — List user notifications with optional unread filter & pagination.
- `GET /unread-count` — Unread count for notification badge.
- `POST /{notification_id}/read` — Mark single notification as read.
- `POST /read-all` — Mark all notifications as read.

---

## Database Models

- `Watchlist` — User-owned list (`id`, `user_id`, `name`, `description`, `is_default`, `created_at`).
- `WatchlistCompany` — Junction table (`id`, `watchlist_id`, `instrument_id`, `added_at`).
- `AlertPreference` — User settings (`user_id`, `minimum_importance`, `event_types_json`, `filter_setting`).
- `Notification` — User alert history (`id`, `user_id`, `event_id`, `title`, `summary`, `importance`, `event_type`, `matched_symbol`, `trigger_reason`, `is_read`, `created_at`).
