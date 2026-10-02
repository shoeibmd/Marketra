# Production Rollback Procedures & Strategy

## Overview
This document specifies the rollback procedures for Marketra Financial Terminal release `v1.1.0`. In the event of a critical production anomaly, administrators follow these steps to restore the system safely.

---

## 1. Emergency Live Trading Halt
Prior to any deployment rollback, verify live trading is disabled:
```bash
python3 -c "from app.services.risk.risk_engine import RiskEngine; RiskEngine._STAGE_B_KILL_SWITCH = True"
```
Or set `TRADING_KILL_SWITCH=true` in environment variables.

---

## 2. Container & Application Rollback
To revert the backend and frontend services to the previous release image (`v1.0.0-phase18-baseline`):
```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

---

## 3. Database Rollback Strategy
- **Forward-Compatible Recovery**: If data has been written under Alembic revision `0010_controlled_live_trading`, do not downgrade migrations destructively.
- **Database Dump Restore**: If schema or data corruption occurred during deployment:
  1. Terminate active database connections.
  2. Restore the pre-deployment PostgreSQL dump:
     ```bash
     pg_restore -d terminal_relational /backups/pre_v1.1.0_snapshot.dump
     ```
  3. Verify revision heads:
     ```bash
     cd backend && uv run alembic current
     ```

---

## 4. Verification & Health Checks
After rolling back:
1. Run `GET /healthz` and `GET /readyz`.
2. Execute `ReconciliationService` to ensure order state integrity.
