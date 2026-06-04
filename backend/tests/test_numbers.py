def _auth_headers(client) -> dict[str, str]:
    response = client.post("/login", json={"username": "admin", "password": "1234"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_numbers_requires_auth(client):
    response = client.get("/numbers")
    assert response.status_code == 401


def test_create_list_and_delete_number(client):
    headers = _auth_headers(client)

    create_response = client.post("/numbers", json={"value": 42}, headers=headers)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["value"] == 42

    list_response = client.get("/numbers?page=1&limit=10", headers=headers)
    assert list_response.status_code == 200
    payload = list_response.json()
    assert payload["username"] == "admin"
    assert payload["total"] >= 1
    assert any(item["id"] == created["id"] for item in payload["numbers"])

    delete_response = client.delete(f"/numbers/{created['id']}", headers=headers)
    assert delete_response.status_code == 204


def test_create_number_invalid_value(client):
    headers = _auth_headers(client)
    response = client.post("/numbers", json={"value": 0}, headers=headers)
    assert response.status_code == 422
