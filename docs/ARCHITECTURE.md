# Architecture (Django API-first)

## Layout
- `elizabeth/elizabeth/settings/` — base/dev/prod configs.
- `elizabeth/apps/`
  - `accounts` — JWT auth (SimpleJWT), user settings.
  - `providers` — provider accounts (encrypted), Armtek credentials endpoint, Armtek search proxy.
  - `products` — Product, ProductDetails, ProductDetailsRequest (`request_id`), ingest/status/jobs endpoints.
  - `search` — single/bulk search orchestration, history (SearchRequest).
  - `frontend` — template + static JS console that talks only to REST.
- `extensions/armtek_extension.user.js` — browser helper posting details with `request_id`.
- `elizabeth_legacy/` — archived Flask code and tests.

## Data Flow
1. **Auth**: `/auth/register` → user + JWT pair; `/auth/login` → JWT pair.
2. **Credentials**: `/providers/armtek/credentials` stores per-user login/password (encrypted) or uses env fallback.
3. **Search**: `/search` or `/search/bulk` (or `/providers/armtek/search` direct) → Armtek service (stub in DEBUG) → upsert `Product` records.
4. **Details orchestration**:
   - Client calls `/products/details/request` with product_ids → `ProductDetailsRequest` per product (status pending).
   - `/products/details/jobs` returns pending jobs with `open_url` to Armtek UI containing `request_id` and `product_id`.
   - Userscript visits `open_url`, parses DOM, POSTs JSON to `/products/<id>/details` with header `X-Details-Token: request_id` → `ProductDetails` saved, status READY.
   - UI polls `/products/details/status` with `request_ids` to render enriched data.
5. **Caching**: `fetched_at` + `SEARCH_CACHE_TTL_MINUTES` guard repeat queries; `ARMTEK_ENABLE_STUB` for offline demo.

## Services/Libs
- Armtek HTTP client (`providers/armtek/client.py`) + search service (`services.py`), stub path when credentials отсутствуют.
- Credentials encrypted via Fernet (`providers/models.py`, key из `PROVIDER_SECRET_KEY`).
- Strict typing: mypy + django/drf plugins; linters via black/isort/flake8.

## Testing & CI
- Unit/API tests live in `tests/` (pytest + pytest-django).
- CI workflow: migrate → check → black → isort → flake8 → mypy → pytest.

## Extension Contract
- URL params: `request_id`, `elizabeth_product_id`.
- Endpoint: `POST /api/v1/products/<id>/details` with JSON {image_url, weight, length, width, height, analog_code} and header `X-Details-Token`.
- Base API URL configurable inside userscript; default `http://127.0.0.1:8000/api/v1`.

## Notes
- Legacy Flask tokens/characteristics endpoints removed; deterministic hashing заменён на UUID `request_id`.
- All API access should go through DRF views; бизнес-логика — в сервисах.
