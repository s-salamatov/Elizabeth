from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env if present (project root or repository root)
env = environ.Env()
for env_path in (BASE_DIR / ".env", BASE_DIR.parent / ".env"):
    if env_path.exists():
        env.read_env(env_path)


ARMTEK_BASE_URL = env("ARMTEK_BASE_URL", default="https://ws.armtek.ru")
ARMTEK_TIMEOUT = env.int("ARMTEK_TIMEOUT", default=10)
ARMTEK_ENABLE_STUB = env.bool("ARMTEK_ENABLE_STUB", default=True)
ARMTEK_HTML_BASE_URL = env(
    "ARMTEK_HTML_BASE_URL", default="https://etp.armtek.ru/artinfo/index"
)
