"""Dead-link checker for apply URLs.

Designed for a scheduled GitHub Action: polite (rate-limited, HEAD-first),
resilient (retries with backoff), and honest (a failure marks the listing for
human review rather than auto-deleting it — many ATS sites block bots).
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import requests

from .loader import load_all

USER_AGENT = "InternAtlas-LinkChecker/1.0 (+https://github.com/internatlas)"
# Status codes that usually mean "bot blocked", not "posting gone".
_SOFT_CODES = {401, 403, 405, 429, 503, 999}


@dataclass
class LinkReport:
    listing_id: str
    url: str
    status: int | None
    verdict: str  # "ok" | "dead" | "review"


def check_url(url: str, timeout: float = 15.0, retries: int = 2) -> tuple[int | None, str]:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    last_code: int | None = None
    for attempt in range(retries + 1):
        try:
            resp = session.head(url, allow_redirects=True, timeout=timeout)
            if resp.status_code == 405:  # HEAD not allowed → try GET
                resp = session.get(url, allow_redirects=True, timeout=timeout, stream=True)
                resp.close()
            last_code = resp.status_code
        except requests.RequestException:
            last_code = None
        if last_code is not None and last_code < 400:
            return last_code, "ok"
        if last_code in _SOFT_CODES:
            return last_code, "review"
        time.sleep(1.5 * (attempt + 1))
    if last_code == 404 or last_code == 410:
        return last_code, "dead"
    return last_code, "review"


def run(root: Path | str = ".", delay: float = 1.0, limit: int | None = None) -> list[LinkReport]:
    listings = load_all(root).listings
    if limit:
        listings = listings[:limit]
    reports: list[LinkReport] = []
    for listing in listings:
        code, verdict = check_url(str(listing.apply_url))
        reports.append(LinkReport(listing.id, str(listing.apply_url), code, verdict))
        symbol = {"ok": "✓", "dead": "✗", "review": "?"}[verdict]
        print(f"{symbol} [{code or '—'}] {listing.id}")
        time.sleep(delay)
    return reports


def main(root: str = ".", limit: int | None = None) -> int:
    reports = run(root, limit=limit)
    dead = [r for r in reports if r.verdict == "dead"]
    review = [r for r in reports if r.verdict == "review"]
    print(f"\n{len(reports)} checked · {len(dead)} dead · {len(review)} need review")
    if dead:
        print("\nDead links (open a PR to archive these):")
        for r in dead:
            print(f"  {r.listing_id}: {r.url}")
    return 1 if dead else 0
