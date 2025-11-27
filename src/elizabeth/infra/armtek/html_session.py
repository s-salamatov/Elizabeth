from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any

import httpx


class SessionStatus(str, Enum):
    OK = "ok"
    LOGIN_REQUIRED = "login_required"
    CAPTCHA_REQUIRED = "captcha_required"


class ArmtekSessionStore:
    """
    Хранит состояние сессии Armtek (Playwright storage_state JSON).

    По сути это обертка над файлом data/armtek_session.json.
    """

    def __init__(self, path: Path) -> None:
        self._path = path

    def exists(self) -> bool:
        """Возвращает True, если файл storage_state существует."""
        return self._path.exists()

    def load_storage_state(self) -> dict[str, Any]:
        """
        Читает JSON из файла.
        Если файл отсутствует или пустой — бросает FileNotFoundError или ValueError.
        """
        if not self._path.exists():
            raise FileNotFoundError(f"Storage state not found at {self._path}")

        content = self._path.read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError("Storage state file is empty")

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid storage state JSON") from exc

        if not isinstance(data, dict):
            raise ValueError("Storage state must be a JSON object")

        return data

    def save_storage_state(self, state: dict[str, Any]) -> None:
        """
        Сохраняет JSON в файл.
        Директорию при необходимости создаёт.
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


class ArmtekHtmlSession:
    """
    Создает httpx.Client с cookie, извлеченными из storage_state Playwright.
    """

    def __init__(
        self,
        store: ArmtekSessionStore,
        base_url: str = "https://etp.armtek.ru",
        user_agent: str | None = None,
    ) -> None:
        self._store = store
        self._base_url = base_url
        self._user_agent = user_agent or ("ELIZABETH-ArmtekHtmlClient/1.0")

    def create_client(self) -> httpx.Client:
        """
        Создает httpx.Client с:
        - base_url = self._base_url,
        - headers["User-Agent"] = self._user_agent,
        - cookies, загруженными из storage_state["cookies"].

        Если файл storage_state отсутствует или некорректен — бросает FileNotFoundError/ValueError.
        """
        storage_state = self._store.load_storage_state()
        cookies_data = storage_state.get("cookies")
        if not isinstance(cookies_data, list):
            raise ValueError("Invalid storage state: cookies must be a list")

        cookies = httpx.Cookies()
        for cookie in cookies_data:
            if not isinstance(cookie, dict):
                raise ValueError("Invalid cookie entry in storage state")
            name = cookie.get("name")
            value = cookie.get("value", "")
            domain = cookie.get("domain")
            path = cookie.get("path", "/")
            if not name or not domain:
                raise ValueError("Cookie entries must include name and domain")
            cookies.set(name, value, domain=domain, path=path)

        headers = {"User-Agent": self._user_agent}

        return httpx.Client(base_url=self._base_url, headers=headers, cookies=cookies, follow_redirects=True)

    def detect_session_status(self, html: str, final_url: str | None = None) -> SessionStatus:
        """
        Анализирует HTML и URL ответа и определяет статус сессии.

        Правила:

        - Если HTML содержит поля логина:
            * input#login
            * input#password
          И/или final_url == "https://etp.armtek.ru/"
          → SessionStatus.LOGIN_REQUIRED

        - Если HTML содержит признаки Cloudflare Turnstile / challenge:
            * строки типа "cf-challenge", "challenges.cloudflare.com", "turnstile"
          → SessionStatus.CAPTCHA_REQUIRED

        - Если HTML содержит контейнер карточки товара:
            * элемент с id="artInfo-container"
          → SessionStatus.OK

        В случае неоднозначности LOGIN_REQUIRED и CAPTCHA_REQUIRED приоритет: CAPTCHA_REQUIRED.
        """

        normalized_html = html.lower()

        captcha_markers = ("cf-challenge", "challenges.cloudflare.com", "turnstile")
        if any(marker in normalized_html for marker in captcha_markers):
            return SessionStatus.CAPTCHA_REQUIRED

        if "id=\"artinfo-container\"" in normalized_html or "id='artinfo-container'" in normalized_html:
            return SessionStatus.OK

        login_markers = (
            'input id="login"',
            "input id='login'",
            "input#login",
            'input id="password"',
            "input#password",
        )
        if any(marker in normalized_html for marker in login_markers) or final_url in {
            "https://etp.armtek.ru/",
            "https://etp.armtek.ru",
        }:
            return SessionStatus.LOGIN_REQUIRED

        return SessionStatus.LOGIN_REQUIRED
