# Phase 18 Release Baseline Specification

## Overview
This document records the exact production release baseline for the Open Financial Terminal ("Marketra") platform following the Phase 17 production audit and Phase 18 operational readiness.

---

## Baseline Specifications

- **Release Version**: `v1.0.0-phase18-baseline`
- **Backend Version**: `0.1.0` (Python 3.12, FastAPI, SQLAlchemy 2.0, AsyncPG, Pydantic v2)
- **Frontend Version**: `0.1.0` (Node.js v22-alpine, React 19, TypeScript 6, Vite 6, Tailwind CSS v4, Zustand 5)
- **Database Migration Revision**: `0010_controlled_live_trading` (Alembic)
- **Container Tooling**: Docker 26+, Docker Compose v2, Astral `uv` toolchain, `pnpm`
- **Target Market**: Indian Financial Market (NSE/BSE equities, INR currency, Asia/Kolkata IST)

---

## Safe Production Defaults

```env
LIVE_TRADING_ENABLED=false
TRADING_KILL_SWITCH=true
RISK_ENGINE_ENABLED=true
BROKER_CONFIGURED=false
DEBUG=false
```

- **SAFE DEFAULT**: All live trading is disabled by default.
- **ISOLATION**: Paper trading (Phase 14) is completely isolated and operates via `PaperBrokerAdapter`.
