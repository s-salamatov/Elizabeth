from __future__ import annotations

from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.products.models import Product
from backend.apps.products.serializers import ProductSerializer
from backend.apps.providers.armtek.exceptions import (
    ArmtekCredentialsError,
    ArmtekError,
)
from backend.apps.search.models import SearchRequest
from backend.apps.search.serializers import (
    BulkSearchSerializer,
    SearchInputSerializer,
    SearchRequestSerializer,
)
from backend.apps.search.services import (
    parse_bulk_payload,
    perform_bulk_search,
    perform_single_search,
)


class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        assert request.user.is_authenticated
        user = cast(Any, request.user)
        history = SearchRequest.objects.filter(user=user)
        return Response(SearchRequestSerializer(history, many=True).data)

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        assert request.user.is_authenticated
        user = cast(Any, request.user)
        serializer = SearchInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            search_request, products = perform_single_search(
                serializer.validated_data["query"],
                user=user,
                source=serializer.validated_data.get("source", "armtek"),
            )
        except ArmtekCredentialsError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except ArmtekError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(
            {
                "request": SearchRequestSerializer(search_request).data,
                "products": ProductSerializer(products, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )


class BulkSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        assert request.user.is_authenticated
        user = cast(Any, request.user)
        serializer = BulkSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queries = parse_bulk_payload(serializer.validated_data)
        try:
            search_request, products = perform_bulk_search(
                queries,
                user=user,
                source=serializer.validated_data.get("source", "armtek"),
            )
        except ArmtekCredentialsError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except ArmtekError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(
            {
                "request": SearchRequestSerializer(search_request).data,
                "products": ProductSerializer(products, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )


class SearchDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(
        self, request: Request, pk: int, *args: object, **kwargs: object
    ) -> Response:
        assert request.user.is_authenticated
        user = cast(Any, request.user)
        try:
            search_request = SearchRequest.objects.get(pk=pk, user=user)
        except SearchRequest.DoesNotExist:
            return Response(
                {"detail": "Search request not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        products = Product.objects.filter(search_request=search_request)
        return Response(
            {
                "request": SearchRequestSerializer(search_request).data,
                "products": ProductSerializer(products, many=True).data,
            }
        )
