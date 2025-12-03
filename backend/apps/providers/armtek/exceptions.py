from __future__ import annotations


class ArmtekError(Exception):
    """Base exception for Armtek client errors."""


class ArmtekCredentialsError(ArmtekError):
    """Raised when credentials are missing or invalid."""


class ArmtekResponseError(ArmtekError):
    """Raised when Armtek returns unexpected payload."""

    def __init__(self, message: str, *, status: int | None = None):
        super().__init__(message)
        self.status = status
