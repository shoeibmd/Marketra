# Open Financial Terminal V1 Release Changelog

## V1.0.0 (2026-09-15)

### Features Implemented
- **Phase 0-1 (Monorepo Foundation)**: React + TypeScript + Vite + Tailwind CSS frontend and FastAPI + SQLAlchemy backend monorepo.
- **Phase 2 (Docker Infrastructure)**: Docker Compose setup for PostgreSQL, TimescaleDB, and Redis.
- **Phase 3 (Domain Model)**: SQLAlchemy 2.0 relational and TimescaleDB time-series models with composite instrument identity (`symbol`, `exchange_code`).
- **Phase 4-5 (Provider Abstraction & Ingestion)**: Normalized schemas, deterministic MockProvider (AAPL, MSFT, GOOGL, TSLA, SPY, BTC-USD, ETH-USD), and chunked bulk TimescaleDB ingestion pipeline.
- **Phase 6 (Realtime Pipeline)**: Redis Pub/Sub quote broadcasting and FastAPI WebSockets.
- **Phase 7 (Core REST APIs)**: Versioned REST endpoints (`/api/v1/instruments`, `/market`, `/fundamentals`, `/news`, `/portfolio`).
- **Phase 8-10 (Terminal Shell & Workspaces)**: PanelRegistry, PanelContainer, and 500ms debounced layout persistence to PostgreSQL.
- **Phases 11-15 (19 V1 Domain Panels)**: Complete suite across Market, Charts, News, Fundamentals, and Portfolio categories.
- **Phase 16 (AI & RAG Integration)**: Structured RAG query completion with source citations, confidence scores, and fact vs. interpretation separation.
- **Phase 17 (Auth & Security)**: Passlib bcrypt password hashing, JWT access/refresh token pair, and token revocation blacklist.
- **Phases 18-20 (Integration QA, Security Gate, Observability)**: End-to-end integration tests, `SECURITY.md`, JSON logging, and `/healthz/detailed` probe.
- **Phases 21-22 (Production & Release)**: Multi-stage Docker builds, production Docker Compose, Nginx reverse proxy configuration, and release documentation.
