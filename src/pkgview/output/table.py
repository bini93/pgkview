from __future__ import annotations

from typing import List

from rich.console import Console, RenderableType
from rich.table import Table
from rich.text import Text

from pkgview.models import Package


MANAGER_STYLES: dict[str, str] = {
    "brew": "bold green",
    "brew-cask": "bold cyan",
    "npm": "bold yellow",
    "pip": "bold blue",
    "pipx": "bold bright_blue",
    "cargo": "bold red",
    "apt": "bold magenta",
    "snap": "bold bright_magenta",
    "flatpak": "bold bright_cyan",
    "conda": "bold green",
    "mamba": "bold bright_green",
    "pacman": "bold cyan",
    "yay": "bold bright_cyan",
    "dnf": "bold magenta",
    "yum": "bold magenta",
    "zypper": "bold bright_magenta",
    "apk": "bold blue",
    "nix": "bold bright_blue",
    "gem": "bold red",
    "composer": "bold yellow",
    "winget": "bold bright_blue",
    "scoop": "bold blue",
    "chocolatey": "bold bright_yellow",
    "nvm": "bold green",
    "asdf": "bold bright_green",
    "pyenv": "bold blue",
    "manual": "bold yellow",
}

MANAGER_ICONS: dict[str, str] = {
    "brew": "🍺",
    "brew-cask": "🍺",
    "npm": "📦",
    "pip": "🐍",
    "pipx": "🐍",
    "cargo": "🦀",
    "apt": "🐧",
    "snap": "🐧",
    "flatpak": "🐧",
    "conda": "🐍",
    "mamba": "🐍",
    "pacman": "🐧",
    "yay": "🐧",
    "dnf": "🐧",
    "yum": "🐧",
    "zypper": "🐧",
    "apk": "🐧",
    "nix": "❄ ",
    "gem": "💎",
    "composer": "🎵",
    "winget": "🪟",
    "scoop": "🪟",
    "chocolatey": "🍫",
    "nvm": "🟩",
    "asdf": "🔧",
    "pyenv": "🐍",
    "manual": "⚠ ",
}


def render_table(
    packages: List[Package],
    console: Console,
    show_paths: bool = False,
    show_outdated: bool = False,
) -> None:
    table = Table(
        show_header=True,
        header_style="bold white",
        border_style="bright_black",
        row_styles=["", "dim"],
    )
    table.add_column("Name", style="white bold", no_wrap=True, min_width=18)
    table.add_column("Manager", no_wrap=True, min_width=14)
    table.add_column("Version", style="dim", min_width=8, max_width=14)
    if show_outdated:
        table.add_column("Latest", style="dim", min_width=8, max_width=14)
    table.add_column("Type", style="dim", min_width=5, max_width=6)
    if show_paths:
        table.add_column("Path", style="dim", overflow="ellipsis", no_wrap=True)

    for pkg in packages:
        style = MANAGER_STYLES.get(pkg.manager, "white")
        icon = MANAGER_ICONS.get(pkg.manager, "  ")
        manager_text = Text(f"{icon} {pkg.manager}", style=style)

        if show_outdated and pkg.outdated:
            version_text = Text(pkg.version or "–", style="bold red")
        else:
            version_text = Text(pkg.version or "–", style="dim")

        row: list[RenderableType] = [
            pkg.name,
            manager_text,
            version_text,
        ]
        if show_outdated:
            if pkg.outdated and pkg.latest_version:
                row.append(Text(pkg.latest_version, style="bold green"))
            else:
                row.append(Text("–", style="dim"))
        row.append(pkg.category)
        if show_paths:
            row.append(pkg.path or "–")

        table.add_row(*row)

    console.print()
    console.print(table)

    managed = sum(1 for p in packages if p.is_managed)
    manual = len(packages) - managed
    outdated_count = sum(1 for p in packages if p.outdated)

    summary = (
        f"\n[dim]Total: [bold white]{len(packages)}[/bold white] programs  "
        f"│  [bold green]{managed}[/bold green] managed  "
        f"│  [bold yellow]{manual}[/bold yellow] manual"
    )
    if show_outdated:
        summary += f"  │  [bold red]{outdated_count}[/bold red] outdated"
    summary += "[/dim]"
    console.print(summary)
