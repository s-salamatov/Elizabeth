from __future__ import annotations

import logging
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

    logger = logging.getLogger(__name__)

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

    @staticmethod
    def _parse_weight_to_grams(value: Any) -> int | None:
        if value is None:
            return None
        if isinstance(value, (list, tuple)) and value:
            value = value[0]
        if isinstance(value, (int, float, Decimal)):
            # Without a unit we cannot be confident; treat as unparsable for the
            # normalized gram fields but leave legacy decimals intact.
            return None
        if not isinstance(value, str):
            return None
        text = value.strip().lower().replace(",", ".")
        match = re.search(r"-?\d+(?:\.\d+)?", text)
        if not match:
            return None
        number = float(match.group(0))
        unit_factor = None
        weight_tokens = (
            ("кг", 1000),
            ("kg", 1000),
            ("килограмм", 1000),
            ("килог", 1000),
            ("г", 1),
            ("гр", 1),
            ("gram", 1),
            ("грамм", 1),
        )
        for token, factor in weight_tokens:
            if token in text:
                unit_factor = factor
                break
        if unit_factor is None:
            return None
        return int(round(number * unit_factor))

    @staticmethod
    def _parse_length_to_mm(value: Any) -> int | None:
        if value is None:
            return None
        if isinstance(value, (list, tuple)) and value:
            value = value[0]
        if isinstance(value, (int, float, Decimal)):
            # Without a unit the number may be ambiguous; skip.
            return None
        if not isinstance(value, str):
            return None
        text = value.strip().lower().replace(",", ".")
        match = re.search(r"-?\d+(?:\.\d+)?", text)
        if not match:
            return None
        number = float(match.group(0))
        unit_factor = None
        length_tokens = (
            ("мм", 1),
            ("mm", 1),
            ("миллиметр", 1),
            ("миллиметров", 1),
            ("см", 10),
            ("cm", 10),
            ("сантиметр", 10),
            ("сантиметров", 10),
            ("centimeter", 10),
            ("centimetre", 10),
        )
        for token, factor in length_tokens:
            if token in text:
                unit_factor = factor
                break
        if unit_factor is None:
            return None
        return int(round(number * unit_factor))

    def _normalize_payload(self, data: dict[str, Any]) -> dict[str, Any]:
        cleaned: dict[str, Any] = {}

        # Flatten single-element lists coming from form-data
        for key, value in data.items():
            if isinstance(value, list) and len(value) == 1:
                cleaned[key] = value[0]
            else:
                cleaned[key] = value

        normalized: dict[str, Any] = {}

        # Legacy numeric fields stay as decimals (backward compatibility)
        for field, places in self.NUMERIC_FIELDS.items():
            parsed = self._parse_decimal(cleaned.get(field), places)
            if parsed is not None:
                normalized[field] = parsed

        # Image URL sanity check
        image_url = cleaned.get("image_url")
        if (
            image_url
            and isinstance(image_url, str)
            and image_url.lower().startswith(("http://", "https://"))
        ):
            normalized["image_url"] = image_url

        # analog_code: strip whitespace
        analog_code = cleaned.get("analog_code")
        if isinstance(analog_code, str):
            analog_code = analog_code.strip()
            if analog_code:
                normalized["analog_code"] = analog_code

        # Raw weight/dimension fields from extension (parsed into grams/mm)
        raw_to_target = {
            "package_weight_raw": "package_weight_g",
            "product_weight_raw": "product_weight_g",
            "package_length_raw": "package_length_mm",
            "package_height_raw": "package_height_mm",
            "package_width_raw": "package_width_mm",
        }

        for raw_field, target in raw_to_target.items():
            raw_value = cleaned.get(raw_field)
            if raw_value is None:
                continue
            parser = (
                self._parse_weight_to_grams
                if "weight" in raw_field
                else self._parse_length_to_mm
            )
            parsed_value = parser(raw_value)
            if parsed_value is None:
                self.logger.warning("Failed to parse %s", raw_field)
            else:
                normalized[target] = parsed_value

        # Fallback: if only legacy numeric fields are present with units, try to
        # populate the normalized gram/mm fields as well.
        if "package_weight_g" not in normalized:
            parsed_weight = self._parse_weight_to_grams(cleaned.get("weight"))
            if parsed_weight is not None:
                normalized["package_weight_g"] = parsed_weight
        if "package_length_mm" not in normalized:
            parsed_length = self._parse_length_to_mm(cleaned.get("length"))
            if parsed_length is not None:
                normalized["package_length_mm"] = parsed_length
        if "package_height_mm" not in normalized:
            parsed_height = self._parse_length_to_mm(cleaned.get("height"))
            if parsed_height is not None:
                normalized["package_height_mm"] = parsed_height
        if "package_width_mm" not in normalized:
            parsed_width = self._parse_length_to_mm(cleaned.get("width"))
            if parsed_width is not None:
                normalized["package_width_mm"] = parsed_width

        # OEM numbers: accept array or comma-separated string
        raw_oems = cleaned.get("oem_numbers")
        oem_list: list[str] = []
        if isinstance(raw_oems, str):
            oem_list = [part.strip() for part in raw_oems.split(",") if part.strip()]
        elif isinstance(raw_oems, (list, tuple, set)):
            for val in raw_oems:
                if isinstance(val, str):
                    trimmed = val.strip()
                    if trimmed:
                        oem_list.append(trimmed)
        if oem_list:
            normalized["oem_number"] = ", ".join(oem_list)
            normalized["oem_number_primary"] = oem_list[0]

        # Pass-through optional text/int fields when provided
        passthrough_fields = [
            "material",
            "manufacturer_part_number",
            "oem_number",
            "oem_number_primary",
        ]
        for field in passthrough_fields:
            if field in cleaned and cleaned.get(field) not in (None, ""):
                normalized[field] = cleaned[field]

        # inner diameter may come as str; try simple int conversion
        inner_diameter = cleaned.get("inner_diameter_mm")
        if inner_diameter not in (None, ""):
            try:
                normalized["inner_diameter_mm"] = int(float(str(inner_diameter)))
            except (TypeError, ValueError):
                self.logger.warning("Failed to parse inner_diameter_mm")

        return normalized

    def post(
        self, request: Request, pk: int, *args: object, **kwargs: object
    ) -> Response:
        self.logger.info(
            "Details ingest raw request", extra={"product_id": pk, "data": request.data}
        )
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
        self.logger.info(
            "Details ingest normalized payload",
            extra={"product_id": pk, "normalized": normalized},
        )
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
        search_request_id_raw = request.query_params.get("search_request_id")
        search_request_id = None
        if search_request_id_raw:
            try:
                search_request_id = int(search_request_id_raw)
            except (TypeError, ValueError):
                search_request_id = None

        pending = (
            Product.objects.filter(details_request__status="pending", user=user)
            .filter(
                **(
                    {"search_request_id": search_request_id}
                    if search_request_id
                    else {}
                )
            )
            .select_related("details_request")
            .order_by("details_request__created_at", "id")[:limit]
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
