# Emergency Trading Shutdown Runbook (Kill Switch)

## Overview
This runbook defines the emergency procedure to halt all live order submission immediately using the server-side kill switch (`TRADING_KILL_SWITCH=true`).

---

## Emergency Activation Protocol

1. **Triggering Kill Switch via API**:
   An authorized administrator sends a `POST /api/v1/admin/live-trading/activate` request:
   ```json
   {
     "stage": "STAGE_B",
     "enable": false,
     "reason": "Emergency market volatility halt"
   }
   ```
2. **Server-Side Enforcement**:
   Setting `TRADING_KILL_SWITCH=true` immediately causes `RiskEngine.evaluate_order_risk` to return `KILL_SWITCH_ACTIVE`, blocking all subsequent live orders before broker dispatch.
3. **Audit Record**:
   The action is recorded in `LiveTradingActivationLog` and `TradingAuditLog`.
4. **Reconciliation Inspection**:
   Run `ReconciliationService` to verify all submitted orders are in `FILLED`, `CANCELLED`, or `RECONCILIATION_REQUIRED` states.
