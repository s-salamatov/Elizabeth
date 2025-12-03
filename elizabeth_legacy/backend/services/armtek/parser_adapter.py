from __future__ import annotations

from backend.backend.models.characteristics import ProductHtmlDetails


class ArmtekParserAdapter:
    """Заглушка для внешнего парсера характеристик товара."""

    def parse_product_by_artid(self, artid: str) -> ProductHtmlDetails:
        raise NotImplementedError(
            "ArmtekParserAdapter should be implemented by extension-aware parser"
        )
