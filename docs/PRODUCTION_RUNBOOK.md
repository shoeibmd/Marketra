# Marketra Financial Terminal — Operational Runbook

## 1. Service Management
```bash
# Start all production services
docker compose -f docker-compose.prod.yml up -d

# Stop services
docker compose -f docker-compose.prod.yml down

# Restart Celery news worker
docker compose -f docker-compose.prod.yml restart backend
```

## 2. Live Operations & Verification Procedures
- **Check News Ingestion:**
  ```bash
  docker compose exec backend python scripts/seed_mock_data.py
  ```
- **Check Database Health:**
  ```bash
  curl http://localhost:8000/readyz
  ```
- **Check News Telemetry:**
  ```bash
  curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/v1/system/news-sources
  ```

## 3. Incident Troubleshooting
- **WebSocket Disconnects:** Verify token validity in localStorage and check port 8000 accessibility.
- **Worker Timeouts:** Inspect Celery task logs via `docker compose logs backend`.
- **Database Connection Pool Exhaustion:** Verify `POSTGRES_SERVER` connection limits and pool sizes in `session.py`.
