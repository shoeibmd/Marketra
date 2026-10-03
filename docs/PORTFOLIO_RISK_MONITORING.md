# Portfolio Risk Monitoring & Intelligent Alerts Architecture

## Overview
Phase 26 implements a real-time Portfolio Risk Monitoring and Intelligent Alerts Engine on the Financial Terminal platform. It periodically evaluates authorized user portfolios against user-configurable risk thresholds, manages deterministic risk alert state transitions (`NORMAL`, `TRIGGERED`, `COOLDOWN`, `RECOVERED`), enforces fingerprint deduplication and cooldown suppression, broadcasts real-time WebSocket events (`portfolio_risk_alert`, `portfolio_risk_recovered`), and integrates with the Notification Center and RAG AI Research Assistant.

---

## Alert Types & Thresholds

Supported risk alert types:
- `PORTFOLIO_DRAWDOWN`: Portfolio max drawdown exceeds threshold (e.g. 5%)
- `PORTFOLIO_DAILY_LOSS`: Daily portfolio loss exceeds percentage or absolute INR threshold
- `PORTFOLIO_VOLATILITY`: Portfolio annualized volatility exceeds threshold
- `PORTFOLIO_VAR`: Historical 95% Value at Risk exceeds threshold
- `PORTFOLIO_EXPECTED_SHORTFALL`: Conditional VaR (Expected Shortfall) exceeds threshold
- `PORTFOLIO_COMPANY_CONCENTRATION`: Single asset concentration exceeds threshold (e.g. 25%)
- `PORTFOLIO_SECTOR_CONCENTRATION`: Single sector concentration exceeds threshold (e.g. 40%)
- `PORTFOLIO_CORRELATION`: Holding return correlation exceeds threshold (e.g. 0.75)
- `PORTFOLIO_RISK_RECOVERED`: Risk condition returned safely below threshold

---

## State Machine & Deduplication

- **State Transitions**:
  - `NORMAL` $\rightarrow$ `TRIGGERED`: Condition met, risk alert generated, Notification persisted, WebSocket event broadcast, state moved to `COOLDOWN`.
  - `COOLDOWN`: Duplicate alerts suppressed during cooldown window (default 60 mins).
  - `TRIGGERED/COOLDOWN` $\rightarrow$ `RECOVERED`: Risk condition drops safely below threshold, generating `PORTFOLIO_RISK_RECOVERED` event and transitioning state to `NORMAL`.
- **Fingerprinting**: `hash(user_id, alert_type, metric_key)` ensures distinct tracking per user and risk metric.

---

## Data Model & Migration
Persisted in three dedicated tables:
- `portfolio_risk_alert_preferences`: Thresholds and cooldown configuration per user.
- `portfolio_risk_alerts`: Recorded alert and recovery instances.
- `portfolio_risk_alert_states`: State machine and cooldown expiration tracking.
- Migration: `0013_portfolio_risk_alerts.py` chained from `0012_portfolio_risk_analytics`.

---

## REST API Specification
- `GET /api/v1/portfolio/risk/alerts`: Fetch user risk alerts (filterable by status/severity)
- `GET /api/v1/portfolio/risk/alerts/active`: Fetch active `TRIGGERED` alerts
- `GET /api/v1/portfolio/risk/alerts/history`: Fetch historical alert log
- `GET /api/v1/portfolio/risk/alerts/preferences`: Fetch alert preference thresholds
- `PUT /api/v1/portfolio/risk/alerts/preferences`: Update alert preference thresholds
- `POST /api/v1/portfolio/risk/alerts/preferences/reset`: Reset preferences to system defaults
- `POST /api/v1/portfolio/risk/alerts/{alert_id}/read`: Mark alert as read
- `POST /api/v1/portfolio/risk/alerts/test`: Trigger evaluation cycle on demand

All routes enforce strict user ownership and IDOR protection.

---

## WebSocket & AI Integration
- Real-time WebSocket payloads: `portfolio_risk_alert` and `portfolio_risk_recovered`.
- RAG AI Assistant retrieves active risk alerts when answering queries such as "Why did I receive this risk alert?". AI remains strictly READ-ONLY.
