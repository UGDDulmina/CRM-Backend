import jwt

from jwt.exceptions import InvalidTokenError

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.users import User, UserRole


bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    database_session: Session = Depends(get_db)
) -> User:

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]}
        )

        if payload.get("type") != "access":
            raise credentials_error

        user_id = int(payload["sub"])

    except (InvalidTokenError, ValueError, TypeError):
        raise credentials_error

    user = database_session.get(User, user_id)

    if user is None or not user.is_active:
        raise credentials_error

    return user

def require_roles(*allowed_roles: UserRole):

    def role_checker(
            current_user: User = Depends(get_current_user)
    ) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission"
                    "to perform this action"
                )
            )

        return current_user

    return role_checker