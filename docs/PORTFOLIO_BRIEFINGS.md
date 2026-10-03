# Automated Portfolio Intelligence, Periodic Research Briefings & Change Detection Architecture

## Overview
Phase 28 transforms the platform's Portfolio Intelligence and Risk Command Center into an automated, scheduled research briefing engine. It continually evaluates user portfolio snapshots, risk metrics, concentration, disclosures, and risk alerts to detect material changes (`INFO`, `MATERIAL`, `HIGH_IMPORTANCE`), generates scheduled daily/weekly/pre-market/intraday briefings with source citations, broadcasts real-time WebSocket events, and integrates with the Notification Center while maintaining strict read-only guarantees.

---

## Architecture Components

1. **Portfolio Change Detection Engine (`PortfolioChangeDetectionService`)**:
   - Monitors deltas between portfolio snapshots.
   - Detects:
     - Portfolio Value Changes ($\ge 2.0\%$)
     - Drawdown Increases ($\ge 1.0\%$)
     - Concentration Shifts ($\ge 5.0\%$)
     - New Exchange Disclosures / Financial Events
   - Assigns deterministic significance levels (`INFO`, `MATERIAL`, `HIGH_IMPORTANCE`).
   - Persists `PortfolioChangeEvent` records and emits `portfolio_change_detected` WebSocket events.

2. **Briefing Generation Engine (`PortfolioBriefingService`)**:
   - Supports briefing types: `DAILY`, `PRE_MARKET`, `INTRADAY`, `WEEKLY`.
   - Uses `RAGRetrievalEngine` for source evidence retrieval.
   - Generates structured sections:
     - `PORTFOLIO_SUMMARY`
     - `WHAT_CHANGED`
     - `RISK_CHANGES`
     - `NEWS_AND_EVENTS`
     - `BENCHMARK_COMPARISON`
     - `IMPORTANT_ALERTS`
     - `DATA_QUALITY`
     - `DISCLAIMER`
   - Briefing statuses: `COMPLETED`, `PARTIAL`, `INSUFFICIENT_DATA`, `FAILED`.
   - Broadcasts `portfolio_briefing_ready` WebSocket events and records Notification Center items.

3. **User Preferences & Scheduling**:
   - `PortfolioBriefingPreference` stores user delivery schedules, enabled briefing types, and minimum significance thresholds.

---

## Data Model & Migration
Persisted in three dedicated tables:
- `portfolio_briefing_preferences`: User briefing schedule & threshold settings.
- `portfolio_briefings`: Generated structured briefings with source evidence.
- `portfolio_change_events`: Detected material portfolio change timeline records.
- Migration: `0014_portfolio_briefings.py` chained from `0013_portfolio_risk_alerts`.

---

## REST API Specification
- `GET /api/v1/portfolio/briefings`: Fetch generated briefings list
- `GET /api/v1/portfolio/briefings/{briefing_id}`: Fetch detailed briefing payload
- `POST /api/v1/portfolio/briefings/generate`: Generate briefing on demand
- `GET /api/v1/portfolio/briefings/preferences`: Get briefing preferences
- `PUT /api/v1/portfolio/briefings/preferences`: Update briefing preferences
- `GET /api/v1/portfolio/briefings/changes`: Fetch real-time change events timeline
- `POST /api/v1/portfolio/briefings/{briefing_id}/read`: Mark briefing as read

All endpoints enforce strict user ownership and IDOR protection.

---

## Financial & Read-Only Safety Guarantees
- Live trading defaults remain strictly active (`LIVE_TRADING_ENABLED=false`, `TRADING_KILL_SWITCH=true`).
- Change detection and briefing generation operate strictly in read-only mode and cannot trigger order execution or bypass `RiskEngine`.
