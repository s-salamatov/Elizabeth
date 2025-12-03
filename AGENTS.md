# Repository Guidelines

## Project Structure (Django)
- `backend/elizabeth/settings/` — base/dev/prod configs.
- `backend/apps/`:
  - `accounts` — auth endpoints (SimpleJWT), user settings.
  - `providers` — provider accounts (encrypted), Armtek credentials endpoint, Armtek search proxy.
  - `products` — Product, ProductDetails, ProductDetailsRequest (UUID `request_id`), ingest/status/jobs endpoints.
  - `search` — single/bulk search flow and history.
  - `frontend` — template + JS console that calls only REST.
- `extensions/armtek_extension.user.js` — Tampermonkey/Greasemonkey helper posting parsed characteristics to `/api/v1/products/<id>/details` using `request_id`.
- `elizabeth_legacy/` — archived Flask implementation and tests (ignore for new work).
- Tests: `tests/` (pytest + pytest-django).

## Build, Test, Development
- Venv: `python -m venv .venv && source .venv/bin/activate`
- Install: `pip install -r requirements.txt`
- Migrate: `python manage.py migrate --noinput`
- Run dev server: `python manage.py runserver 0.0.0.0:8000`
- Full checks: `./scripts/check_backend.sh` + `./scripts/check_frontend.sh` (lint.sh теперь просто вызывает их).
- CI повторяет те же шаги, см. `.github/workflows/backend-ci.yml` и `.github/workflows/frontend-ci.yml`.

## Coding Style
- Python 3.12, black + isort; flake8 with bugbear/comprehensions; mypy strict with django/drf plugins.
- Keep business-логика в сервисах, DRF views тонкие. Не подавлять линтеры без крайней необходимости.
- Absolute imports `backend.apps.*`.

## Testing Guidelines
- `pytest` (unit/API). Сетевые интеграции — только со stub или при наличии реальных кредов.
- Помечайте потенциально сетевые тесты маркером `integration` если добавляете.

## Feature Flow (Armtek)
- Сохранение Armtek credentials: `POST /api/v1/providers/armtek/credentials`.
- Поиск: `/api/v1/search` или `/search/bulk` (или `/providers/armtek/search` для прямого Armtek).
- Детали: `/products/details/request` → `/products/details/jobs` (open_url с request_id) → userscript → `/products/<id>/details` → `/products/details/status`.

## Security & Config
- Credentials только через env или encrypted provider accounts; ключ шифрования `PROVIDER_SECRET_KEY`.
- `ARMTEK_ENABLE_STUB` для офлайна, отключать в проде.
- CORS/CSRF настраиваются через env (`CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `ELIZABETH_EXTENSION_ALLOWED_ORIGIN`).

## Commit/PR
- Коммит-месседжи: короткие, императивные, Title Case, без точки.
- PR: описывайте область, риски, команды тестов; если меняете API/парсинг — приведите примеры payload/flow.
