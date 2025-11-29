from __future__ import annotations


class ArmtekError(Exception):
    """Base error for Armtek client."""


class ArmtekHttpError(ArmtekError):
    """HTTP/transport level issues."""


class ArmtekStatusError(ArmtekError):
    def __init__(self, status: int, messages: list[str] | None = None):
        self.status = status
        self.messages = messages or []
        super().__init__(f"Armtek returned status {status}: {'; '.join(self.messages)}")


class ArmtekResponseFormatError(ArmtekError):
    """Raised when response structure is unexpected."""


class ArmtekInteractiveLoginRequired(ArmtekError):
    """
    Бросается, когда после попыток интерактивного логина страница всё ещё
    требует входа или капчу.
    """
