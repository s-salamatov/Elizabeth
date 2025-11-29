# Repository Guidelines

## Project Structure & Module Organization
- `elizabeth/backend/models/`: Pydantic models for Armtek payloads (`search_result.py`) and dataclasses for characteristics (`characteristics.py`).
- `elizabeth/backend/services/tokens.py`: Deterministic token helpers for Armtek API calls and extension callbacks built on `ArmtekSearchContext`.
- `elizabeth/backend/services/armtek/`: Armtek HTTP client, endpoint wrappers, orchestration service, exceptions, and the extension parser stub (`parser_adapter.py`).
- `elizabeth/backend/repositories/`: Dataclasses and repository interfaces for storing parsed product characteristics (default in-memory impl used by web callbacks).
- `elizabeth/backend/api/`: Flask blueprints for search, characteristics callbacks, and health checks; `backend/app.py` wires dependencies and template/static paths.
- `elizabeth/backend/utils/`: Validation helpers for response parsing and type coercion plus a lightweight logger helper.
- `elizabeth/frontend/`: Templates and static assets served by `run.py`; keep presentation concerns separate from backend logic.
- `elizabeth/extensions/armtek_extension.user.js`: Tampermonkey/Greasemonkey helper posting data to `/api/armtek/characteristics`.
- Tests sit in `tests/` (`backend/`, `logic/`, `tokens/`); `pytest.ini` holds markers, dependencies live in `requirements.txt`.

## Build, Test, and Development Commands
- Optional venv: `python -m venv .venv && source .venv/bin/activate`.
- Install deps: `pip install -r requirements.txt`.
- Run fast suite: `pytest` (integration test skips unless credentials are set).
- Live check: `pytest -m integration` with `ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, `ARMTEK_PIN`, optionally `ARMTEK_BASE_URL`, `ARMTEK_VKORG`, `ARMTEK_KUNNR_RG`.
- Run the Flask UI locally with `python run.py` or `FLASK_APP=run.py flask run --debug`; set `ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, `ARMTEK_PIN`, `ARMTEK_VKORG`, `ARMTEK_KUNNR_RG` (plus optional `ARMTEK_PROGRAM`, `ARMTEK_KUNNR_ZA`, `ARMTEK_INCOTERMS`, `ARMTEK_VBELN`, `ARMTEK_TIMEOUT`) for real data, and use `ELIZABETH_BACKEND_BASE_URL`/`ELIZABETH_EXTENSION_ALLOWED_ORIGIN` to control frontend fetch base and extension CORS.
- For ad-hoc scripts outside tests, import from `elizabeth.*` directly (package lives at repo root).

## Coding Style & Naming Conventions
- Python defaults: 4-space indents, snake_case modules/functions, PascalCase for models; keep type hints and `dataclass`/Pydantic usage consistent.
- Reuse parsing helpers in `backend/utils/validation.py` and raise `Armtek*Error` subclasses instead of swallowing malformed responses.
- Keep docstrings concise; close HTTP clients/services via context managers (`ArmtekClient`, `ArmtekService`) to release connections.
- Prefer extending service layers rather than inlining HTTP calls in domain logic.
- Token helpers (`backend/services/tokens.py`) and characteristic repositories should remain deterministic; adjust `tests/tokens/test_tokens_and_repository.py` when changing hashing/registration semantics.
- Inject new storage or parsers through `create_app`/`ArmtekCharacteristicsRepository`/`ArmtekProductParser` rather than bypassing the existing hooks in `backend/app.py`.

## Testing Guidelines
- Name tests `test_*.py` under `tests/` and mirror the module you cover.
- Favor dummy clients/mocks for HTTP behavior; assert both happy paths and error handling (status errors, missing fields, bad formats).
- Gate any network-dependent checks behind the `integration` marker and document required env vars in the test.
- When adding parsers or validators, add edge-case fixtures (empty arrays, unexpected types) similar to existing service tests.
- For web endpoints and token/repository changes, extend `tests/backend/test_app.py` and `tests/tokens/test_tokens_and_repository.py` to cover serialization, CORS headers, and ready/pending flows.

## Commit & Pull Request Guidelines
- Follow the existing log style: short, imperative summaries in Title Case without trailing periods (e.g., `Refactor project into layered architecture`).
- PRs should state scope, risks, and test commands (include whether integration was run and which env vars were used); link issues when relevant.
- For new endpoints or parsing changes, include example payload snippets or response notes to aid review.

## Security & Configuration Tips
- Keep credentials in env vars only (`ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, etc.); never commit real responses or configs with secrets.
- Make `ArmtekConfig` values explicit in code paths, and avoid logging sensitive fields when dumping errors or response excerpts.
- Treat API/characteristics tokens and extension traffic as sensitive; set `ELIZABETH_EXTENSION_ALLOWED_ORIGIN` when exposing `/api/armtek/characteristics` and avoid logging raw tokens or user-supplied payloads.
