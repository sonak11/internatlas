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


# ── community-feed ingestion ─────────────────────────────────────────────────

from internatlas.ingest import (Feed, map_feed_entry, parse_locations,
                                 resolve_term, clean_url, reconcile_batch)
from internatlas.models import Season, VisaSponsorship, DegreeLevel

SIMPLIFY = Feed(label="simplify", name="Simplify", url="http://x", homepage="http://h",
                terms=("Summer 2027", "Fall 2026", "Winter 2027", "Spring 2027"))
VANSH = Feed(label="vanshb03", name="vansh", url="http://x", homepage="http://h",
             season_years={"summer": 2027, "fall": 2026, "winter": 2027, "spring": 2027})


def _entry(**kw):
    base = dict(title="Software Engineer Intern", url="https://job-boards.greenhouse.io/acme/jobs/1",
                company_name="Acme", locations=["New York, NY"], active=True, is_visible=True,
                sponsorship="Other", date_posted=1750000000)
    base.update(kw)
    return base


def test_feed_terms_filter_via_terms_list():
    # Simplify entries carry an explicit terms[] list; only allow-listed pass.
    assert map_feed_entry(_entry(terms=["Summer 2027"]), SIMPLIFY, TODAY).year == 2027
    assert map_feed_entry(_entry(terms=["Summer 2026"]), SIMPLIFY, TODAY) is None
    assert map_feed_entry(_entry(terms=["Fall 2026"]), SIMPLIFY, TODAY).season is Season.FALL


def test_feed_season_year_fallback():
    # vansh entries have no terms[]; season maps to a year.
    l = map_feed_entry(_entry(season="Summer"), VANSH, TODAY)
    assert l.season is Season.SUMMER and l.year == 2027
    l2 = map_feed_entry(_entry(season="Fall"), VANSH, TODAY)
    assert l2.season is Season.FALL and l2.year == 2026


def test_feed_sponsorship_mapping():
    yes = map_feed_entry(_entry(terms=["Summer 2027"], sponsorship="Offers Sponsorship"), SIMPLIFY, TODAY)
    assert yes.eligibility.visa_sponsorship is VisaSponsorship.YES
    cit = map_feed_entry(_entry(terms=["Summer 2027"], sponsorship="U.S. Citizenship is Required"), SIMPLIFY, TODAY)
    assert cit.eligibility.visa_sponsorship is VisaSponsorship.NO
    assert cit.eligibility.citizenship_required is True


def test_feed_degrees_mapping():
    l = map_feed_entry(_entry(terms=["Summer 2027"], degrees=["Master's", "PhD", "Bachelor's"]), SIMPLIFY, TODAY)
    assert DegreeLevel.MASTERS in l.eligibility.degree_levels
    assert DegreeLevel.PHD in l.eligibility.degree_levels


def test_feed_remote_and_mixed_locations():
    remote = map_feed_entry(_entry(terms=["Summer 2027"], locations=["Remote"]), SIMPLIFY, TODAY)
    assert remote.work_mode is WorkMode.REMOTE and remote.locations == []
    mixed = map_feed_entry(_entry(terms=["Summer 2027"], locations=["Remote", "Austin, TX"]), SIMPLIFY, TODAY)
    assert mixed.work_mode is WorkMode.ONSITE
    assert "remote-available" in mixed.tags


def test_feed_international_location():
    mode, locs, _ = parse_locations(["London, UK"], "USA")
    assert mode is WorkMode.ONSITE
    assert locs[0].city == "London" and locs[0].country == "UK"


def test_feed_url_is_cleaned_of_tracking():
    dirty = "https://job-boards.greenhouse.io/acme/jobs/1?utm_source=x&gh_jid=99&ref=abc"
    l = map_feed_entry(_entry(terms=["Summer 2027"], url=dirty), SIMPLIFY, TODAY)
    s = str(l.apply_url)
    assert "gh_jid=99" in s and "utm_source" not in s and "ref=abc" not in s


def test_feed_src_tag_present():
    l = map_feed_entry(_entry(terms=["Summer 2027"]), SIMPLIFY, TODAY)
    assert "src:simplify" in l.tags and AUTO_TAG in l.tags


def test_feed_skips_non_intern_and_bad_rows():
    assert map_feed_entry(_entry(terms=["Summer 2027"], title="Staff Engineer"), SIMPLIFY, TODAY) is None
    assert map_feed_entry(_entry(terms=["Summer 2027"], url="not-a-url"), SIMPLIFY, TODAY) is None
    assert map_feed_entry(_entry(terms=["Summer 2027"], company_name=""), SIMPLIFY, TODAY) is None


def test_reconcile_collapses_same_url_different_id():
    # Same posting under two company spellings + www/trailing-slash variance.
    a = map_feed_entry(_entry(terms=["Summer 2027"], company_name="Tower Research",
                              url="https://tower.com/jobs/?gh_jid=5"), SIMPLIFY, TODAY)
    b = map_feed_entry(_entry(terms=["Summer 2027"], company_name="Tower Research Capital",
                              url="https://www.tower.com/jobs?gh_jid=5"), SIMPLIFY, TODAY)
    assert a.id != b.id
    resolved = reconcile_batch([a, b])
    assert len(resolved) == 1                      # collapsed to one
    # Deterministic winner: lexicographically-smallest id.
    assert min(a.id, b.id) in resolved


def test_reconcile_is_order_independent():
    a = map_feed_entry(_entry(terms=["Summer 2027"], company_name="Tower Research",
                              url="https://tower.com/jobs/?gh_jid=5"), SIMPLIFY, TODAY)
    b = map_feed_entry(_entry(terms=["Summer 2027"], company_name="Tower Research Capital",
                              url="https://www.tower.com/jobs?gh_jid=5"), SIMPLIFY, TODAY)
    r1 = set(reconcile_batch([a, b]))
    # rebuild fresh objects (reconcile mutates ids) for the reversed run
    a2 = map_feed_entry(_entry(terms=["Summer 2027"], company_name="Tower Research",
                               url="https://tower.com/jobs/?gh_jid=5"), SIMPLIFY, TODAY)
    b2 = map_feed_entry(_entry(terms=["Summer 2027"], company_name="Tower Research Capital",
                               url="https://www.tower.com/jobs?gh_jid=5"), SIMPLIFY, TODAY)
    r2 = set(reconcile_batch([b2, a2]))
    assert r1 == r2


def test_sync_feeds_via_monkeypatched_fetcher(tmp_path, monkeypatch):
    (tmp_path / "automation").mkdir()
    (tmp_path / "automation/sources.yaml").write_text(
        "feeds:\n  - label: simplify\n    name: S\n    homepage: http://h\n"
        "    url: http://x\n    terms: ['Summer 2027']\n")
    entries = [
        _entry(terms=["Summer 2027"], url="https://a.co/1", title="SWE Intern", company_name="Acme"),
        _entry(terms=["Summer 2027"], url="https://b.co/2", title="ML Intern", company_name="Beta"),
        _entry(terms=["Summer 2026"], url="https://c.co/3", title="SWE Intern", company_name="Gamma"),  # filtered
    ]
    monkeypatch.setattr(ingest, "_FEED_FETCHER", lambda url: entries)
    c = sync(tmp_path, today=TODAY, only="feeds")
    assert c["created"] == 2 and c["errors"] == 0
    ids = {l.id for l in load_all(tmp_path).listings}
    assert any(i.startswith("acme-") for i in ids)
    assert not any(i.startswith("gamma-") for i in ids)   # Summer 2026 excluded
