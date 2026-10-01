# Trading Safety Gates & Kill Switch

## Mandatory Order Flow

```
User / Strategy Order Request
          ↓
  Order Pre-Check
          ↓
Confirmation Token Generation
          ↓
Manual Order Confirmation
          ↓
Re-Evaluate RiskEngine & Safety Gate
          ↓
Broker Dispatch / Reconciliation
```

1. **KILL SWITCH OVERRIDE**: `TRADING_KILL_SWITCH=true` immediately overrides live trading activation and blocks all live orders.
2. **PARAMETER MUTATION PROTECTION**: Order confirmations compute a SHA-256 parameter snapshot hash. If any parameter changes between confirmation generation and execution, the confirmation is invalidated.
