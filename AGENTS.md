# Repository Guidelines

## Project Structure & Module Organization
- `src/elizabeth/domain/armtek_models.py`: Pydantic models and validators that normalize Armtek payloads (buyers, contracts, search items).
- `src/elizabeth/domain/tokens.py`: Deterministic token helpers for Armtek API calls and characteristic callbacks built on `ArmtekSearchContext`.
- `src/elizabeth/infra/armtek/`: HTTP config, client, parsing helpers, and service endpoints (`services/search.py`, `services/user.py`); HTML parser placeholder lives in `src/elizabeth/infra/armtek_parser/armtek_parser.py`.
- `src/elizabeth/services/armtek_service.py`: Service layer that selects the main search result and delegates HTML parsing via a protocol.
- `src/elizabeth/services/characteristics_repository.py`: Dataclasses and repository interface for storing parsed product characteristics (default in-memory impl used by web callbacks).
- `src/elizabeth/web/`: Flask UI (`web/app.py` + static assets/templates) served via `run.py`; Tampermonkey/Greasemonkey helper script lives at `src/elizabeth/core/other/armtek_extension.user.js` and posts data to `/api/armtek/characteristics`.
- Tests sit in `tests/` (unit plus one `@pytest.mark.integration` manual check); `pytest.ini` holds markers, dependencies live in `requirements.txt`.

## Build, Test, and Development Commands
- Optional venv: `python -m venv .venv && source .venv/bin/activate`.
- Install deps: `pip install -r requirements.txt`.
- Run fast suite: `pytest` (integration test skips unless credentials are set).
- Live check: `pytest -m integration` with `ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, `ARMTEK_PIN`, optionally `ARMTEK_BASE_URL`, `ARMTEK_VKORG`, `ARMTEK_KUNNR_RG`.
- Run the Flask UI locally with `python run.py` or `FLASK_APP=run.py flask run --debug`; set `ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, `ARMTEK_PIN`, `ARMTEK_VKORG`, `ARMTEK_KUNNR_RG` (plus optional `ARMTEK_PROGRAM`, `ARMTEK_KUNNR_ZA`, `ARMTEK_INCOTERMS`, `ARMTEK_VBELN`, `ARMTEK_TIMEOUT`) for real data, and use `ELIZABETH_BACKEND_BASE_URL`/`ELIZABETH_EXTENSION_ALLOWED_ORIGIN` to control frontend fetch base and extension CORS.
- For ad-hoc scripts outside tests, set `PYTHONPATH=src` or install the package in editable mode.

## Coding Style & Naming Conventions
- Python defaults: 4-space indents, snake_case modules/functions, PascalCase for models; keep type hints and `dataclass`/Pydantic usage consistent.
- Reuse parsing helpers in `infra/armtek/parsing.py` and raise `Armtek*Error` subclasses instead of swallowing malformed responses.
- Keep docstrings concise; close HTTP clients/services via context managers (`ArmtekClient`, `ArmtekService`) to release connections.
- Prefer extending service/infra layers rather than inlining HTTP calls in domain logic.
- Token helpers (`domain/tokens.py`) and characteristic repositories should remain deterministic; adjust `tests/test_tokens_and_repository.py` when changing hashing/registration semantics.
- Inject new storage or parsers through `create_app`/`ArmtekCharacteristicsRepository`/`ArmtekProductParser` rather than bypassing the existing hooks in `web/app.py`.

## Testing Guidelines
- Name tests `test_*.py` under `tests/` and mirror the module you cover.
- Favor dummy clients/mocks for HTTP behavior; assert both happy paths and error handling (status errors, missing fields, bad formats).
- Gate any network-dependent checks behind the `integration` marker and document required env vars in the test.
- When adding parsers or validators, add edge-case fixtures (empty arrays, unexpected types) similar to existing service tests.
- For web endpoints and token/repository changes, extend `tests/test_web_app.py` and `tests/test_tokens_and_repository.py` to cover serialization, CORS headers, and ready/pending flows.

## Commit & Pull Request Guidelines
- Follow the existing log style: short, imperative summaries in Title Case without trailing periods (e.g., `Refactor project into layered architecture`).
- PRs should state scope, risks, and test commands (include whether integration was run and which env vars were used); link issues when relevant.
- For new endpoints or parsing changes, include example payload snippets or response notes to aid review.

## Security & Configuration Tips
- Keep credentials in env vars only (`ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, etc.); never commit real responses or configs with secrets.
- Make `ArmtekConfig` values explicit in code paths, and avoid logging sensitive fields when dumping errors or response excerpts.
- Treat API/characteristics tokens and extension traffic as sensitive; set `ELIZABETH_EXTENSION_ALLOWED_ORIGIN` when exposing `/api/armtek/characteristics` and avoid logging raw tokens or user-supplied payloads.
