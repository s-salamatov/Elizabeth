import pytest

from backend.apps.products.models import DetailsRequestStatus, Product
from backend.apps.products.services import (
    ensure_details_request,
    mark_requests_pending,
)


@pytest.mark.django_db
def test_ensure_request_and_status(db):
    product = Product.objects.create(
        artid="ART1",
        brand="BR",
        pin="PIN",
        oem="",
        name="Name",
        source="armtek",
    )
    req = ensure_details_request(product)
    assert req.status == DetailsRequestStatus.PENDING
    assert req.request_id


@pytest.mark.django_db
def test_mark_requests_pending_updates_status(db):
    p1 = Product.objects.create(
        artid="A1", brand="B", pin="P", oem="", name="n", source="armtek"
    )
    p2 = Product.objects.create(
        artid="A2", brand="B", pin="P2", oem="", name="n2", source="armtek"
    )
    mark_requests_pending([p1, p2])
    assert p1.details_request.status == DetailsRequestStatus.PENDING
    assert p2.details_request.status == DetailsRequestStatus.PENDING
