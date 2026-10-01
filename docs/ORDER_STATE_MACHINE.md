# Order Lifecycle State Machine

## Overview
Orders transition deterministically through defined states in `BrokerOrderMapping`.

---

## Order State Transitions

```
[CREATED]
    ↓
[RISK_PENDING] ──(Risk Rejected)──> [RISK_REJECTED]
    ↓ (Risk Approved)
[SUBMITTING]
    ↓
[SUBMITTED] ──(Broker Rejected)──> [REJECTED]
    ↓ (Broker Ack)
[ACKNOWLEDGED]
    ↓
[PARTIALLY_FILLED] / [FILLED] / [CANCELLED]
```

---

## Client Order ID Idempotency
Submitting a duplicate `client_order_id` returns the existing order record immediately without creating duplicate broker executions.
