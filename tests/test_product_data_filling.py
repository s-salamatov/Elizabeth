import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from backend.apps.products.models import Product
from backend.apps.products.services import (
    ensure_details_request,
    upsert_product_from_search,
)
from backend.apps.providers.armtek.types import ArmtekSearchItem
from backend.apps.search.models import SearchRequest


@pytest.mark.django_db
def test_upsert_product_sets_quantity_and_alt_articles():
    user = get_user_model().objects.create_user(
        email="fill@example.com",
        password="secret123",
        phone_number="+70000000001",
    )
    search_request = SearchRequest.objects.create(
        user=user, source="armtek", query_string="PIN1"
    )

    main = ArmtekSearchItem(
        pin="PIN1",
        brand="BR1",
        name="Main",
        artid="ART1",
        is_analog=False,
        price=10.5,
        available_quantity=7,
        raw={},
    )
    analog1 = ArmtekSearchItem(
        pin="PIN2",
        brand="BR2",
        name="A1",
        artid="ART2",
        is_analog=True,
        raw={},
    )
    analog2 = ArmtekSearchItem(
        pin="PIN3",
        brand="BR3",
        name="A2",
        artid="ART3",
        is_analog=True,
        raw={},
    )

    product = upsert_product_from_search(
        main,
        analogs=[analog1, analog2],
        source="armtek",
        user=user,
        search_request=search_request,
    )
    product.refresh_from_db()

    assert product.quantity == 7
    assert product.alt_articles == [
        {"pin": "PIN2", "brand": "BR2"},
        {"pin": "PIN3", "brand": "BR3"},
    ]


@pytest.mark.django_db
def test_ingest_parses_raw_metrics_and_oems():
    user = get_user_model().objects.create_user(
        email="ingest@example.com",
        password="secret123",
        phone_number="+70000000002",
    )
    product = Product.objects.create(
        artid="ART100",
        brand="BR",
        pin="PIN100",
        oem="",
        name="Test",
        user=user,
        source="armtek",
    )
    request = ensure_details_request(product)

    client = Client()
    payload = {
        "image_url": "https://example.com/img.jpg",
        "package_weight_raw": "0,56 кг",
        "package_length_raw": "12 см",
        "package_height_raw": "120 мм",
        "package_width_raw": "5,5 см",
        "product_weight_raw": "56 кг",
        "oem_numbers": ["OEM1", " OEM2 "],
    }

    resp = client.post(
        f"/api/v1/products/{product.id}/details",
        payload,
        content_type="application/json",
        **{"HTTP_X_DETAILS_TOKEN": str(request.request_id)},
    )

    assert resp.status_code == 201

    product.refresh_from_db()
    details = product.details
    assert details.package_weight_g == 560
    assert details.package_length_mm == 120
    assert details.package_height_mm == 120
    assert details.package_width_mm == 55
    assert details.product_weight_g == 56000
    assert details.oem_number == "OEM1, OEM2"
    assert details.oem_number_primary == "OEM1"
