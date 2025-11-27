from __future__ import annotations

from pathlib import Path
from typing import Optional
from selectolax.parser import HTMLParser

from elizabeth.domain.armtek_models import ProductHtmlDetails
from elizabeth.infra.armtek.exceptions import ArmtekInteractiveLoginRequired
from elizabeth.infra.armtek.html_session import ArmtekHtmlSession, SessionStatus
from elizabeth.infra.armtek.interactive_login import ArmtekInteractiveLoginFlow


class ArmtekHtmlParser:
    """
    Парсер HTML-страницы товара Armtek.
    """

    def __init__(
        self,
        session: ArmtekHtmlSession,
        login_flow: ArmtekInteractiveLoginFlow,
    ) -> None:
        self._session = session
        self._login_flow = login_flow

    def get_product_details(self, artid: str) -> ProductHtmlDetails:
        """
        Возвращает ProductHtmlDetails(artid=..., image_url=...).
        """
        try:
            html, status = self._fetch_html(artid)
        except (FileNotFoundError, ValueError):
            raise ArmtekInteractiveLoginRequired(
                "Требуется интерактивная авторизация или прохождение капчи"
            ) from None

        if status in {SessionStatus.LOGIN_REQUIRED, SessionStatus.CAPTCHA_REQUIRED}:
            self._login_flow.run(artid=artid)
            html, status = self._fetch_html(artid)

            if status in {SessionStatus.LOGIN_REQUIRED, SessionStatus.CAPTCHA_REQUIRED}:
                raise ArmtekInteractiveLoginRequired("Требуется интерактивная авторизация или прохождение капчи")

        image_url = self._parse_image_url_from_html(artid, html)

        if image_url is None:
            image_url = self._fallback_playwright_parse(artid)

        return ProductHtmlDetails(artid=artid, image_url=image_url)

    def _fetch_html(self, artid: str) -> tuple[str, SessionStatus]:
        """
        Использует ArmtekHtmlSession.create_client() и httpx, чтобы:
        - выполнить GET /artinfo/index/{artid},
        - получить финальный HTML (resp.text),
        - определить SessionStatus через ArmtekHtmlSession.detect_session_status.
        """
        with self._session.create_client() as client:
            response = client.get(f"/artinfo/index/{artid}")
            response.raise_for_status()
            html = response.text
            final_url = str(response.url)
            status = self._session.detect_session_status(html, final_url)
            return html, status

    def _parse_image_url_from_html(self, artid: str, html: str) -> str | None:
        """
        Чистый HTML-разбор (без HTTP).
        """
        root = HTMLParser(html)
        container = root.css_first("#artInfo-container")
        if container is None:
            return None

        link = container.css_first("div.galleryInfo div.main-image a[data-imagelightbox='tecdoc']")
        if link is None:
            return None

        href = link.attributes.get("id") or link.attributes.get("href")
        return href

    def _fallback_playwright_parse(self, artid: str) -> Optional[str]:
        """
        Опциональный fallback на Playwright для динамического DOM.
        """
        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
            from playwright.sync_api import sync_playwright
        except ImportError:
            return None

        start_url = self._login_flow._config.artinfo_url_template.format(artid=artid)  # type: ignore[attr-defined]
        storage_state_path = Path(self._login_flow._config.storage_state_path)  # type: ignore[attr-defined]

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context_kwargs: dict[str, object] = {}
            context = None
            try:
                store = getattr(self._session, "_store", None)
                if store and store.exists():
                    context_kwargs["storage_state"] = storage_state_path

                context = browser.new_context(**context_kwargs)
                page = context.new_page()
                page.goto(start_url, wait_until="domcontentloaded")
                try:
                    page.wait_for_selector(
                        "div.galleryInfo div.main-image a[data-imagelightbox='tecdoc']", timeout=5000
                    )
                    link = page.query_selector("div.galleryInfo div.main-image a[data-imagelightbox='tecdoc']")
                    if link:
                        href = link.get_attribute("id") or link.get_attribute("href")
                        return href
                except PlaywrightTimeoutError:
                    return None
                finally:
                    if context is not None:
                        context.close()
            finally:
                browser.close()

        return None
