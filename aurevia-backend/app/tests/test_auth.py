def test_register_and_login(client):
    register_resp = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "supersecret123", "display_name": "Test User"},
    )
    assert register_resp.status_code == 201
    assert register_resp.json()["email"] == "test@example.com"

    login_resp = client.post(
        "/auth/login", json={"email": "test@example.com", "password": "supersecret123"}
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()


def test_register_duplicate_email_fails(client):
    payload = {"email": "dup@example.com", "password": "supersecret123"}
    first = client.post("/auth/register", json=payload)
    second = client.post("/auth/register", json=payload)
    assert first.status_code == 201
    assert second.status_code == 409


def test_login_wrong_password_fails(client):
    client.post("/auth/register", json={"email": "wrong@example.com", "password": "correctpass1"})
    resp = client.post("/auth/login", json={"email": "wrong@example.com", "password": "wrongpass1"})
    assert resp.status_code == 401


def test_me_requires_auth(client):
    resp = client.get("/users/me")
    assert resp.status_code == 401
