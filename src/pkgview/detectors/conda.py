from __future__ import annotations

import json
import subprocess
from typing import Dict, List

from pkgview.detectors.base import Detector
from pkgview.models import Package


def _conda_list(cmd: str) -> List[Dict]:
    """Run ``cmd list --json`` and return the parsed list. Never raises."""
    try:
        result = subprocess.run(
            [cmd, "list", "--json"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return []
        return json.loads(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return []


class CondaDetector(Detector):
    """
    Detects packages installed in the active conda/mamba environment.

    Tries mamba first (it is typically a drop-in replacement); falls back
    to conda. The manager label reflects whichever tool responded.
    """

    @property
    def name(self) -> str:
        return "conda"

    def detect(self) -> Dict[str, Package]:
        packages: Dict[str, Package] = {}
        manager_label = "conda"

        items = _conda_list("mamba")
        if items:
            manager_label = "mamba"
        else:
            items = _conda_list("conda")

        for item in items:
            name = item.get("name", "").strip()
            version = item.get("version")
            channel = item.get("channel", "")
            if not name:
                continue
            # Skip packages that came from pip inside the conda env
            if channel in ("pypi",):
                continue
            packages[name] = Package(
                name=name,
                manager=manager_label,
                version=version,
                category="cli",
            )
        return packages
