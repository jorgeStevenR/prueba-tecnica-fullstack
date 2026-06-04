from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities import Number, User


class UserRepository(ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def upsert(self, user: User) -> User:
        raise NotImplementedError


class RefreshTokenRepository(ABC):
    @abstractmethod
    def store(self, jti: str, user_id: str, expires_at: datetime) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_active(self, jti: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def revoke(self, jti: str) -> None:
        raise NotImplementedError


class NumberRepository(ABC):
    @abstractmethod
    def create(self, number: Number) -> Number:
        raise NotImplementedError

    @abstractmethod
    def get_by_id_for_user(self, number_id: str, user_id: str) -> Number | None:
        raise NotImplementedError

    @abstractmethod
    def list_for_user(self, user_id: str, page: int, limit: int) -> tuple[list[Number], int]:
        raise NotImplementedError

    @abstractmethod
    def update(self, number: Number) -> Number:
        raise NotImplementedError

    @abstractmethod
    def delete(self, number_id: str, user_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def stats_for_user(self, user_id: str) -> dict[str, int | float | None]:
        raise NotImplementedError
