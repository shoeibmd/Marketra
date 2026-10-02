# Release Notes — v1.1.0 (Production Stabilization)

## Overview
Marketra Financial Terminal `v1.1.0-production-stabilization` includes all core platform subsystems across Phases 1 through 21, configured for the Indian Financial Market (NSE/BSE).

---

## Major Subsystems Included

1. **Indian Market News Intelligence**: Public RSS regulatory ingestion (NSE, BSE, SEBI, RBI), SHA-256 deduplication, multi-company entity matcher, and AI event extraction.
2. **AI Financial Research Assistant**: Source-grounded RAG query parser, prompt-injection protection, citation generation, and conversational session memory.
3. **Structured Financial Event Intelligence**: Financial event clustering, role mappings, company timelines, and evidenced network graphs.
4. **Personal Watchlists & Smart Alerts**: User multi-watchlists, configurable importance preferences, second-degree event notifications, and WebSocket alerts.
5. **Historical Market Analytics**: Factual window returns (1D, 3D, 5D, 10D, 20D), IST session classification, sample-size thresholding ($n < 5$), and neutral observational terminology.
6. **Paper Trading & Strategy Simulator**: Exact Decimal financial precision, order validation, look-ahead protected backtesting engine, and pre-built strategy registry (`SMA_CROSSOVER`, `EVENT_REACTION_RESEARCH`).
7. **Broker Adapter & Pre-Trade Risk Engine**: `BaseBrokerAdapter`, `RiskEngine` evaluating configurable order/portfolio limits, order state machine, idempotency via `client_order_id`, and `ReconciliationService`.
8. **Controlled Live Trading & Safety Gate**: Two-stage admin live activation (Stage A & Stage B), 5-minute single-use parameter-bound confirmation tokens, double `RiskEngine` evaluation, and emergency kill switch override (`TRADING_KILL_SWITCH=true`).

---

## Safety & Non-Broker Notice
- **DEFAULT SETTINGS**: `LIVE_TRADING_ENABLED=false`, `TRADING_KILL_SWITCH=true`, `RISK_ENGINE_ENABLED=true`, `BROKER_CONFIGURED=false`.
- **AUTOMATED STRATEGIES**: `PAPER ONLY`. Automated strategies cannot submit live broker orders.
