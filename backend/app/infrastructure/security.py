from datetime import UTC, datetime, timedelta
from uuid import uuid4

import bcrypt
from jose import JWTError, jwt

from app.application.security_ports import PasswordHasher, TokenService
from app.domain.entities import User
from app.domain.exceptions import InvalidTokenError
from app.infrastructure.config import Settings


class BcryptPasswordHasher(PasswordHasher):
    def verify(self, plain_password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))

    def hash(self, plain_password: str) -> str:
        return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


class JwtTokenService(TokenService):
    algorithm = "HS256"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def create_access_token(self, user: User) -> str:
        expires_at = datetime.now(UTC) + timedelta(
            minutes=self.settings.access_token_expire_minutes
        )
        payload = {"sub": user.id, "username": user.username, "type": "access", "exp": expires_at}
        return jwt.encode(payload, self.settings.jwt_secret, algorithm=self.algorithm)

    def create_refresh_token(self, user: User) -> tuple[str, str]:
        jti = str(uuid4())
        expires_at = datetime.now(UTC) + timedelta(days=self.settings.refresh_token_expire_days)
        payload = {
            "sub": user.id,
            "username": user.username,
            "type": "refresh",
            "jti": jti,
            "exp": expires_at,
        }
        token = jwt.encode(payload, self.settings.jwt_refresh_secret, algorithm=self.algorithm)
        return token, jti

    def verify_access_token(self, token: str) -> str:
        user_id, _ = self._verify(token, self.settings.jwt_secret, expected_type="access")
        return user_id

    def verify_refresh_token(self, token: str) -> tuple[str, str]:
        user_id, jti = self._verify(token, self.settings.jwt_refresh_secret, expected_type="refresh")
        if not jti:
            raise InvalidTokenError()
        return user_id, jti

    def _verify(self, token: str, secret: str, expected_type: str) -> tuple[str, str | None]:
        try:
            payload = jwt.decode(token, secret, algorithms=[self.algorithm])
            if payload.get("type") != expected_type or not payload.get("sub"):
                raise InvalidTokenError()
            jti = str(payload["jti"]) if payload.get("jti") else None
            return str(payload["sub"]), jti
        except JWTError as exc:
            raise InvalidTokenError() from exc
