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
src/pkgview/
├── cli.py              ← entry point, typer app, parallel orchestration
├── models.py           ← Package dataclass
├── detectors/
│   ├── base.py         ← abstract Detector class
│   ├── brew.py
│   ├── npm.py
│   ├── pip.py
│   ├── cargo.py
│   ├── apt.py
│   ├── snap.py
│   ├── flatpak.py
│   ├── macos_apps.py
│   └── manual.py
└── output/
    ├── table.py        ← rich table renderer
    └── json_out.py     ← JSON renderer
```

## Adding a New Detector

See the **Adding a New Detector** section in [README.md](README.md) for a step-by-step guide.
