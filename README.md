# Elizabeth

Typed Python backend plus a lightweight Flask UI around the Armtek API, with deterministic tokens and a browser-extension callback flow for product characteristics.

## Why This Project Exists
- Armtek exposes catalog search and client structure over HTTP, but **product characteristics (images, weight/size, analog codes) live only in the HTML UI**.
- Server-side scraping is brittle because of interactive logins and anti-bot protections. Instead, a small userscript reads the rendered page and posts the parsed data back.
- The project packages the API access, deterministic tokens, and callback endpoints needed to orchestrate this flow with minimal manual steps.

## Goals
- Provide typed, validated access to Armtek endpoints with deterministic behavior and clear error surfaces.
- Offer a small UI to search by article/brand, generate per-item tokens, and receive characteristics from the browser helper.
- Keep extension/backend communication isolated and configurable so no sensitive Armtek credentials leave the controlled environment.

## Architecture
- `elizabeth/backend/` — backend core
  - `api/` blueprints for `/api/search`, `/api/armtek/characteristics`, `/health`.
  - `services/armtek/` Armtek HTTP client, endpoint wrappers, and `ArmtekService` orchestrator; `parser_adapter.py` is a stub for extension-aware parsers.
  - `services/tokens.py` deterministic token helpers plus `ArmtekSearchContext`.
  - `repositories/` in-memory storage for characteristics callbacks.
  - `models/` Pydantic models for search responses and dataclasses for characteristics.
  - `utils/` validation helpers and logging helper.
  - `config.py` Armtek configuration dataclass; `app.py` wires the Flask app.
- `elizabeth/frontend/` — static assets and templates served by Flask.
- `elizabeth/extensions/` — Tampermonkey/Greasemonkey helper (`armtek_extension.user.js`).
- `tests/` — unit tests under `backend/`, `logic/`, `tokens/`; one manual integration test is marked `integration`.
- `docs/` — `ARCHITECTURE.md` and `HOW_TO_RUN.md` for onboarding and operations.

## How Characteristics Flow Works
1. Search: UI hits `/api/armtek/search`, which calls `ArmtekService.get_main_search_item`. The backend returns normalized data plus two tokens:
   - `api_token`: deterministic hash for the Armtek API call context.
   - `elizabeth_token`: deterministic hash per `artid` used to link extension callbacks.
2. Browser: the userscript opens `https://etp.armtek.ru/artinfo/index/{ARTID}?elizabeth_token=...`, reads the DOM (image URL, weight/size, analog code), and posts JSON to `/api/armtek/characteristics`.
3. Persistence: the Flask app stores pending/ready records in `ArmtekCharacteristicsRepository` (in-memory by default; pluggable later).
4. Retrieval: the UI polls `/api/armtek/characteristics?token=...` until the record is ready, then renders the enriched data.

## Usage (API / Services)
```python
from elizabeth import ArmtekClient, ArmtekConfig

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
To skip analogs and work with HTML parsers, use `ArmtekService` (`elizabeth.backend.services.armtek.service`) and provide a parser implementing `parse_product_by_artid`.

## Running Locally
- Prerequisites: Python 3.12+, optional virtualenv.
- Install deps: `pip install -r requirements.txt`.
- Launch backend/UI: `python run.py` (or `FLASK_APP=run.py flask run --debug`).
- Environment:
  - Required for real data: `ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, `ARMTEK_PIN`, `ARMTEK_VKORG`, `ARMTEK_KUNNR_RG`.
  - Optional: `ARMTEK_BASE_URL`, `ARMTEK_PROGRAM`, `ARMTEK_KUNNR_ZA`, `ARMTEK_INCOTERMS`, `ARMTEK_VBELN`, `ARMTEK_TIMEOUT`.
  - Frontend/ext: `ELIZABETH_BACKEND_BASE_URL` (UI fetch base), `ELIZABETH_EXTENSION_ALLOWED_ORIGIN` (CORS for extension callbacks).
- See `docs/HOW_TO_RUN.md` for step-by-step commands.

## Testing
- Fast suite: `pytest`.
- Integration (manual, networked): `pytest -m integration` with `ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, `ARMTEK_PIN`, and optionally `ARMTEK_BASE_URL`, `ARMTEK_VKORG`, `ARMTEK_KUNNR_RG`.
- Linting/typing: `scripts/lint.sh` (black, isort, flake8, mypy).

## Browser Helper
Install `elizabeth/extensions/armtek_extension.user.js` into Tampermonkey/Greasemonkey; it reads tokens from the Armtek URL and posts characteristics back.

## Docs
- `docs/ARCHITECTURE.md` — layering, responsibilities, and extension hooks.
- `docs/HOW_TO_RUN.md` — environment variables, commands, and troubleshooting notes.

## Future Work
- Implement a real HTML parser where authenticated scraping is feasible.
- Add persistent storage for `ArmtekCharacteristicsRepository` (Redis/SQL) with TTLs and traceability.
- Optional auth for the Flask UI and callback endpoints; rate limiting for extension posts.
- Packaging and deployment: Dockerfile, CI, and release automation; add LICENSE before publishing publicly.
