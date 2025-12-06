from __future__ import annotations

import logging
from typing import Any, Iterable, List, Tuple

from django.db import transaction

from backend.apps.products.models import Product
from backend.apps.products.services import upsert_product_from_search
from backend.apps.providers.armtek.services import ArmtekSearchService
from backend.apps.providers.services import resolve_armtek_credentials
from backend.apps.search.models import SearchRequest, SearchStatus
from backend.apps.search.parsers import split_pin_and_brand

logger = logging.getLogger(__name__)


@transaction.atomic
def perform_single_search(
    query: str,
    *,
    user: Any,
    source: str = "armtek",
) -> Tuple[SearchRequest, list[Product]]:
    search_request = SearchRequest.objects.create(
        user=user,
        source=source,
        query_string=query,
        status=SearchStatus.IN_PROGRESS,
    )
    try:
        products = _run_search_flow(
            [query], user=user, source=source, search_request=search_request
        )
    except Exception:
        search_request.status = SearchStatus.FAILED
        search_request.save(update_fields=["status", "updated_at"])
        raise

    search_request.total_items = len(products)
    search_request.status = SearchStatus.DONE
    search_request.save(update_fields=["total_items", "status", "updated_at"])
    return search_request, products


def perform_bulk_search(
    queries: Iterable[str],
    *,
    user: Any,
    source: str = "armtek",
) -> Tuple[SearchRequest, list[Product]]:
    normalized = [q for q in queries if q]
    query_string = "\n".join(normalized)
    search_request = SearchRequest.objects.create(
        user=user,
        source=source,
        query_string=query_string,
        status=SearchStatus.IN_PROGRESS,
    )
    try:
        products = _run_search_flow(
            normalized, user=user, source=source, search_request=search_request
        )
    except Exception:
        search_request.status = SearchStatus.FAILED
        search_request.save(update_fields=["status", "updated_at"])
        raise

    search_request.total_items = len(products)
    search_request.status = SearchStatus.DONE
    search_request.save(update_fields=["total_items", "status", "updated_at"])
    return search_request, products


def _run_search_flow(
    queries: Iterable[str],
    *,
    user: Any,
    source: str,
    search_request: SearchRequest,
) -> List[Product]:
    if source != "armtek":
        return []

    credentials = resolve_armtek_credentials(user)
    service = ArmtekSearchService(credentials)
    products: list[Product] = []
    for query in queries:
        pin, brand = split_pin_and_brand(query)
        items = service.search(pin=pin, brand=brand)
        logger.info(
            "Armtek search items fetched",
            extra={
                "query": query,
                "pin": pin,
                "brand": brand,
                "items_count": len(items),
            },
        )
        if not items:
            continue
        main = ArmtekSearchService._pick_first_non_analog(items)
        if main is None and items:
            main = items[0]
        if main is None:
            continue
        analogs = [item for item in items if item.is_analog is True and item != main]
        logger.info(
            "Persisting main product from search",
            extra={
                "artid": main.artid,
                "pin": main.pin,
                "brand": main.brand,
                "analogs_count": len(analogs),
            },
        )
        products.append(
            upsert_product_from_search(
                main,
                analogs=analogs,
                source=source,
                user=user,
                search_request=search_request,
            )
        )
    return products


def parse_bulk_payload(data: dict[str, Any]) -> List[str]:
    return [q for q in data.get("queries", []) if q]
