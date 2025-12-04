# mypy: ignore-errors
"""Runtime compatibility fixes for the Elizabeth project.

Currently Django 5.1.x is not compatible with Python 3.14 because
``django.template.context.BaseContext.__copy__`` tries to copy a ``super``
object, which no longer supports attribute assignment in 3.14.  The
admin (and any template rendering) crashes with
``AttributeError: 'super' object has no attribute 'dicts'``.

We patch ``BaseContext.__copy__`` to perform a shallow copy that is
compatible with 3.14 while keeping the original semantics (copying the
``dicts`` stack and other attributes).  Remove once the project is on a
supported Python version (3.12 per repo guidelines) or after upgrading
Django when upstream fixes the issue.
"""

from __future__ import annotations

import sys
from typing import Callable, cast

import django
from django.template import context as _context


def patch_basecontext_copy() -> None:
    """Patch ``BaseContext.__copy__`` for Python 3.14 compatibility."""
    if getattr(_context.BaseContext.__copy__, "_elizabeth_patched", False):
        return

    def _basecontext_copy(self: _context.BaseContext) -> _context.BaseContext:
        # Create a blank instance of the same class without calling __init__
        duplicate = self.__class__.__new__(self.__class__)
        # Shallow-copy all attrs set on the instance (autoescape, request, etc.)
        duplicate.__dict__.update(self.__dict__)
        # Explicitly copy the context stack to decouple from the original
        duplicate.dicts = list(self.dicts)  # type: ignore[attr-defined]
        return duplicate

    _basecontext_copy._elizabeth_patched = True  # type: ignore[attr-defined]
    _context.BaseContext.__copy__ = cast(
        "Callable[[object], object]", _basecontext_copy
    )  # type: ignore[method-assign]


def apply_runtime_patches() -> None:
    if sys.version_info < (3, 14):
        return
    # Guard to only patch Django 5.1.x where the regression is observed.
    if django.VERSION[:2] != (5, 1):
        return
    patch_basecontext_copy()


# Apply on import so any code path (including manage.py) gets the fix early.
apply_runtime_patches()
