# Marketra Financial Terminal — Production Readiness Document

## 1. System Architecture
Marketra is built as a 100% free/open-source browser-based Financial Terminal for the Indian Market (NSE/BSE).

```text
Public News Sources (NSE, BSE, SEBI, RBI RSS)
       ↓
RSSNewsProvider / Celery Background Tasks
       ↓
CompanyMatcher (Symbol, ISIN, Name & Alias Mapping)
       ↓
AIEnrichmentProcessor (NewsAIAnalysis with Safety Rules)
       ↓
PostgreSQL 16 (Relational & Junction) & TimescaleDB (Time-series)
       ↓
FastAPI Backend (REST /api/v1 & /ws WebSockets with JWT Auth)
       ↓
Zustand Stores (Auth, Market, Workspaces, Notifications)
       ↓
React Terminal Shell (Vite, Tailwind, React Grid Layout, Toast Alerts)
```

## 2. Environment Variables & Security
Configure environment variables using `.env.example`:
- `ENVIRONMENT`: `production`
- `SECRET_KEY`: Generate via `openssl rand -hex 32`
- `POSTGRES_SERVER`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `TIMESCALE_SERVER`, `TIMESCALE_PORT`, `TIMESCALE_USER`, `TIMESCALE_PASSWORD`, `TIMESCALE_DB`
- `REDIS_URL`: `redis://redis:6379/0`
- `VITE_API_BASE_URL`: `http://localhost:8000`
- `VITE_WS_BASE_URL`: `ws://localhost:8000`

## 3. Database Migration Procedures
Migrations are managed via Alembic in `backend/alembic`:
```bash
# Execute outstanding database migrations
docker compose exec backend alembic upgrade head
```

## 4. News Pipeline Telemetry & Health Monitoring
- Health probe: `GET /api/v1/health`
- Readiness probe: `GET /api/v1/health/readiness`
- Liveness probe: `GET /api/v1/health/liveness`
- News sources telemetry: `GET /api/v1/system/news-sources`
- Metrics: `GET /metrics`

## 5. Backup & Recovery Procedures
- **PostgreSQL Backup:**
  ```bash
  docker exec -t terminal_postgres pg_dump -U terminal_prod_user terminal_relational_prod > backup_relational_$(date +%Y%m%d).sql
  ```
- **PostgreSQL Restore:**
  ```bash
  cat backup_relational.sql | docker exec -i terminal_postgres psql -U terminal_prod_user -d terminal_relational_prod
  ```
