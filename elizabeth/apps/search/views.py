from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.serializers import ProductSerializer
from apps.providers.armtek.exceptions import ArmtekCredentialsError, ArmtekError
from apps.search.serializers import (
    BulkSearchSerializer,
    SearchInputSerializer,
    SearchRequestSerializer,
)
from apps.search.services import parse_bulk_payload, perform_bulk_search, perform_single_search


class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = SearchInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            search_request, products = perform_single_search(
                serializer.validated_data["query"],
                user=request.user,
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

    def post(self, request, *args, **kwargs):
        serializer = BulkSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queries = parse_bulk_payload(serializer.validated_data)
        try:
            search_request, products = perform_bulk_search(
                queries,
                user=request.user,
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
