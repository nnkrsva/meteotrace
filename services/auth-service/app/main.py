import uuid

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

from app.security import create_access_token, decode_access_token, hash_password, verify_password

app = FastAPI(title="MeteoTrace auth-service", version="0.1.0")
bearer = HTTPBearer()

# Stage 1: in-memory storage; PostgreSQL is introduced at stage 2.
_users: dict[str, dict] = {}


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105 - OAuth2 token type, not a secret


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "auth-service"}


@app.post("/api/v1/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: Credentials) -> UserOut:
    email = body.email.lower()
    if email in _users:
        raise HTTPException(status.HTTP_409_CONFLICT, "User already exists")
    user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "role": "user",
        "password_hash": hash_password(body.password),
    }
    _users[email] = user
    return UserOut(**user)


@app.post("/api/v1/auth/login", response_model=Token)
def login(body: Credentials) -> Token:
    user = _users.get(body.email.lower())
    if not user or not verify_password(user["password_hash"], body.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return Token(access_token=create_access_token(user["id"], user["role"]))


@app.get("/api/v1/auth/me", response_model=UserOut)
def me(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> UserOut:
    try:
        payload = decode_access_token(creds.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from exc
    for user in _users.values():
        if user["id"] == payload["sub"]:
            return UserOut(**user)
    raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
