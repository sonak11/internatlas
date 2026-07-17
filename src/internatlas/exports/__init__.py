"""Machine-readable exports: CSV, JSON, ICS calendar, RSS feed, weekly digest.

All exports land in ``generated/exports/`` and are rebuilt by CI on every merge.
The CSV opens directly in Google Sheets / Excel (File → Import → upload, or
``IMPORTDATA()`` pointed at the raw GitHub URL).
"""

from __future__ import annotations

import csv
import io
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

from ..models import Internship
from ..generate.common import pay_cell

EXPORT_DIR = Path("generated/exports")

CSV_COLUMNS = [
    "id", "company", "role", "category", "subcategory", "status", "work_mode",
    "location", "country", "pay", "visa_sponsorship", "citizenship_required",
    "deadline", "posted", "apply_url", "graduation_years", "degree_levels",
    "languages", "season", "year",
]


def _row(l: Internship) -> dict[str, str]:
    return {
        "id": l.id,
        "company": l.company.name,
        "role": l.role,
        "category": l.category.value,
        "subcategory": l.subcategory or "",
        "status": l.status.value,
        "work_mode": l.work_mode.value,
        "location": l.primary_location,
        "country": l.locations[0].country if l.locations else "",
        "pay": pay_cell(l),
        "visa_sponsorship": l.eligibility.visa_sponsorship.value,
        "citizenship_required": str(l.eligibility.citizenship_required).lower(),
        "deadline": l.dates.deadline.isoformat() if l.dates.deadline else "",
        "posted": l.dates.posted.isoformat() if l.dates.posted else "",
        "apply_url": str(l.apply_url),
        "graduation_years": ";".join(map(str, l.eligibility.graduation_years)),
        "degree_levels": ";".join(d.value for d in l.eligibility.degree_levels),
        "languages": ";".join(l.tech.languages),
        "season": l.season.value,
        "year": str(l.year),
    }


def to_csv(listings: list[Internship]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for l in listings:
        writer.writerow(_row(l))
    return buf.getvalue()


def to_json(listings: list[Internship]) -> str:
    payload = {
        "generated": date.today().isoformat(),
        "count": len(listings),
        "internships": [l.model_dump(mode="json", exclude_none=True) for l in listings],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _ics_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def to_ics(listings: list[Internship]) -> str:
    """All-day VEVENT per application deadline — import into Google/Apple Calendar."""
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0",
        "PRODID:-//InternAtlas//Deadlines//EN",
        "X-WR-CALNAME:InternAtlas Deadlines",
    ]
    for l in listings:
        if not l.dates.deadline or not l.is_open:
            continue
        d = l.dates.deadline
        lines += [
            "BEGIN:VEVENT",
            f"UID:{l.id}@internatlas",
            f"DTSTAMP:{now}",
            f"DTSTART;VALUE=DATE:{d.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{(d + timedelta(days=1)).strftime('%Y%m%d')}",
            f"SUMMARY:{_ics_escape(f'⏰ {l.company.name} — {l.role} deadline')}",
            f"DESCRIPTION:{_ics_escape(f'Apply: {l.apply_url}')}",
            f"URL:{l.apply_url}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def to_rss(listings: list[Internship], repo_url: str = "https://github.com/OWNER/REPO") -> str:
    """RSS 2.0 feed of the newest listings (by posted/discovered date)."""
    newest = sorted(listings, key=lambda l: (l.dates.posted or l.dates.discovered), reverse=True)[:50]
    items = []
    for l in newest:
        pub = l.dates.posted or l.dates.discovered
        pub_rfc = datetime(pub.year, pub.month, pub.day, tzinfo=timezone.utc).strftime(
            "%a, %d %b %Y %H:%M:%S +0000")
        items.append(
            "<item>"
            f"<title>{escape(f'{l.company.name}: {l.role}')}</title>"
            f"<link>{escape(str(l.apply_url))}</link>"
            f"<guid isPermaLink=\"false\">{escape(l.id)}</guid>"
            f"<pubDate>{pub_rfc}</pubDate>"
            f"<category>{escape(l.category.value)}</category>"
            f"<description>{escape(f'{l.primary_location} · {l.work_mode.value} · {pay_cell(l)}')}</description>"
            "</item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0"><channel>'
        "<title>InternAtlas — New Internships</title>"
        f"<link>{escape(repo_url)}</link>"
        "<description>Newest Summer internship listings tracked by InternAtlas</description>"
        + "".join(items) +
        "</channel></rss>\n"
    )


def weekly_digest(listings: list[Internship], today: date | None = None) -> str:
    """Markdown digest of the last 7 days — posted to Discussions by CI."""
    today = today or date.today()
    week_ago = today - timedelta(days=7)
    week_out = today + timedelta(days=7)

    new = [l for l in listings if (l.dates.posted or l.dates.discovered) >= week_ago]
    closing = [l for l in listings
               if l.is_open and l.dates.deadline and today <= l.dates.deadline <= week_out]

    lines = [f"# 📬 InternAtlas Weekly Digest — {today.isoformat()}", ""]
    lines += [f"## 🆕 New this week ({len(new)})", ""]
    lines += [f"- **{l.company.name}** — [{l.role}]({l.apply_url}) · {l.category.value} · {pay_cell(l)}"
              for l in sorted(new, key=lambda l: l.company.name)] or ["_Nothing new this week._"]
    lines += ["", f"## ⏰ Closing within 7 days ({len(closing)})", ""]
    lines += [f"- **{l.dates.deadline}** — {l.company.name}: [{l.role}]({l.apply_url})"
              for l in sorted(closing, key=lambda l: l.dates.deadline)] or ["_No imminent deadlines._"]  # type: ignore[arg-type, return-value]
    lines += ["", "---", "_Subscribe to the [RSS feed](../exports/feed.xml) or import "
              "[deadlines.ics](../exports/deadlines.ics) into your calendar._", ""]
    return "\n".join(lines)


def write_all(root: Path, listings: list[Internship]) -> list[Path]:
    out = root / EXPORT_DIR
    out.mkdir(parents=True, exist_ok=True)
    files = {
        "internships.csv": to_csv(listings),
        "internships.json": to_json(listings),
        "deadlines.ics": to_ics(listings),
        "feed.xml": to_rss(listings),
        "digest.md": weekly_digest(listings),
    }
    written = []
    for name, content in files.items():
        path = out / name
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written
