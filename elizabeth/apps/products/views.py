from __future__ import annotations

from django.conf import settings
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from elizabeth.apps.products.models import Product
from elizabeth.apps.products.serializers import (
    ProductDetailsInputSerializer,
    ProductDetailsSerializer,
    ProductSerializer,
)
from elizabeth.apps.products.services import (
    mark_requests_pending,
    update_product_details,
)


class ProductListView(ListAPIView[Product]):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer


class ProductDetailView(RetrieveAPIView[Product]):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailsIngestView(APIView):
    permission_classes = [AllowAny]

    def post(
        self, request: Request, pk: int, *args: object, **kwargs: object
    ) -> Response:
        token = request.headers.get("X-Details-Token") or request.query_params.get(
            "request_id"
        )
        serializer = ProductDetailsInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # Request correlation check (if provided we require match)
        if token:
            if (
                not getattr(product, "details_request", None)
                or str(product.details_request.request_id) != token
            ):
                return Response(
                    {"detail": "Invalid request_id"}, status=status.HTTP_403_FORBIDDEN
                )
        details = update_product_details(product, data=serializer.validated_data)
        return Response(
            ProductDetailsSerializer(details).data,
            status=status.HTTP_201_CREATED,
        )


class ProductDetailsRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        product_ids = request.data.get("product_ids") or []
        if not isinstance(product_ids, list) or not product_ids:
            return Response(
                {"detail": "Provide product_ids array"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        products = list(Product.objects.filter(id__in=product_ids))
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
        limit_raw = request.query_params.get("limit") or "20"
        try:
            limit = max(1, min(int(limit_raw), 200))
        except ValueError:
            limit = 20

        pending = (
            Product.objects.filter(details_request__status="pending")
            .select_related("details_request")
            .order_by("-details_request__created_at")[:limit]
        )
        base_url = getattr(
            settings, "ARMTEK_HTML_BASE_URL", "https://etp.armtek.ru/artinfo/index"
        ).rstrip("/")
        jobs = []
        for product in pending:
            req = product.details_request
            open_url = (
                f"{base_url}/{product.artid}"
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
