import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"

# 🔥 CONFIG
ACCESS_TOKEN_EXPIRE_MINUTES = 60   # 1h
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Use pbkdf2_sha256 to avoid bcrypt's 72-byte password truncation limit
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


# =========================
# 🔐 PASSWORD
# =========================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# =========================
# 🔐 TOKENS
# =========================
def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# =========================
# 🔐 VERIFY
# =========================
def verify_token(token: str, expected_type: str = "access") -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != expected_type:
            raise ValueError("Invalid token type")

        return payload

    except JWTError:
        raise ValueError("Invalid or expired token")


# =========================
# 🔄 REFRESH FLOW (POPRAWNY)
# =========================
def refresh_access_token(refresh_token: str) -> str:
    payload = verify_token(refresh_token, expected_type="refresh")

    user_id = payload.get("user_id")
    if not user_id:
        raise ValueError("Invalid token payload")

    return create_access_token({"user_id": user_id})