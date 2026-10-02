# Phase 21 Post-Pilot Stabilization Baseline

## Overview
This document records the production release baseline for the Open Financial Terminal ("Marketra") platform following the Phase 21 post-pilot stabilization and performance optimization audit.

---

## Baseline Specifications

- **Release Version**: `v1.1.0-production-stabilization`
- **Backend Version**: `0.1.0` (Python 3.12, FastAPI, SQLAlchemy 2.0, AsyncPG, Pydantic v2)
- **Frontend Version**: `0.1.0` (Node.js v22-alpine, React 19, TypeScript 6, Vite 6, Tailwind CSS v4, Zustand 5)
- **Database Migration Revision**: `0010_controlled_live_trading` (Alembic)
- **Container Tooling**: Docker 26+, Docker Compose v2, Astral `uv` toolchain, `pnpm`
- **Target Market**: Indian Financial Market (NSE/BSE equities, INR currency, Asia/Kolkata IST)

---

## Production Safety Defaults

```env
LIVE_TRADING_ENABLED=false
TRADING_KILL_SWITCH=true
RISK_ENGINE_ENABLED=true
BROKER_CONFIGURED=false
DEBUG=false
```

- **AUTOMATED STRATEGIES**: Strictly `PAPER ONLY`. Direct broker access is prohibited.
- **MANUAL LIVE TRADING**: Guarded by multi-condition Live Safety Gate, time-limited confirmation tokens, double `RiskEngine` pre-trade evaluation, and `ReconciliationService` state checks.
