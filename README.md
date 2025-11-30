# Elizabeth (Django, API-first)

Elizabeth is now a clean Django + Django REST Framework project. The API (v1) is the only interface for the web UI, browser extension, desktop/mobile clients, and future integrations. The legacy Flask codebase is preserved under `elizabeth_legacy/` for reference.

## Top-Level Layout
- `elizabeth/` — Django project + settings (`base.py`, `dev.py`, `prod.py`)
- `apps/` — domain apps
  - `accounts/` — auth endpoints, user settings
  - `providers/` — provider accounts and Armtek integration (`armtek/` client + services)
  - `products/` — product + product details models and serializers
  - `search/` — single/bulk search orchestration and history
  - `frontend/` — templates + static JS calling the API only
- `elizabeth_legacy/` — previous Flask implementation (kept for historical reference)

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate            # create DB (default SQLite)
python manage.py createsuperuser    # optional
python run.py                       # runs dev server at 0.0.0.0:8000
```

## Environment
All variables are optional; set them in `.env` (loaded automatically):

- Django: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`
- CORS/CSRF: `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `ELIZABETH_EXTENSION_ALLOWED_ORIGIN`
- Armtek auth: `ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, `ARMTEK_PIN`, `ARMTEK_VKORG`, `ARMTEK_KUNNR_RG`, `ARMTEK_PROGRAM`, `ARMTEK_KUNNR_ZA`, `ARMTEK_INCOTERMS`, `ARMTEK_VBELN`, `ARMTEK_BASE_URL`, `ARMTEK_TIMEOUT`
- Provider secrets: `PROVIDER_SECRET_KEY` (used to encrypt provider passwords; falls back to `SECRET_KEY`)
- Cache: `SEARCH_CACHE_TTL_MINUTES` (freshness window for stored products)

## REST API (v1)
- `POST /api/v1/auth/register` — create user, returns JWT pair
- `POST /api/v1/auth/login` — obtain JWT pair
- `POST /api/v1/search` — search one query (PIN, `PIN BRAND`, or `PIN_BRAND`)
- `POST /api/v1/search/bulk` — bulk search (comma/semicolon/newline or `queries[]`)
- `GET /api/v1/products` — list stored products
- `GET /api/v1/products/<id>` — retrieve product
- `POST /api/v1/products/<id>/details` — accept characteristics payload from the extension
- `POST /api/v1/providers/armtek/search` — direct Armtek call, cached into products

Default auth: Bearer JWT (SimpleJWT). `ProductDetails` ingest endpoint is open to allow the browser extension to push data.

## Frontend
`apps/frontend/templates/frontend/search.html` renders a lightweight console UI. It only talks to the API via `fetch`, supports login, single search, bulk search (paste or `.txt` upload), and renders results. Styling uses Space Grotesk/Roboto Mono with a dark, non-default palette.

## Armtek integration
`apps/providers/armtek` contains the HTTP client and service wrapper. Credentials are taken from the current user’s provider account (if stored) or environment variables. With `DEBUG=True`, a stub search item is returned when credentials are missing so the UI can be demoed offline.

## Legacy code
The original Flask implementation now lives in `elizabeth_legacy/`. It is excluded from the active app and kept only for historical reference.

## Testing & Tooling
- `pytest` — placeholder; add new tests alongside the rewritten modules.
- Format/lint configs live in `pyproject.toml`, `mypy.ini`, `pytest.ini`.
- Planned linters: black, isort, flake8, mypy (already in requirements).

## Roadmap (matching migration brief)
1. Django scaffold + app layout ✅
2. Core models and API v1 ✅
3. Frontend template calling the API ✅
4. Armtek client + stub for offline dev ✅
5. Bulk search + characteristics ingest ✅
6. Harden tests/linters and expand provider ecosystem (next)
