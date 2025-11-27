import pytest

from elizabeth.infra.armtek.html_session import ArmtekHtmlSession, ArmtekSessionStore, SessionStatus
from elizabeth.parsers.armtek_parser import ArmtekHtmlParser


def test_session_store_save_and_load(tmp_path):
    path = tmp_path / "data" / "armtek_session.json"
    store = ArmtekSessionStore(path)
    state = {"cookies": [{"name": "sid", "value": "abc", "domain": ".example.com", "path": "/"}], "origins": []}

    store.save_storage_state(state)

    loaded = store.load_storage_state()
    assert loaded == state


def test_session_store_missing_file(tmp_path):
    store = ArmtekSessionStore(tmp_path / "missing.json")
    with pytest.raises(FileNotFoundError):
        store.load_storage_state()


def test_session_store_invalid_json(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("not-json", encoding="utf-8")
    store = ArmtekSessionStore(path)

    with pytest.raises(ValueError):
        store.load_storage_state()


def test_detect_session_status_login_required(tmp_path):
    store = ArmtekSessionStore(tmp_path / "state.json")
    session = ArmtekHtmlSession(store)
    html = "<html><body><input id='login'><input id='password'></body></html>"
    assert session.detect_session_status(html, final_url="https://etp.armtek.ru/") == SessionStatus.LOGIN_REQUIRED


def test_detect_session_status_captcha(tmp_path):
    store = ArmtekSessionStore(tmp_path / "state.json")
    session = ArmtekHtmlSession(store)
    html = "<html><body>cf-challenge turnstile</body></html>"
    assert session.detect_session_status(html) == SessionStatus.CAPTCHA_REQUIRED


def test_detect_session_status_ok(tmp_path):
    store = ArmtekSessionStore(tmp_path / "state.json")
    session = ArmtekHtmlSession(store)
    html = "<div id='artInfo-container'></div>"
    assert session.detect_session_status(html) == SessionStatus.OK


def test_parse_image_url_from_html(tmp_path):
    store = ArmtekSessionStore(tmp_path / "state.json")

    class DummyLoginFlow:
        def run(self, artid=None):
            raise AssertionError("Login flow should not be called")

    parser = ArmtekHtmlParser(session=ArmtekHtmlSession(store), login_flow=DummyLoginFlow())
    html = """
    <div id="artInfo-container">
      <div class="galleryInfo">
        <div class="main-image">
          <a data-imagelightbox="tecdoc" id="https://img.armtek.ru/img/article/123/12345/500x500/12345_0.webp"></a>
        </div>
      </div>
    </div>
    """
    image_url = parser._parse_image_url_from_html("12345", html)  # pylint: disable=protected-access
    assert image_url == "https://img.armtek.ru/img/article/123/12345/500x500/12345_0.webp"


def test_parse_image_url_from_html_missing(tmp_path):
    store = ArmtekSessionStore(tmp_path / "state.json")

    class DummyLoginFlow:
        def run(self, artid=None):
            raise AssertionError("Login flow should not be called")

    parser = ArmtekHtmlParser(session=ArmtekHtmlSession(store), login_flow=DummyLoginFlow())
    html = "<div id='artInfo-container'></div>"
    image_url = parser._parse_image_url_from_html("12345", html)  # pylint: disable=protected-access
    assert image_url is None
