import uuid
from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.db.session import get_db
from app.models.domain import User
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


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency: Extract and validate JWT token from Bearer header and query PostgreSQL."""
    token = credentials.credentials
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims",
            )
        stmt = select(User).where(User.email == str(email))
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        return user
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate authentication credentials",
        ) from e


@router.post("/register", response_model=UserProfileResponse)
async def register(
    req: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    """Register a new user in PostgreSQL database."""
    stmt = select(User).where(User.email == str(req.email))
    res = await db.execute(stmt)
    existing_user = res.scalar_one_or_none()

    if existing_user:
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

    user = User(
        id=uuid.uuid4(),
        email=str(req.email),
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role="user",
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserProfileResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        role=user.role,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    req: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate email/password against PostgreSQL database and return JWT token pair."""
    stmt = select(User).where(User.email == str(req.email))
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    claims = {"sub": user.email, "user_id": str(user.id), "role": user.role}
    access_token = create_access_token(claims)
    refresh_token = create_refresh_token({"sub": user.email, "user_id": str(user.id)})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    req: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh access token using valid refresh token."""
    try:
        payload = decode_token(req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")

        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token subject")

        stmt = select(User).where(User.email == str(email))
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")

        claims = {"sub": user.email, "user_id": str(user.id), "role": user.role}
        new_access = create_access_token(claims)
        new_refresh = create_refresh_token({"sub": user.email, "user_id": str(user.id)})

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
    current_user: User = Depends(get_current_user),
) -> UserProfileResponse:
    """Get profile details for authenticated user."""
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        role=current_user.role,
    )


@router.put("/password")
async def change_password(
    req: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Change authenticated user password."""
    if not verify_password(req.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    valid, err_msg = validate_password_complexity(req.new_password)
    if not valid:
        raise HTTPException(status_code=400, detail=err_msg)

    current_user.hashed_password = hash_password(req.new_password)
    db.add(current_user)
    await db.commit()

    return {"message": "Password updated successfully"}
