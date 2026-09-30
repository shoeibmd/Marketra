# News Clustering & Duplicate Coverage Prevention

## Cluster Identification
News articles covering the same event type and company are assigned a `cluster_id` hash:
```text
cluster_id = sha256(event_type + primary_symbol)[:16]
```
This groups related coverage under a single event node in the UI and WebSocket streams, preventing alert spam.
