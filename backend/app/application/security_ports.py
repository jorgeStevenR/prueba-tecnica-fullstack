from abc import ABC, abstractmethod

from app.domain.entities import User


class PasswordHasher(ABC):
    @abstractmethod
    def verify(self, plain_password: str, password_hash: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def hash(self, plain_password: str) -> str:
        raise NotImplementedError


class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, user: User) -> str:
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(self, user: User) -> tuple[str, str]:
        raise NotImplementedError

    @abstractmethod
    def verify_access_token(self, token: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify_refresh_token(self, token: str) -> tuple[str, str]:
        raise NotImplementedError
