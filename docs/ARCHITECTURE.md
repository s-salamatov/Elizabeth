# Architecture

## High-Level Layout
- `elizabeth/backend/api/` — Flask blueprints for `/api/search`, `/api/armtek/characteristics`, `/health`.
- `elizabeth/backend/services/armtek/` — HTTP client (`ArmtekHttpClient`), endpoint wrappers (`SearchService`, `UserService`), orchestration (`ArmtekService`), and the extension stub (`parser_adapter.py`).
- `elizabeth/backend/services/tokens.py` — deterministic token helpers and `ArmtekSearchContext`.
- `elizabeth/backend/repositories/` — characteristics storage interfaces and the in-memory implementation.
- `elizabeth/backend/models/` — Pydantic models for Armtek payloads plus dataclasses for characteristics.
- `elizabeth/backend/utils/` — validation helpers (response parsing, type normalization) and logging helper.
- `elizabeth/backend/app.py` — Flask app factory wiring the blueprints and dependency instances.
- `elizabeth/frontend/` — static assets and templates; delivered by Flask but kept separate from backend logic.
- `elizabeth/extensions/` — browser userscript for collecting characteristics from the Armtek UI.
- `tests/` — split by concern (`backend/` for Flask endpoints, `logic/` for service/client logic, `tokens/` for hashing and repositories).

## Layering
- **API**: Blueprints receive requests, validate payloads, and delegate to services/repositories. CORS for the extension is isolated in the characteristics blueprint.
- **Services**: `ArmtekService` orchestrates calls to `ArmtekClient` (search + structure). `SearchService` and `UserService` focus on endpoint-specific parsing and status handling. `parser_adapter.py` is the placeholder for extension-aware HTML parsing.
- **Repositories**: `ArmtekCharacteristicsRepository` defines the persistence contract; `InMemoryArmtekCharacteristicsRepository` is the default for callbacks.
- **Models**: Pydantic schemas normalize Armtek payloads; `CharacteristicsRecord` tracks callback lifecycle timestamps and readiness.
- **Utils**: `validation.py` centralizes response shape checks and type coercion; `logger.py` provides a tiny logger helper.

## Flow Overview
1. `/api/armtek/search` → `ArmtekService.get_main_search_item` → tokens generated (`api_token`, `elizabeth_token`), repository registers pending record.
2. Userscript opens the Armtek product page with `elizabeth_token`, scrapes characteristics, and POSTs to `/api/armtek/characteristics`.
3. Repository marks the record ready; UI polls the same endpoint until `status == ok`.

## Notes
- No Playwright or legacy HTML parsers are kept in backend code; the only parsing hook is the extension adapter.
- Imports inside the project use absolute paths (e.g., `from elizabeth.backend.services.armtek.service import ArmtekService`).
- Flask template/static folders point to `elizabeth/frontend/` to keep presentation assets separate from backend modules.
