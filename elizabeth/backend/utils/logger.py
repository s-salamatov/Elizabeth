from __future__ import annotations

import logging
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Lightweight logger helper to avoid scattered ``logging.getLogger`` calls.
    """

    return logging.getLogger(name or __name__)
