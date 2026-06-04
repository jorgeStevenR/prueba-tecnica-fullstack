from datetime import datetime

from app.domain.entities import Number, User


def user_from_record(record: dict) -> User:
    return User(
        id=record["id"],
        username=record["username"],
        password_hash=record["password_hash"],
    )


def user_to_record(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "password_hash": user.password_hash,
    }


def number_from_record(record: dict) -> Number:
    return Number(
        id=record["id"],
        user_id=record["user_id"],
        value=record["value"],
        created_at=datetime.fromisoformat(record["created_at"]),
        updated_at=datetime.fromisoformat(record["updated_at"]),
    )


def number_to_record(number: Number) -> dict:
    return {
        "id": number.id,
        "user_id": number.user_id,
        "value": number.value,
        "created_at": number.created_at.isoformat(),
        "updated_at": number.updated_at.isoformat(),
    }
