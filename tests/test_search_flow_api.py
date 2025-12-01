import pytest
from django.test import Client


@pytest.mark.django_db
def test_stub_search_and_details_flow(settings):
    settings.ARMTEK_ENABLE_STUB = True
    client = Client()

    # register + login
    creds = {"username": "flowuser", "password": "StrongPass123"}
    client.post("/api/v1/auth/register", creds, content_type="application/json")
    login = client.post("/api/v1/auth/login", creds, content_type="application/json")
    token = login.json()["tokens"]["access"]

    headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    # search via Armtek proxy (stubbed)
    resp = client.post(
        "/api/v1/providers/armtek/search",
        {"query": "1234_KYB"},
        content_type="application/json",
        **headers,
    )
    assert resp.status_code == 200
    products = resp.json()
    assert products, "Expected at least one product"
    product = products[0]
    product_id = product["id"]
    request_id = product["request_id"]
    assert request_id

    # status is pending initially
    status_resp = client.post(
        "/api/v1/products/details/status",
        {"request_ids": [request_id]},
        content_type="application/json",
    )
    assert status_resp.status_code == 200
    assert status_resp.json()[0]["details_status"] == "pending"

    # ingest details via extension callback
    ingest_resp = client.post(
        f"/api/v1/products/{product_id}/details",
        {"weight": "1.23", "analog_code": "A1"},
        content_type="application/json",
        **{"HTTP_X_DETAILS_TOKEN": request_id},
    )
    assert ingest_resp.status_code == 201

    # poll again -> ready with details
    status_resp = client.post(
        "/api/v1/products/details/status",
        {"request_ids": [request_id]},
        content_type="application/json",
    )
    assert status_resp.status_code == 200
    data = status_resp.json()[0]
    assert data["details_status"] == "ready"
    assert data["details"]["weight"] == "1.230"


@pytest.mark.django_db
def test_search_history_list(settings):
    settings.ARMTEK_ENABLE_STUB = True
    client = Client()

    creds = {"username": "historyuser", "password": "StrongPass123"}
    client.post("/api/v1/auth/register", creds, content_type="application/json")
    login = client.post("/api/v1/auth/login", creds, content_type="application/json")
    token = login.json()["tokens"]["access"]
    headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    search_resp = client.post(
        "/api/v1/search/bulk",
        {"bulk_text": "1234_KYB"},
        content_type="application/json",
        **headers,
    )
    assert search_resp.status_code == 201

    list_resp = client.get("/api/v1/search/", **headers)
    assert list_resp.status_code == 200
    history = list_resp.json()
    assert history, "Expected at least one history entry"
    assert history[0]["query_string"]
