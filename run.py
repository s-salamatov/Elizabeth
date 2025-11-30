"""Convenience wrapper to launch the Django dev server.

Usage: ``python run.py``
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent / "elizabeth"
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from elizabeth.manage import main as django_main


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elizabeth.settings.dev")
    # Default to ``runserver`` if no arguments are provided.
    if len(sys.argv) == 1:
        sys.argv.extend(["runserver", "0.0.0.0:8000"])
    django_main()
