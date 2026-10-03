# Advanced Market Intelligence, Sector Analytics, Market Regime & Anomaly Detection Architecture

## Overview
Phase 30 establishes the market intelligence layer connecting market-wide indices, sector performance, market breadth, volatility regimes, statistical anomaly detection, and disclosure event context across the terminal platform.

$$\text{MARKET} \longrightarrow \text{SECTORS} \longrightarrow \text{COMPANIES} \longrightarrow \text{NEWS/EVENTS} \longrightarrow \text{PORTFOLIOS} \longrightarrow \text{RISK} \longrightarrow \text{AI RESEARCH}$$

---

## Architectural Services

1. **Market Intelligence & Breadth Engine (`MarketIntelligenceService`)**:
   - Index tracking for NIFTY50 & SENSEX.
   - Market breadth calculations: Advances, Declines, Unchanged, Advance/Decline Ratio, Advancing Volume vs Declining Volume.

2. **Sector Intelligence & Sector Correlation**:
   - Calculates sector returns, volatility %, volume, and sector-to-sector Pearson correlation matrix across Indian equity sectors.

3. **Market Regime Classification**:
   - Deterministic classification into descriptive categories (`TRENDING_UP`, `TRENDING_DOWN`, `RANGE_BOUND`, `HIGH_VOLATILITY`, `LOW_VOLATILITY`, `MIXED`, `INSUFFICIENT_DATA`).
   - Persisted in `market_regime_snapshots`.

4. **Market Anomaly Detection Engine**:
   - Detects statistical price shocks ($\ge 3\%$), volume surges, and correlation breakdowns.
   - Emits real-time WebSocket event `market_anomaly` and records instances in `market_anomaly_records`.

---

## Data Model & Migration
Persisted in two dedicated tables:
- `market_regime_snapshots`: Historical regime classifications.
- `market_anomaly_records`: Statistically detected price and volume anomalies.
- Migration: `0016_market_intelligence.py` chained from `0015_multi_portfolio_intelligence`.

---

## REST API Specification
- `GET /api/v1/market-intelligence/overview`: Overview indices & breadth
- `GET /api/v1/market-intelligence/breadth`: Standalone breadth meter
- `GET /api/v1/market-intelligence/sectors`: Sector performance & correlation matrix
- `GET /api/v1/market-intelligence/regime`: Historical market regime classification
- `GET /api/v1/market-intelligence/anomalies`: Statistically detected unusual price/volume shocks

---

## Safety & Read-Only Guarantees
- Live trading defaults remain strictly active (`LIVE_TRADING_ENABLED=false`, `TRADING_KILL_SWITCH=true`).
- All market intelligence services operate strictly in read-only mode without making forecasts or investment recommendations.
