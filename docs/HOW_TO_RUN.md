# How to Run

## Setup
1. (Optional) Create venv: `python -m venv .venv && source .venv/bin/activate`
2. Install deps: `pip install -r requirements.txt`

## Environment
- Required for real data: `ARMTEK_LOGIN`, `ARMTEK_PASSWORD`, `ARMTEK_PIN`, `ARMTEK_VKORG`, `ARMTEK_KUNNR_RG`
- Optional: `ARMTEK_BASE_URL`, `ARMTEK_PROGRAM`, `ARMTEK_KUNNR_ZA`, `ARMTEK_INCOTERMS`, `ARMTEK_VBELN`, `ARMTEK_TIMEOUT`
- Frontend/extension: `ELIZABETH_BACKEND_BASE_URL` (UI fetch base), `ELIZABETH_EXTENSION_ALLOWED_ORIGIN` (CORS for extension callbacks)

## Run the Backend/UI
```bash
python run.py
# or
FLASK_APP=run.py flask run --debug
```

Routes to verify after start:
- `GET /health` → `{"status": "ok"}`
- `POST /api/armtek/search` (JSON `{"query": "332101 KYB"}`) → search response with tokens
- `GET|POST /api/armtek/characteristics` → pending/ready flow for extension callbacks

## Testing
- Fast suite: `pytest`
- Integration (manual, calls real Armtek): `pytest -m integration` with the environment variables above set

## Browser Helper
- Install `elizabeth/extensions/armtek_extension.user.js` into Tampermonkey/Greasemonkey
- The script reads `elizabeth_token` from the Armtek product URL and POSTs characteristics to `/api/armtek/characteristics`
