from datetime import date

import pytest
from pydantic import ValidationError

from conftest import make_listing
from internatlas.models import (Compensation, Dates, DegreeLevel, Eligibility,
                                VisaSponsorship, WorkMode, make_slug)


def test_valid_listing_roundtrip(listing):
    data = listing.model_dump(mode="json")
    from internatlas.models import Internship
    assert Internship.model_validate(data).id == listing.id


def test_id_must_start_with_company_slug():
    with pytest.raises(ValidationError, match="must start with company slug"):
        make_listing(id="wrong-prefix-2027")


def test_onsite_requires_location():
    with pytest.raises(ValidationError, match="at least one location"):
        make_listing(locations=[])


def test_remote_needs_no_location():
    l = make_listing(work_mode=WorkMode.REMOTE, locations=[])
    assert l.primary_location == "Remote"


def test_compensation_range_validated():
    with pytest.raises(ValidationError, match="hourly_min cannot exceed"):
        Compensation(hourly_min=60, hourly_max=40)


def test_hourly_midpoint():
    assert Compensation(hourly_min=40, hourly_max=60).hourly_midpoint == 50
    assert Compensation(hourly_min=45).hourly_midpoint == 45
    assert Compensation().hourly_midpoint is None


def test_deadline_ordering_validated():
    with pytest.raises(ValidationError, match="after the deadline"):
        Dates(discovered=date(2026, 7, 1), posted=date(2026, 9, 1), deadline=date(2026, 8, 1))


def test_international_friendly():
    e = Eligibility(visa_sponsorship=VisaSponsorship.YES)
    assert e.international_friendly
    e = Eligibility(visa_sponsorship=VisaSponsorship.YES, citizenship_required=True)
    assert not e.international_friendly


def test_freshman_friendly():
    assert Eligibility(degree_levels=[DegreeLevel.FRESHMAN]).freshman_friendly


def test_make_slug():
    assert make_slug("Jane Street!!") == "jane-street"
    assert make_slug("  C++ / Systems  ") == "c-systems"


def test_extra_fields_rejected():
    with pytest.raises(ValidationError):
        make_listing(surprise_field=1)
