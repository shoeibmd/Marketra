# Controlled Live Trading Architecture

## Overview
Phase 16 introduces controlled live trading architecture for virtual and future broker endpoints. Live order dispatch requires passing through two-stage administrative activation controls, single-use parameter-bound confirmation tokens, double `RiskEngine` evaluation, and continuous order reconciliation.

---

## Production Safety Defaults

```env
LIVE_TRADING_ENABLED=false
TRADING_KILL_SWITCH=true
RISK_ENGINE_ENABLED=true
BROKER_CONFIGURED=false
```

- **SAFE DEFAULT**: Live order submissions are blocked by server-side safety gates unless all four environment conditions pass and administrative Stage A & Stage B controls are active.
- **ISOLATION**: Paper trading (Phase 14) remains completely isolated and continues executing using `PaperBrokerAdapter`.
