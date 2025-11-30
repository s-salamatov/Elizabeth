from elizabeth.backend.models.search_result import SearchItem
from elizabeth.backend.services.armtek.service import ArmtekService


class DummyArmtekClient:
    def __init__(self, responses):
        self.responses = responses
        self.last_kwargs = None

    def search(self, **kwargs):
        self.last_kwargs = kwargs
        return self.responses


def _service_with_items(items):
    client = DummyArmtekClient(items)
    service = ArmtekService(
        client,
        vkorg="2000",
        kunnr_rg="3000",
        program="LP",
        kunnr_za="4000",
        incoterms=0,
        vbeln="VB123",
    )
    return service, client


def test_choose_first_non_analog_first_item():
    service, _ = _service_with_items(
        [
            SearchItem(artid="1", pin="A", is_analog=False),
            SearchItem(artid="2", pin="A", is_analog=True),
        ]
    )

    result = service.get_main_search_item(pin="A")

    assert result is not None
    assert result.artid == "1"


def test_choose_first_non_analog_skips_analogs():
    service, _ = _service_with_items(
        [
            SearchItem(artid="1", pin="A", is_analog=True),
            SearchItem(artid="2", pin="A", is_analog=None),
        ]
    )

    result = service.get_main_search_item(pin="A")

    assert result is not None
    assert result.artid == "2"


def test_choose_first_non_analog_all_analogs():
    service, _ = _service_with_items(
        [
            SearchItem(artid="1", pin="A", is_analog=True),
            SearchItem(artid="2", pin="A", is_analog=True),
        ]
    )

    result = service.get_main_search_item(pin="A")

    assert result is None


def test_get_main_artid_returns_value():
    service, _ = _service_with_items(
        [
            SearchItem(artid="11", pin="A", is_analog=False),
        ]
    )

    artid = service.get_main_artid(pin="A")

    assert artid == "11"


def test_search_items_override_defaults():
    service, client = _service_with_items(
        [
            SearchItem(artid="11", pin="A", is_analog=False),
        ]
    )

    service.search_items(
        pin="A",
        program="GP",
        kunnr_za="override",
        incoterms=1,
        vbeln="VB999",
    )

    assert client.last_kwargs["program"] == "GP"
    assert client.last_kwargs["kunnr_za"] == "override"
    assert client.last_kwargs["incoterms"] == 1
    assert client.last_kwargs["vbeln"] == "VB999"
