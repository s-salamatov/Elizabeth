from datetime import datetime
from decimal import Decimal

import pytest

from elizabeth.domain.armtek_models import SearchItem
from elizabeth.infra.armtek.exceptions import ArmtekError
from elizabeth.web.app import create_app, parse_query


class DummyArmtekService:
    def __init__(self, item=None, error: Exception | None = None):
        self.item = item
        self.error = error
        self.calls = []

    def get_main_search_item(self, *, pin: str, brand: str | None = None):
        self.calls.append({"pin": pin, "brand": brand})
        if self.error:
            raise self.error
        return self.item

    def close(self) -> None:
        pass


@pytest.mark.parametrize(
    "query,expected",
    [
        ("332101_KYB", ("332101", "KYB")),
        ("  332101 KYB  ", ("332101", "KYB")),
        ("ABC123", ("ABC123", None)),
    ],
)
def test_parse_query(query, expected):
    assert parse_query(query) == expected


def test_parse_query_empty_raises():
    with pytest.raises(ValueError):
        parse_query("   ")


def test_api_search_success():
    item = SearchItem(
        artid="11",
        pin="332101",
        brand="KYB",
        name="Амортизатор",
        price=Decimal("4011.0"),
        currency="RUB",
        quantity_available=Decimal("8"),
        delivery_date=datetime(2025, 11, 28, 16, 0, 0),
        guaranteed_delivery_date=datetime(2025, 11, 30, 16, 0, 0),
        is_analog=False,
    )
    service = DummyArmtekService(item=item)
    app = create_app(armtek_service=service)
    client = app.test_client()

    response = client.post("/api/search", json={"query": "332101 KYB"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["pin"] == "332101"
    assert data["brand"] == "KYB"
    assert data["price"] == pytest.approx(4011.0)
    assert data["delivery_date"].startswith("2025-11-28T16:00:00")
    assert service.calls == [{"pin": "332101", "brand": "KYB"}]


def test_api_search_not_found():
    service = DummyArmtekService(item=None)
    app = create_app(armtek_service=service)
    client = app.test_client()

    response = client.post("/api/search", json={"query": "UNKNOWN"})

    assert response.status_code == 404
    assert response.get_json()["error"]


def test_api_search_handles_armtek_error():
    service = DummyArmtekService(error=ArmtekError("boom"))
    app = create_app(armtek_service=service)
    client = app.test_client()

    response = client.post("/api/search", json={"query": "332101"})

    assert response.status_code == 500
    assert response.get_json()["error"]
