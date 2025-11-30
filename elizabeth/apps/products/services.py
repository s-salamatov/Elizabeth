from __future__ import annotations

from datetime import timedelta
from typing import Iterable

from uuid import uuid4

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.products.models import (
    DetailsRequestStatus,
    Product,
    ProductDetails,
    ProductDetailsRequest,
)


def _cache_ttl() -> timedelta:
    minutes = getattr(settings, "SEARCH_CACHE_TTL_MINUTES", 60)
    return timedelta(minutes=minutes)


def is_product_fresh(product: Product) -> bool:
    if product.fetched_at is None:
        return False
    return timezone.now() - product.fetched_at <= _cache_ttl()


def upsert_product_from_search(item, *, source: str = "armtek") -> Product:
    defaults = {
        "brand": item.brand,
        "pin": item.pin,
        "oem": getattr(item, "oem", "") or "",
        "name": item.name,
        "source": source,
        "fetched_at": timezone.now(),
    }
    product, created = Product.objects.get_or_create(
        artid=item.artid,
        source=source,
        defaults=defaults,
    )
    if not created:
        changed = False
        for field, value in defaults.items():
            if getattr(product, field) != value and value:
                setattr(product, field, value)
                changed = True
        if not is_product_fresh(product):
            product.fetched_at = timezone.now()
            changed = True
        if changed:
            product.save()
    ensure_details_request(product)
    return product


def upsert_products_from_search(items: Iterable, *, source: str = "armtek") -> list[Product]:
    products: list[Product] = []
    for item in items:
        products.append(upsert_product_from_search(item, source=source))
    return products


def update_product_details(product: Product, *, data: dict) -> ProductDetails:
    details, _ = ProductDetails.objects.get_or_create(product=product)
    for field in ["image_url", "weight", "length", "width", "height", "analog_code"]:
        if field in data:
            setattr(details, field, data[field])
    details.fetched_at = timezone.now()
    details.save()
    _set_details_request_status(product, DetailsRequestStatus.READY)
    return details


def ensure_details_request(product: Product) -> ProductDetailsRequest:
    request, created = ProductDetailsRequest.objects.get_or_create(
        product=product,
        defaults={
            "request_id": uuid4(),
            "status": DetailsRequestStatus.PENDING,
        },
    )
    return request


@transaction.atomic
def mark_requests_pending(products: list[Product]) -> list[ProductDetailsRequest]:
    requests: list[ProductDetailsRequest] = []
    for product in products:
        req = ensure_details_request(product)
        if req.status != DetailsRequestStatus.PENDING:
            req.status = DetailsRequestStatus.PENDING
            req.save(update_fields=["status", "updated_at"])
        requests.append(req)
    return requests


def _set_details_request_status(product: Product, status: DetailsRequestStatus) -> None:
    try:
        req = product.details_request
    except ProductDetailsRequest.DoesNotExist:
        req = ensure_details_request(product)
    if req.status != status:
        req.status = status
        req.save(update_fields=["status", "updated_at"])
