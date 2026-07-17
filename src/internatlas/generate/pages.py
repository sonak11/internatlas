"""Generate company pages, category pages, index pages, and stats pages."""

from __future__ import annotations

import shutil
from collections import defaultdict
from datetime import date
from pathlib import Path

from ..models import ApplicationStatus, Category, Internship, VisaSponsorship, WorkMode
from ..stats import RepoStats, compute
from .common import GENERATED_BANNER, esc, listing_table, pay_cell, sort_listings
from .readme import CATEGORY_LABELS

GEN = Path("generated")


def _write(root: Path, rel: Path, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(GENERATED_BANNER + body, encoding="utf-8")
    return path


def _clean_dir(root: Path, rel: Path) -> None:
    target = root / rel
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)


# ── Company pages ─────────────────────────────────────────────────────────────

def company_pages(root: Path, listings: list[Internship], archived: list[Internship]) -> list[Path]:
    _clean_dir(root, GEN / "companies")
    by_company: dict[str, list[Internship]] = defaultdict(list)
    for l in listings:
        by_company[l.company.slug].append(l)
    history: dict[str, list[Internship]] = defaultdict(list)
    for l in archived:
        history[l.company.slug].append(l)

    written: list[Path] = []
    for slug in sorted(set(by_company) | set(history)):
        current = sort_listings(by_company.get(slug, []))
        past = sorted(history.get(slug, []), key=lambda l: l.year, reverse=True)
        info = (current or past)[0].company

        lines = [f"# {info.name}", ""]
        meta = []
        if info.industry:
            meta.append(f"**Industry:** {info.industry.value}")
        if info.size:
            meta.append(f"**Size:** {info.size.value}")
        if info.company_type:
            meta.append(f"**Type:** {info.company_type.value}")
        if info.fortune_500:
            meta.append("**Fortune 500** ✅")
        if info.career_page:
            meta.append(f"[Careers page]({info.career_page})")
        if meta:
            lines += [" · ".join(meta), ""]

        lines += ["## Current openings", "", listing_table(current, company_link=False), ""]

        timelines = sorted({l.recruiting_timeline for l in current if l.recruiting_timeline})
        if timelines:
            lines += ["## Recruiting timeline", ""]
            lines += [f"- {t}" for t in timelines] + [""]

        iv_notes = []
        for l in current + past:
            parts = []
            if l.interview.online_assessment:
                parts.append("OA")
            if l.interview.technical:
                parts.append("technical")
            if l.interview.behavioral:
                parts.append("behavioral")
            if l.interview.system_design:
                parts.append("system design")
            if l.interview.rounds:
                parts.append(f"{l.interview.rounds} rounds")
            if parts:
                iv_notes.append(f"- **{esc(l.role)}** ({l.year}): {', '.join(parts)}"
                                + (f" — {esc(l.interview.notes)}" if l.interview.notes else ""))
        if iv_notes:
            lines += ["## Interview process", ""] + sorted(set(iv_notes)) + [""]

        paid = [l for l in current if pay_cell(l) != "—"]
        if paid:
            lines += ["## Compensation", ""]
            lines += [f"- {esc(l.role)}: {pay_cell(l)}" for l in paid] + [""]

        if past:
            lines += ["## Hiring history", "",
                      "| Year | Role | Category |", "|---|---|---|"]
            lines += [f"| {l.year} | {esc(l.role)} | {l.category.value} |" for l in past]
            lines += [""]

        cats = sorted({l.category for l in current}, key=lambda c: c.value)
        if cats:
            related = ", ".join(f"[{CATEGORY_LABELS[c]}](../categories/{c.value}.md)" for c in cats)
            lines += ["## Related", "", f"Browse more roles in: {related}", ""]

        written.append(_write(root, GEN / "companies" / f"{slug}.md", "\n".join(lines)))
    return written


# ── Category pages ────────────────────────────────────────────────────────────

def category_pages(root: Path, listings: list[Internship]) -> list[Path]:
    _clean_dir(root, GEN / "categories")
    written: list[Path] = []
    for cat in Category:
        subset = sort_listings([l for l in listings if l.category is cat])
        cat_stats = compute(subset)
        lines = [f"# {CATEGORY_LABELS[cat]} Internships", ""]
        lines += [f"**{cat_stats.total}** tracked · **{cat_stats.open}** open now", ""]
        lines += ["## Current openings", "", listing_table(subset), ""]
        if cat_stats.by_company:
            lines += ["## Hiring companies", ""]
            lines += [f"- {name} ({n})" for name, n in cat_stats.by_company.most_common()] + [""]
        if cat_stats.salary.count:
            lines += ["## Salary snapshot", "",
                      f"- Average: **${cat_stats.salary.average:.2f}/hr** "
                      f"· Median: **${cat_stats.salary.median:.2f}/hr** "
                      f"(from {cat_stats.salary.count} listings reporting pay)", ""]
        if cat_stats.top_languages:
            langs = ", ".join(f"{n} ({c})" for n, c in cat_stats.top_languages[:8])
            lines += ["## Most requested languages", "", langs, ""]
        deadlines = [l for l in subset if l.is_open and l.dates.deadline]
        if deadlines:
            lines += ["## Timeline", "", "| Deadline | Company | Role |", "|---|---|---|"]
            lines += [f"| {l.dates.deadline} | {esc(l.company.name)} | [{esc(l.role)}]({l.apply_url}) |"
                      for l in sorted(deadlines, key=lambda l: l.dates.deadline)]  # type: ignore[arg-type, return-value]
            lines += [""]
        tips = root / "docs" / "tips" / f"{cat.value}.md"
        if tips.exists():
            lines += ["## Tips", "", tips.read_text(encoding="utf-8").strip(), ""]
        written.append(_write(root, GEN / "categories" / f"{cat.value}.md", "\n".join(lines)))
    return written


# ── Index pages ───────────────────────────────────────────────────────────────

def index_pages(root: Path, listings: list[Internship]) -> list[Path]:
    _clean_dir(root, GEN / "indexes")
    written: list[Path] = []

    sponsor = sort_listings([
        l for l in listings if l.eligibility.visa_sponsorship is VisaSponsorship.YES
    ])
    written.append(_write(root, GEN / "indexes" / "visa-sponsorship.md",
        "# 🌍 Visa-Sponsoring Internships\n\nListings whose employer sponsors work visas.\n\n"
        + listing_table(sponsor) + "\n"))

    intl = sort_listings([l for l in listings if l.eligibility.international_friendly])
    written.append(_write(root, GEN / "indexes" / "international-students.md",
        "# 🛂 International-Student Friendly\n\nSponsorship available (or case-by-case) "
        "and no citizenship requirement.\n\n" + listing_table(intl) + "\n"))

    remote = sort_listings([l for l in listings if l.work_mode is WorkMode.REMOTE])
    written.append(_write(root, GEN / "indexes" / "remote.md",
        "# 🏠 Remote Internships\n\n" + listing_table(remote) + "\n"))

    for level, title in [("freshman", "🐣 Freshman-Friendly"), ("sophomore", "🌱 Sophomore-Friendly"),
                         ("masters", "🎓 Masters"), ("phd", "🔬 PhD")]:
        subset = sort_listings([
            l for l in listings
            if any(d.value == level for d in l.eligibility.degree_levels)
        ])
        written.append(_write(root, GEN / "indexes" / f"{level}.md",
            f"# {title} Internships\n\n" + listing_table(subset) + "\n"))

    dated = [l for l in listings if l.is_open and l.dates.deadline]
    lines = ["# 📅 Deadline Timeline", "", "| Deadline | Company | Role | Category |", "|---|---|---|---|"]
    lines += [
        f"| **{l.dates.deadline}** | {esc(l.company.name)} | [{esc(l.role)}]({l.apply_url}) | {l.category.value} |"
        for l in sorted(dated, key=lambda l: l.dates.deadline)  # type: ignore[arg-type, return-value]
    ]
    rolling = sort_listings([l for l in listings if l.is_open and not l.dates.deadline])
    if rolling:
        lines += ["", "## Rolling deadlines", ""]
        lines += [f"- {esc(l.company.name)} — [{esc(l.role)}]({l.apply_url})" for l in rolling]
    written.append(_write(root, GEN / "indexes" / "timeline.md", "\n".join(lines) + "\n"))

    by_company: dict[str, list[Internship]] = defaultdict(list)
    for l in listings:
        by_company[l.company.name].append(l)
    lines = ["# 🏢 Company Index", "", "| Company | Open roles | Categories |", "|---|---|---|"]
    for name in sorted(by_company):
        group = by_company[name]
        cats = ", ".join(sorted({l.category.value for l in group}))
        n_open = sum(1 for l in group if l.is_open)
        lines.append(f"| [{esc(name)}](../companies/{group[0].company.slug}.md) | {n_open}/{len(group)} | {cats} |")
    written.append(_write(root, GEN / "indexes" / "companies.md", "\n".join(lines) + "\n"))
    return written


# ── Stats pages ───────────────────────────────────────────────────────────────

def stats_pages(root: Path, listings: list[Internship], stats: RepoStats) -> list[Path]:
    _clean_dir(root, GEN / "stats")
    today = date.today().isoformat()
    lines = [f"# 📊 Statistics", "", f"_Generated {today}_", ""]

    lines += ["## Top hiring companies", "", "| Company | Listings |", "|---|---|"]
    lines += [f"| {esc(n)} | {c} |" for n, c in stats.by_company.most_common(20)] + [""]

    lines += ["## Listings by category", "", "| Category | Count | Share |", "|---|---|---|"]
    total = max(stats.total, 1)
    for name, count in stats.by_category.most_common():
        bar = "█" * max(1, round(count / total * 25))
        lines.append(f"| {name} | {count} | `{bar}` |")
    lines += [""]

    if stats.salary.count:
        lines += ["## Salary", "",
                  f"- Reported by **{stats.salary.count}** listings",
                  f"- Average: **${stats.salary.average:.2f}/hr** · Median: **${stats.salary.median:.2f}/hr**", "",
                  "### Leaderboard", "", "| # | Company | Listing | Hourly |", "|---|---|---|---|"]
        lines += [f"| {i} | {esc(co)} | `{lid}` | ${pay:.2f} |"
                  for i, (co, lid, pay) in enumerate(stats.salary.top, 1)] + [""]

    if stats.top_languages:
        lines += ["## Most requested programming languages", "", "| Language | Mentions |", "|---|---|"]
        lines += [f"| {esc(n)} | {c} |" for n, c in stats.top_languages] + [""]

    if stats.top_skills:
        lines += ["## Most requested skills", "", "| Skill | Mentions |", "|---|---|"]
        lines += [f"| {esc(n)} | {c} |" for n, c in stats.top_skills] + [""]

    if stats.interview_shape:
        lines += ["## Interview process (share of listings with data)", ""]
        labels = {"online_assessment": "Online assessment", "behavioral": "Behavioral",
                  "technical": "Technical", "system_design": "System design"}
        lines += [f"- {labels[k]}: {v}" for k, v in sorted(stats.interview_shape.items(),
                                                           key=lambda kv: -kv[1])] + [""]

    if stats.newest:
        lines += ["## Newest listings", ""]
        lines += [f"- {(l.dates.posted or l.dates.discovered)} — **{esc(l.company.name)}**: "
                  f"[{esc(l.role)}]({l.apply_url})" for l in stats.newest] + [""]

    if stats.recently_closed:
        lines += ["## Recently closed", ""]
        lines += [f"- {esc(l.company.name)} — {esc(l.role)}" for l in stats.recently_closed] + [""]

    return [_write(root, GEN / "stats" / "README.md", "\n".join(lines))]
