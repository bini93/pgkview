from __future__ import annotations

import csv
import io
from typing import List

from pkgview.models import Package


def render_csv(packages: List[Package]) -> str:
    """Serialize packages as a UTF-8 CSV string."""
    buf = io.StringIO()
    fieldnames = [
        "name", "manager", "version", "latest_version",
        "path", "category", "managed", "outdated",
    ]
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for pkg in packages:
        writer.writerow({
            "name": pkg.name,
            "manager": pkg.manager,
            "version": pkg.version or "",
            "latest_version": pkg.latest_version or "",
            "path": pkg.path or "",
            "category": pkg.category,
            "managed": pkg.is_managed,
            "outdated": pkg.outdated,
        })
    return buf.getvalue()
