from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


MANAGED_MANAGERS: frozenset[str] = frozenset({
    # macOS / cross-platform
    "brew", "brew-cask",
    # JavaScript
    "npm",
    # Python
    "pip", "pipx",
    # Rust
    "cargo",
    # Debian/Ubuntu
    "apt",
    # Linux universal
    "snap", "flatpak",
    # Data Science
    "conda", "mamba",
    # Arch Linux
    "pacman", "yay",
    # Fedora / RHEL
    "dnf", "yum",
    # openSUSE
    "zypper",
    # Alpine Linux
    "apk",
    # Nix
    "nix",
    # Ruby
    "gem",
    # PHP
    "composer",
    # Windows
    "winget", "scoop", "chocolatey",
    # Version managers
    "nvm", "asdf", "pyenv",
})


@dataclass
class Package:
    name: str
    manager: str
    version: Optional[str] = None
    path: Optional[str] = None
    category: str = "cli"  # "cli" | "app"
    outdated: bool = False
    latest_version: Optional[str] = None

    @property
    def is_managed(self) -> bool:
        return self.manager in MANAGED_MANAGERS
