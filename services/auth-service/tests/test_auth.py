import pytest
from fastapi.testclient import TestClient

from app import main
from app.security import hash_password, verify_password

client = TestClient(main.app)
CREDS = {"email": "user@example.com", "password": "correct-horse-1"}


@pytest.fixture(autouse=True)
def clean_users():
    main._users.clear()


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_password_is_hashed_with_argon2id():
    hashed = hash_password("secret-pass")
    assert hashed.startswith("$argon2id$")
    assert verify_password(hashed, "secret-pass")
    assert not verify_password(hashed, "wrong-pass")


def test_register_login_and_me():
    r = client.post("/api/v1/auth/register", json=CREDS)
    assert r.status_code == 201
    assert "password_hash" not in r.json()

    token = client.post("/api/v1/auth/login", json=CREDS).json()["access_token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == CREDS["email"]


def test_duplicate_registration_is_rejected():
    client.post("/api/v1/auth/register", json=CREDS)
    assert client.post("/api/v1/auth/register", json=CREDS).status_code == 409


def test_wrong_password_is_rejected():
    client.post("/api/v1/auth/register", json=CREDS)
    r = client.post("/api/v1/auth/login", json={**CREDS, "password": "wrong-password"})
    assert r.status_code == 401


def test_short_password_is_rejected():
    r = client.post("/api/v1/auth/register", json={**CREDS, "password": "123"})
    assert r.status_code == 422


def test_invalid_token_is_rejected():
    r = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert r.status_code == 401
