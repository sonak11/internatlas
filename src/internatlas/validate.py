"""Repository-wide validation: schema, file layout, and cross-file rules."""

from __future__ import annotations

from pathlib import Path

from .dedupe import find_duplicates
from .loader import LoadResult, load_all


def validate_repo(root: Path | str = ".", include_archive: bool = True) -> tuple[LoadResult, list[str]]:
    """Validate the whole data tree.

    Returns the load result plus a list of cross-file problems
    (duplicate ids, duplicate apply URLs, near-duplicate listings).
    """
    result = load_all(root, include_archive=include_archive)
    problems: list[str] = []

    seen_ids: dict[str, int] = {}
    for listing in result.listings:
        seen_ids[listing.id] = seen_ids.get(listing.id, 0) + 1
    for lid, count in sorted(seen_ids.items()):
        if count > 1:
            problems.append(f"duplicate id {lid!r} appears {count} times")

    for dup in find_duplicates(result.listings):
        problems.append(str(dup))

    return result, problems


def main(root: str = ".") -> int:
    result, problems = validate_repo(root)
    for err in result.errors:
        print(f"✗ {err.path}: {err.message}")
    for problem in problems:
        print(f"✗ {problem}")
    n = len(result.listings)
    if result.errors or problems:
        print(f"\nValidation failed: {len(result.errors)} file error(s), "
              f"{len(problems)} cross-file problem(s) across {n} listing(s).")
        return 1
    print(f"✓ {n} listing(s) valid.")
    return 0
