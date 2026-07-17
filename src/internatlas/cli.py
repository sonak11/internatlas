"""Unified command-line interface: ``python -m internatlas <command>``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _cmd_validate(args: argparse.Namespace) -> int:
    from .validate import main
    return main(args.root)


def _cmd_generate(args: argparse.Namespace) -> int:
    from .exports import write_all as write_exports
    from .generate import pages, readme
    from .loader import load_all
    from .stats import compute

    root = Path(args.root)
    active = load_all(root)
    archived = load_all(root, include_archive=True)
    if not active.ok:
        for err in active.errors:
            print(f"✗ {err.path}: {err.message}", file=sys.stderr)
        print("Fix validation errors before generating.", file=sys.stderr)
        return 1

    archive_only = [l for l in archived.listings if l.id not in {x.id for x in active.listings}]
    stats = compute(active.listings)

    written: list[Path] = [readme.write(root, active.listings, stats)]
    written += pages.company_pages(root, active.listings, archive_only)
    written += pages.category_pages(root, active.listings)
    written += pages.index_pages(root, active.listings)
    written += pages.stats_pages(root, active.listings, stats)
    written += write_exports(root, active.listings)
    print(f"✓ Generated {len(written)} files from {len(active.listings)} listings.")
    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    from .search import run
    return run(args, root=args.root)


def _cmd_linkcheck(args: argparse.Namespace) -> int:
    from .linkcheck import main
    return main(args.root, limit=args.limit)


def _cmd_dedupe(args: argparse.Namespace) -> int:
    from .dedupe import find_duplicates
    from .loader import load_all
    dups = find_duplicates(load_all(args.root).listings)
    for d in dups:
        print(f"✗ {d}")
    print(f"{len(dups)} possible duplicate(s).")
    return 1 if dups else 0


def _cmd_schema(args: argparse.Namespace) -> int:
    from .models import Internship
    schema = Internship.model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = "https://raw.githubusercontent.com/OWNER/REPO/main/schemas/internship.schema.json"
    out = Path(args.root) / "schemas" / "internship.schema.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(f"✓ Wrote {out}")
    return 0


def _cmd_new(args: argparse.Namespace) -> int:
    """Interactive scaffold for a new listing file."""
    from datetime import date

    from .loader import write_listing
    from .models import (Category, CompanyInfo, Dates, Internship, WorkMode,
                         make_slug, Location)

    company = input("Company name: ").strip()
    role = input("Role title: ").strip()
    cats = ", ".join(c.value for c in Category)
    category = input(f"Category ({cats}): ").strip()
    apply_url = input("Direct apply URL: ").strip()
    mode = input("Work mode (remote/hybrid/onsite): ").strip().lower()
    slug = make_slug(company)
    listing = Internship(
        id=f"{slug}-{make_slug(role)}-{args.year}",
        company=CompanyInfo(name=company, slug=slug),
        role=role,
        category=Category(category),
        apply_url=apply_url,  # type: ignore[arg-type]
        work_mode=WorkMode(mode),
        year=args.year,
        locations=[] if mode == "remote" else [
            Location(country=input("Country: ").strip() or "USA",
                     city=input("City (optional): ").strip() or None)
        ],
        dates=Dates(discovered=date.today()),
    )
    path = write_listing(Path(args.root), listing)
    print(f"✓ Created {path} — fill in the optional fields, then open a PR!")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="internatlas",
                                     description="InternAtlas data-platform toolkit")
    parser.add_argument("--root", default=".", help="Repository root (default: cwd)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="Validate every listing + cross-file rules")
    sub.add_parser("generate", help="Regenerate README, pages, indexes, stats, exports")
    sub.add_parser("dedupe", help="Report likely duplicate listings")
    sub.add_parser("schema", help="Export JSON Schema from the Pydantic models")

    p_link = sub.add_parser("linkcheck", help="Check apply URLs for dead links")
    p_link.add_argument("--limit", type=int, default=None)

    p_new = sub.add_parser("new", help="Scaffold a new listing interactively")
    p_new.add_argument("--year", type=int, default=2027)

    p_search = sub.add_parser("search", help="Search listings from the terminal")
    from .search import add_arguments
    add_arguments(p_search)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    dispatch = {
        "validate": _cmd_validate,
        "generate": _cmd_generate,
        "search": _cmd_search,
        "linkcheck": _cmd_linkcheck,
        "dedupe": _cmd_dedupe,
        "schema": _cmd_schema,
        "new": _cmd_new,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
