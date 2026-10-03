# Multi-Portfolio Intelligence, Cross-Portfolio Analytics & Consolidated Risk Management Architecture

## Overview
Phase 29 extends the platform's portfolio architecture to support multi-portfolio management, side-by-side factual comparisons, cross-portfolio risk aggregation, duplicate exposure detection, and performance attribution across user-owned accounts while preserving strict portfolio isolation, IDOR authorization, and read-only financial safety controls.

---

## Domain Architecture & Isolation

1. **Portfolio Account Management**:
   - Reuses `PaperTradingAccount` as the core portfolio entity (`MANUAL`, `PAPER`, `BROKER`, `STRATEGY`, `CUSTOM`).
   - `PortfolioGroup` and `PortfolioGroupMembership` support user-defined portfolio grouping without cross-user leakage.

2. **Side-by-Side Portfolio Comparison (`MultiPortfolioService.compare_portfolios`)**:
   - Provides factual side-by-side metric comparisons (Equity, Return %, Realized/Unrealized P&L, Max Drawdown, VaR 95%, Volatility, HHI Index, Diversification Score).
   - Terms are neutral and non-judgmental (no "Winner" or "Best Portfolio" labels).

3. **Consolidated Risk & Exposure Aggregation (`get_consolidated_portfolio`)**:
   - Aggregates total combined equity, cash, positions value, realized and unrealized P&L.
   - Computes consolidated company/sector exposure percentages and weighted risk metrics.

4. **Duplicate Cross-Portfolio Exposure Detection (`detect_duplicate_exposures`)**:
   - Identifies overlapping company assets and sectors held across multiple user portfolios.
   - Displays portfolio count, portfolio-level exposures, and combined market value.

5. **Performance Attribution (`get_portfolio_attribution`)**:
   - Explains total consolidated P&L contributions across user-owned portfolio accounts.

---

## Data Model & Migration
- `PortfolioGroup` & `PortfolioGroupMembership`
- Migration: `0015_multi_portfolio_intelligence.py` chained from `0014_portfolio_briefings`.

---

## REST API Specification
- `GET /api/v1/portfolios`: List user portfolios
- `POST /api/v1/portfolios`: Create new portfolio
- `GET /api/v1/portfolios/compare`: Side-by-side portfolio comparison
- `GET /api/v1/portfolios/consolidated`: Consolidated multi-portfolio summary
- `GET /api/v1/portfolios/consolidated/exposure`: Duplicate exposure detection
- `GET /api/v1/portfolios/consolidated/attribution`: Performance P&L attribution

All routes enforce strict user ownership and IDOR protection.

---

## Read-Only & Trading Safety Controls
- Production live-trading safety gates remain strictly active (`LIVE_TRADING_ENABLED=false`, `TRADING_KILL_SWITCH=true`).
- Multi-portfolio analytics operate strictly in read-only mode and cannot execute trades or rebalance accounts automatically.
