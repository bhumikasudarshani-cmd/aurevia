from unittest.mock import AsyncMock, patch


def _register_and_get_token(client, email="chat@example.com"):
    client.post("/auth/register", json={"email": email, "password": "supersecret123"})
    login_resp = client.post("/auth/login", json={"email": email, "password": "supersecret123"})
    return login_resp.json()["access_token"]


@patch("app.services.chat_service.ai_service.get_ai_reply", new_callable=AsyncMock)
def test_send_message_creates_session_and_replies(mock_get_reply, client):
    mock_get_reply.return_value = ("I'm here for you. Tell me more.", False)

    token = _register_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/chat", json={"message": "I'm feeling anxious today."}, headers=headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == "I'm here for you. Tell me more."
    assert body["flagged_for_safety"] is False
    assert body["session_id"]


@patch("app.services.chat_service.ai_service.get_ai_reply", new_callable=AsyncMock)
def test_chat_requires_auth(mock_get_reply, client):
    resp = client.post("/chat", json={"message": "hello"})
    assert resp.status_code == 401
    mock_get_reply.assert_not_called()
