from __future__ import annotations

import re
import subprocess
from typing import Dict, List

from pkgview.detectors.base import Detector
from pkgview.models import Package


def _run(cmd: List[str]) -> List[str]:
    """Run a command and return non-empty output lines. Never raises."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return []


def _versions() -> Dict[str, str]:
    """Return {name: version} for all installed formulae via brew list --versions."""
    versions: Dict[str, str] = {}
    for line in _run(["brew", "list", "--versions"]):
        parts = line.split()
        if len(parts) >= 2:
            versions[parts[0]] = parts[1]
    return versions


class BrewDetector(Detector):
    @property
    def name(self) -> str:
        return "brew"

    def detect(self) -> Dict[str, Package]:
        packages: Dict[str, Package] = {}
        versions = _versions()

        for name in _run(["brew", "list", "--formula"]):
            packages[name] = Package(
                name=name,
                manager="brew",
                version=versions.get(name),
                category="cli",
            )

        for name in _run(["brew", "list", "--cask"]):
            packages[name] = Package(
                name=name,
                manager="brew-cask",
                version=versions.get(name),
                category="app",
            )

        return packages

    def check_outdated(self, packages: Dict[str, Package]) -> None:
        """Uses ``brew outdated --verbose`` to find formulae and casks with updates."""
        try:
            result = subprocess.run(
                ["brew", "outdated", "--verbose"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            # brew outdated exits 0 whether or not there are outdated packages
            for line in result.stdout.splitlines():
                # Formula format:  "git (2.44.0) < 2.49.0"
                # Cask format:     "firefox (134.0) != 135.0"
                m = re.match(r"^(\S+)\s+\([^)]+\)\s+(?:<|!=)\s+(\S+)", line.strip())
                if m:
                    name, latest = m.group(1), m.group(2)
                    if name in packages:
                        packages[name].outdated = True
                        packages[name].latest_version = latest
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass
