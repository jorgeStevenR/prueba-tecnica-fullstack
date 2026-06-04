from datetime import UTC, datetime

from tinydb import Query, TinyDB

from app.domain.entities import Number, User
from app.domain.repositories import NumberRepository, RefreshTokenRepository, UserRepository
from app.infrastructure.mappers import (
    number_from_record,
    number_to_record,
    user_from_record,
    user_to_record,
)


class TinyDBUserRepository(UserRepository):
    def __init__(self, db: TinyDB) -> None:
        self.table = db.table("users")
        self.query = Query()

    def get_by_username(self, username: str) -> User | None:
        record = self.table.get(self.query.username == username)
        return user_from_record(record) if record else None

    def get_by_id(self, user_id: str) -> User | None:
        record = self.table.get(self.query.id == user_id)
        return user_from_record(record) if record else None

    def upsert(self, user: User) -> User:
        self.table.upsert(user_to_record(user), self.query.id == user.id)
        return user


class TinyDBRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, db: TinyDB) -> None:
        self.table = db.table("refresh_tokens")
        self.query = Query()

    def store(self, jti: str, user_id: str, expires_at: datetime) -> None:
        self.table.upsert(
            {
                "jti": jti,
                "user_id": user_id,
                "expires_at": expires_at.isoformat(),
                "revoked": False,
            },
            self.query.jti == jti,
        )

    def is_active(self, jti: str) -> bool:
        record = self.table.get(self.query.jti == jti)
        if record is None or record.get("revoked"):
            return False

        expires_at = datetime.fromisoformat(record["expires_at"])
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return expires_at > datetime.now(UTC)

    def revoke(self, jti: str) -> None:
        record = self.table.get(self.query.jti == jti)
        if record is None:
            return
        record["revoked"] = True
        self.table.update(record, self.query.jti == jti)


class TinyDBNumberRepository(NumberRepository):
    def __init__(self, db: TinyDB) -> None:
        self.table = db.table("numbers")
        self.query = Query()

    def create(self, number: Number) -> Number:
        self.table.insert(number_to_record(number))
        return number

    def get_by_id_for_user(self, number_id: str, user_id: str) -> Number | None:
        record = self.table.get((self.query.id == number_id) & (self.query.user_id == user_id))
        return number_from_record(record) if record else None

    def list_for_user(self, user_id: str, page: int, limit: int) -> tuple[list[Number], int]:
        records = self.table.search(self.query.user_id == user_id)
        records.sort(key=lambda item: item["created_at"], reverse=True)
        total = len(records)
        start = (page - 1) * limit
        end = start + limit
        return [number_from_record(record) for record in records[start:end]], total

    def update(self, number: Number) -> Number:
        self.table.update(
            number_to_record(number),
            (self.query.id == number.id) & (self.query.user_id == number.user_id),
        )
        return number

    def delete(self, number_id: str, user_id: str) -> bool:
        deleted = self.table.remove((self.query.id == number_id) & (self.query.user_id == user_id))
        return len(deleted) > 0

    def stats_for_user(self, user_id: str) -> dict[str, int | float | None]:
        values = [record["value"] for record in self.table.search(self.query.user_id == user_id)]
        if not values:
            return {"total": 0, "sum": 0, "average": None, "maximum": None, "minimum": None}

        return {
            "total": len(values),
            "sum": sum(values),
            "average": sum(values) / len(values),
            "maximum": max(values),
            "minimum": min(values),
        }
