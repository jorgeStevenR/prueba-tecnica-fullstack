from datetime import UTC, datetime
from uuid import uuid4

from app.domain.entities import Number
from app.domain.exceptions import NumberNotFoundError, ValidationError
from app.domain.repositories import NumberRepository


class NumberService:
    def __init__(self, number_repository: NumberRepository) -> None:
        self.number_repository = number_repository

    def create_number(self, user_id: str, value: int) -> Number:
        self._validate_value(value)
        now = datetime.now(UTC)
        number = Number(
            id=str(uuid4()),
            user_id=user_id,
            value=value,
            created_at=now,
            updated_at=now,
        )
        return self.number_repository.create(number)

    def list_numbers(self, user_id: str, page: int, limit: int) -> tuple[list[Number], int]:
        if page < 1:
            raise ValidationError("Page must be greater than 0")
        if limit < 1 or limit > 100:
            raise ValidationError("Limit must be between 1 and 100")

        return self.number_repository.list_for_user(user_id, page, limit)

    def get_number(self, user_id: str, number_id: str) -> Number:
        number = self.number_repository.get_by_id_for_user(number_id, user_id)
        if number is None:
            raise NumberNotFoundError()

        return number

    def update_number(self, user_id: str, number_id: str, value: int) -> Number:
        self._validate_value(value)
        current = self.get_number(user_id, number_id)
        updated = Number(
            id=current.id,
            user_id=current.user_id,
            value=value,
            created_at=current.created_at,
            updated_at=datetime.now(UTC),
        )
        return self.number_repository.update(updated)

    def delete_number(self, user_id: str, number_id: str) -> None:
        deleted = self.number_repository.delete(number_id, user_id)
        if not deleted:
            raise NumberNotFoundError()

    def get_stats(self, user_id: str) -> dict[str, int | float | None]:
        return self.number_repository.stats_for_user(user_id)

    def _validate_value(self, value: int) -> None:
        if value <= 0:
            raise ValidationError("Value must be greater than 0")
