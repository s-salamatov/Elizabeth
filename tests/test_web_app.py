from datetime import datetime
from decimal import Decimal

import pytest

from elizabeth.domain.armtek_models import SearchItem
from elizabeth.domain.tokens import ArmtekSearchContext, generate_characteristics_token
from elizabeth.infra.armtek.exceptions import ArmtekError
from elizabeth.services.characteristics_repository import InMemoryArmtekCharacteristicsRepository
from elizabeth.web.app import create_app, parse_query


class DummyArmtekService:
    def __init__(self, items=None, error: Exception | None = None, context: ArmtekSearchContext | None = None):
        self.items = items or []
        self.error = error
        self.calls = []
        self.search_context = context or ArmtekSearchContext(vkorg="4000", kunnr_rg="123")

    def get_main_search_item(self, *, pin: str, brand: str | None = None, **kwargs):
        del kwargs
        self.calls.append({"pin": pin, "brand": brand})
        if self.error:
            raise self.error
        for item in self.items:
            if item.is_analog is not True:
                return item
        return None

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


def test_api_search_success_returns_tokens_and_registers_pending_repo():
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
    repo = InMemoryArmtekCharacteristicsRepository()
    service = DummyArmtekService(items=[item])
    app = create_app(armtek_service=service, characteristics_repository=repo)
    client = app.test_client()

    response = client.post("/api/armtek/search", json={"query": "332101 KYB"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    result = data["items"][0]
    assert len(data["items"]) == 1
    assert result["artid"] == "11"
    assert "api_token" in result
    assert "elizabeth_token" in result
    repo_record = repo.get_by_token(result["elizabeth_token"])
    assert repo_record is not None
    assert repo_record.ready is False
    assert service.calls == [{"pin": "332101", "brand": "KYB"}]


def test_api_search_handles_armtek_error():
    service = DummyArmtekService(error=ArmtekError("boom"))
    app = create_app(armtek_service=service)
    client = app.test_client()

    response = client.post("/api/armtek/search", json={"query": "332101"})

    assert response.status_code == 500
    assert response.get_json()["error"]


def test_api_search_skips_analogs():
    analog = SearchItem(artid="1", pin="P", brand="B", is_analog=True)
    main = SearchItem(artid="2", pin="P", brand="B", is_analog=None)
    repo = InMemoryArmtekCharacteristicsRepository()
    service = DummyArmtekService(items=[analog, main])
    app = create_app(armtek_service=service, characteristics_repository=repo)
    client = app.test_client()

    response = client.post("/api/armtek/search", json={"query": "P B"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["items"][0]["artid"] == "2"


def test_characteristics_endpoints_flow():
    repo = InMemoryArmtekCharacteristicsRepository()
    token = generate_characteristics_token(artid="123")
    repo.register(token, "123")
    service = DummyArmtekService()
    app = create_app(armtek_service=service, characteristics_repository=repo)
    client = app.test_client()

    pending = client.get(f"/api/armtek/characteristics?token={token}")
    assert pending.status_code == 200
    assert pending.get_json()["status"] == "pending"

    invalid = client.post("/api/armtek/characteristics", json={"token": "", "artid": "123"})
    assert invalid.status_code == 400
    invalid_type = client.post("/api/armtek/characteristics", json={"token": token, "artid": 123})
    assert invalid_type.status_code == 400

    ok_resp = client.post(
        "/api/armtek/characteristics",
        json={
            "token": token,
            "artid": "123",
            "image_url": "https://example.com/img.png",
            "weight": "3.2 кг",
            "length": "500 мм",
            "height": "120 мм",
            "width": "80 мм",
            "analog_code": "ABC123",
        },
    )
    assert ok_resp.status_code == 200
    assert ok_resp.get_json()["status"] == "ok"

    ready = client.get(f"/api/armtek/characteristics?token={token}")
    payload = ready.get_json()
    assert ready.status_code == 200
    assert payload["status"] == "ok"
    assert payload["image_url"] == "https://example.com/img.png"
    assert payload["weight"] == "3.2 кг"
    assert payload["length"] == "500 мм"
    assert payload["height"] == "120 мм"
    assert payload["width"] == "80 мм"
    assert payload["analog_code"] == "ABC123"
    assert payload["token"] == token
