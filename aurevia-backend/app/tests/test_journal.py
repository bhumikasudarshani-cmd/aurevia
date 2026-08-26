def _register_and_get_token(client, email="journal@example.com"):
    client.post("/auth/register", json={"email": email, "password": "supersecret123"})
    login_resp = client.post("/auth/login", json={"email": email, "password": "supersecret123"})
    return login_resp.json()["access_token"]


def test_create_and_list_journal_entry(client):
    token = _register_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post(
        "/journal", json={"content": "Had a tough day but I journaled about it.", "mood_score": 4},
        headers=headers,
    )
    assert create_resp.status_code == 201
    assert create_resp.json()["mood_score"] == 4

    list_resp = client.get("/journal", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


def test_journal_requires_auth(client):
    resp = client.post("/journal", json={"content": "no auth"})
    assert resp.status_code == 401
