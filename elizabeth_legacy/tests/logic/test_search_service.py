import pytest

from backend.backend.models.search_result import SearchItem
from backend.backend.services.armtek.exceptions import (
    ArmtekHttpError,
    ArmtekResponseFormatError,
    ArmtekStatusError,
)
from backend.backend.services.armtek.search import SearchService


class DummyHttpClient:
    def __init__(self, responses):
        self.responses = responses
        self.last_payload = None

    def post(self, path, data=None):
        result = self.responses.get(("post", path))
        if isinstance(result, Exception):
            raise result
        self.last_payload = data
        return result


def test_search_success():
    response = {
        "STATUS": 200,
        "MESSAGES": [],
        "RESP": {
            "ARRAY": [
                {
                    "PIN": "123",
                    "BRAND": "BMW",
                    "NAME": "Part name",
                    "ARTID": "A1",
                    "PARNR": "S1",
                    "KEYZAK": "K1",
                    "RVALUE": "10",
                    "RETDAYS": "5",
                    "RDPRF": "1",
                    "MINBM": "2",
                    "VENSL": "0.95",
                    "PRICE": "100.5",
                    "WAERS": "USD",
                    "DLVDT": "20240101120000",
                    "WRNTDT": "20240105120000",
                    "ANALOG": "0",
                }
            ]
        },
    }
    client = DummyHttpClient({("post", "/api/ws_search/search"): response})
    service = SearchService(client)

    result = service.search(
        vkorg="2000", kunnr_rg="3000", pin="PIN123", brand=None, query_type=None
    )

    assert isinstance(result[0], SearchItem)
    assert client.last_payload["QUERY_TYPE"] == 1  # default when brand is not set
    assert result[0].quantity_available == 10
    assert result[0].is_analog is False


def test_search_with_missing_analog():
    response = {
        "STATUS": 200,
        "MESSAGES": [],
        "RESP": {
            "ARRAY": [
                {
                    "PIN": "123",
                    "BRAND": "BMW",
                    "NAME": "Part name",
                    "ARTID": "A1",
                    "PARNR": "S1",
                    "KEYZAK": "K1",
                    "RVALUE": "10",
                    "RETDAYS": "5",
                    "RDPRF": "1",
                    "MINBM": "2",
                    "VENSL": "0.95",
                    "PRICE": "100.5",
                    "WAERS": "USD",
                    "DLVDT": "20240101120000",
                }
            ]
        },
    }
    service = SearchService(
        DummyHttpClient({("post", "/api/ws_search/search"): response})
    )

    result = service.search(vkorg="2000", kunnr_rg="3000", pin="PIN")

    assert result[0].is_analog is False


def test_search_with_inequality_decimal():
    response = {
        "STATUS": 200,
        "MESSAGES": [],
        "RESP": {
            "ARRAY": [
                {
                    "PIN": "123",
                    "BRAND": "BMW",
                    "NAME": "Part name",
                    "ARTID": "A1",
                    "PARNR": "S1",
                    "KEYZAK": "K1",
                    "RVALUE": ">100",
                    "RETDAYS": "5",
                    "RDPRF": "1",
                    "MINBM": "2",
                    "VENSL": "0.95",
                    "PRICE": "100.5",
                    "WAERS": "USD",
                    "DLVDT": "20240101120000",
                    "ANALOG": "0",
                }
            ]
        },
    }
    service = SearchService(
        DummyHttpClient({("post", "/api/ws_search/search"): response})
    )

    result = service.search(vkorg="2000", kunnr_rg="3000", pin="PIN")

    assert result[0].quantity_available == 100


def test_search_with_trailing_inequality_decimal():
    response = {
        "STATUS": 200,
        "MESSAGES": [],
        "RESP": {
            "ARRAY": [
                {
                    "PIN": "123",
                    "BRAND": "BMW",
                    "NAME": "Part name",
                    "ARTID": "A1",
                    "PARNR": "S1",
                    "KEYZAK": "K1",
                    "RVALUE": "50>",
                    "RETDAYS": "5",
                    "RDPRF": "1",
                    "MINBM": "2",
                    "VENSL": "0.95",
                    "PRICE": "100.5",
                    "WAERS": "USD",
                    "DLVDT": "20240101120000",
                    "ANALOG": "0",
                }
            ]
        },
    }
    service = SearchService(
        DummyHttpClient({("post", "/api/ws_search/search"): response})
    )

    result = service.search(vkorg="2000", kunnr_rg="3000", pin="PIN")

    assert result[0].quantity_available == 50


def test_search_with_grouping_separators():
    response = {
        "STATUS": 200,
        "MESSAGES": [],
        "RESP": {
            "ARRAY": [
                {
                    "PIN": "123",
                    "BRAND": "BMW",
                    "NAME": "Part name",
                    "ARTID": "A1",
                    "PARNR": "S1",
                    "KEYZAK": "K1",
                    "RVALUE": ">50,000",
                    "RETDAYS": "5",
                    "RDPRF": "1",
                    "MINBM": "2",
                    "VENSL": "0.95",
                    "PRICE": "100.5",
                    "WAERS": "USD",
                    "DLVDT": "20240101120000",
                    "ANALOG": "0",
                }
            ]
        },
    }
    service = SearchService(
        DummyHttpClient({("post", "/api/ws_search/search"): response})
    )

    result = service.search(vkorg="2000", kunnr_rg="3000", pin="PIN")

    assert result[0].quantity_available == 50000


def test_search_with_textual_availability():
    response = {
        "STATUS": 200,
        "MESSAGES": [],
        "RESP": {
            "ARRAY": [
                {
                    "PIN": "123",
                    "BRAND": "BMW",
                    "NAME": "Part name",
                    "ARTID": "A1",
                    "PARNR": "S1",
                    "KEYZAK": "K1",
                    "RVALUE": "ЕСТЬ",
                    "RETDAYS": "5",
                    "RDPRF": "1",
                    "MINBM": "2",
                    "VENSL": "0.95",
                    "PRICE": "100.5",
                    "WAERS": "USD",
                    "DLVDT": "20240101120000",
                    "ANALOG": "0",
                }
            ]
        },
    }
    service = SearchService(
        DummyHttpClient({("post", "/api/ws_search/search"): response})
    )

    result = service.search(vkorg="2000", kunnr_rg="3000", pin="PIN")

    assert result[0].quantity_available == 1


def test_search_status_error():
    response = {"STATUS": 500, "MESSAGES": ["fail"], "RESP": {}}
    service = SearchService(
        DummyHttpClient({("post", "/api/ws_search/search"): response})
    )

    with pytest.raises(ArmtekStatusError):
        service.search(vkorg="2000", kunnr_rg="3000", pin="PIN")


def test_search_missing_array_returns_empty_list():
    response = {"STATUS": 200, "MESSAGES": [], "RESP": {}}
    service = SearchService(
        DummyHttpClient({("post", "/api/ws_search/search"): response})
    )

    result = service.search(vkorg="2000", kunnr_rg="3000", pin="PIN")

    assert not result


def test_search_format_error_missing_field():
    response = {"STATUS": 200, "MESSAGES": [], "RESP": {"ARRAY": [{"PIN": "123"}]}}
    service = SearchService(
        DummyHttpClient({("post", "/api/ws_search/search"): response})
    )

    with pytest.raises(ArmtekResponseFormatError):
        service.search(vkorg="2000", kunnr_rg="3000", pin="PIN")


def test_search_http_error():
    service = SearchService(
        DummyHttpClient({("post", "/api/ws_search/search"): ArmtekHttpError("oops")})
    )

    with pytest.raises(ArmtekHttpError):
        service.search(vkorg="2000", kunnr_rg="3000", pin="PIN")
