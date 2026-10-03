# Advanced Portfolio Risk, Correlation & Stress Testing Architecture

## Overview
Phase 25 extends the platform's Portfolio Intelligence capability with production-grade risk, correlation, diversification, and stress testing analytics. All analytics utilize exact `Decimal/Numeric` precision to prevent binary floating-point rounding errors and enforce strict user ownership / IDOR protection across REST APIs and RAG AI Assistant interfaces.

---

## Analytical Methodologies

### 1. Portfolio Stress Testing
- **Deterministic Parallel Shocks**:
  - Global Market Shocks: NIFTY50 (-10%, -5%, -3%, -1%, +1%, +3%, +5%, +10%)
  - Sector-Level Shocks: E.g., IT -10%, Banking -10%, Energy -10%
  - Holding-Level Shocks: E.g., RELIANCE -10%, TCS -10%
  - Custom Scenarios: Custom combination of symbol/sector percentage shocks.
- **Calculated Outputs**: Current Portfolio Value, Scenario Portfolio Value, Absolute P&L Impact, Percentage Portfolio Impact, Company Impact, Sector Impact.
- **Labeling & Transparency**: Explicitly labeled as hypothetical scenarios without forecasting or return guarantees.

### 2. Value at Risk (VaR) and Expected Shortfall (CVaR)
- **Historical VaR**: Percentile rank method over historical daily portfolio return distribution at 90%, 95%, and 99% confidence levels.
- **Parametric VaR**: Normal distribution assumption ($VaR = Z_{\alpha} \times \sigma_p - \mu_p$).
- **Expected Shortfall (CVaR)**: Conditional expectation of loss given returns fall beyond the VaR threshold.
- **Data Quality Safeguards**: Requires a minimum of 5 daily snapshot observations ($n \ge 5$). Returns `INSUFFICIENT_DATA` status when observation count is inadequate.

### 3. Correlation Analytics
- **Holding Correlation Matrix**: Pearson correlation $r_{x,y} = \frac{\text{Cov}(X,Y)}{\sigma_X \sigma_Y}$ calculated across synchronized daily OHLCV closing price returns.
- **Highly Correlated Pairs**: Automatically flags holding pairs with $r \ge 0.70$.
- **Observational Disclaimer**: Explicitly states correlation reflects historical co-movement and does not imply causation.

### 4. Diversification & Concentration Analytics
- **Herfindahl-Hirschman Index (HHI)**: $HHI = \sum w_i^2$ where $w_i$ is position weight.
- **Effective Number of Constituents**: $N_{\text{eff}} = \frac{1}{HHI}$.
- **Diversification Score**: Scale from 0 to 100 based on effective constituents and concentration distribution.

### 5. Risk Contribution
- **Marginal Risk Contribution**: Percentage contribution of each holding and sector to portfolio volatility, reconciled to 100%.

---

## Data Model & Migration
Snapshot state is persisted in `portfolio_risk_snapshots`:
- Migration: `0012_portfolio_risk_analytics.py`
- Revision chain: `0011_portfolio_intelligence` $\rightarrow$ `0012_portfolio_risk_analytics`

---

## REST API Specification
- `GET /api/v1/portfolio/risk/summary`: Comprehensive portfolio risk summary
- `GET /api/v1/portfolio/risk/var`: VaR & Expected Shortfall metrics
- `GET /api/v1/portfolio/risk/expected-shortfall`: Standalone CVaR metrics
- `GET /api/v1/portfolio/risk/correlation`: Holding correlation matrix
- `GET /api/v1/portfolio/risk/diversification`: Diversification score & HHI
- `GET /api/v1/portfolio/risk/contribution`: Asset/Sector risk contribution
- `POST /api/v1/portfolio/risk/stress-test`: Run custom stress scenarios
- `GET /api/v1/portfolio/risk/history`: Historical risk snapshots

---

## Safety & Read-Only Guarantees
- Live trading defaults remain strictly active (`LIVE_TRADING_ENABLED=false`, `TRADING_KILL_SWITCH=true`).
- Stress testing and risk analytics operate in read-only mode and cannot trigger order execution or bypass the `RiskEngine`.
