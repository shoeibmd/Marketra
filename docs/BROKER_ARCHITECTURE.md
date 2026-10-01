# Broker Integration Architecture

## Overview
Phase 15 establishes an extensible broker adapter layer (`BaseBrokerAdapter`) decoupling order routing and risk evaluation from specific broker execution APIs. It supports paper trading via `PaperBrokerAdapter` and sandbox simulation via `MockLiveBrokerAdapter`.

---

## Core Interfaces & Adapters

1. **`BaseBrokerAdapter` Interface**:
   - `get_provider_name() -> str`
   - `health_check() -> dict[str, Any]`
   - `place_order(order_data: dict) -> dict[str, Any]`
   - `cancel_order(broker_order_id: str) -> dict[str, Any]`
   - `get_order_status(broker_order_id: str) -> dict[str, Any]`

2. **`PaperBrokerAdapter`**: Wraps Phase 14 `PaperTradingEngine` without code duplication.
3. **`MockLiveBrokerAdapter`**: Simulated sandbox broker adapter for live lifecycle testing. Explicitly marked `SANDBOX / MOCK ONLY`.

---

## Credential Security & Isolation
- **NO CREDENTIAL LEAKS**: Broker secrets and tokens are never stored in plaintext in the database, returned via REST APIs, sent through WebSockets, or logged in application logs.
