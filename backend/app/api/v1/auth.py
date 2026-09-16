import uuid
from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth.jwt_handler import (
    blacklist_token,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.auth.password import (
    hash_password,
    validate_password_complexity,
    verify_password,
)
from app.schemas.auth import (
    PasswordChangeRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserProfileResponse,
    UserRegisterRequest,
)

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()

_USERS_DB: dict[str, dict[str, Any]] = {
    "trader@terminal.org": {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "trader@terminal.org",
        "hashed_password": hash_password("Secret123"),
        "full_name": "Alpha Trader",
        "is_active": True,
        "is_superuser": False,
        "role": "USER",
    }
}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    """Dependency: Extract and validate JWT token from Bearer header."""
    token = credentials.credentials
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if not email or email not in _USERS_DB:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims",
            )
        return _USERS_DB[email]
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate authentication credentials",
        ) from e


@router.post("/register", response_model=UserProfileResponse)
async def register(req: UserRegisterRequest) -> UserProfileResponse:
    """Register a new user."""
    if req.email in _USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    valid, err_msg = validate_password_complexity(req.password)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg,
        )

    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": str(req.email),
        "hashed_password": hash_password(req.password),
        "full_name": req.full_name,
        "is_active": True,
        "is_superuser": False,
        "role": "USER",
    }
    _USERS_DB[req.email] = user
    return UserProfileResponse(
        id=user_id,
        email=req.email,
        full_name=req.full_name,
        is_active=True,
        is_superuser=False,
        role="USER",
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: UserLoginRequest) -> TokenResponse:
    """Authenticate email/password and return JWT token pair."""
    user = _USERS_DB.get(req.email)
    if not user or not verify_password(req.password, str(user["hashed_password"])):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    claims = {"sub": str(user["email"]), "user_id": str(user["id"]), "role": str(user["role"])}
    access_token = create_access_token(claims)
    refresh_token = create_refresh_token({"sub": str(user["email"]), "user_id": str(user["id"])})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: TokenRefreshRequest) -> TokenResponse:
    """Refresh access token using valid refresh token."""
    try:
        payload = decode_token(req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")

        email = payload.get("sub")
        user = _USERS_DB.get(email) if email else None
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        claims = {"sub": str(user["email"]), "user_id": str(user["id"]), "role": str(user["role"])}
        new_access = create_access_token(claims)
        new_refresh = create_refresh_token({"sub": str(user["email"]), "user_id": str(user["id"])})

        return TokenResponse(access_token=new_access, refresh_token=new_refresh)
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from e


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, str]:
    """Logout current user and revoke access token."""
    blacklist_token(credentials.credentials)
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> UserProfileResponse:
    """Get profile details for authenticated user."""
    return UserProfileResponse(
        id=str(current_user["id"]),
        email=str(current_user["email"]),
        full_name=current_user.get("full_name"),
        is_active=bool(current_user["is_active"]),
        is_superuser=bool(current_user["is_superuser"]),
        role=str(current_user.get("role", "USER")),
    )


@router.put("/password")
async def change_password(
    req: PasswordChangeRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, str]:
    """Change authenticated user password."""
    if not verify_password(req.old_password, str(current_user["hashed_password"])):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    valid, err_msg = validate_password_complexity(req.new_password)
    if not valid:
        raise HTTPException(status_code=400, detail=err_msg)

    current_user["hashed_password"] = hash_password(req.new_password)
    return {"message": "Password updated successfully"}
