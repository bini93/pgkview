from __future__ import annotations

import re
import subprocess
from typing import Dict

from pkgview.detectors.base import Detector
from pkgview.models import Package


class ApkDetector(Detector):
    """Detects installed packages on Alpine Linux via apk."""

    @property
    def name(self) -> str:
        return "apk"

    def detect(self) -> Dict[str, Package]:
        packages: Dict[str, Package] = {}
        try:
            result = subprocess.run(
                ["apk", "list", "--installed"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                return {}
            for line in result.stdout.splitlines():
                # Format: "package-version-r0 arch {repo} (license) [installed]"
                # e.g.: "bash-5.2.21-r0 x86_64 {main} (GPL-3.0-or-later) [installed]"
                parts = line.split()
                if not parts:
                    continue
                full = parts[0]  # "bash-5.2.21-r0"
                # Split off the last two dash-separated segments (version-release)
                segments = full.rsplit("-", 2)
                if len(segments) == 3:
                    name, version, _rel = segments
                    ver_full = f"{version}-{_rel}"
                else:
                    name = full
                    ver_full = None
                packages[name] = Package(
                    name=name,
                    manager="apk",
                    version=ver_full,
                    category="cli",
                )
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass
        return packages

    def check_outdated(self, packages: Dict[str, Package]) -> None:
        """Uses ``apk upgrade --simulate`` to find upgradable packages."""
        try:
            result = subprocess.run(
                ["apk", "upgrade", "--simulate"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                return
            for line in result.stdout.splitlines():
                # Format: "(1/3) Upgrading bash (5.2.21-r0 -> 5.2.26-r0)"
                if "Upgrading" in line:
                    m = re.search(r"Upgrading\s+(\S+)\s+\(([^)]+)\s+->\s+([^)]+)\)", line)
                    if m:
                        name, _old, latest = m.group(1), m.group(2), m.group(3)
                        if name in packages:
                            packages[name].outdated = True
                            packages[name].latest_version = latest
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass
