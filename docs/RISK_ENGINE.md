# Pre-Trade Risk Engine & Rules

## Overview
The `RiskEngine` sits mandatorily between strategy order requests and broker dispatch. Every order (paper or live) is evaluated against configurable server-side pre-trade risk rules.

---

## Pre-Trade Risk Rules

1. **`MAX_ORDER_QUANTITY`**: Rejects orders exceeding configured share limit (e.g. max 10,000 shares).
2. **`MAX_ORDER_VALUE`**: Rejects orders exceeding notional value threshold (e.g. max ₹2,50,000 INR).
3. **`DAILY_LOSS_LIMIT`**: Blocks new orders when account daily realized loss reaches threshold (e.g. ₹50,000 INR).
4. **`MAX_OPEN_ORDERS`**: Restricts active open orders count.
5. **`SYMBOL_STATUS`**: Verifies instrument `is_active == True` before order dispatch.

---

## Decision Audit Trail
Every evaluation creates an immutable `RiskDecision` record (`user_id`, `client_order_id`, `rule_name`, `input_value`, `threshold_value`, `decision`, `reason`, `created_at`).
