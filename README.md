# Elizabeth

Typed Python client and service layer for the Armtek API with Pydantic validation, small service helpers, and manual integration hooks.

## Features
- HTTP client with error handling for Armtek status codes and response formats.
- Pydantic models that normalize Armtek payloads (buyers, delivery points, search items) with parsing helpers for dates/decimals/flags.
- Service layer to pick the main search result and plug in custom HTML parsers.
- Manual integration test scaffold guarded by a pytest marker.

## Quickstart
1. Python 3.12+ (CI currently targets 3.14 preview).
2. Create a virtualenv: `python -m venv .venv && source .venv/bin/activate`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run tests: `pytest` (integration test is skipped unless env vars are set).

## Usage
```python
from elizabeth.infra.armtek import ArmtekClient, ArmtekConfig

config = ArmtekConfig(
    base_url="https://ws.armtek.ru",
    login="YOUR_LOGIN",
    password="YOUR_PASSWORD",
)

with ArmtekClient(config) as client:
    items = client.search(vkorg="2000", kunnr_rg="3000", pin="123456")
    main = items[0] if items else None
    print(main.artid if main else "not found")
```
To select the first non-analog result or delegate HTML parsing, use `ArmtekService` from `src/elizabeth/services/armtek_service.py`.

## Tests
- Fast suite: `pytest`.
- Integration: `pytest -m integration` with `ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, `ARMTEK_PIN`; optionally `ARMTEK_BASE_URL`, `ARMTEK_VKORG`, `ARMTEK_KUNNR_RG`.

## Project Layout
- `src/elizabeth/domain/`: Pydantic models for Armtek data.
- `src/elizabeth/infra/`: HTTP client, parsing helpers, and Armtek service wrappers.
- `src/elizabeth/services/`: Higher-level service orchestrators.
- `tests/`: Unit tests plus one manual integration check.

## Contributing
See `AGENTS.md` for contributor guidelines, coding style, and pull request expectations.

## License
License is not specified in this repository. Add a LICENSE file before publishing publicly.
