from __future__ import annotations

from elizabeth.backend.models.characteristics import ProductHtmlDetails


class ArmtekParserAdapter:
    """
    Заглушка для внешнего парсера, который может получать характеристики
    товара (HTML, расширение, и т.п.).
    """

    def parse_product_by_artid(self, artid: str) -> ProductHtmlDetails:
        raise NotImplementedError(
            "ArmtekParserAdapter should be implemented by extension-aware parser"
        )
