# Broker Configuration & Credential Protection

## Security Rules
1. **NO EXPOSED SECRETS**: Broker API keys, API secrets, access tokens, and passwords must never be stored in plaintext database columns or exposed in REST responses, WebSockets, or logs.
2. **ENVIRONMENT CONFIGURATION**: Broker connection credentials are loaded server-side via environment variables or secret managers.
