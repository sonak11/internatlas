"""Shared markdown rendering helpers. All generators import from here so every
table across the repo stays visually consistent."""

from __future__ import annotations

from ..models import ApplicationStatus, Internship, VisaSponsorship

GENERATED_BANNER = (
    "<!-- ⚠️ AUTO-GENERATED FILE — do not edit by hand.\n"
    "     Edit JSON in data/internships/ and run `python -m internatlas generate`. -->\n"
)

STATUS_EMOJI = {
    ApplicationStatus.OPEN: "🟢 Open",
    ApplicationStatus.CLOSED: "🔴 Closed",
    ApplicationStatus.NOT_YET_OPEN: "🟡 Soon",
    ApplicationStatus.UNVERIFIED: "⚪ Unverified",
}

VISA_EMOJI = {
    VisaSponsorship.YES: "✅",
    VisaSponsorship.NO: "❌",
    VisaSponsorship.CASE_BY_CASE: "🔶",
    VisaSponsorship.UNKNOWN: "❔",
}


def esc(text: str) -> str:
    """Escape characters that would break a markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ")


def pay_cell(l: Internship) -> str:
    c = l.compensation
    if c.hourly_min and c.hourly_max and c.hourly_min != c.hourly_max:
        return f"${c.hourly_min:g}–{c.hourly_max:g}/hr"
    if c.hourly_min or c.hourly_max:
        return f"${(c.hourly_min or c.hourly_max):g}/hr"
    if c.monthly:
        return f"${c.monthly:,.0f}/mo"
    return "—"


def deadline_cell(l: Internship) -> str:
    return l.dates.deadline.isoformat() if l.dates.deadline else "Rolling"


def posted_cell(l: Internship) -> str:
    """Posting date if known, else the date we discovered it (marked with *)."""
    if l.dates.posted:
        return l.dates.posted.isoformat()
    return f"{l.dates.discovered.isoformat()}*"


def listing_row(l: Internship, company_link: bool = True) -> str:
    """One canonical table row used by README, category and index pages.

    Columns: Company · Role · Location · Mode · Posted · Deadline · Status · Visa.
    Pay is omitted (rarely reported by upstream sources); Visa sits last so the
    scannable columns (role, location, dates, status) lead.
    """
    company = (
        f"[{esc(l.company.name)}](generated/companies/{l.company.slug}.md)"
        if company_link else esc(l.company.name)
    )
    return (
        f"| {company} "
        f"| [{esc(l.role)}]({l.apply_url}) "
        f"| {esc(l.primary_location)} "
        f"| {l.work_mode.value.title()} "
        f"| {posted_cell(l)} "
        f"| {deadline_cell(l)} "
        f"| {STATUS_EMOJI[l.status]} "
        f"| {VISA_EMOJI[l.eligibility.visa_sponsorship]} |"
    )


TABLE_HEADER = (
    "| Company | Role | Location | Mode | Posted | Deadline | Status | Visa |\n"
    "|---|---|---|---|---|---|---|---|"
)


def listing_table(listings: list[Internship], company_link: bool = True) -> str:
    if not listings:
        return "_No listings yet — [add one!](CONTRIBUTING.md)_"
    rows = "\n".join(listing_row(l, company_link) for l in listings)
    return f"{TABLE_HEADER}\n{rows}"


def sort_listings(listings: list[Internship]) -> list[Internship]:
    """Canonical ordering: open first, earliest deadline first, then company."""
    status_rank = {
        ApplicationStatus.OPEN: 0,
        ApplicationStatus.NOT_YET_OPEN: 1,
        ApplicationStatus.UNVERIFIED: 2,
        ApplicationStatus.CLOSED: 3,
    }
    far_future = "9999-12-31"
    return sorted(
        listings,
        key=lambda l: (
            status_rank[l.status],
            l.dates.deadline.isoformat() if l.dates.deadline else far_future,
            l.company.name.lower(),
            l.role.lower(),
        ),
    )
