"""Automatic ingestion of live internship postings from public ATS APIs.

Sources are declared in ``automation/sources.yaml``. Two ATS providers are
supported, both via their public, keyless JSON endpoints:

- **Greenhouse**: ``https://boards-api.greenhouse.io/v1/boards/<token>/jobs``
- **Lever**:      ``https://api.lever.co/v0/postings/<token>?mode=json``

The sync is conservative and idempotent:

- Only jobs whose title matches the intern pattern are considered.
- Auto-ingested listings are tagged ``auto-ingested`` and are the *only*
  listings the sync will ever modify. Hand-curated files are never touched.
- Jobs present upstream → listing created/updated, ``last_verified`` = today,
  ``status`` = open.
- Previously-ingested jobs that vanished upstream → ``status`` = closed.
- Every write goes through the Pydantic model, so bad upstream data cannot
  corrupt the repo — CI validation still gates everything.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

import requests
import yaml

from .loader import load_all, write_listing
from .models import (ApplicationStatus, Category, CompanyInfo, Dates, Internship,
                     Location, TechProfile, WorkMode, make_slug)

AUTO_TAG = "auto-ingested"
SOURCES_FILE = Path("automation/sources.yaml")
USER_AGENT = "InternAtlas-Sync/1.0 (+https://github.com/internatlas)"

# \bintern\b or \binternship(s)\b — avoids matching "International".
_INTERN_RE = re.compile(r"\bintern(ship)?s?\b", re.IGNORECASE)
_EXCLUDE_RE = re.compile(r"\binternal\b|\binternational\b", re.IGNORECASE)

# Title keywords → category overrides (first match wins), checked before the
# per-company default category.
_CATEGORY_KEYWORDS: list[tuple[re.Pattern[str], Category]] = [
    (re.compile(r"machine learning|\bml\b|deep learning", re.I), Category.MACHINE_LEARNING),
    (re.compile(r"\bai\b|artificial intelligence", re.I), Category.AI),
    (re.compile(r"data scien", re.I), Category.DATA_SCIENCE),
    (re.compile(r"data engineer|analytics engineer", re.I), Category.DATA_ENGINEERING),
    (re.compile(r"quant|trading", re.I), Category.QUANT),
    (re.compile(r"security|infosec|appsec", re.I), Category.SECURITY),
    (re.compile(r"embedded|firmware", re.I), Category.EMBEDDED),
    (re.compile(r"hardware|asic|fpga|silicon", re.I), Category.HARDWARE),
    (re.compile(r"\bcloud\b|infrastructure|platform|devops|sre", re.I), Category.CLOUD),
    (re.compile(r"product manage|\bapm\b", re.I), Category.PRODUCT),
    (re.compile(r"design(er)?\b|\bux\b|\bui\b", re.I), Category.DESIGN),
    (re.compile(r"research", re.I), Category.RESEARCH),
]


@dataclass(frozen=True)
class Source:
    """One company's ATS board, as declared in automation/sources.yaml."""
    company: str
    slug: str
    ats: str                       # "greenhouse" | "lever"
    token: str
    default_category: Category
    country: str = "USA"
    career_page: str | None = None


@dataclass(frozen=True)
class RawJob:
    """Normalized job record from any ATS."""
    title: str
    url: str
    location: str
    posted: date | None


def load_sources(root: Path) -> list[Source]:
    path = root / SOURCES_FILE
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    sources = []
    for entry in data.get("sources", []):
        sources.append(Source(
            company=entry["company"],
            slug=entry.get("slug") or make_slug(entry["company"]),
            ats=entry["ats"],
            token=entry["token"],
            default_category=Category(entry.get("default_category", "software-engineering")),
            country=entry.get("country", "USA"),
            career_page=entry.get("career_page"),
        ))
    return sources


# ── ATS fetchers ──────────────────────────────────────────────────────────────

def _get_json(url: str, timeout: float = 20.0) -> Any:
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
    resp.raise_for_status()
    return resp.json()


def fetch_greenhouse(token: str) -> list[RawJob]:
    payload = _get_json(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs")
    jobs = []
    for j in payload.get("jobs", []):
        posted = None
        for key in ("first_published", "updated_at"):
            if j.get(key):
                try:
                    posted = datetime.fromisoformat(j[key].replace("Z", "+00:00")).date()
                    break
                except ValueError:
                    pass
        jobs.append(RawJob(
            title=j.get("title", ""),
            url=j.get("absolute_url", ""),
            location=(j.get("location") or {}).get("name", ""),
            posted=posted,
        ))
    return jobs


def fetch_lever(token: str) -> list[RawJob]:
    payload = _get_json(f"https://api.lever.co/v0/postings/{token}?mode=json")
    jobs = []
    for j in payload if isinstance(payload, list) else []:
        posted = None
        if j.get("createdAt"):
            posted = datetime.utcfromtimestamp(j["createdAt"] / 1000).date()
        jobs.append(RawJob(
            title=j.get("text", ""),
            url=j.get("hostedUrl", ""),
            location=(j.get("categories") or {}).get("location", "") or "",
            posted=posted,
        ))
    return jobs


_FETCHERS = {"greenhouse": fetch_greenhouse, "lever": fetch_lever}


# ── mapping ───────────────────────────────────────────────────────────────────

def is_internship(title: str) -> bool:
    return bool(_INTERN_RE.search(title)) and not (
        _EXCLUDE_RE.search(title) and not _INTERN_RE.search(_EXCLUDE_RE.sub("", title))
    )


def classify(title: str, default: Category) -> Category:
    for pattern, category in _CATEGORY_KEYWORDS:
        if pattern.search(title):
            return category
    return default


def parse_location(raw: str, default_country: str) -> tuple[WorkMode, list[Location]]:
    text = raw.strip()
    if not text or re.search(r"\bremote\b", text, re.I):
        return WorkMode.REMOTE, []
    parts = [p.strip() for p in re.split(r"[,;/]| - ", text) if p.strip()]
    city = parts[0] if parts else None
    state = parts[1] if len(parts) > 1 and len(parts[1]) <= 3 else None
    return WorkMode.ONSITE, [Location(city=city, state=state, country=default_country)]


def map_job(job: RawJob, source: Source, year: int, today: date) -> Internship | None:
    if not is_internship(job.title) or not job.url:
        return None
    role_slug = make_slug(job.title)[:60].rstrip("-")
    work_mode, locations = parse_location(job.location, source.country)
    return Internship(
        id=f"{source.slug}-{role_slug}-{year}",
        company=CompanyInfo(name=source.company, slug=source.slug,
                            career_page=source.career_page),  # type: ignore[arg-type]
        role=job.title.strip(),
        category=classify(job.title, source.default_category),
        apply_url=job.url,  # type: ignore[arg-type]
        work_mode=work_mode,
        locations=locations,
        year=year,
        dates=Dates(posted=job.posted, discovered=today, last_verified=today),
        status=ApplicationStatus.OPEN,
        tech=TechProfile(),
        tags=[AUTO_TAG],
    )


# ── sync ──────────────────────────────────────────────────────────────────────

def sync(root: Path | str = ".", year: int = 2027, today: date | None = None) -> dict[str, int]:
    """Run one sync pass. Returns counters for logging."""
    root = Path(root)
    today = today or date.today()
    sources = load_sources(root)
    counters = {"sources": len(sources), "fetched": 0, "created": 0,
                "updated": 0, "closed": 0, "errors": 0}

    existing = {l.id: l for l in load_all(root).listings}
    auto_ids_by_slug: dict[str, set[str]] = {}
    for l in existing.values():
        if AUTO_TAG in l.tags:
            auto_ids_by_slug.setdefault(l.company.slug, set()).add(l.id)

    for source in sources:
        try:
            raw_jobs = _FETCHERS[source.ats](source.token)
        except Exception as exc:  # noqa: BLE001 — one bad source must not kill the sync
            print(f"! {source.company}: fetch failed ({exc})")
            counters["errors"] += 1
            continue

        seen: set[str] = set()
        for job in raw_jobs:
            listing = map_job(job, source, year, today)
            if listing is None:
                continue
            counters["fetched"] += 1
            if listing.id in seen:      # same title posted in several offices
                continue
            seen.add(listing.id)

            prior = existing.get(listing.id)
            if prior is not None:
                if AUTO_TAG not in prior.tags:
                    continue            # never touch hand-curated listings
                # preserve first-discovered date and any enrichment humans added
                listing.dates.discovered = prior.dates.discovered
                if prior.dates.posted and not listing.dates.posted:
                    listing.dates.posted = prior.dates.posted
                listing.tech = prior.tech
                listing.eligibility = prior.eligibility
                listing.compensation = prior.compensation
                listing.notes = prior.notes
                counters["updated"] += 1
            else:
                counters["created"] += 1
            write_listing(root, listing)

        for stale_id in auto_ids_by_slug.get(source.slug, set()) - seen:
            stale = existing[stale_id]
            if stale.status is not ApplicationStatus.CLOSED:
                stale.status = ApplicationStatus.CLOSED
                stale.dates.last_verified = today
                write_listing(root, stale)
                counters["closed"] += 1

    return counters


def main(root: str = ".") -> int:
    counters = sync(root)
    print(", ".join(f"{k}={v}" for k, v in counters.items()))
    return 0
