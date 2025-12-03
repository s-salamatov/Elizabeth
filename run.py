from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = REPO_ROOT / "frontend"


def run_cmd(
    cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None
) -> None:
    display_cmd = " ".join(cmd)
    print(f"→ {display_cmd} (cwd={cwd or REPO_ROOT})")
    subprocess.run(cmd, check=True, cwd=cwd or REPO_ROOT, env=env)


def main() -> None:
    env = os.environ.copy()
    env.setdefault("DJANGO_SETTINGS_MODULE", "backend.elizabeth.settings.dev")

    venv_dir = REPO_ROOT / ".venv"
    venv_python = venv_dir / "bin" / "python"
    if not venv_python.exists():
        print("→ Creating virtual environment (.venv)")
        run_cmd([sys.executable, "-m", "venv", str(venv_dir)], env=env)
    python_bin = str(venv_python)

    # Install backend dependencies (includes django-phonenumber-field)
    run_cmd(
        [python_bin, "-m", "pip", "install", "-U", "pip", "setuptools", "wheel"],
        env=env,
    )
    run_cmd([python_bin, "-m", "pip", "install", "-r", "requirements.txt"], env=env)

    run_cmd(["npm", "ci"], cwd=FRONTEND_DIR, env=env)
    run_cmd(["npm", "run", "build"], cwd=FRONTEND_DIR, env=env)
    run_cmd([python_bin, "manage.py", "makemigrations"], env=env)
    run_cmd([python_bin, "manage.py", "migrate"], env=env)
    server = subprocess.Popen(
        [python_bin, "manage.py", "runserver", "127.0.0.1:8000"],
        cwd=REPO_ROOT,
        env=env,
    )
    try:
        server.wait()
    except KeyboardInterrupt:
        print("\nStopping dev server (Ctrl+C)...")
        server.send_signal(signal.SIGINT)
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.terminate()
            server.wait()
        return
    if server.returncode != 0:
        raise subprocess.CalledProcessError(server.returncode, server.args)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}: {exc.cmd}")
        sys.exit(exc.returncode)
