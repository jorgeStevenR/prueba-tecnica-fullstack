from datetime import UTC, datetime, timedelta

from app.application.security_ports import PasswordHasher, TokenService
from app.domain.entities import User
from app.domain.exceptions import InvalidCredentialsError, InvalidTokenError
from app.domain.repositories import RefreshTokenRepository, UserRepository
from app.infrastructure.config import Settings


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
        settings: Settings,
    ) -> None:
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.settings = settings

    def login(self, username: str, password: str) -> tuple[str, str]:
        user = self.user_repository.get_by_username(username)
        if user is None or not self.password_hasher.verify(password, user.password_hash):
            raise InvalidCredentialsError()

        return self._issue_tokens(user)

    def refresh(self, refresh_token: str) -> tuple[str, str]:
        user_id, jti = self.token_service.verify_refresh_token(refresh_token)
        if not self.refresh_token_repository.is_active(jti):
            raise InvalidTokenError()

        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise InvalidTokenError()

        self.refresh_token_repository.revoke(jti)
        return self._issue_tokens(user)

    def logout(self, refresh_token: str) -> None:
        try:
            _, jti = self.token_service.verify_refresh_token(refresh_token)
        except InvalidTokenError:
            return
        self.refresh_token_repository.revoke(jti)

    def get_user_from_access_token(self, access_token: str) -> User:
        user_id = self.token_service.verify_access_token(access_token)
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise InvalidTokenError()

        return user

    def _issue_tokens(self, user: User) -> tuple[str, str]:
        access_token = self.token_service.create_access_token(user)
        refresh_token, jti = self.token_service.create_refresh_token(user)
        expires_at = datetime.now(UTC) + timedelta(days=self.settings.refresh_token_expire_days)
        self.refresh_token_repository.store(jti, user.id, expires_at)
        return access_token, refresh_token
