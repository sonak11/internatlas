"""Offline tests for the ATS ingestion mapping (no network)."""
from datetime import date
from pathlib import Path

from internatlas import ingest
from internatlas.ingest import (AUTO_TAG, RawJob, Source, classify, is_internship,
                                map_job, parse_location, sync)
from internatlas.loader import load_all, write_listing
from internatlas.models import ApplicationStatus, Category, WorkMode

SRC = Source(company="Acme", slug="acme", ats="greenhouse", token="acme",
             default_category=Category.SOFTWARE_ENGINEERING)
TODAY = date(2026, 7, 16)


def test_intern_title_filter():
    assert is_internship("Software Engineering Intern")
    assert is_internship("2027 Summer Internship - Trading")
    assert is_internship("Machine Learning Internships")
    assert not is_internship("International Sales Manager")
    assert not is_internship("Internal Tools Engineer")
    assert not is_internship("Senior Software Engineer")


def test_classify_overrides_default():
    assert classify("Machine Learning Intern", Category.SOFTWARE_ENGINEERING) \
        is Category.MACHINE_LEARNING
    assert classify("Quantitative Trading Intern", Category.SOFTWARE_ENGINEERING) \
        is Category.QUANT
    assert classify("Backend Intern", Category.SOFTWARE_ENGINEERING) \
        is Category.SOFTWARE_ENGINEERING


def test_parse_location():
    mode, locs = parse_location("New York, NY", "USA")
    assert mode is WorkMode.ONSITE
    assert locs[0].city == "New York" and locs[0].state == "NY"
    mode, locs = parse_location("Remote - US", "USA")
    assert mode is WorkMode.REMOTE and locs == []


def test_map_job_produces_valid_listing():
    job = RawJob(title="Security Engineering Intern (Summer 2027)",
                 url="https://boards.greenhouse.io/acme/jobs/1",
                 location="Austin, TX", posted=date(2026, 7, 1))
    listing = map_job(job, SRC, 2027, TODAY)
    assert listing is not None
    assert listing.category is Category.SECURITY
    assert listing.status is ApplicationStatus.OPEN
    assert AUTO_TAG in listing.tags
    assert listing.dates.posted == date(2026, 7, 1)
    assert listing.id.startswith("acme-")


def test_map_job_rejects_non_intern():
    job = RawJob(title="Staff Engineer", url="https://x.example/1", location="", posted=None)
    assert map_job(job, SRC, 2027, TODAY) is None


def test_sync_creates_updates_and_closes(tmp_path: Path, monkeypatch):
    (tmp_path / "automation").mkdir()
    (tmp_path / "automation/sources.yaml").write_text(
        "sources:\n  - company: Acme\n    slug: acme\n    ats: greenhouse\n"
        "    token: acme\n    default_category: software-engineering\n")

    batches = {
        "run1": [RawJob("SWE Intern", "https://x.example/1", "NYC, NY", date(2026, 7, 1)),
                 RawJob("ML Intern", "https://x.example/2", "Remote", date(2026, 7, 2))],
        "run2": [RawJob("SWE Intern", "https://x.example/1", "NYC, NY", date(2026, 7, 1))],
    }
    current = {"key": "run1"}
    monkeypatch.setitem(ingest._FETCHERS, "greenhouse", lambda token: batches[current["key"]])

    c1 = sync(tmp_path, today=TODAY)
    assert c1["created"] == 2 and c1["closed"] == 0

    current["key"] = "run2"
    c2 = sync(tmp_path, today=TODAY)
    assert c2["updated"] == 1 and c2["closed"] == 1

    listings = {l.id: l for l in load_all(tmp_path).listings}
    assert listings["acme-ml-intern-2027"].status is ApplicationStatus.CLOSED
    assert listings["acme-swe-intern-2027"].status is ApplicationStatus.OPEN


def test_sync_never_touches_manual_listings(tmp_path: Path, monkeypatch):
    from conftest import make_listing
    manual = make_listing(id="acme-swe-intern-2027", notes="hand-curated")
    write_listing(tmp_path, manual)
    (tmp_path / "automation").mkdir()
    (tmp_path / "automation/sources.yaml").write_text(
        "sources:\n  - company: Acme\n    slug: acme\n    ats: greenhouse\n"
        "    token: acme\n    default_category: software-engineering\n")
    monkeypatch.setitem(
        ingest._FETCHERS, "greenhouse",
        lambda token: [RawJob("SWE Intern", "https://other.example/9", "Austin, TX", None)])
    sync(tmp_path, today=TODAY)
    reloaded = {l.id: l for l in load_all(tmp_path).listings}
    assert reloaded["acme-swe-intern-2027"].notes == "hand-curated"
    assert str(reloaded["acme-swe-intern-2027"].apply_url) == "https://example.com/jobs/123"
