"""安全工具：密码哈希（bcrypt）与 JWT 签发/校验"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import jwt, JWTError

from app.config import settings


def hash_password(password: str) -> str:
    """bcrypt 哈希密码"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    """返回 user_id（sub），失败返回 None"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
