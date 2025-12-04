# How to Run (Django)

## 1. Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Environment
Create `.env` (dev defaults are fine):
- Core: `SECRET_KEY`, `DEBUG=1`
- DB: `DATABASE_URL` (по умолчанию SQLite)
- Armtek: `ARMTEK_BASE_URL`, `ARMTEK_TIMEOUT`, `ARMTEK_ENABLE_STUB=1` for offline demo, `ARMTEK_HTML_BASE_URL=https://etp.armtek.ru/artinfo/index`. Логин/пароль и привязанные VKORG/KUNNR данные сохраняются пользователем через `/api/v1/providers/armtek/credentials`.
- CORS/CSRF: `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `ELIZABETH_EXTENSION_ALLOWED_ORIGIN`

## 3. Migrate & Run
```bash
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000
```

## 4. Workflow
1. Откройте UI на `http://127.0.0.1:8000/`, зарегистрируйтесь/войдите.
2. Сохраните Armtek credentials (форма в блоке Auth).
3. Выполните поиск (single/bulk). Товары сохраняются в БД.
4. Нажмите “Получить дополнительные характеристики” — бэкенд отдаст jobs с `open_url`.
5. Userscript (Tampermonkey) открывает страницы Armtek, парсит и POST’ит в `/api/v1/products/<id>/details`.
6. UI поллит `/api/v1/products/details/status` и отображает характеристики.

## 5. Userscript
`extensions/armtek_extension.user.js`
- Настройте `API_BASE` внутри под своё окружение.
- Ожидает параметры `request_id` и `elizabeth_product_id` в URL страницы Armtek.
- Отправляет JSON в `/api/v1/products/<id>/details` с заголовком `X-Details-Token`.

## 6. Tests & Linters
- Backend: `./scripts/check_backend.sh` (migrate → manage.py check → black --check → isort --check-only → flake8 → mypy → pytest).
- Frontend: `./scripts/check_frontend.sh` (on-demand npm ci → Playwright install → npm run lint/test/build/e2e).
- Pre-commit автоматически запускает оба скрипта; пропуск — `SKIP_PRECOMMIT=1 git commit -m "..."` или `git commit --no-verify`.

## 7. Integration (реальные запросы)
Установите реальные креды Armtek и отключите `ARMTEK_ENABLE_STUB`.
