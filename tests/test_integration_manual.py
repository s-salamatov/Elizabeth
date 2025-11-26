import os

import pytest

from elizabeth import ArmtekClient, ArmtekConfig


def _env(var: str) -> str | None:
    return os.getenv(var)


def _pick_vkorg(client: ArmtekClient, env_vkorg: str | None) -> str:
    if env_vkorg:
        return env_vkorg
    vkorgs = client.get_vkorg_list()
    assert vkorgs, "API did not return VKORG list"
    return vkorgs[0].vkorg


def _pick_kunnr_rg(client: ArmtekClient, vkorg: str, env_kunnr_rg: str | None) -> str:
    if env_kunnr_rg:
        return env_kunnr_rg
    structure = client.get_client_structure(vkorg)
    assert structure.buyers, "Client structure does not contain buyers (RG_TAB)"
    default_buyer = next((buyer for buyer in structure.buyers if buyer.is_default), structure.buyers[0])
    return default_buyer.id


@pytest.mark.integration
def test_integration_search_manual():
    base_url = _env("ARMTEK_BASE_URL") or "https://ws.armtek.ru"
    login = _env("ARMTEK_LOGIN")
    password = _env("ARMTEK_PASSWORD")
    brand = _env("ARMTEK_BRAND")
    vkorg = _env("ARMTEK_VKORG")
    kunnr_rg = _env("ARMTEK_KUNNR_RG")
    pin = _env("ARMTEK_PIN")
    if not all([login, password, pin, brand]):
        pytest.skip("Set ARMTEK_LOGIN/PASSWORD/PIN/BRAND to run integration test")

    config = ArmtekConfig(base_url=base_url, login=login, password=password)
    with ArmtekClient(config) as client:
        selected_vkorg = _pick_vkorg(client, vkorg)
        selected_kunnr_rg = _pick_kunnr_rg(client, selected_vkorg, kunnr_rg)
        results = client.search(vkorg=selected_vkorg, kunnr_rg=selected_kunnr_rg, pin=pin, brand=brand)
        assert isinstance(results, list)
