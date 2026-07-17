import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from internatlas.models import (ApplicationStatus, Category, CompanyInfo, Compensation,
                                Dates, DegreeLevel, Eligibility, Internship, Location,
                                VisaSponsorship, WorkMode)


def make_listing(**overrides) -> Internship:
    base = dict(
        id="acme-swe-intern-2027",
        company=CompanyInfo(name="Acme", slug="acme"),
        role="Software Engineering Intern",
        category=Category.SOFTWARE_ENGINEERING,
        apply_url="https://example.com/jobs/123",
        work_mode=WorkMode.ONSITE,
        locations=[Location(city="Austin", state="TX", country="USA")],
        year=2027,
        dates=Dates(discovered=date(2026, 7, 1)),
    )
    base.update(overrides)
    return Internship(**base)


@pytest.fixture
def listing() -> Internship:
    return make_listing()
