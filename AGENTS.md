# Repository Guidelines

## Project Structure & Module Organization
- `src/elizabeth/domain/armtek_models.py`: Pydantic models and validators that normalize Armtek payloads (buyers, contracts, search items).
- `src/elizabeth/infra/armtek/`: HTTP config, client, parsing helpers, and service endpoints (`services/search.py`, `services/user.py`); HTML parser placeholder lives in `src/elizabeth/infra/armtek_parser/armtek_parser.py`.
- `src/elizabeth/services/armtek_service.py`: Service layer that selects the main search result and delegates HTML parsing via a protocol.
- Tests sit in `tests/` (unit plus one `@pytest.mark.integration` manual check); `pytest.ini` holds markers, dependencies live in `requirements.txt`.

## Build, Test, and Development Commands
- Optional venv: `python -m venv .venv && source .venv/bin/activate`.
- Install deps: `pip install -r requirements.txt`.
- Run fast suite: `pytest` (integration test skips unless credentials are set).
- Live check: `pytest -m integration` with `ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, `ARMTEK_PIN`, optionally `ARMTEK_BASE_URL`, `ARMTEK_VKORG`, `ARMTEK_KUNNR_RG`.
- For ad-hoc scripts outside tests, set `PYTHONPATH=src` or install the package in editable mode.

## Coding Style & Naming Conventions
- Python defaults: 4-space indents, snake_case modules/functions, PascalCase for models; keep type hints and `dataclass`/Pydantic usage consistent.
- Reuse parsing helpers in `infra/armtek/parsing.py` and raise `Armtek*Error` subclasses instead of swallowing malformed responses.
- Keep docstrings concise; close HTTP clients/services via context managers (`ArmtekClient`, `ArmtekService`) to release connections.
- Prefer extending service/infra layers rather than inlining HTTP calls in domain logic.

## Testing Guidelines
- Name tests `test_*.py` under `tests/` and mirror the module you cover.
- Favor dummy clients/mocks for HTTP behavior; assert both happy paths and error handling (status errors, missing fields, bad formats).
- Gate any network-dependent checks behind the `integration` marker and document required env vars in the test.
- When adding parsers or validators, add edge-case fixtures (empty arrays, unexpected types) similar to existing service tests.

## Commit & Pull Request Guidelines
- Follow the existing log style: short, imperative summaries in Title Case without trailing periods (e.g., `Refactor project into layered architecture`).
- PRs should state scope, risks, and test commands (include whether integration was run and which env vars were used); link issues when relevant.
- For new endpoints or parsing changes, include example payload snippets or response notes to aid review.

## Security & Configuration Tips
- Keep credentials in env vars only (`ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, etc.); never commit real responses or configs with secrets.
- Make `ArmtekConfig` values explicit in code paths, and avoid logging sensitive fields when dumping errors or response excerpts.
