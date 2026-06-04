from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    id: str
    username: str
    password_hash: str


@dataclass(frozen=True)
class Number:
    id: str
    user_id: str
    value: int
    created_at: datetime
    updated_at: datetime
