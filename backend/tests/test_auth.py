import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.auth.jwt_handler import blacklist_token, create_access_token, decode_token
from app.core.auth.password import hash_password, validate_password_complexity, verify_password
from app.main import app

client = TestClient(app)


def test_password_hashing_and_complexity() -> None:
    hashed = hash_password("Secret123")
    assert verify_password("Secret123", hashed) is True
    assert verify_password("Wrong123", hashed) is False

    valid, _ = validate_password_complexity("Secret123")
    assert valid is True

    valid_short, msg = validate_password_complexity("short")
    assert valid_short is False
    assert "8 characters" in msg


def test_jwt_token_flow() -> None:
    token = create_access_token({"sub": "trader@terminal.org"})
    decoded = decode_token(token)
    assert decoded["sub"] == "trader@terminal.org"

    blacklist_token(token)
    with pytest.raises(jwt.PyJWTError):
        decode_token(token)


def test_auth_api_register_and_login() -> None:
    # 1. Register new user
    reg_payload = {
        "email": "newuser@terminal.org",
        "password": "SecurePassword123",
        "full_name": "New Trader",
    }
    res_reg = client.post("/api/v1/auth/register", json=reg_payload)
    assert res_reg.status_code == 200
    assert res_reg.json()["email"] == "newuser@terminal.org"

    # Duplicate registration fails
    res_dup = client.post("/api/v1/auth/register", json=reg_payload)
    assert res_dup.status_code == 400

    # 2. Login
    login_payload = {"email": "newuser@terminal.org", "password": "SecurePassword123"}
    res_login = client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    tokens = res_login.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Wrong password fails
    res_bad = client.post("/api/v1/auth/login", json={"email": "newuser@terminal.org", "password": "Wrong"})
    assert res_bad.status_code == 401

    # 3. Access protected route /me
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    res_me = client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["email"] == "newuser@terminal.org"

    # 4. Logout
    res_out = client.post("/api/v1/auth/logout", headers=headers)
    assert res_out.status_code == 200

    # Token now revoked
    res_rev = client.get("/api/v1/auth/me", headers=headers)
    assert res_rev.status_code == 401
