from __future__ import annotations

from typing import Any, Dict, List

from pydantic import ValidationError

from ..exceptions import ArmtekResponseFormatError
from ..http import ArmtekHttpClient
from ..models import SearchItem
from ..parsing import ensure_mapping, require_value
from .base import extract_array, unwrap_resp


class SearchService:
    def __init__(self, http_client: ArmtekHttpClient):
        self._http = http_client

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
        params: Dict[str, Any] = {
            "VKORG": vkorg,
            "KUNNR_RG": kunnr_rg,
            "PIN": pin,
        }
        if brand:
            params["BRAND"] = brand
        if query_type is None and brand is None:
            params["QUERY_TYPE"] = 1
        elif query_type is not None:
            params["QUERY_TYPE"] = query_type
        if program:
            params["PROGRAM"] = program
        if kunnr_za:
            params["KUNNR_ZA"] = kunnr_za
        if incoterms is not None:
            params["INCOTERMS"] = incoterms
        if vbeln:
            params["VBELN"] = vbeln

        raw = self._http.post("/api/ws_search/search", data=params)
        resp = unwrap_resp(raw)
        array = extract_array(resp, "ARRAY")
        items: List[SearchItem] = []
        for entry in array:
            mapping = ensure_mapping("RESP.ARRAY item", entry)
            try:
                items.append(
                    SearchItem(
                        pin=str(require_value(mapping, ("PIN",), "PIN")),
                        brand=str(require_value(mapping, ("BRAND",), "BRAND")),
                        name=str(require_value(mapping, ("NAME",), "NAME")),
                        artid=str(require_value(mapping, ("ARTID",), "ARTID")),
                        partner_store_code=str(require_value(mapping, ("PARNR",), "PARNR")),
                        store_code=str(require_value(mapping, ("KEYZAK",), "KEYZAK")),
                        quantity_available=require_value(mapping, ("RVALUE",), "RVALUE"),
                        return_days=require_value(mapping, ("RETDAYS",), "RETDAYS"),
                        multiplicity=require_value(mapping, ("RDPRF",), "RDPRF"),
                        min_quantity=require_value(mapping, ("MINBM",), "MINBM"),
                        supply_probability=require_value(mapping, ("VENSL",), "VENSL"),
                        price=require_value(mapping, ("PRICE",), "PRICE"),
                        currency=str(require_value(mapping, ("WAERS",), "WAERS")),
                        delivery_date=mapping.get("DLVDT"),
                        guaranteed_delivery_date=mapping.get("WRNTDT"),
                        is_analog=mapping.get("ANALOG"),
                    )
                )
            except ValidationError as exc:
                raise ArmtekResponseFormatError("Invalid search item format") from exc
        return items
