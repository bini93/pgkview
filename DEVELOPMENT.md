# Contributing / Development Setup

This document is for contributors and developers who want to work on the pkgview source code.

## Prerequisites

- Python 3.9+
- `make` (pre-installed on macOS and Linux)

## Quick Start

```bash
git clone https://github.com/yourname/pkgview.git
cd pkgview
make dev
source .venv/bin/activate
```

`make dev` creates a virtual environment and installs pkgview in editable mode including all dev dependencies (`pytest`, `pytest-mock`). Changes to the source code take effect immediately without reinstalling.

## Available `make` Targets

| Command | Description |
|---------|-------------|
| `make dev` | Create `.venv` and install all dependencies |
| `make test` | Run the test suite with pytest |
| `make install` | Install via pipx in editable mode (personal use) |
| `make clean` | Remove `.venv`, `__pycache__`, and build artefacts |

## Running Tests

```bash
make test

# or directly with pytest options:
.venv/bin/pytest -x          # stop on first failure
.venv/bin/pytest -k brew     # run only tests matching "brew"
```

## Project Structure

```
pgkview/
├── pyproject.toml              ← packaging config, entry point: pkgview
├── src/
│   └── pkgview/
│       ├── cli.py              ← typer app, all flags, parallel orchestration
│       ├── models.py           ← Package dataclass
│       ├── detectors/
│       │   ├── base.py         ← abstract Detector class
│       │   ├── brew.py
│       │   ├── npm.py
│       │   ├── pip.py
│       │   ├── cargo.py
│       │   ├── apt.py
│       │   ├── snap.py
│       │   ├── flatpak.py
│       │   ├── macos_apps.py   ← scans /Applications
│       │   └── manual.py       ← PATH scan, marks unknowns as "manual"
│       └── output/
│           ├── table.py        ← rich table renderer
│           └── json_out.py     ← JSON renderer
└── PLAN.md                     ← architecture decisions and future roadmap
```

## Adding a New Detector

Adding support for a new package manager takes ~30 lines. Here is a minimal example:

```python
# src/pkgview/detectors/my_manager.py
from __future__ import annotations

import subprocess
from typing import Dict

from pkgview.detectors.base import Detector
from pkgview.models import Package


class MyManagerDetector(Detector):
    @property
    def name(self) -> str:
        return "my_manager"

    def detect(self) -> Dict[str, Package]:
        packages: Dict[str, Package] = {}
        try:
            result = subprocess.run(
                ["my_manager", "list"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                return {}
            for line in result.stdout.splitlines():
                name = line.strip()
                if name:
                    packages[name] = Package(name=name, manager="my_manager")
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass
        return packages
```

Then register it in `src/pkgview/cli.py`:

```python
from pkgview.detectors.my_manager import MyManagerDetector

INDEPENDENT_DETECTORS = [
    ...,
    MyManagerDetector,   # ← add here
]
```

And add a color/icon in `src/pkgview/output/table.py`:

```python
MANAGER_STYLES["my_manager"] = "bold green"
MANAGER_ICONS["my_manager"]  = "🔧"
```

Also add the name to `VALID_MANAGERS` in `cli.py` so `--filter my_manager` works.
