from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.core.config import settings

ALGORITHM = "HS256"
_BLACKLISTED_TOKENS: set[str] = set()


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Generate JWT Access Token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict[str, Any]) -> str:
    """Generate JWT Refresh Token (7 days validity)."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate JWT token."""
    if token in _BLACKLISTED_TOKENS:
        raise jwt.PyJWTError("Token has been revoked/logout")
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def blacklist_token(token: str) -> None:
    """Revoke/Blacklist JWT token."""
    _BLACKLISTED_TOKENS.add(token)
