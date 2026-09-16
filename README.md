# Open Financial Terminal V1

## Overview
Open Financial Terminal is an open-source, browser-based financial analytics terminal built with React, FastAPI, PostgreSQL, TimescaleDB, and Redis.

## Core Features
- **Realtime Quotes & Streaming**: Redis pub/sub + FastAPI WebSockets broadcasting normalized market quotes.
- **Interactive Technical Charts**: Candlestick charts, RSI, MACD, Volume, and VWAP overlays.
- **RAG & AI Research Assistant**: Structured AI analysis with traceable citations and clear separation of facts from interpretations.
- **Persisted Layout System**: Customizable workspace layout system with 500ms debounced auto-save.
- **Portfolio & Order Ledger**: Position tracking and unrealized P&L valuations.

## Quick Start (Development)
```bash
make up       # Start local services with Docker Compose
make test     # Run backend and frontend test suites
make lint     # Run code linters
```

## Production Deployment
```bash
docker compose -f docker-compose.prod.yml up -d
```

## License
MIT
