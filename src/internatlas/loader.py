"""Load internship listings from the repository data tree.

The data tree layout is::

    data/internships/<company-slug>/<listing-id>.json
    archive/internships/<company-slug>/<listing-id>.json   (closed listings)

The loader streams files so memory stays flat even at 10k+ listings.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from pydantic import ValidationError

from .models import Internship

DATA_DIR = Path("data/internships")
ARCHIVE_DIR = Path("archive/internships")


@dataclass
class LoadError:
    path: Path
    message: str


@dataclass
class LoadResult:
    listings: list[Internship] = field(default_factory=list)
    errors: list[LoadError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def iter_listing_files(root: Path, include_archive: bool = False) -> Iterator[Path]:
    """Yield every listing JSON file under *root*, sorted for determinism."""
    dirs = [root / DATA_DIR]
    if include_archive:
        dirs.append(root / ARCHIVE_DIR)
    for d in dirs:
        if not d.exists():
            continue
        yield from sorted(p for p in d.rglob("*.json") if p.is_file())


def load_one(path: Path) -> Internship:
    """Load and validate a single listing file. Raises on any problem."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    listing = Internship.model_validate(raw)
    expected_name = f"{listing.id}.json"
    if path.name != expected_name:
        raise ValueError(f"file should be named {expected_name} (id is {listing.id!r})")
    if path.parent.name != listing.company.slug:
        raise ValueError(
            f"file should live in a {listing.company.slug!r}/ directory, "
            f"found in {path.parent.name!r}/"
        )
    return listing


def load_all(root: Path | str = ".", include_archive: bool = False) -> LoadResult:
    """Load every listing, collecting errors instead of failing fast."""
    root = Path(root)
    result = LoadResult()
    for path in iter_listing_files(root, include_archive=include_archive):
        try:
            result.listings.append(load_one(path))
        except (json.JSONDecodeError, ValidationError, ValueError, OSError) as exc:
            result.errors.append(LoadError(path=path.relative_to(root), message=str(exc)))
    return result


def dump_listing(listing: Internship) -> str:
    """Serialize a listing to the canonical on-disk JSON format."""
    data = listing.model_dump(mode="json", exclude_none=True)
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def write_listing(root: Path, listing: Internship, archived: bool = False) -> Path:
    base = ARCHIVE_DIR if archived else DATA_DIR
    path = root / base / listing.company.slug / f"{listing.id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_listing(listing), encoding="utf-8")
    return path


def delete_listing(root: Path, listing: Internship, archived: bool = False) -> bool:
    """Remove a listing's JSON file (and its company dir if now empty).

    Returns True if a file was removed. Used by the sync to clean up orphaned
    auto-ingested duplicates — the same posting previously written under a
    different id.
    """
    base = ARCHIVE_DIR if archived else DATA_DIR
    path = root / base / listing.company.slug / f"{listing.id}.json"
    if not path.exists():
        return False
    path.unlink()
    parent = path.parent
    try:
        if parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()
    except OSError:
        pass
    return True
