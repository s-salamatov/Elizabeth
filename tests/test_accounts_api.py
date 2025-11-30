import pytest
from django.test import Client


@pytest.mark.django_db
def test_register_and_login_returns_tokens():
    client = Client()
    payload = {
        "username": "user1",
        "password": "Password123",
        "email": "u1@example.com",
    }
    resp = client.post(
        "/api/v1/auth/register", payload, content_type="application/json"
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access" in data["tokens"]
    assert "refresh" in data["tokens"]

    # Login should work with same credentials
    resp_login = client.post(
        "/api/v1/auth/login",
        {"username": "user1", "password": "Password123"},
        content_type="application/json",
    )
    assert resp_login.status_code == 200
    data_login = resp_login.json()
    assert data_login["user"]["username"] == "user1"
    assert data_login["tokens"]["access"]
