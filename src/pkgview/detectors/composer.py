from __future__ import annotations

import json
import subprocess
from typing import Dict

from pkgview.detectors.base import Detector
from pkgview.models import Package


class ComposerDetector(Detector):
    """Detects globally installed PHP Composer packages."""

    @property
    def name(self) -> str:
        return "composer"

    def detect(self) -> Dict[str, Package]:
        packages: Dict[str, Package] = {}
        try:
            result = subprocess.run(
                ["composer", "global", "show", "--format=json", "--no-interaction"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                return {}
            data = json.loads(result.stdout)
            for item in data.get("installed", []):
                name = item.get("name", "").strip()
                version = item.get("version")
                if not name:
                    continue
                packages[name] = Package(
                    name=name,
                    manager="composer",
                    version=version,
                    category="cli",
                )
        except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
            pass
        return packages

    def check_outdated(self, packages: Dict[str, Package]) -> None:
        """Uses ``composer global outdated --format=json`` to find updates."""
        try:
            result = subprocess.run(
                ["composer", "global", "outdated", "--format=json", "--no-interaction"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode not in (0, 1):
                return
            data = json.loads(result.stdout)
            for item in data.get("installed", []):
                name = item.get("name", "")
                latest = item.get("latest")
                if name in packages and latest:
                    packages[name].outdated = True
                    packages[name].latest_version = latest
        except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
            pass
