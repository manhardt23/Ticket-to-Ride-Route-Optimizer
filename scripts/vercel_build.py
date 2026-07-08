"""Vercel build: seed DB + export Next.js static site into public/."""

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
FRONTEND_OUT = FRONTEND_DIR / "out"
PUBLIC_DIR = PROJECT_ROOT / "public"
API_STATIC_DIR = PROJECT_ROOT / "api" / "static"


def main() -> None:
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "seed_db.py")],
        check=True,
        cwd=PROJECT_ROOT,
    )

    npm = shutil.which("npm")
    if not npm:
        print("Vercel build: npm not found, skipping frontend export")
        return

    subprocess.run([npm, "install"], check=True, cwd=FRONTEND_DIR)
    subprocess.run([npm, "run", "build"], check=True, cwd=FRONTEND_DIR)

    if not FRONTEND_OUT.is_dir():
        raise SystemExit(f"Expected Next.js export at {FRONTEND_OUT}")

    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    shutil.copytree(FRONTEND_OUT, PUBLIC_DIR)

    if API_STATIC_DIR.exists():
        shutil.rmtree(API_STATIC_DIR)
    shutil.copytree(FRONTEND_OUT, API_STATIC_DIR)

    print("Vercel build: board.db seeded, frontend copied to public/ and api/static/")


if __name__ == "__main__":
    main()
