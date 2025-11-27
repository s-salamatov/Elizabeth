import os
import shutil
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from elizabeth.web.app import create_app


def ensure_playwright_chromium() -> None:
    """
    Install Playwright Chromium browser if available.

    This runs a best-effort install and logs to stdout only on failure.
    """

    if os.getenv("SKIP_PLAYWRIGHT_INSTALL") == "1":
        return

    playwright_bin = shutil.which("playwright")
    if not playwright_bin:
        return

    try:
        result = subprocess.run(
            [playwright_bin, "install", "chromium"],
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception:
        return

    if result.returncode != 0:
        sys.stderr.write(f"playwright install chromium failed: {result.stderr.strip()}\n")


app = create_app()

if __name__ == "__main__":
    ensure_playwright_chromium()
    app.run(debug=True)
