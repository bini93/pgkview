from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from pkgview.detectors.base import Detector
from pkgview.models import Package


def _brew_cask_names() -> set[str]:
    """Return the set of cask names currently managed by Homebrew."""
    try:
        result = subprocess.run(
            ["brew", "list", "--cask"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return {line.strip().lower() for line in result.stdout.splitlines() if line.strip()}
    except (subprocess.TimeoutExpired, OSError):
        pass
    return set()


class MacOsAppsDetector(Detector):
    """Scans /Applications and ~/Applications for .app bundles on macOS.

    Pass ``brew_casks`` (a set of already-detected cask names) to avoid a
    redundant ``brew list --cask`` subprocess call. When omitted the detector
    falls back to calling brew itself.
    """

    def __init__(self, brew_casks: frozenset[str] | None = None) -> None:
        # None signals "auto-detect"; an empty frozenset means "no casks known".
        self._brew_casks = brew_casks

    @property
    def name(self) -> str:
        return "macos_apps"

    def detect(self) -> dict[str, Package]:
        packages: dict[str, Package] = {}

        # Only relevant on macOS
        if sys.platform != "darwin":
            return {}

        brew_casks = self._brew_casks if self._brew_casks is not None else _brew_cask_names()
        scan_dirs = [
            Path("/Applications"),
            Path("/Applications/Utilities"),
            Path.home() / "Applications",
        ]

        for scan_dir in scan_dirs:
            if not scan_dir.is_dir():
                continue
            try:
                for entry in scan_dir.iterdir():
                    if entry.suffix != ".app":
                        continue
                    app_name = entry.stem
                    # Known limitation: simple heuristic; fails for casks
                    # whose name differs from the app name (e.g. "1password").
                    normalized = app_name.lower().replace(" ", "-")
                    manager = "brew-cask" if normalized in brew_casks else "manual"
                    packages[app_name] = Package(
                        name=app_name,
                        manager=manager,
                        path=str(entry),
                        category="app",
                    )
            except OSError:
                pass

        return packages
