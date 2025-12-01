from __future__ import annotations

from typing import Any, Iterable, List, Tuple

from django.db import transaction

from elizabeth.apps.products.models import Product
from elizabeth.apps.products.services import upsert_products_from_search
from elizabeth.apps.providers.armtek.services import ArmtekSearchService
from elizabeth.apps.providers.services import resolve_armtek_credentials
from elizabeth.apps.search.models import SearchRequest, SearchStatus
from elizabeth.apps.search.parsers import split_pin_and_brand


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
        products.extend(
            upsert_products_from_search(
                items,
                source=source,
                user=user,
                search_request=search_request,
            )
        )
    return products


def parse_bulk_payload(data: dict[str, Any]) -> List[str]:
    return [q for q in data.get("queries", []) if q]
