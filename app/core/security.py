from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password
)

def create_access_token(user_id: int) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(
    minutes=settings.access_token_expire_minutes
)

    payload = {
        "sub": str(user_id),
        "exp": expiration,
        "type": "access"
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )