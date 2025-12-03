from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any, List, cast
from urllib.parse import quote

from django.conf import settings
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.products.models import DetailsRequestStatus, Product
from backend.apps.products.serializers import (
    ProductDetailsInputSerializer,
    ProductDetailsSerializer,
    ProductSerializer,
)
from backend.apps.products.services import (
    _set_details_request_status,
    mark_requests_pending,
    update_product_details,
)


class ProductListView(ListAPIView[Product]):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self) -> QuerySet[Product]:
        assert self.request.user.is_authenticated
        user = cast(Any, self.request.user)
        qs = Product.objects.filter(user=user).order_by("-created_at")
        search_request_id_raw = self.request.query_params.get("search_request_id")
        if search_request_id_raw:
            try:
                search_request_id = int(search_request_id_raw)
            except (TypeError, ValueError):
                search_request_id = None
            if search_request_id is not None:
                qs = qs.filter(search_request_id=search_request_id)
        return qs


class ProductDetailView(RetrieveAPIView[Product]):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self) -> QuerySet[Product]:
        assert self.request.user.is_authenticated
        user = cast(Any, self.request.user)
        return Product.objects.filter(user=user)


class ProductDetailsIngestView(APIView):
    permission_classes = [AllowAny]

    NUMERIC_FIELDS = {
        "weight": 3,
        "length": 2,
        "width": 2,
        "height": 2,
    }

    @staticmethod
    def _parse_decimal(value: Any, max_places: int) -> Decimal | None:
        if value is None:
            return None
        if isinstance(value, (int, float, Decimal)):
            try:
                return Decimal(str(value))
            except InvalidOperation:
                return None
        if not isinstance(value, str):
            return None
        normalized = value.replace(",", ".")
        match = re.search(r"-?\d+(?:\.\d+)?", normalized)
        if not match:
            return None
        try:
            quant = Decimal(10) ** -max_places
            return Decimal(match.group(0)).quantize(quant)
        except InvalidOperation:
            return None

    def _normalize_payload(self, data: dict[str, Any]) -> dict[str, Any]:
        cleaned: dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, list) and len(value) == 1:
                cleaned[key] = value[0]
            else:
                cleaned[key] = value
        # numeric fields: try to extract number, silently drop if not parseable
        for field, places in self.NUMERIC_FIELDS.items():
            parsed = self._parse_decimal(cleaned.get(field), places)
            if parsed is None:
                cleaned.pop(field, None)
            else:
                cleaned[field] = parsed
        # image_url: keep only valid http(s)
        image_url = cleaned.get("image_url")
        if image_url:
            if not isinstance(image_url, str) or not image_url.lower().startswith(
                ("http://", "https://")
            ):
                cleaned.pop("image_url", None)
        # analog_code: strip whitespace
        if "analog_code" in cleaned and isinstance(cleaned.get("analog_code"), str):
            cleaned["analog_code"] = cleaned["analog_code"].strip()
        return cleaned

    def post(
        self, request: Request, pk: int, *args: object, **kwargs: object
    ) -> Response:
        token = request.headers.get("X-Details-Token") or request.query_params.get(
            "request_id"
        )
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if not token:
            _set_details_request_status(
                product, DetailsRequestStatus.FAILED, error="request_id is required"
            )
            return Response(
                {"detail": "request_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Request correlation check (if provided we require match)
        if (
            not getattr(product, "details_request", None)
            or str(product.details_request.request_id) != token
        ):
            _set_details_request_status(
                product, DetailsRequestStatus.FAILED, error="Invalid request_id"
            )
            return Response(
                {"detail": "Invalid request_id"}, status=status.HTTP_403_FORBIDDEN
            )
        normalized = self._normalize_payload(dict(request.data))
        serializer = ProductDetailsInputSerializer(data=normalized)
        if not serializer.is_valid():
            error_text = str(serializer.errors)
            _set_details_request_status(
                product, DetailsRequestStatus.FAILED, error=error_text
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            details = update_product_details(product, data=serializer.validated_data)
        except Exception as exc:  # pragma: no cover - safety net for ingest path
            _set_details_request_status(
                product, DetailsRequestStatus.FAILED, error=str(exc)
            )
            return Response(
                {"detail": "Failed to save details"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(
            ProductDetailsSerializer(details).data,
            status=status.HTTP_201_CREATED,
        )


class ProductDetailsRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        assert request.user.is_authenticated
        user = cast(Any, request.user)
        product_ids = request.data.get("product_ids") or []
        if not isinstance(product_ids, list) or not product_ids:
            return Response(
                {"detail": "Provide product_ids array"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        products: List[Product] = list(
            Product.objects.filter(id__in=product_ids, user=user)
        )
        if not products:
            return Response(
                {"detail": "No products found"}, status=status.HTTP_404_NOT_FOUND
            )
        requests = mark_requests_pending(products)
        data = [
            {
                "product_id": req.product_id,
                "request_id": str(req.request_id),
                "status": req.status,
                "artid": req.product.artid,
            }
            for req in requests
        ]
        return Response(data, status=status.HTTP_200_OK)


class ProductDetailsStatusView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        tokens = request.data.get("request_ids") or []
        if not isinstance(tokens, list) or not tokens:
            return Response(
                {"detail": "Provide request_ids array"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        requests = list(
            Product.objects.filter(details_request__request_id__in=tokens)
            .select_related("details", "details_request")
            .all()
        )
        serialized = []
        for product in requests:
            serialized.append(ProductSerializer(product).data)
        return Response(serialized)


class ProductDetailsJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        assert request.user.is_authenticated
        user = cast(Any, request.user)
        limit_raw = request.query_params.get("limit") or "20"
        try:
            limit = max(1, min(int(limit_raw), 200))
        except ValueError:
            limit = 20

        pending = (
            Product.objects.filter(details_request__status="pending", user=user)
            .select_related("details_request")
            .order_by("-details_request__created_at")[:limit]
        )
        base_url = getattr(
            settings, "ARMTEK_HTML_BASE_URL", "https://etp.armtek.ru/artinfo/index"
        ).rstrip("/")
        jobs = []
        for product in pending:
            req = product.details_request
            artid_encoded = quote(product.artid, safe="")
            open_url = (
                f"{base_url}/{artid_encoded}"
                f"?elizabeth_product_id={product.id}&request_id={req.request_id}"
            )
            jobs.append(
                {
                    "product_id": product.id,
                    "artid": product.artid,
                    "request_id": str(req.request_id),
                    "open_url": open_url,
                }
            )
        return Response(jobs)
