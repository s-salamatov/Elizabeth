from datetime import datetime

import pytest

from armtek_client.client import ArmtekClient
from armtek_client.config import ArmtekConfig
from armtek_client.models import Buyer, ClientStructure, DeliveryAddress, PickupPoint


class DummyUserService:
    def __init__(self, structure: ClientStructure):
        self.structure = structure
        self.calls = 0

    def get_client_structure(self, vkorg: str) -> ClientStructure:
        self.calls += 1
        return self.structure

    def get_vkorg_list(self):
        return []


def make_structure() -> ClientStructure:
    return ClientStructure(
        kunag="1",
        vkorg="2000",
        buyers=[Buyer(id="B", is_default=True)],
        delivery_addresses=[DeliveryAddress(id="D", is_default=False)],
        pickup_points=[PickupPoint(id="P")],
        contracts=[],
    )


def test_get_client_structure_uses_cache():
    dummy_config = ArmtekConfig(base_url="https://example.com", login="l", password="p")
    client = ArmtekClient(dummy_config)
    structure = make_structure()
    dummy_service = DummyUserService(structure)
    client._user_service = dummy_service  # type: ignore[attr-defined]

    first = client.get_client_structure("2000", with_cache=True)
    second = client.get_client_structure("2000", with_cache=True)

    assert first is second
    assert dummy_service.calls == 1
    client.close()


def test_get_client_structure_no_cache():
    dummy_config = ArmtekConfig(base_url="https://example.com", login="l", password="p")
    client = ArmtekClient(dummy_config)
    structure = make_structure()
    dummy_service = DummyUserService(structure)
    client._user_service = dummy_service  # type: ignore[attr-defined]

    client.get_client_structure("2000", with_cache=False)
    client.get_client_structure("2000", with_cache=False)

    assert dummy_service.calls == 2
    client.close()
