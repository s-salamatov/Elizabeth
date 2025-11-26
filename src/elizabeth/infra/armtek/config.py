from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ArmtekConfig:
    base_url: str
    login: str
    password: str
    timeout: float = 5.0
