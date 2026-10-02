# Live Trading Activation Checklist

## Overview
Live trading activation requires explicit administrative sign-off across 18 mandatory safety checks prior to enabling Stage A (`LIVE_TRADING_ENABLED=true`) or Stage B (`TRADING_KILL_SWITCH=false`).

---

## Mandatory Activation Checklist

- [ ] **1. Code Audit**: Phase 17 production audit completed with 0 Critical/High findings.
- [ ] **2. Test Suite**: 100% pass rate across all 22 backend test modules.
- [ ] **3. Secrets Audit**: Zero API keys or private credentials exposed in code or logs.
- [ ] **4. Backup Verification**: Database backup and restore dry-run verified.
- [ ] **5. Broker Health**: Broker adapter connection health and rate-limit limits verified.
- [ ] **6. Risk Engine Active**: `RISK_ENGINE_ENABLED=true` verified server-side.
- [ ] **7. Risk Limits**: Account max order quantity and max order value limits configured.
- [ ] **8. Order Confirmation**: Time-limited single-use confirmation tokens verified.
- [ ] **9. Snapshot Hashing**: SHA-256 order parameter mutation protection verified.
- [ ] **10. Reconciliation Ledger**: Zero unresolved reconciliation discrepancies.
- [ ] **11. Idempotency**: `client_order_id` duplicate submission protection verified.
- [ ] **12. Paper Mode Isolation**: Paper trading verified 100% isolated from live routing.
- [ ] **13. Strategy Security**: Unsanctioned executable code strictly prohibited.
- [ ] **14. Stage A Approval**: Admin authorization logged in `LiveTradingActivationLog`.
- [ ] **15. Stage B Approval**: Emergency kill switch deactivation authorized.
- [ ] **16. WebSocket Telemetry**: Normalized live event broadcasts operational.
- [ ] **17. Admin Monitoring**: Real-time risk and broker status dashboard operational.
- [ ] **18. Emergency Runbook**: Operational kill switch procedure tested.
