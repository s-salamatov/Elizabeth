from __future__ import annotations

from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.models import Product
from apps.products.serializers import (
    ProductDetailsInputSerializer,
    ProductDetailsSerializer,
    ProductSerializer,
)
from apps.products.services import update_product_details


class ProductListView(ListAPIView):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer


class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailsIngestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk: int, *args, **kwargs):
        serializer = ProductDetailsInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )
        details = update_product_details(product, data=serializer.validated_data)
        return Response(
            ProductDetailsSerializer(details).data,
            status=status.HTTP_201_CREATED,
        )
