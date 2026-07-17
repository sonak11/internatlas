import argparse
from datetime import date

from conftest import make_listing
from internatlas.models import (ApplicationStatus, Category, Compensation, Dates,
                                DegreeLevel, Eligibility, VisaSponsorship, WorkMode)
from internatlas.search import add_arguments, matches
from internatlas.stats import compute


def _args(**kw) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    ns = parser.parse_args([])
    for k, v in kw.items():
        setattr(ns, k, v)
    return ns


def test_stats_salary_and_categories():
    listings = [
        make_listing(compensation=Compensation(hourly_min=40, hourly_max=60)),
        make_listing(id="acme-quant-intern-2027", role="Quant Intern",
                     category=Category.QUANT,
                     apply_url="https://example.com/jobs/2",
                     compensation=Compensation(hourly_min=100, hourly_max=100)),
    ]
    s = compute(listings, today=date(2026, 7, 16))
    assert s.total == 2
    assert s.salary.count == 2
    assert s.salary.average == 75.0
    assert s.by_category["quant"] == 1


def test_deadline_this_week_window():
    l = make_listing(status=ApplicationStatus.OPEN,
                     dates=Dates(discovered=date(2026, 7, 1), deadline=date(2026, 7, 20)))
    s = compute([l], today=date(2026, 7, 16))
    assert s.deadlines_this_week == [l]
    s = compute([l], today=date(2026, 6, 1))
    assert s.deadlines_this_week == []


def test_search_filters():
    l = make_listing(
        eligibility=Eligibility(visa_sponsorship=VisaSponsorship.YES,
                                degree_levels=[DegreeLevel.SOPHOMORE],
                                graduation_years=[2029]),
        compensation=Compensation(hourly_min=50, hourly_max=70),
    )
    assert matches(l, _args(company="acme"))
    assert matches(l, _args(visa="yes"))
    assert matches(l, _args(min_pay=55.0))
    assert not matches(l, _args(min_pay=80.0))
    assert matches(l, _args(level="sophomore", grad_year=2029))
    assert not matches(l, _args(grad_year=2027))
    assert matches(l, _args(location="austin"))
    assert not matches(l, _args(remote=True))
