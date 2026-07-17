"""Pure analytics over listing collections. No I/O — trivially testable."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date, timedelta

from .models import ApplicationStatus, Internship, VisaSponsorship


@dataclass
class SalaryStats:
    count: int = 0
    average: float | None = None
    median: float | None = None
    top: list[tuple[str, str, float]] = field(default_factory=list)  # (company, id, hourly)


@dataclass
class RepoStats:
    total: int = 0
    open: int = 0
    closed: int = 0
    by_category: Counter = field(default_factory=Counter)
    by_company: Counter = field(default_factory=Counter)
    sponsoring_companies: list[str] = field(default_factory=list)
    international_hiring_companies: list[str] = field(default_factory=list)
    remote_count: int = 0
    salary: SalaryStats = field(default_factory=SalaryStats)
    top_languages: list[tuple[str, int]] = field(default_factory=list)
    top_skills: list[tuple[str, int]] = field(default_factory=list)
    interview_shape: dict[str, int] = field(default_factory=dict)
    newest: list[Internship] = field(default_factory=list)
    deadlines_this_week: list[Internship] = field(default_factory=list)
    recently_closed: list[Internship] = field(default_factory=list)


def _median(values: list[float]) -> float:
    s = sorted(values)
    mid = len(s) // 2
    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2


def compute(listings: list[Internship], today: date | None = None) -> RepoStats:
    today = today or date.today()
    stats = RepoStats(total=len(listings))

    hourly: list[float] = []
    salary_rows: list[tuple[str, str, float]] = []
    lang_counter: Counter = Counter()
    skill_counter: Counter = Counter()

    for l in listings:
        stats.by_category[l.category.value] += 1
        stats.by_company[l.company.name] += 1
        if l.status is ApplicationStatus.OPEN:
            stats.open += 1
        elif l.status is ApplicationStatus.CLOSED:
            stats.closed += 1
        if l.work_mode.value == "remote":
            stats.remote_count += 1
        if l.eligibility.visa_sponsorship is VisaSponsorship.YES:
            if l.company.name not in stats.sponsoring_companies:
                stats.sponsoring_companies.append(l.company.name)
        if l.eligibility.international_friendly:
            if l.company.name not in stats.international_hiring_companies:
                stats.international_hiring_companies.append(l.company.name)
        if (mid := l.compensation.hourly_midpoint) is not None:
            hourly.append(mid)
            salary_rows.append((l.company.name, l.id, mid))
        lang_counter.update(x.strip() for x in l.tech.languages)
        skill_counter.update(x.strip() for x in l.tech.required_skills + l.tech.preferred_skills)
        for key in ("online_assessment", "behavioral", "technical", "system_design"):
            if getattr(l.interview, key):
                stats.interview_shape[key] = stats.interview_shape.get(key, 0) + 1

    if hourly:
        stats.salary = SalaryStats(
            count=len(hourly),
            average=round(sum(hourly) / len(hourly), 2),
            median=round(_median(hourly), 2),
            top=sorted(salary_rows, key=lambda r: -r[2])[:15],
        )

    stats.top_languages = lang_counter.most_common(15)
    stats.top_skills = skill_counter.most_common(20)
    stats.sponsoring_companies.sort()
    stats.international_hiring_companies.sort()

    dated = [l for l in listings if l.dates.posted or l.dates.discovered]
    stats.newest = sorted(
        dated, key=lambda l: (l.dates.posted or l.dates.discovered), reverse=True
    )[:20]

    week_out = today + timedelta(days=7)
    stats.deadlines_this_week = sorted(
        (l for l in listings
         if l.is_open and l.dates.deadline and today <= l.dates.deadline <= week_out),
        key=lambda l: l.dates.deadline,  # type: ignore[arg-type, return-value]
    )
    stats.recently_closed = [
        l for l in listings
        if l.status is ApplicationStatus.CLOSED
        and l.dates.last_verified and (today - l.dates.last_verified).days <= 14
    ]
    return stats
