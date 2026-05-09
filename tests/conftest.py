"""Test bootstrap — make ``src/`` importable without an editable install.

Mentat-Learn ships its source under ``src/mentat_learn/``. When the
package isn't installed (CI fresh checkout, sandboxed test runs, etc.)
imports in ``tests/`` fail. This conftest prepends ``src/`` to
``sys.path`` so ``from mentat_learn.foo import bar`` resolves cleanly.
"""
from __future__ import annotations

import sys
from pathlib import Path


_SRC = Path(__file__).resolve().parent.parent / "src"
if _SRC.is_dir():
    sys.path.insert(0, str(_SRC))


# Skip test modules that require external packages we don't ship.
collect_ignore = []
try:
    import harness_skills  # noqa: F401
except ImportError:
    # The skills-adapter test depends on the `harness-skills` package
    # which is an optional cross-project integration. Tests skip
    # cleanly when it isn't installed.
    collect_ignore.append("test_skills_adapter.py")
try:
    import fastapi  # noqa: F401
except ImportError:
    # The HTTP-app test imports FastAPI's TestClient. Skip cleanly
    # in environments where FastAPI isn't installed.
    collect_ignore.append("test_app.py")
try:
    import httpx  # noqa: F401
except ImportError:
    pass  # httpx is FastAPI's TestClient backend; covered above
try:
    # The TUI tests import harness-tui; skip if absent.
    import harness_tui  # noqa: F401
except ImportError:
    # No tui tests in the current set, but skip preemptively if added.
    pass
