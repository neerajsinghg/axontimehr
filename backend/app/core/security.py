from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from typing import Any, Dict, Optional, Tuple
import jwt

from passlib.context import CryptContext
from app.core.config import settings
from app.core.logging import logger

# Password context supporting Argon2 and Bcrypt
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashes plain text password securely using Argon2 or Bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain text password against stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def generate_secure_token(length: int = 32) -> str:
    """Generates a cryptographically secure random token string."""
    return secrets.token_urlsafe(length)

def hash_token(token: str) -> str:
    """Hashes token using SHA-256 for secure storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def create_access_token(
    subject: str,
    jti: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Creates short-lived JWT Access Token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "type": "access",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int(expire.timestamp()),
        "jti": jti or generate_secure_token(16)
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(
    subject: str,
    jti: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> Tuple[str, str, datetime]:
    """Creates long-lived JWT Refresh Token, returning (token_string, jti, expiry_datetime)."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    token_jti = jti or generate_secure_token(16)
    payload: Dict[str, Any] = {
        "sub": str(subject),
        "type": "refresh",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int(expire.timestamp()),
        "jti": token_jti
    }

    token_str = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token_str, token_jti, expire

def decode_jwt_token(token: str) -> Dict[str, Any]:
    """Decodes and validates JWT token signature and expiration."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.PyJWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")
