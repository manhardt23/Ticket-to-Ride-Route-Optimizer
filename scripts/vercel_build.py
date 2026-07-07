"""Vercel build step: seed the SQLite board database before deploy."""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
  subprocess.run(
    [sys.executable, str(PROJECT_ROOT / "scripts" / "seed_db.py")],
    check=True,
    cwd=PROJECT_ROOT,
  )
  print("Vercel build: board.db seeded")


if __name__ == "__main__":
  main()
