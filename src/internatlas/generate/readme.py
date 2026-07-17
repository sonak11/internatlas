"""Generate the top-level README.md.

The README is assembled from ``docs/README.template.md`` — human-authored prose
lives in the template; everything between generation markers is machine-owned.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from ..models import Category, Internship
from ..stats import RepoStats
from .common import GENERATED_BANNER, listing_table, sort_listings

CATEGORY_LABELS: dict[Category, str] = {
    Category.SOFTWARE_ENGINEERING: "💻 Software Engineering",
    Category.MACHINE_LEARNING: "🧠 Machine Learning",
    Category.AI: "🤖 AI",
    Category.DATA_SCIENCE: "📊 Data Science",
    Category.DATA_ENGINEERING: "🛠 Data Engineering",
    Category.QUANT: "📈 Quant",
    Category.HARDWARE: "🔩 Hardware",
    Category.EMBEDDED: "⚙️ Embedded",
    Category.SECURITY: "🔐 Security",
    Category.CLOUD: "☁️ Cloud",
    Category.PRODUCT: "🧭 Product",
    Category.DESIGN: "🎨 Design",
    Category.RESEARCH: "🔬 Research",
    Category.FINANCE: "💰 Finance",
    Category.CONSULTING: "🤝 Consulting",
}


def _badges(stats: RepoStats) -> str:
    def badge(label: str, value: str, color: str) -> str:
        label_e = label.replace(" ", "%20").replace("-", "--")
        value_e = str(value).replace(" ", "%20").replace("-", "--")
        return f"![{label}](https://img.shields.io/badge/{label_e}-{value_e}-{color}?style=for-the-badge)"

    return " ".join([
        badge("internships", str(stats.total), "blue"),
        badge("open now", str(stats.open), "brightgreen"),
        badge("companies", str(len(stats.by_company)), "purple"),
        badge("visa sponsors", str(len(stats.sponsoring_companies)), "orange"),
        badge("remote roles", str(stats.remote_count), "teal"),
        badge("updated", date.today().isoformat(), "lightgrey"),
    ])


def _quick_stats(stats: RepoStats) -> str:
    lines = ["| Metric | Value |", "|---|---|"]
    lines.append(f"| Total tracked | **{stats.total}** |")
    lines.append(f"| Currently open | **{stats.open}** |")
    lines.append(f"| Companies | **{len(stats.by_company)}** |")
    if stats.salary.average is not None:
        lines.append(f"| Average hourly (reported) | **${stats.salary.average:.2f}** |")
        lines.append(f"| Median hourly (reported) | **${stats.salary.median:.2f}** |")
    if stats.top_languages:
        top3 = ", ".join(name for name, _ in stats.top_languages[:3])
        lines.append(f"| Most requested languages | {top3} |")
    return "\n".join(lines)


def _category_nav() -> str:
    cells = [
        f"[{label}](generated/categories/{cat.value}.md)"
        for cat, label in CATEGORY_LABELS.items()
    ]
    rows = ["| " + " | ".join(cells[i:i + 5]) + " |" for i in range(0, len(cells), 5)]
    sep = "|" + "---|" * min(5, len(cells))
    return "\n".join([rows[0], sep, *rows[1:]])


def _deadline_alert(stats: RepoStats) -> str:
    if not stats.deadlines_this_week:
        return ""
    lines = ["> [!WARNING]", "> **⏰ Deadlines in the next 7 days:**"]
    for l in stats.deadlines_this_week[:10]:
        lines.append(f"> - **{l.company.name}** — [{l.role}]({l.apply_url}) closes **{l.dates.deadline}**")
    return "\n".join(lines) + "\n"


def _listings_by_category(listings: list[Internship]) -> str:
    """Every listing, inline in the README, grouped by category — no clicking around."""
    blocks: list[str] = []
    for cat, label in CATEGORY_LABELS.items():
        subset = sort_listings([l for l in listings if l.category is cat])
        if not subset:
            continue
        open_n = sum(1 for l in subset if l.is_open)
        blocks.append(
            f"### {label} ({len(subset)}{f' · {open_n} open' if open_n else ''})\n\n"
            f"{listing_table(subset)}\n"
        )
    return "\n".join(blocks)


def render(listings: list[Internship], stats: RepoStats, template_path: Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    ordered = sort_listings(listings)

    sections: dict[str, str] = {
        "BADGES": _badges(stats),
        "QUICK_STATS": _quick_stats(stats),
        "CATEGORY_NAV": _category_nav(),
        "DEADLINE_ALERT": _deadline_alert(stats),
        "ALL_LISTINGS": listing_table(ordered),
        "LISTINGS_BY_CATEGORY": _listings_by_category(listings),
        "LISTING_COUNT": str(stats.total),
    }
    out = template
    for key, value in sections.items():
        out = out.replace(f"{{{{{key}}}}}", value)
    return GENERATED_BANNER + out


def write(root: Path, listings: list[Internship], stats: RepoStats) -> Path:
    template = root / "docs" / "README.template.md"
    target = root / "README.md"
    target.write_text(render(listings, stats, template), encoding="utf-8")
    return target
