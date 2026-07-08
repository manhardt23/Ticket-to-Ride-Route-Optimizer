"""Vercel serverless entrypoint."""

import sys
from pathlib import Path

# Vercel bundles src/ but may not install the editable package; add src to path.
_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ttro.api.app import app  # noqa: E402

__all__ = ["app"]
