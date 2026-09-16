# Security Architecture & Operations

## Authentication & Authorization Architecture
- **Password Security**: Passwords are hashed using `bcrypt` with `passlib`. Plaintext passwords are never logged, stored, or exposed.
- **JWT Management**: Access tokens and refresh tokens are signed with `HS256` using 256-bit environment secrets (`SECRET_KEY`).
- **Token Revocation**: Tokens are blacklisted in memory upon logout.
- **Role-Based Access Control**: API routes and workspace operations enforce ownership checks (`user_id` matches JWT claims).

## Data & API Protection
- **No API Keys in Frontend**: Provider credentials and DB secrets are kept strictly on the backend.
- **Normalized Domain Schemas**: All data served to clients uses internal Pydantic models.
- **SQL Injection Safeguards**: SQLAlchemy 2.0 ORM parameterization protects against SQL injection.
- **CORS Policy**: Configured to restrict access.

## Vulnerability Reporting
For security concerns, contact security@terminal.org.
