# Backtest Simulation Engine & Look-Ahead Protection

## Overview
The Backtest Simulation Engine allows deterministic historical strategy testing across Indian equity OHLCV datasets. It includes strict protection against look-ahead bias and calculates performance metrics (Total Return %, Max Drawdown %, Win Rate %, Trade Count, Equity Curve).

---

## Look-Ahead Bias Protection Architecture

To ensure strict historical validity and prevent future data leakage:
1. Historical daily OHLCV bars are processed sequentially $t = 0, 1, 2, \dots, N$.
2. At timestamp $t$, technical indicator signals (e.g. SMA crossovers) are calculated using **only** OHLCV data available at or before timestamp $t$.
3. Any buy/sell signal generated at timestamp $t$ is recorded as a pending signal and executed on the **next** candle bar $t+1$ (Open/Close price) with simulated slippage and fees.
4. Future candles $t+1, t+2, \dots$ are strictly hidden from the strategy decision function at step $t$.

---

## Performance Metrics & Metrics Calculation

- **Final Equity**: Cash + Position Valuation at bar $N$.
- **Total P&L**: $\text{Final Equity} - \text{Initial Capital}$.
- **Total Return %**: $\left( \frac{\text{Total P\&L}}{\text{Initial Capital}} \right) \times 100$.
- **Max Drawdown %**: Peak-to-trough decline measured continuously across equity snapshots:
  $$ \text{Drawdown}_t = \frac{\text{Peak Equity}_t - \text{Current Equity}_t}{\text{Peak Equity}_t} \times 100 $$
- **Win Rate %**: Percentage of closed trades yielding positive net realized P&L.
