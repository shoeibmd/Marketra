# Daily Operations Runbook

## Overview
This runbook defines daily operational verification procedures for system administrators managing the Marketra Financial Terminal in production.

---

## Daily Operational Verification Tasks

### 1. System Liveness & Readiness Probes
- `GET /healthz` — Verify HTTP 200 `{"status": "ok"}`.
- `GET /readyz` — Verify HTTP 200 `{"status": "ready"}`.
- `GET /api/v1/brokers` — Verify `PAPER_BROKER` and `MOCK_LIVE_BROKER` statuses.

### 2. Pre-Trade Risk & Safety Gate Verification
- `GET /api/v1/risk/status` — Verify:
  - `LIVE_TRADING_ENABLED` = `false`
  - `TRADING_KILL_SWITCH` = `true`
  - `RISK_ENGINE_ENABLED` = `true`

### 3. Background News & Event Pipeline
- `GET /api/v1/system/news-sources` — Verify RSS ingestion feeds (NSE, BSE, SEBI, RBI) and deduplication telemetry.

### 4. Database & Redis Telemetry
- Check PostgreSQL connection pool utilization.
- Check Redis memory usage and Celery task queue depth.

### 5. Order Reconciliation Ledger
- `GET /api/v1/reconciliation` — Verify zero unresolved reconciliation discrepancies (`RECONCILIATION_REQUIRED`).
