from pkgview.detectors.brew import BrewDetector
from pkgview.detectors.npm import NpmDetector
from pkgview.detectors.pip import PipDetector
from pkgview.detectors.cargo import CargoDetector
from pkgview.detectors.apt import AptDetector
from pkgview.detectors.snap import SnapDetector
from pkgview.detectors.flatpak import FlatpakDetector
from pkgview.detectors.conda import CondaDetector
from pkgview.detectors.mamba import MambaDetector
from pkgview.detectors.pacman import PacmanDetector
from pkgview.detectors.dnf import DnfDetector
from pkgview.detectors.apk import ApkDetector
from pkgview.detectors.nix import NixDetector
from pkgview.detectors.gem import GemDetector
from pkgview.detectors.composer import ComposerDetector
from pkgview.detectors.winget import WingetDetector
from pkgview.detectors.scoop import ScoopDetector
from pkgview.detectors.choco import ChocoDetector
from pkgview.detectors.nvm import NvmDetector
from pkgview.detectors.asdf import AsdfDetector
from pkgview.detectors.pyenv import PyenvDetector
from pkgview.detectors.macos_apps import MacOsAppsDetector
from pkgview.detectors.manual import ManualDetector

__all__ = [
    "BrewDetector",
    "NpmDetector",
    "PipDetector",
    "CargoDetector",
    "AptDetector",
    "SnapDetector",
    "FlatpakDetector",
    "CondaDetector",
    "MambaDetector",
    "PacmanDetector",
    "DnfDetector",
    "ApkDetector",
    "NixDetector",
    "GemDetector",
    "ComposerDetector",
    "WingetDetector",
    "ScoopDetector",
    "ChocoDetector",
    "NvmDetector",
    "AsdfDetector",
    "PyenvDetector",
    "MacOsAppsDetector",
    "ManualDetector",
]
