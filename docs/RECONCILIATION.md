# Reconciliation & Order State Machine

## Overview
`ReconciliationService` continuously compares local `BrokerOrderMapping` against broker execution state to identify status or quantity discrepancies (`MATCHED`, `STATUS_MISMATCH`, `QUANTITY_MISMATCH`, `RECONCILIATION_REQUIRED`). Discrepancies require administrator review before order retry.
