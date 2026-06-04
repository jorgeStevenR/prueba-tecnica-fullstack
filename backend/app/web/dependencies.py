from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.auth_service import AuthService
from app.application.number_service import NumberService
from app.domain.entities import User
from app.infrastructure.config import Settings, get_settings
from app.infrastructure.db import get_database
from app.infrastructure.repositories import (
    TinyDBNumberRepository,
    TinyDBRefreshTokenRepository,
    TinyDBUserRepository,
)
from app.infrastructure.security import BcryptPasswordHasher, JwtTokenService

bearer_scheme = HTTPBearer()


def get_auth_service(settings: Annotated[Settings, Depends(get_settings)]) -> AuthService:
    db = get_database()
    return AuthService(
        user_repository=TinyDBUserRepository(db),
        refresh_token_repository=TinyDBRefreshTokenRepository(db),
        password_hasher=BcryptPasswordHasher(),
        token_service=JwtTokenService(settings),
        settings=settings,
    )


def get_number_service() -> NumberService:
    db = get_database()
    return NumberService(number_repository=TinyDBNumberRepository(db))


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    return auth_service.get_user_from_access_token(credentials.credentials)
