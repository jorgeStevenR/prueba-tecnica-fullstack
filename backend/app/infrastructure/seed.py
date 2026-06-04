from app.domain.entities import User
from app.domain.repositories import UserRepository
from app.infrastructure.security import BcryptPasswordHasher


def seed_default_user(user_repository: UserRepository) -> None:
    if user_repository.get_by_username("admin") is not None:
        return

    password_hasher = BcryptPasswordHasher()
    user_repository.upsert(
        User(
            id="admin-user",
            username="admin",
            password_hash=password_hasher.hash("1234"),
        )
    )
