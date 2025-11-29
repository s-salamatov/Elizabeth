"""Service layer for selecting main Armtek search results."""

# pylint: disable=duplicate-code

from __future__ import annotations

from typing import Iterable, Optional, Protocol

from elizabeth.backend.config import ArmtekConfig
from elizabeth.backend.models.characteristics import ProductHtmlDetails
from elizabeth.backend.models.search_result import SearchItem
from elizabeth.backend.services.armtek.client import ArmtekClient
from elizabeth.backend.services.tokens import ArmtekSearchContext


class ArmtekProductParser(Protocol):
    def parse_product_by_artid(self, artid: str) -> ProductHtmlDetails:
        """
        Parser interface for fetching product details by Armtek ID.

        Implementations are responsible for retrieving and parsing the HTML page
        for the provided ``artid``.
        """


class ArmtekService:
    """
    Сервисный слой для работы с поиском товаров через :class:`ArmtekClient`.
    """

    def __init__(
        self,
        client: ArmtekClient,
        *,
        vkorg: str,
        kunnr_rg: str,
        program: str | None = None,
        kunnr_za: str | None = None,
        incoterms: int | None = None,
        vbeln: str | None = None,
    ) -> None:
        """Инициализация сервиса."""

        self._client = client
        self._vkorg = vkorg
        self._kunnr_rg = kunnr_rg
        self._program = program
        self._kunnr_za = kunnr_za
        self._incoterms = incoterms
        self._vbeln = vbeln
        self._search_context = ArmtekSearchContext(
            vkorg=vkorg,
            kunnr_rg=kunnr_rg,
            program=program,
            kunnr_za=kunnr_za,
            incoterms=incoterms,
            vbeln=vbeln,
        )

    @classmethod
    def from_config(
        cls,
        config: ArmtekConfig,
        *,
        vkorg: str,
        kunnr_rg: str,
        program: str | None = None,
        kunnr_za: str | None = None,
        incoterms: int | None = None,
        vbeln: str | None = None,
    ) -> "ArmtekService":
        client = ArmtekClient(config)
        return cls(
            client,
            vkorg=vkorg,
            kunnr_rg=kunnr_rg,
            program=program,
            kunnr_za=kunnr_za,
            incoterms=incoterms,
            vbeln=vbeln,
        )

    def search_items(
        self,
        *,
        pin: str,
        brand: str | None = None,
        query_type: int | None = None,
        program: str | None = None,
        kunnr_za: str | None = None,
        incoterms: int | None = None,
        vbeln: str | None = None,
    ) -> list[SearchItem]:
        """
        Получить список ``SearchItem`` напрямую из ``ArmtekClient``.

        Аргументы метода переопределяют значения, переданные при инициализации
        сервиса.
        """

        return self._client.search(
            vkorg=self._vkorg,
            kunnr_rg=self._kunnr_rg,
            pin=pin,
            brand=brand,
            query_type=query_type,
            program=program if program is not None else self._program,
            kunnr_za=kunnr_za if kunnr_za is not None else self._kunnr_za,
            incoterms=incoterms if incoterms is not None else self._incoterms,
            vbeln=vbeln if vbeln is not None else self._vbeln,
        )

    def get_main_search_item(
        self,
        *,
        pin: str,
        brand: str | None = None,
        query_type: int | None = None,
        program: str | None = None,
        kunnr_za: str | None = None,
        incoterms: int | None = None,
        vbeln: str | None = None,
    ) -> Optional[SearchItem]:
        """Вернуть первый элемент поиска, который не отмечен как аналог."""

        items = self.search_items(
            pin=pin,
            brand=brand,
            query_type=query_type,
            program=program,
            kunnr_za=kunnr_za,
            incoterms=incoterms,
            vbeln=vbeln,
        )
        return self._choose_first_non_analog(items)

    def get_main_artid(
        self,
        *,
        pin: str,
        brand: str | None = None,
        query_type: int | None = None,
        program: str | None = None,
        kunnr_za: str | None = None,
        incoterms: int | None = None,
        vbeln: str | None = None,
    ) -> Optional[str]:
        """Получить ARTID основного товара или ``None``."""

        item = self.get_main_search_item(
            pin=pin,
            brand=brand,
            query_type=query_type,
            program=program,
            kunnr_za=kunnr_za,
            incoterms=incoterms,
            vbeln=vbeln,
        )
        return item.artid if item else None

    def get_product_details_via_parser(
        self,
        parser: ArmtekProductParser,
        *,
        pin: str,
        brand: str | None = None,
    ) -> Optional[ProductHtmlDetails]:
        """
        Получить детали товара через внешний парсер HTML.

        - получаем ARTID через :meth:`get_main_artid`;
        - если ARTID найден — делегируем парсеру.
        """

        artid = self.get_main_artid(pin=pin, brand=brand)
        if artid is None:
            return None
        return parser.parse_product_by_artid(artid)

    @property
    def search_context(self) -> ArmtekSearchContext:
        return self._search_context

    def _choose_first_non_analog(
        self, items: Iterable[SearchItem]
    ) -> Optional[SearchItem]:
        """Вернуть первый элемент, у которого ``is_analog`` не равен ``True``."""

        for item in items:
            if item.is_analog is not True:
                return item
        return None

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "ArmtekService":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
