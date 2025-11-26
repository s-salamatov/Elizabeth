from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..exceptions import ArmtekResponseFormatError, ArmtekStatusError


def unwrap_resp(raw: Any) -> Mapping[str, Any]:
    if not isinstance(raw, Mapping):
        raise ArmtekResponseFormatError("Response must be a mapping")
    if "STATUS" not in raw:
        raise ArmtekResponseFormatError("Missing STATUS field")
    status = raw["STATUS"]
    messages_raw = raw.get("MESSAGES", [])
    messages: list[str] = []
    if isinstance(messages_raw, Sequence) and not isinstance(messages_raw, (str, bytes)):
        messages = [str(item) for item in messages_raw]
    elif messages_raw:
        messages = [str(messages_raw)]
    if status != 200:
        raise ArmtekStatusError(int(status), messages)
    if "RESP" not in raw:
        raise ArmtekResponseFormatError("Missing RESP section")
    resp = raw["RESP"]
    if isinstance(resp, list):
        resp = {"ARRAY": resp}
    elif not isinstance(resp, Mapping):
        raise ArmtekResponseFormatError("RESP section must be a mapping")
    return resp


def extract_array(resp: Mapping[str, Any], name: str) -> list[Any]:
    if name not in resp:
        raise ArmtekResponseFormatError(f"Missing RESP.{name}")
    value = resp[name]
    if not isinstance(value, list):
        raise ArmtekResponseFormatError(f"RESP.{name} must be a list")
    return value
