from pathlib import Path

from tinydb import TinyDB

from app.infrastructure.config import get_settings


def get_database() -> TinyDB:
    settings = get_settings()
    db_path = Path(settings.db_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return TinyDB(db_path)
