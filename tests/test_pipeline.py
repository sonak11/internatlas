"""End-to-end: write listings to a temp repo, validate, generate, export."""
from datetime import date
from pathlib import Path

from conftest import make_listing
from internatlas.exports import to_csv, to_ics, to_rss, weekly_digest, write_all
from internatlas.loader import load_all, write_listing
from internatlas.models import ApplicationStatus, Dates
from internatlas.validate import validate_repo


def _repo(tmp_path: Path) -> Path:
    write_listing(tmp_path, make_listing())
    write_listing(tmp_path, make_listing(
        id="acme-quant-intern-2027", role="Quant Intern",
        apply_url="https://example.com/jobs/2",
        status=ApplicationStatus.OPEN,
        dates=Dates(discovered=date(2026, 7, 1), deadline=date(2026, 9, 15)),
    ))
    return tmp_path


def test_load_write_roundtrip(tmp_path):
    _repo(tmp_path)
    result = load_all(tmp_path)
    assert result.ok and len(result.listings) == 2


def test_validate_repo_clean(tmp_path):
    _repo(tmp_path)
    result, problems = validate_repo(tmp_path)
    assert result.ok and problems == []


def test_validate_catches_bad_json(tmp_path):
    _repo(tmp_path)
    bad = tmp_path / "data/internships/acme/acme-broken-2027.json"
    bad.write_text("{not json", encoding="utf-8")
    result, _ = validate_repo(tmp_path)
    assert not result.ok


def test_exports(tmp_path):
    listings = load_all(_repo(tmp_path)).listings
    csv_text = to_csv(listings)
    assert csv_text.splitlines()[0].startswith("id,company,role")
    assert "acme-quant-intern-2027" in csv_text
    ics = to_ics(listings)
    assert "BEGIN:VEVENT" in ics and "20260915" in ics
    rss = to_rss(listings)
    assert "<rss" in rss and "Quant Intern" in rss
    digest = weekly_digest(listings, today=date(2026, 7, 2))
    assert "Weekly Digest" in digest
    files = write_all(tmp_path, listings)
    assert all(f.exists() for f in files)
