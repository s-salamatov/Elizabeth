from __future__ import annotations

from typing import Iterable, List, Tuple

from django.db import transaction

from apps.products.services import upsert_products_from_search
from apps.providers.armtek.services import ArmtekSearchService
from apps.providers.services import resolve_armtek_credentials
from apps.search.models import SearchRequest, SearchStatus
from apps.search.parsers import split_bulk_input, split_pin_and_brand


@transaction.atomic
def perform_single_search(query: str, *, user=None, source: str = "armtek") -> Tuple[SearchRequest, list]:
    search_request = SearchRequest.objects.create(
        user=user,
        source=source,
        query_string=query,
        status=SearchStatus.IN_PROGRESS,
    )
    try:
        products = _run_search_flow([query], user=user, source=source)
    except Exception:
        search_request.status = SearchStatus.FAILED
        search_request.save(update_fields=["status", "updated_at"])
        raise

    search_request.total_items = len(products)
    search_request.status = SearchStatus.DONE
    search_request.save(update_fields=["total_items", "status", "updated_at"])
    return search_request, products


def perform_bulk_search(
    queries: Iterable[str], *, user=None, source: str = "armtek"
) -> Tuple[SearchRequest, list]:
    normalized = [q for q in queries if q]
    query_string = "\n".join(normalized)
    search_request = SearchRequest.objects.create(
        user=user,
        source=source,
        query_string=query_string,
        status=SearchStatus.IN_PROGRESS,
    )
    try:
        products = _run_search_flow(normalized, user=user, source=source)
    except Exception:
        search_request.status = SearchStatus.FAILED
        search_request.save(update_fields=["status", "updated_at"])
        raise

    search_request.total_items = len(products)
    search_request.status = SearchStatus.DONE
    search_request.save(update_fields=["total_items", "status", "updated_at"])
    return search_request, products


def _run_search_flow(queries: Iterable[str], *, user=None, source: str) -> List:
    if source != "armtek":
        return []

    credentials = resolve_armtek_credentials(user)
    service = ArmtekSearchService(credentials)
    products = []
    for query in queries:
        pin, brand = split_pin_and_brand(query)
        items = service.search(pin=pin, brand=brand)
        products.extend(upsert_products_from_search(items, source=source))
    # Deduplicate by PK
    unique_products: dict[int, object] = {p.pk: p for p in products if p.pk is not None}
    return list(unique_products.values())


def parse_bulk_payload(data: dict) -> List[str]:
    queries = data.get("queries") or []
    bulk_text = data.get("bulk_text") or ""
    if bulk_text:
        queries.extend(split_bulk_input(bulk_text))
    return [q for q in queries if q]
