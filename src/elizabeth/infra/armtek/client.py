from __future__ import annotations

from typing import Dict, List

from elizabeth.domain.armtek_models import ClientStructure, SearchItem, Vkorg

from .config import ArmtekConfig
from .http import ArmtekHttpClient
from .services.search import SearchService
from .services.user import UserService


class ArmtekClient:
    def __init__(self, config: ArmtekConfig):
        self._http = ArmtekHttpClient(config)
        self._user_service = UserService(self._http)
        self._search_service = SearchService(self._http)
        self._structure_cache: Dict[str, ClientStructure] = {}

    def close(self) -> None:
        self._http.close()

    def get_vkorg_list(self) -> List[Vkorg]:
        return self._user_service.get_vkorg_list()

    def get_client_structure(self, vkorg: str, *, with_cache: bool = True) -> ClientStructure:
        if with_cache and vkorg in self._structure_cache:
            return self._structure_cache[vkorg]
        structure = self._user_service.get_client_structure(vkorg)
        if with_cache:
            self._structure_cache[vkorg] = structure
        return structure

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
    ) -> List[SearchItem]:
        return self._search_service.search(
            vkorg=vkorg,
            kunnr_rg=kunnr_rg,
            pin=pin,
            brand=brand,
            query_type=query_type,
            program=program,
            kunnr_za=kunnr_za,
            incoterms=incoterms,
            vbeln=vbeln,
        )

    def __enter__(self) -> "ArmtekClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
