from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from .config import ArmtekConfig
from .exceptions import ArmtekHttpError, ArmtekResponseFormatError

logger = logging.getLogger(__name__)


class ArmtekHttpClient:
    def __init__(self, config: ArmtekConfig):
        self._config = config
        self._client = httpx.Client(
            base_url=self._config.base_url.rstrip("/"),
            auth=(self._config.login, self._config.password),
            timeout=self._config.timeout,
        )

    def close(self) -> None:
        self._client.close()

    def _normalize_path(self, path: str) -> str:
        return path if path.startswith("/") else f"/{path}"

    def _merge_params(self, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        merged: Dict[str, Any] = {}
        if params:
            merged.update(params)
        lower_keys = {str(k).lower() for k in merged}
        if "format" not in lower_keys:
            merged["format"] = "json"
        return merged

    def _parse_json(self, response: httpx.Response) -> Dict[str, Any]:
        try:
            return response.json()
        except ValueError as exc:  # json.JSONDecodeError is a subclass
            raise ArmtekResponseFormatError("Response is not valid JSON") from exc

    def _body_excerpt(self, response: httpx.Response, limit: int = 500) -> str:
        try:
            text = response.text
        except UnicodeDecodeError:
            return ""
        return text[:limit]

    def _request(
        self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        merged_params = self._merge_params(params)
        try:
            response = self._client.request(
                method,
                self._normalize_path(path),
                params=merged_params,
                data=data,
            )
            logger.info("%s %s -> %s", method.upper(), response.url, response.status_code)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                snippet = self._body_excerpt(exc.response)
                message = f"Armtek HTTP {exc.response.status_code}"
                if snippet:
                    message = f"{message}: {snippet}"
                raise ArmtekHttpError(message) from exc
            return self._parse_json(response)
        except httpx.TimeoutException as exc:
            raise ArmtekHttpError("Armtek request timed out") from exc
        except httpx.RequestError as exc:
            raise ArmtekHttpError(f"Armtek HTTP request failed: {exc}") from exc

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("get", path, params=params)

    def post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("post", path, data=data)

    def __enter__(self) -> "ArmtekHttpClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
