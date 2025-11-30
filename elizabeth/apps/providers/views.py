from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.serializers import ProductSerializer
from apps.products.services import upsert_products_from_search
from apps.providers.armtek.exceptions import ArmtekError, ArmtekCredentialsError
from apps.providers.armtek.services import ArmtekSearchService
from apps.providers.serializers import ArmtekSearchInputSerializer
from apps.providers.services import resolve_armtek_credentials


class ArmtekSearchProxyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = ArmtekSearchInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        credentials = resolve_armtek_credentials(request.user)
        service = ArmtekSearchService(credentials)

        try:
            items = service.search(
                pin=serializer.validated_data["pin"],
                brand=serializer.validated_data.get("brand"),
            )
        except ArmtekCredentialsError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        except ArmtekError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY
            )

        products = upsert_products_from_search(items, source="armtek")
        return Response(ProductSerializer(products, many=True).data)
