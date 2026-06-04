def _login(client) -> dict:
    response = client.post("/login", json={"username": "admin", "password": "1234"})
    assert response.status_code == 200
    return response.json()


def test_login_returns_tokens(client):
    data = _login(client)
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]


def test_login_invalid_credentials(client):
    response = client.post("/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_refresh_rotates_token(client):
    tokens = _login(client)
    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refreshed = refresh_response.json()
    assert refreshed["access_token"]
    assert refreshed["refresh_token"]
    assert refreshed["refresh_token"] != tokens["refresh_token"]

    old_refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert old_refresh_response.status_code == 401


def test_logout_blacklists_refresh_token(client):
    tokens = _login(client)
    logout_response = client.post(
        "/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert logout_response.status_code == 204

    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 401
