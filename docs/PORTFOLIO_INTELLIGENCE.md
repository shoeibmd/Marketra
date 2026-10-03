# Portfolio Intelligence & Risk Analytics Architecture

## Overview
The Portfolio Intelligence & Risk Analytics engine provides exact, audit-grade financial and risk metrics for user investment accounts on the Financial Terminal platform. It calculates time-series risk ratios, drawdowns, profit factors, win rates, sector concentration, and benchmark comparison statistics without floating-point precision issues.

---

## Core Analytics & Metrics

1. **Exact P&L & Valuation**:
   - `total_equity`: $\text{Cash Balance} + \sum (\text{Position Quantity} \times \text{Current Price})$
   - `realized_pnl`: Sum of all completed trade closed P&L
   - `unrealized_pnl`: Sum of current position market value minus cost basis

2. **Risk & Drawdown Metrics**:
   - `max_drawdown_pct`: Peak-to-trough decline measured against historical daily equity snapshots.
   - `sharpe_ratio`: Annualized excess return over 6.5% INR RBI Repo Rate baseline divided by equity curve standard deviation.
   - `sortino_ratio`: Annualized excess return over downside standard deviation (loss volatility).
   - `annualized_volatility_pct`: Standard deviation of daily log returns scaled by $\sqrt{252}$.

3. **Performance Metrics**:
   - `win_rate_pct`: $\frac{\text{Winning Trades}}{\text{Total Trades}} \times 100$
   - `profit_factor`: $\frac{\text{Gross Gains}}{\text{Gross Losses}}$

4. **Concentration & Benchmark Analysis**:
   - `max_position_concentration_pct`: Largest single position value as % of total equity.
   - `sector_exposure_pct`: Breakdown of portfolio equity allocation by sector.
   - `benchmark_comparison`: Relative return and alpha measured against NIFTY50 / SENSEX baselines.

---

## Data Model & Auditability

All analytical runs persist snapshot state in `portfolio_analytics_snapshots`:
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key)
- `account_id` (UUID, Foreign Key)
- `timestamp` (DateTime UTC)
- `total_equity` (Numeric 18, 2)
- `cash_balance` (Numeric 18, 2)
- `positions_value` (Numeric 18, 2)
- `realized_pnl` (Numeric 18, 2)
- `unrealized_pnl` (Numeric 18, 2)
- `drawdown_pct` (Numeric 18, 2)
- `exposure_json` (JSON - sector concentrations)
- `metrics_json` (JSON - Sharpe, Sortino, Win Rate, Data Status)

---

## REST Endpoints

- `GET /api/v1/portfolio-analytics/summary`: Comprehensive portfolio intelligence summary.
- `GET /api/v1/portfolio-analytics/risk-ratios`: Focused risk metrics and ratios.

---

## RAG AI Integration

The RAG AI Research Assistant queries `PortfolioAnalyticsService` when `user_id` is present, augmenting research evidence with current portfolio holdings, risk metrics, and position matches for queried stock symbols.
