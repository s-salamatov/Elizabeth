from __future__ import annotations

from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.products.serializers import ProductSerializer
from backend.apps.providers.armtek.exceptions import (
    ArmtekCredentialsError,
    ArmtekError,
)
from backend.apps.providers.serializers import (
    ArmtekCredentialsSerializer,
    ArmtekSearchInputSerializer,
    ProviderAccountSerializer,
)
from backend.apps.providers.services import (
    resolve_armtek_credentials,
    save_provider_account,
    update_armtek_account_context,
)
from backend.apps.search.services import perform_single_search


class ProviderAccountListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        assert request.user.is_authenticated
        user = cast(Any, request.user)
        accounts = user.provider_accounts.all()
        return Response(ProviderAccountSerializer(accounts, many=True).data)


class ArmtekSearchProxyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        assert request.user.is_authenticated
        user = cast(Any, request.user)
        serializer = ArmtekSearchInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            search_request, products = perform_single_search(
                serializer.validated_data["query"],
                user=user,
                source="armtek",
            )
        except ArmtekCredentialsError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except ArmtekError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(ProductSerializer(products, many=True).data)


class ArmtekCredentialsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        assert request.user.is_authenticated
        user = cast(Any, request.user)
        credentials = resolve_armtek_credentials(user)
        if credentials is None:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response(
            {
                "login": credentials.login,
                "pin": credentials.pin,
                "vkorg": credentials.vkorg,
                "kunnr_rg": credentials.kunnr_rg,
                "program": credentials.program,
                "kunnr_za": credentials.kunnr_za,
                "incoterms": credentials.incoterms,
                "vbeln": credentials.vbeln,
            }
        )

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        assert request.user.is_authenticated
        user = cast(Any, request.user)
        serializer = ArmtekCredentialsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        account = save_provider_account(
            user=user,
            provider_name="armtek",
            login=data["login"],
            password=data["password"],
            pin=data.get("pin"),
            vkorg=data.get("vkorg"),
            kunnr_rg=data.get("kunnr_rg"),
            program=data.get("program"),
            kunnr_za=data.get("kunnr_za"),
            incoterms=data.get("incoterms"),
            vbeln=data.get("vbeln"),
        )
        try:
            update_armtek_account_context(account)
        except ArmtekCredentialsError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except ArmtekError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request: Request, *args: object, **kwargs: object) -> Response:
        assert request.user.is_authenticated
        user = cast(Any, request.user)
        user.provider_accounts.filter(provider_name="armtek").delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
