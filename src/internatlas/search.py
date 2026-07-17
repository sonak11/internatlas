"""CLI search over the data tree.

Examples::

    python -m internatlas search --company google
    python -m internatlas search --category quant --visa yes
    python -m internatlas search --remote --min-pay 50
    python -m internatlas search --grad-year 2028 --level sophomore
    python -m internatlas search --skill python --open --json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .generate.common import deadline_cell, pay_cell, sort_listings
from .loader import load_all
from .models import Internship


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--company", help="Company name or slug (substring match)")
    parser.add_argument("--role", help="Role title substring")
    parser.add_argument("--category", help="Category slug, e.g. machine-learning, quant")
    parser.add_argument("--location", help="City/state/country substring")
    parser.add_argument("--remote", action="store_true", help="Remote roles only")
    parser.add_argument("--visa", choices=["yes", "no", "case-by-case", "unknown"])
    parser.add_argument("--international", action="store_true",
                        help="International-student friendly (sponsorship, no citizenship req.)")
    parser.add_argument("--no-clearance", action="store_true", help="Exclude clearance-required roles")
    parser.add_argument("--min-pay", type=float, help="Minimum hourly pay (uses range midpoint)")
    parser.add_argument("--grad-year", type=int, help="Your graduation year")
    parser.add_argument("--level", help="freshman|sophomore|junior|senior|masters|phd")
    parser.add_argument("--skill", help="Required/preferred skill or language substring")
    parser.add_argument("--open", action="store_true", help="Only listings open right now")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of a table")
    parser.add_argument("--limit", type=int, default=50)


def matches(l: Internship, args: argparse.Namespace) -> bool:
    def has(text: str | None, needle: str) -> bool:
        return needle.lower() in (text or "").lower()

    if args.company and not (has(l.company.name, args.company) or has(l.company.slug, args.company)):
        return False
    if args.role and not has(l.role, args.role):
        return False
    if args.category and l.category.value != args.category.lower():
        return False
    if args.location:
        blob = " ".join(f"{x.city or ''} {x.state or ''} {x.country}" for x in l.locations)
        if l.work_mode.value == "remote":
            blob += " remote"
        if not has(blob, args.location):
            return False
    if args.remote and l.work_mode.value != "remote":
        return False
    if args.visa and l.eligibility.visa_sponsorship.value != args.visa:
        return False
    if args.international and not l.eligibility.international_friendly:
        return False
    if args.no_clearance and l.eligibility.security_clearance_required:
        return False
    if args.min_pay is not None:
        mid = l.compensation.hourly_midpoint
        if mid is None or mid < args.min_pay:
            return False
    if args.grad_year and l.eligibility.graduation_years \
            and args.grad_year not in l.eligibility.graduation_years:
        return False
    if args.level and not any(d.value == args.level.lower() for d in l.eligibility.degree_levels):
        return False
    if args.skill:
        pool = l.tech.required_skills + l.tech.preferred_skills + l.tech.languages + l.tech.frameworks
        if not any(has(s, args.skill) for s in pool):
            return False
    if args.open and not l.is_open:
        return False
    return True


def run(args: argparse.Namespace, root: Path | str = ".") -> int:
    result = load_all(root)
    hits = sort_listings([l for l in result.listings if matches(l, args)])[: args.limit]

    if args.json:
        print(json.dumps([l.model_dump(mode="json", exclude_none=True) for l in hits],
                         indent=2, ensure_ascii=False))
        return 0

    if not hits:
        print("No matching internships. Try loosening a filter.")
        return 1

    widths = (28, 40, 22, 12, 12)
    header = ("COMPANY", "ROLE", "LOCATION", "PAY", "DEADLINE")
    print("  ".join(h.ljust(w) for h, w in zip(header, widths)))
    print("  ".join("─" * w for w in widths))
    for l in hits:
        row = (l.company.name[:27], l.role[:39], l.primary_location[:21],
               pay_cell(l)[:11], deadline_cell(l))
        print("  ".join(c.ljust(w) for c, w in zip(row, widths)))
    print(f"\n{len(hits)} result(s). Apply links: run with --json for full records.")
    return 0
