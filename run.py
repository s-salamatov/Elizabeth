import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from elizabeth.web.app import create_app  # noqa: E402


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5500, debug=True)
