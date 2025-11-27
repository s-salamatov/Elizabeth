from datetime import datetime
from decimal import Decimal

import pytest

from elizabeth.domain.armtek_models import ProductHtmlDetails, SearchItem
from elizabeth.infra.armtek.exceptions import ArmtekError, ArmtekInteractiveLoginRequired
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


class DummyHtmlParser:
    def __init__(self, details: ProductHtmlDetails | None = None, error: Exception | None = None):
        self.details = details
        self.error = error
        self.calls: list[str] = []

    def get_product_details(self, artid: str) -> ProductHtmlDetails:
        self.calls.append(artid)
        if self.error:
            raise self.error
        if self.details is None:
            raise RuntimeError("No details provided")
        return self.details


class DummyLoginFlow:
    def __init__(self, error: Exception | None = None):
        self.error = error
        self.calls: list[str | None] = []

    def run(self, artid: str | None = None) -> None:
        self.calls.append(artid)
        if self.error:
            raise self.error


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


def test_api_product_details_success():
    service = DummyArmtekService(item=None)
    details = ProductHtmlDetails(artid="123", image_url="https://example.com/image.png")
    html_parser = DummyHtmlParser(details=details)
    login_flow = DummyLoginFlow()
    app = create_app(armtek_service=service, html_parser=html_parser, login_flow=login_flow)
    client = app.test_client()

    response = client.post("/api/product/details", json={"artid": "123"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["image_url"] == "https://example.com/image.png"
    assert html_parser.calls == ["123"]


def test_api_product_details_interactive_required():
    service = DummyArmtekService(item=None)
    html_parser = DummyHtmlParser(error=ArmtekInteractiveLoginRequired("login"))
    login_flow = DummyLoginFlow()
    app = create_app(armtek_service=service, html_parser=html_parser, login_flow=login_flow)
    client = app.test_client()

    response = client.post("/api/product/details", json={"artid": "555"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "interactive_login_required"
    assert html_parser.calls == ["555"]


def test_api_product_details_interactive_on_missing_state():
    service = DummyArmtekService(item=None)
    html_parser = DummyHtmlParser(error=FileNotFoundError("missing"))
    login_flow = DummyLoginFlow()
    app = create_app(armtek_service=service, html_parser=html_parser, login_flow=login_flow)
    client = app.test_client()

    response = client.post("/api/product/details", json={"artid": "555"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "interactive_login_required"
    assert html_parser.calls == ["555"]


def test_api_product_details_error_path():
    service = DummyArmtekService(item=None)
    html_parser = DummyHtmlParser(error=RuntimeError("boom"))
    login_flow = DummyLoginFlow()
    app = create_app(armtek_service=service, html_parser=html_parser, login_flow=login_flow)
    client = app.test_client()

    response = client.post("/api/product/details", json={"artid": "777"})

    assert response.status_code == 500
    data = response.get_json()
    assert data["status"] == "error"
    assert html_parser.calls == ["777"]


def test_api_interactive_login_endpoint_success():
    service = DummyArmtekService(item=None)
    html_parser = DummyHtmlParser(details=ProductHtmlDetails(artid="1", image_url=None))
    login_flow = DummyLoginFlow()
    app = create_app(armtek_service=service, html_parser=html_parser, login_flow=login_flow)
    client = app.test_client()

    response = client.post("/api/product/interactive-login", json={"artid": "123"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert login_flow.calls == ["123"]


def test_api_interactive_login_endpoint_failure():
    service = DummyArmtekService(item=None)
    html_parser = DummyHtmlParser(details=ProductHtmlDetails(artid="1", image_url=None))
    login_flow = DummyLoginFlow(error=RuntimeError("fail"))
    app = create_app(armtek_service=service, html_parser=html_parser, login_flow=login_flow)
    client = app.test_client()

    response = client.post("/api/product/interactive-login", json={"artid": "123"})

    assert response.status_code == 500
    data = response.get_json()
    assert data["status"] == "error"
    assert login_flow.calls == ["123"]
