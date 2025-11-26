from __future__ import annotations

from elizabeth.domain.armtek_models import ClientStructure, SearchItem, Vkorg
from elizabeth.infra.armtek.client import ArmtekClient
from elizabeth.infra.armtek.config import ArmtekConfig


class ArmtekService:
    """Service layer wrapper around :class:`ArmtekClient`."""

    def __init__(self, client: ArmtekClient):
        self._client = client

    @classmethod
    def from_config(cls, config: ArmtekConfig) -> "ArmtekService":
        return cls(ArmtekClient(config))

    def get_vkorg_list(self) -> list[Vkorg]:
        return self._client.get_vkorg_list()

    def get_client_structure(self, vkorg: str, *, with_cache: bool = True) -> ClientStructure:
        return self._client.get_client_structure(vkorg, with_cache=with_cache)

    def search(
        self,
        *,
        vkorg: str,
        kunnr_rg: str,
        pin: str,
        brand: str | None = None,
        query_type: int | None = None,
        program: str | None = None,
        kunnr_za: str | None = None,
        incoterms: int | None = None,
        vbeln: str | None = None,
    ) -> list[SearchItem]:
        params = {
            "vkorg": vkorg,
            "kunnr_rg": kunnr_rg,
            "pin": pin,
            "brand": brand,
            "query_type": query_type,
            "program": program,
            "kunnr_za": kunnr_za,
            "incoterms": incoterms,
            "vbeln": vbeln,
        }
        return self._client.search(**params)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "ArmtekService":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
