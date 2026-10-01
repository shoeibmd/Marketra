# Broker Order Reconciliation

## Overview
Reconciliation compares client order states against broker execution responses. Discrepancies create a `ReconciliationRecord` marked `RECONCILIATION_REQUIRED` for administrative audit.
