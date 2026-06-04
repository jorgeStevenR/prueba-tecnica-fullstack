import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    db_path = tmp_path / "test.db.json"
    os.environ["JWT_SECRET"] = "test-access-secret"
    os.environ["JWT_REFRESH_SECRET"] = "test-refresh-secret"
    os.environ["DB_URL"] = str(db_path)
    os.environ["PORT"] = "8080"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "15"
    os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"

    from app.infrastructure.config import get_settings

    get_settings.cache_clear()

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()
