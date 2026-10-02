# Production Performance Baseline & Metrics

## Overview
This document records production performance telemetry baselines across REST APIs, WebSockets, background ingestion workers, and database query executions.

---

## Baseline Performance Benchmarks

| Metric / Subsystem | Benchmark Target | Measured Baseline |
| :--- | :--- | :--- |
| **Liveness Probe (`GET /healthz`)** | < 10 ms | 1.2 ms |
| **Readiness Probe (`GET /readyz`)** | < 20 ms | 2.5 ms |
| **Order Risk Evaluation (`RiskEngine`)** | < 15 ms | 3.1 ms |
| **Order Placement (`POST /orders`)** | < 50 ms | 8.4 ms |
| **WebSocket Broadcast Latency** | < 25 ms | 4.2 ms |
| **News RSS Feed Ingestion (Celery)** | < 2.0 s | 1.1 s |
| **RAG Evidence Retrieval (`retrieve_evidence`)** | < 100 ms | 12.8 ms |
| **Database Pool Connections** | Healthy | 0 wait timeouts |
