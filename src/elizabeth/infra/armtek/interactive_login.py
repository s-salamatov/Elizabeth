from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from elizabeth.infra.armtek.html_session import ArmtekSessionStore


@dataclass
class ArmtekInteractiveLoginConfig:
    base_url: str = "https://etp.armtek.ru"
    storage_state_path: str = "data/armtek_session.json"
    login_env_var: str = "ARMTEK_LOGIN"
    password_env_var: str = "ARMTEK_PASSWORD"
    login_page_url: str = "https://etp.armtek.ru/"
    artinfo_url_template: str = "https://etp.armtek.ru/artinfo/index/{artid}"
    timeout_seconds: int = 120


class ArmtekInteractiveLoginFlow:
    """
    Отвечает за интерактивный логин пользователя через Playwright.
    """

    def __init__(
        self,
        config: ArmtekInteractiveLoginConfig,
        store: ArmtekSessionStore,
    ) -> None:
        self._config = config
        self._store = store

    def run(self, artid: str | None = None) -> None:
        """
        Запускает интерактивный логин/обновление сессии.

        Параметры:
        - artid: если задан, логин начинается с открытия страницы товара:
            https://etp.armtek.ru/artinfo/index/{artid}
          Иначе открывается https://etp.armtek.ru/.

        Поведение:
        - Автоподстановка логина/пароля только на странице входа:
            * input#login
            * input#password
            * checkbox#remember (галочка "запомнить")
            * button#login-btn (кнопка "войти")
        - Капчу пользователь проходит самостоятельно.
        - По завершении или по таймауту — storage_state сохраняется в файл.
        """
        start_url = (
            self._config.artinfo_url_template.format(artid=artid)
            if artid
            else self._config.login_page_url
        )
        storage_state_path = Path(self._config.storage_state_path)
        deadline = time.time() + self._config.timeout_seconds

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=IsolateOrigins,site-per-process",
                ],
            )
            context_kwargs: dict[str, object] = {
                "ignore_https_errors": True,
                "viewport": None,
                "user_agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "locale": "ru-RU",
                "timezone_id": "Europe/Moscow",
                "color_scheme": "light",
            }
            context = None
            try:
                if self._store.exists():
                    context_kwargs["storage_state"] = storage_state_path

                context = browser.new_context(**context_kwargs)
                context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
                context.add_init_script(
                    "window.chrome = {runtime: {}, webstore: {onInstallStageChanged:{}, onDownloadProgress: {}}, app: {}};"
                )
                context.add_init_script("Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});")
                context.add_init_script(
                    "Object.defineProperty(navigator, 'languages', {get: () => ['ru-RU','ru','en-US','en']});"
                )
                page = context.new_page()
                # Начинаем с главной страницы, чтобы сначала отработали возможные challenge/редиректы, потом переходим к карточке.
                page.goto(self._config.login_page_url, wait_until="domcontentloaded")
                if artid:
                    page.goto(start_url, wait_until="domcontentloaded")

                try:
                    page.wait_for_selector("input#login", timeout=3000)
                    login = os.getenv(self._config.login_env_var, "")
                    password = os.getenv(self._config.password_env_var, "")

                    if login:
                        page.fill("input#login", login)
                    if password:
                        page.fill("input#password", password)

                    try:
                        page.check("input#remember", force=True)
                    except Exception:
                        # Checkbox might not exist on the page; ignore.
                        pass

                    try:
                        page.click("button#login-btn")
                    except Exception:
                        # Button may not be present if already authorized; ignore.
                        pass
                except PlaywrightTimeoutError:
                    # No login form found — likely already authorized or redirected to captcha.
                    pass

                while time.time() < deadline:
                    if page.is_closed():
                        break
                    page.wait_for_timeout(1000)

                state = context.storage_state()
                self._store.save_storage_state(state)
            finally:
                if context is not None:
                    context.close()
                browser.close()
