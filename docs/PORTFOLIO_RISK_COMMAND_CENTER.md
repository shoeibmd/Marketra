# Portfolio Risk Command Center & Executive Portfolio Intelligence

## Overview
Phase 27 consolidates all existing Portfolio Intelligence (Phase 24), Portfolio Risk Analytics (Phase 25), Risk Monitoring & Alerts (Phase 26), Benchmark Analytics, and AI Research capabilities into a single, unified Portfolio Risk Command Center. The Command Center provides executive observability, historical trend visualization, benchmark comparison (NIFTY50 & SENSEX), risk alert tracking, stress test simulation, and exportable structured risk reports.

---

## Command Center Architecture

1. **Executive Summary Cockpit**:
   - Total Portfolio Equity & Cash Balance
   - Total Return %, Realized P&L, Unrealized P&L
   - Max Drawdown %, Volatility %, Sharpe & Sortino Ratios
   - Historical 95% VaR & Expected Shortfall (CVaR 95%)
   - Active Risk Alerts Count & Data Quality Status

2. **Benchmark Comparison Engine**:
   - Compares portfolio period returns (1D, 1W, 1M, 3M, 6M, YTD, ALL) against Indian market benchmark indices (`NIFTY50`, `SENSEX`).

3. **Risk Metrics & Exposure Center**:
   - Asset & sector concentration breakdown, Herfindahl-Hirschman Index (HHI), top concentration contributors, and marginal risk contribution by asset and sector.

4. **Correlation & Stress Testing Commands**:
   - Pearson return correlation matrix over synchronized daily OHLCV bars.
   - Pre-configured (NIFTY50 -10% to +10%) and custom stress test scenarios.

5. **AI Portfolio Risk Copilot**:
   - RAG AI Assistant integration retrieving authorized Command Center risk metrics, active alerts, and stress test scenarios for source-grounded answers. Operates strictly in READ-ONLY mode.

6. **Exportable Risk Report**:
   - Generates structured Markdown & JSON risk report containing a mandatory disclaimer:
     *"Analytical information only. Historical and hypothetical metrics do not guarantee future portfolio performance."*

---

## REST API Specification
- `GET /api/v1/portfolio/risk-command-center`: Consolidated Command Center data payload
- `GET /api/v1/portfolio/risk-command-center/history`: Historical snapshot risk trends
- `GET /api/v1/portfolio/risk-command-center/export`: Downloadable structured risk report

All endpoints enforce strict user ownership and IDOR protection.

---

## Safety & Read-Only Guarantees
- Production live-trading safety gates remain active (`LIVE_TRADING_ENABLED=false`, `TRADING_KILL_SWITCH=true`).
- Command Center and AI Copilot operate strictly in READ-ONLY mode and cannot execute orders or modify risk limits.
