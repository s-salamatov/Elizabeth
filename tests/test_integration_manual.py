import os

import pytest

from armtek_client import ArmtekClient, ArmtekConfig


def _env(var: str) -> str | None:
    return os.getenv(var)


@pytest.mark.integration
def test_integration_search_manual():
    base_url = _env("ARMTEK_BASE_URL") or "https://ws.armtek.ru"
    login = _env("ARMTEK_LOGIN")
    password = _env("ARMTEK_PASSWORD")
    vkorg = _env("ARMTEK_VKORG")
    kunnr_rg = _env("ARMTEK_KUNNR_RG")
    pin = _env("ARMTEK_PIN")
    if not all([login, password, vkorg, kunnr_rg, pin]):
        pytest.skip("Set ARMTEK_BASE_URL/LOGIN/PASSWORD/VKORG/KUNNR_RG/PIN to run integration test")

    config = ArmtekConfig(base_url=base_url, login=login, password=password)
    with ArmtekClient(config) as client:
        vkorgs = client.get_vkorg_list()
        assert isinstance(vkorgs, list)
        results = client.search(vkorg=vkorg, kunnr_rg=kunnr_rg, pin=pin)
        assert isinstance(results, list)
