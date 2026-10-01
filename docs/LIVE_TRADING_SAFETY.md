# Production Live Trading Safety Controls

## Production Defaults

```env
LIVE_TRADING_ENABLED=false
TRADING_KILL_SWITCH=true
RISK_ENGINE_ENABLED=true
BROKER_CONFIGURED=false
```

---

## Live Trading Safety Gate Conditions
A live order will ONLY be dispatched if ALL four server-side conditions pass simultaneously:
1. `LIVE_TRADING_ENABLED == true`
2. `TRADING_KILL_SWITCH == false`
3. `BROKER_CONFIGURED == true`
4. `RISK_ENGINE_ENABLED == true`

If any condition fails, the order is rejected immediately on the server.
