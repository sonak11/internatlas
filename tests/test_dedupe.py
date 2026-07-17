from conftest import make_listing
from internatlas.dedupe import canonicalize_url, find_duplicates, role_similarity


def test_url_canonicalization():
    a = canonicalize_url("https://www.example.com/jobs/123/?utm_source=x&ref=y")
    b = canonicalize_url("http://example.com/jobs/123")
    assert a == b


def test_url_duplicate_detected():
    a = make_listing()
    b = make_listing(id="acme-backend-intern-2027", role="Backend Intern",
                     apply_url="https://example.com/jobs/123?utm_source=linkedin")
    dups = find_duplicates([a, b])
    assert any(d.kind == "url" for d in dups)


def test_fuzzy_role_duplicate():
    a = make_listing()
    b = make_listing(id="acme-software-engineer-intern-2027",
                     role="Software Engineer Intern",
                     apply_url="https://example.com/jobs/999")
    assert any(d.kind == "fuzzy-role" for d in find_duplicates([a, b]))


def test_distinct_roles_not_flagged():
    a = make_listing()
    b = make_listing(id="acme-hardware-intern-2027", role="Hardware Verification Intern",
                     apply_url="https://example.com/jobs/777")
    assert find_duplicates([a, b]) == []


def test_role_similarity_ignores_boilerplate():
    assert role_similarity("Summer 2027 SWE Internship", "SWE Intern") == 1.0
