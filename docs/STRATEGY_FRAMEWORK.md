# Strategy Framework & Security Rules

## Security Rule: Server-Side Strategy Registry
To prevent arbitrary code execution, unsandboxed Python/JavaScript user-submitted code is **strictly prohibited**. All backtest simulations must use server-side registered, trusted strategy implementations configured via validated parameters.

---

## Supported Pre-Built Strategies

1. **`SMA_CROSSOVER`**:
   - **Description**: Moving Average Crossover strategy comparing a short-term SMA against a long-term SMA.
   - **Parameters**:
     - `short_window` (int, default 5): Short SMA period.
     - `long_window` (int, default 20): Long SMA period.
     - `position_size` (float, default 0.20): Percentage of cash allocated per signal.

2. **`EVENT_REACTION_RESEARCH`**:
   - **Description**: Research strategy simulating position entries following corporate financial disclosures.
   - **Parameters**:
     - `event_type` (str, default "ACQUISITION"): Filtered event category.
     - `hold_days` (int, default 5): Simulated position holding window.
     - `position_size` (float, default 0.10): Capital allocation per trade.
