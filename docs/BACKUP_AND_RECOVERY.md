# Database Backup & Disaster Recovery Procedures

## Overview
This document outlines automated backup schedules, Point-In-Time Recovery (PITR), and disaster recovery procedures for PostgreSQL and TimescaleDB instances in production.

---

## Backup Strategy & Retention

1. **Automated Daily Backups**:
   - `pg_dump` snapshot taken daily at 00:00 UTC.
   - Stored in encrypted cloud storage with a 30-day retention policy.
2. **Write-Ahead Log (WAL) Archiving**:
   - Continuous WAL archiving enabled for Point-In-Time Recovery (PITR) up to any second within the past 7 days.

---

## Disaster Recovery Execution Flow

1. Stop application containers (`docker compose down`).
2. Provision new isolated database volume.
3. Restore baseline dump:
   ```bash
   pg_restore -d terminal_relational /backups/terminal_relational_latest.dump
   ```
4. Verify Alembic migration status:
   ```bash
   cd backend && uv run alembic heads
   ```
5. Restart application services (`docker compose up -d`).
6. Run `ReconciliationService` to verify zero client order ID or broker order mapping discrepancies.
