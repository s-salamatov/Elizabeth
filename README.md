# Elizabeth

Typed Python client, service layer, and small web UI around the Armtek API plus browser-automation hooks for the parts that Armtek does not expose via API.

## Why This Project Exists
- Armtek exposes catalog search, client structure, and ordering flows via HTTP endpoints, but **product characteristics (images, weight/size, analog codes) are only present in the Armtek HTML pages**, not in the documented API responses.
- Directly scraping those pages server-side is brittle because of login flows, anti-bot protections, and user-specific cookies. Instead, we rely on a lightweight browser extension/userscript that reads the already-rendered page and posts the data back.
- The project packages the API access, deterministic tokens, and callback endpoints needed to orchestrate this flow with minimal manual steps.

## Goals
- Provide typed, validated access to Armtek endpoints with deterministic behavior and clear error surfaces.
- Offer a small UI to search by article/brand, generate per-item tokens, and receive characteristics from the browser helper.
- Keep extension/backend communication isolated and configurable so no sensitive Armtek credentials leave the controlled environment.

## Architecture at a Glance
- Domain (`src/elizabeth/domain/`): Pydantic models for API payloads (`armtek_models.py`) and token helpers (`tokens.py`).
- Infra (`src/elizabeth/infra/armtek/`): HTTP config/client, parsing utilities, and per-endpoint services (`services/search.py`, `services/user.py`); HTML parser stub lives in `infra/armtek_parser/armtek_parser.py`.
- Services (`src/elizabeth/services/`): `ArmtekService` picks the main (non-analog) search result and allows plugging in HTML parsers; `characteristics_repository.py` holds the in-memory store for extension callbacks.
- Web (`src/elizabeth/web/`): Flask app with a search UI plus API routes for search and `/api/armtek/characteristics`; `run.py` is the entrypoint. Static assets live under `src/elizabeth/web/static/`, templates under `src/elizabeth/web/templates/`.
- Browser helper (`src/elizabeth/core/other/armtek_extension.user.js`): Tampermonkey/Greasemonkey script that reads an Armtek product page and posts characteristics to the backend using a token received from the UI.
- Tests (`tests/`): Unit tests for parsing, services, tokens/repository, and web routes; one manual integration test gated by the `integration` marker.

## Solving the “no API for characteristics” gap
1. Search flow: the UI or API client requests `/api/armtek/search`, which calls `ArmtekService.get_main_search_item`. The backend returns normalized data plus two tokens:
   - `api_token`: deterministic hash for the Armtek API call context.
   - `elizabeth_token`: deterministic hash per `artid` used to link extension callbacks.
2. Browser step: the helper script opens `https://etp.armtek.ru/artinfo/index/{ARTID}?elizabeth_token=...`, reads the page DOM (image URL, weight/size, analog code), and posts a JSON payload to `/api/armtek/characteristics`.
3. Backend persistence: the Flask app stores pending/ready records in `ArmtekCharacteristicsRepository` (in-memory by default; pluggable for other backends).
4. Retrieval: the UI polls `/api/armtek/characteristics?token=...` until the record is ready, then renders the enriched data.

## Usage (API/Service)
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
To skip analogs and integrate HTML parsing, use `ArmtekService` (`src/elizabeth/services/armtek_service.py`) and pass a parser that implements `ArmtekProductParser`.

## Running the Web UI
- Prerequisites: Python 3.12+, optional virtualenv.
- Install deps: `pip install -r requirements.txt`.
- Launch: `python run.py` (or `FLASK_APP=run.py flask run --debug`).
- Environment:
  - Required for real data: `ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, `ARMTEK_PIN`, `ARMTEK_VKORG`, `ARMTEK_KUNNR_RG`.
  - Optional: `ARMTEK_BASE_URL`, `ARMTEK_PROGRAM`, `ARMTEK_KUNNR_ZA`, `ARMTEK_INCOTERMS`, `ARMTEK_VBELN`, `ARMTEK_TIMEOUT`.
  - Frontend/ext: `ELIZABETH_BACKEND_BASE_URL` (UI fetch base), `ELIZABETH_EXTENSION_ALLOWED_ORIGIN` (CORS for extension callbacks).
- Browser helper: install `src/elizabeth/core/other/armtek_extension.user.js` into Tampermonkey/Greasemonkey; it reads tokens from the Armtek URL and posts characteristics back.

## Development & Testing
- Fast tests: `pytest`.
- Integration (manual, networked): `pytest -m integration` with `ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, `ARMTEK_PIN`, and optionally `ARMTEK_BASE_URL`, `ARMTEK_VKORG`, `ARMTEK_KUNNR_RG`.
- Set `PYTHONPATH=src` for ad-hoc scripts, or install the package in editable mode.
- See `AGENTS.md` for coding conventions, layering rules, and contribution expectations.

## Future Work
- Implement a real HTML parser in `infra/armtek_parser/armtek_parser.py` for environments where authenticated scraping is feasible.
- Add a persistent `ArmtekCharacteristicsRepository` (Redis/SQL) with TTLs and traceability.
- Optional auth for the Flask UI and callback endpoints; rate limiting for extension posts.
- Packaging and deployment: Dockerfile, CI, and release automation; clear LICENSE.
- Improve observability: structured logging without leaking credentials or tokens.

## License
License is not specified in this repository. Add a LICENSE file before publishing publicly.
