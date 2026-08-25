def test_login_returns_token_and_user(client, user_a):
    response = client.post(
        "/login",
        json={"email": user_a.email, "password": "password123"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["token"]
    assert body["user"]["email"] == user_a.email


def test_login_rejects_wrong_password(client, user_a):
    response = client.post(
        "/login",
        json={"email": user_a.email, "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.get_json()["errors"] == ["Invalid email or password"]


def test_login_rejects_unknown_email(client):
    response = client.post(
        "/login",
        json={"email": "missing@example.com", "password": "password123"},
    )

    assert response.status_code == 401


def test_protected_route_requires_jwt(client):
    response = client.get("/me")

    assert response.status_code == 401
    assert response.get_json()["msg"] == "Missing Authorization Header"


def test_protected_route_rejects_malformed_jwt(client):
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )

    assert response.status_code == 422
