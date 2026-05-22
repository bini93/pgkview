from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict

from pkgview.models import Package


class Detector(ABC):
    """Abstract base class for all package manager detectors."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this detector (e.g. 'brew', 'npm')."""
        ...

    @abstractmethod
    def detect(self) -> Dict[str, Package]:
        """
        Run detection and return a mapping of binary_name -> Package.

        Must never raise exceptions – return an empty dict on any failure
        so that one broken detector cannot crash the whole tool.
        """
        ...

    def check_outdated(self, packages: Dict[str, Package]) -> None:
        """
        Optionally update packages in-place with outdated / latest_version info.

        ``packages`` contains only the packages belonging to this detector.
        Implementations should set ``pkg.outdated = True`` and
        ``pkg.latest_version = "<new_version>"`` for each outdated package.

        Must never raise exceptions. Default implementation is a no-op.
        """
