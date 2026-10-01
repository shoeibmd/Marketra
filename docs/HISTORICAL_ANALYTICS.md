# Advanced Historical Market Analytics & Event Correlation

## Overview
Phase 13 introduces a factual historical market analytics layer linking **News**, **Financial Events**, **Company Relationships**, and **Historical OHLCV Market Data**. It enables observation of historical asset behavior around documented financial events without generating trading recommendations, future price predictions, or unproven causality claims.

---

## Core Capabilities

1. **Event Market Observation Domain Model (`EventMarketObservation`)**:
   - Stores derived window observations (1D, 3D, 5D, 10D, 20D percentage returns and volume changes) linked to `FinancialEvent` and `Instrument`.
   - Leaves underlying `OHLCV` and `Quote` tables as immutable single sources of truth without data duplication.

2. **Trading Session Classification (Asia/Kolkata IST)**:
   - `PRE_MARKET`: Mon–Fri < 09:15 IST
   - `INTRADAY`: Mon–Fri 09:15 to 15:30 IST
   - `POST_MARKET`: Mon–Fri > 15:30 IST
   - `WEEKEND`: Saturday / Sunday
   - `MARKET_HOLIDAY`: Designated trading calendar holidays

3. **Baseline & Return Calculations**:
   - Baseline price explicitly set to preceding trading session close.
   - Calculates 1D, 3D, 5D, 10D, 20D percentage return windows.
   - Calculates volume changes relative to baseline.
   - Marks observations as `INSUFFICIENT` if market history is incomplete.

4. **Aggregate Statistics & Strict Sample Size Rules ($n < 5$)**:
   - Displays mean, median, min, max, positive observations, and negative observations.
   - Strict rule: If sample size $n < 5$, aggregate statistics display `"Insufficient historical sample for meaningful aggregate statistics."`.
   - Never implies statistical reliability or predictive validity.

5. **REST APIs & RAG AI Assistant Integration**:
   - `/api/v1/events/{id}/market-context` — Factual event market observations.
   - `/api/v1/company/{symbol}/event-analytics` — Company event return timeline.
   - `/api/v1/analytics/event-types` — Aggregate statistics per event category.
   - `/api/v1/analytics/compare` — Side-by-side factual comparison.
   - Extended `RAGRetrievalEngine` to retrieve historical observations with strictly non-causal language.

6. **Frontend Analytics Panels**:
   - `EVENT_MARKET_CONTEXT`: Event timestamp, session classification, and multi-window return observations.
   - `COMPANY_HISTORICAL_ANALYTICS`: Company-level aggregate statistics with sample size indicators.
   - `HISTORICAL_EVENT_ANALYTICS`: Factual side-by-side company comparison.

---

## Compliance & Non-Causality Disclaimer
- "Statistical correlation does not imply causation."
- "Historical observations reflect past price measurements and do not predict future returns."
- Strictly excludes buy/sell recommendations, target prices, and future forecasts.
