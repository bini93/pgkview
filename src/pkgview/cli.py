from __future__ import annotations

import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Type

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from pkgview.detectors.base import Detector
from pkgview.detectors.brew import BrewDetector
from pkgview.detectors.npm import NpmDetector
from pkgview.detectors.pip import PipDetector
from pkgview.detectors.cargo import CargoDetector
from pkgview.detectors.apt import AptDetector
from pkgview.detectors.snap import SnapDetector
from pkgview.detectors.flatpak import FlatpakDetector
from pkgview.detectors.conda import CondaDetector
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
from pkgview import __version__
from pkgview.models import Package, MANAGED_MANAGERS
from pkgview.output.table import render_table
from pkgview.output.json_out import render_json
from pkgview.output.csv_out import render_csv

app = typer.Typer(
    help="[bold]pkgview[/bold] – list all installed programs and who manages them.",
    rich_markup_mode="rich",
    no_args_is_help=False,
)

console = Console()

# Detectors that are fully independent (run in parallel)
INDEPENDENT_DETECTORS: List[Type[Detector]] = [
    BrewDetector,
    NpmDetector,
    PipDetector,
    CargoDetector,
    AptDetector,
    SnapDetector,
    FlatpakDetector,
    CondaDetector,
    PacmanDetector,
    DnfDetector,
    ApkDetector,
    NixDetector,
    GemDetector,
    ComposerDetector,
    WingetDetector,
    ScoopDetector,
    ChocoDetector,
    NvmDetector,
    AsdfDetector,
    PyenvDetector,
]

VALID_SORT_KEYS = {"name", "manager", "version"}
VALID_MANAGERS = MANAGED_MANAGERS | {"manual"}


@app.command()
def main(
    filter_manager: Optional[str] = typer.Option(
        None,
        "--filter",
        "-f",
        help="Only show programs from a specific manager. "
             "E.g. [cyan]brew[/cyan], [yellow]npm[/yellow], [yellow]manual[/yellow].",
    ),
    as_json: bool = typer.Option(False, "--json", "-j", help="Output raw JSON instead of a table."),
    no_apps: bool = typer.Option(False, "--no-apps", help="Exclude GUI apps (e.g. /Applications on macOS)."),
    sort_by: str = typer.Option(
        "manager",
        "--sort",
        "-s",
        help=f"Sort column: {', '.join(sorted(VALID_SORT_KEYS))}.",
    ),
    no_manual: bool = typer.Option(
        False,
        "--no-manual",
        help="Hide manually installed programs.",
    ),
    show_paths: bool = typer.Option(
        False,
        "--paths",
        "-p",
        help="Add a Path column to the table.",
    ),
    check_outdated: bool = typer.Option(
        False,
        "--outdated",
        "-o",
        help="Check each package manager for available updates and highlight outdated packages.",
    ),
    export_path: Optional[str] = typer.Option(
        None,
        "--export",
        "-e",
        help="Save snapshot to file. Format is auto-detected from the extension: "
             "[cyan].csv[/cyan] for CSV, anything else (e.g. [cyan].json[/cyan]) for JSON.",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        is_eager=True,
    ),
) -> None:
    if version:
        console.print(f"pkgview {__version__}")
        raise typer.Exit()
    if filter_manager and filter_manager not in VALID_MANAGERS:
        console.print(
            f"[red]Unknown manager '[bold]{filter_manager}[/bold]'. "
            f"Valid values: {', '.join(sorted(VALID_MANAGERS))}[/red]"
        )
        raise typer.Exit(code=1)

    if sort_by not in VALID_SORT_KEYS:
        console.print(
            f"[red]Unknown sort key '[bold]{sort_by}[/bold]'. "
            f"Valid values: {', '.join(sorted(VALID_SORT_KEYS))}[/red]"
        )
        raise typer.Exit(code=1)

    all_packages: dict[str, Package] = {}
    _warnings: list[str] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Scanning package managers …", total=None)

        # ── Phase 1: independent detectors in parallel ──────────────────────
        # Note: INDEPENDENT_DETECTORS holds direct class references; patch the
        # list itself (pkgview.cli.INDEPENDENT_DETECTORS) in tests, not the
        # individual class names.
        with ThreadPoolExecutor(max_workers=min(len(INDEPENDENT_DETECTORS), 8)) as executor:
            futures = {
                executor.submit(cls().detect): cls.__name__
                for cls in INDEPENDENT_DETECTORS
            }
            for future in as_completed(futures):
                try:
                    result = future.result()
                    all_packages.update(result)
                except Exception as exc:
                    _warnings.append(f"[yellow]Warning: {futures[future]} failed: {exc}[/yellow]")

        # ── Phase 2: GUI apps (macOS only, sequential) ───────────────────────
        if not no_apps:
            progress.update(task, description="Scanning GUI apps …")
            try:
                # Reuse brew-cask names already detected in Phase 1 to avoid a
                # second `brew list --cask` subprocess call.
                brew_casks = frozenset(
                    name for name, pkg in all_packages.items()
                    if pkg.manager == "brew-cask"
                )
                all_packages.update(MacOsAppsDetector(brew_casks=brew_casks).detect())
            except Exception as exc:
                _warnings.append(f"[yellow]Warning: MacOsAppsDetector failed: {exc}[/yellow]")

        # ── Phase 3: manual (needs all managed packages as reference) ────────
        if not no_manual:
            progress.update(task, description="Scanning PATH for manual installs …")
            try:
                manual = ManualDetector(managed=all_packages).detect()
                all_packages.update(manual)
            except Exception as exc:
                _warnings.append(f"[yellow]Warning: ManualDetector failed: {exc}[/yellow]")

        # ── Phase 4: outdated checks (optional, parallel) ────────────────────
        if check_outdated:
            progress.update(task, description="Checking for updates …")
            detector_instances = [cls() for cls in INDEPENDENT_DETECTORS]
            tasks_outdated = [
                (det, {k: v for k, v in all_packages.items() if v.manager == det.name})
                for det in detector_instances
            ]
            # Also check brew-cask via BrewDetector (same instance handles both managers)
            brew_det = next(
                (det for det in detector_instances if isinstance(det, BrewDetector)), None
            )
            if brew_det:
                cask_pkgs = {k: v for k, v in all_packages.items() if v.manager == "brew-cask"}
                if cask_pkgs:
                    # Merge brew-cask into the brew detector's package dict
                    for idx, (det, pkgs) in enumerate(tasks_outdated):
                        if isinstance(det, BrewDetector):
                            pkgs.update(cask_pkgs)
                            break

            max_workers = min(len(tasks_outdated), 8) or 1
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures_out = {
                    executor.submit(det.check_outdated, pkgs): det.name
                    for det, pkgs in tasks_outdated
                    if pkgs  # skip detectors that found nothing
                }
                for future in as_completed(futures_out):
                    try:
                        future.result()
                    except Exception as exc:
                        _warnings.append(
                            f"[yellow]Warning: outdated check for "
                            f"{futures_out[future]} failed: {exc}[/yellow]"
                        )

    for w in _warnings:
        console.print(w)

    packages = list(all_packages.values())

    # ── Filter ───────────────────────────────────────────────────────────────
    if filter_manager:
        packages = [p for p in packages if p.manager == filter_manager]

    # ── Sort ─────────────────────────────────────────────────────────────────
    if sort_by == "name":
        packages.sort(key=lambda p: p.name.lower())
    elif sort_by == "version":
        packages.sort(key=lambda p: (p.version or "").lower())
    else:  # default: manager
        packages.sort(key=lambda p: (p.manager, p.name.lower()))

    # ── Export ───────────────────────────────────────────────────────────────
    if export_path:
        out = pathlib.Path(export_path)
        if out.suffix.lower() == ".csv":
            content = render_csv(packages)
        else:
            content = render_json(packages)
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(content, encoding="utf-8")
        except OSError as exc:
            console.print(f"[red]Could not write to [bold]{out}[/bold]: {exc}[/red]")
            raise typer.Exit(code=1)
        console.print(f"[green]Snapshot saved to [bold]{out}[/bold][/green]")

    # ── Render ───────────────────────────────────────────────────────────────
    if as_json:
        print(render_json(packages))
    else:
        render_table(packages, console, show_paths=show_paths, show_outdated=check_outdated)


def run() -> None:
    app()


if __name__ == "__main__":
    run()
