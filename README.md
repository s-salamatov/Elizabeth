# Elizabeth (Django, API-first)

Elizabeth — новая реализация на Django + Django REST Framework. API v1 — единственная точка для веб-UI, браузерного расширения и будущих клиентов.

## Кратко о слоях
- `elizabeth/elizabeth/settings/` — base/dev/prod конфигурации.
- `elizabeth/apps/` — доменные приложения:
  - `accounts` — JWT-логин/регистрация, пользовательские настройки.
  - `providers` — учётки провайдеров, Armtek credentials, Armtek proxy search.
  - `products` — товары, детали, заявки на детали (`request_id`).
  - `search` — single/bulk поиск, история запросов.
  - `frontend` — шаблон + JS, работает только через REST.
- `extensions/armtek_extension.user.js` — Tampermonkey/Greasemonkey-скрипт для сбора характеристик из Armtek HTML.
- `elizabeth_legacy/` — старый Flask-код сохранён для истории.

## Быстрый старт
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000
```
Переменные окружения (dev): см. `.env` пример; ключевые — `ARMTEK_ENABLE_STUB=1` чтобы демо работало без кредов.

### SPA-фронтенд (Vue 3 + Vite)
- Исходники: `frontend_spa/`, билд кладётся в `elizabeth/apps/frontend/static/frontend/`.
- Установка зависимостей: `cd frontend_spa && npm install`.
- Запуск dev-сервера: `npm run dev` (раздаёт `index.html`, но в проде используется Django-шаблон `frontend/app.html`).
- Продакшн сборка: `npm run build`, затем `python manage.py collectstatic` при необходимости.
- Страница приложения доступна по `/`, монтируется в `<div id="app"></div>` и работает только с REST API `/api/v1/...`.

## Поток работы (как в старом сценарии)
1) Пользователь регистрируется/логинится через UI (JWT).
2) В форме “Armtek credentials” сохраняет логин/пароль (endpoint `POST /api/v1/providers/armtek/credentials`).
3) Вводит артикулы (один или bulk) → `POST /api/v1/search` или `/search/bulk`; данные кешируются в БД.
4) Нажимает “Получить дополнительные характеристики”: backend создаёт `request_id` на каждый товар и отдаёт jobs с `open_url` на Armtek.
5) JS открывает эти URLs; userscript читает DOM Armtek и POST’ит в `/api/v1/products/<id>/details` (заголовок `X-Details-Token` = `request_id`).
6) UI поллит `/api/v1/products/details/status` и показывает готовые характеристики в таблице.

## Основные endpoints (v1)
- `POST /auth/register`, `POST /auth/login`
- `POST /providers/armtek/credentials`, `GET /providers/armtek/credentials`
- `POST /providers/armtek/search`
- `POST /search`, `POST /search/bulk`
- `GET /products`, `GET /products/<id>`
- `POST /products/details/request`, `GET /products/details/jobs`, `POST /products/details/status`
- `POST /products/<id>/details` — колбэк от расширения

## Тесты и линтеры
- Backend: `scripts/check_backend.sh` (migrate → manage.py check → black --check → isort --check-only → flake8 → mypy → pytest).
- Frontend: `scripts/check_frontend.sh` (on-demand npm ci → Playwright browsers install → npm run lint → npm run test → npm run build → npm run e2e).
- Pre-commit hook (`.git/hooks/pre-commit`) запускает оба скрипта перед коммитом; пропуск: `SKIP_PRECOMMIT=1 git commit -m "msg"` или `git commit --no-verify`.

## Userscript
Файл: `extensions/armtek_extension.user.js`
- Ожидает в URL параметры `request_id` и `elizabeth_product_id`.
- Парсит страницу Armtek, отправляет JSON в `/api/v1/products/<id>/details`.
- По умолчанию API_BASE в скрипте: `http://127.0.0.1:8000/api/v1` — смените на прод при деплое.

## ENV важное
- Armtek API: `ARMTEK_BASE_URL`, `ARMTEK_TIMEOUT`, `ARMTEK_ENABLE_STUB`, `ARMTEK_HTML_BASE_URL` (для ссылок jobs). Логин/пароль и контекст (VKORG/KUNNR_RG/…) задаёт сам пользователь через `/api/v1/providers/armtek/credentials` и хранится в БД.
- CORS/CSRF: `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `ELIZABETH_EXTENSION_ALLOWED_ORIGIN`.
- Security: `SECRET_KEY`, `PROVIDER_SECRET_KEY` (для шифрования паролей провайдеров).

## Документы
- `docs/HOW_TO_RUN.md` — запуск и конфиг.
- `docs/ARCHITECTURE.md` — слои и поток данных.

## Примечание
Старые Flask-тесты и код не используются; новые тесты лежат в `tests/`.
