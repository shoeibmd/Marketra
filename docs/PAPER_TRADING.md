# Paper Trading Environment

## Overview
Phase 14 introduces a 100% simulated paper trading environment for virtual Indian equity instruments (NSE/BSE). Users can manage virtual capital (default ₹10,00,000 INR), execute Market and Limit simulated buy/sell orders, track positions, realized & unrealized P&L, order history, and trade execution ledgers without real money or broker connections.

---

## Safety & Non-Broker Guarantee
- **PAPER TRADING ONLY**: Zero connection to real stockbrokers or live exchange execution APIs.
- **NO REAL MONEY**: All account capital and position valuations are virtual.
- **DISCLAIMER**: Every UI panel and API response clearly states: `"PAPER TRADING — SIMULATION ONLY — NO REAL MONEY OR BROKER EXECUTION"`.

---

## Domain Models & Financial Precision

- `PaperTradingAccount`: `id`, `user_id`, `name`, `initial_cash` (Decimal), `available_cash` (Decimal).
- `PaperOrder`: `id`, `account_id`, `instrument_id`, `side` (`BUY`/`SELL`), `order_type` (`MARKET`/`LIMIT`), `quantity` (Decimal), `executed_price` (Decimal), `status` (`PENDING`, `EXECUTED`, `REJECTED`).
- `PaperPosition`: `id`, `account_id`, `instrument_id`, `quantity` (Decimal), `average_entry_price` (Decimal), `realized_pnl` (Decimal).
- `PaperTrade`: `id`, `account_id`, `order_id`, `instrument_id`, `side`, `quantity`, `execution_price`, `fees`, `slippage`, `realized_pnl`.
- `PaperPortfolioSnapshot`: `id`, `account_id`, `timestamp`, `cash`, `positions_value`, `total_equity`, `unrealized_pnl`, `realized_pnl`.

All financial storage uses exact `Decimal/Numeric` precision to prevent floating-point rounding errors.

---

## Order Execution Rules & Validation

1. **BUY Orders**:
   - Validation: Requires `available_cash >= (quantity * execution_price) + fee`.
   - Rejection: Returns `INSUFFICIENT_CASH` if funds are inadequate.
   - Position Average Price Formula:
     $$ \text{New Average Entry Price} = \frac{(\text{Old Qty} \times \text{Old Avg Price}) + (\text{Buy Qty} \times \text{Execution Price})}{\text{Old Qty} + \text{Buy Qty}} $$

2. **SELL Orders**:
   - Validation: Requires `position.quantity >= quantity`.
   - Rejection: Returns `INSUFFICIENT_POSITION` if holdings are inadequate.
   - Realized P&L Formula:
     $$ \text{Realized P\&L} = (\text{Execution Price} - \text{Average Entry Price}) \times \text{Sell Qty} - \text{Fees} $$

3. **Fees & Slippage**:
   - Default Simulated Fee: ₹20.00 fixed per execution trade.
   - Configurable Simulated Slippage: Default 0.05% applied to market orders.
