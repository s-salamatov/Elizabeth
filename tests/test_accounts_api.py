import pytest
from django.test import Client


@pytest.mark.django_db
def test_register_and_login_returns_tokens():
    client = Client()
    payload = {
        "password": "Sup3rStrongP@ssw0rd!",
        "email": "u1@example.com",
        "phone_number": "+79000000001",
        "country": "RU",
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
        {"email": "u1@example.com", "password": "Sup3rStrongP@ssw0rd!"},
        content_type="application/json",
    )
    assert resp_login.status_code == 200
    data_login = resp_login.json()
    assert data_login["user"]["email"] == "u1@example.com"
    assert data_login["tokens"]["access"]
