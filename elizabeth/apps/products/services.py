from __future__ import annotations

from datetime import timedelta
from typing import Iterable

from django.conf import settings
from django.utils import timezone

from apps.products.models import Product, ProductDetails


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
    return details
