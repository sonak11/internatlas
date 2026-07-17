"""Duplicate detection.

Two independent signals:

1. **Canonical apply-URL collision** — the same posting submitted twice with
   cosmetically different URLs (tracking params, trailing slashes, http/https).
2. **Fuzzy role match** — same company + same year + role titles whose
   normalized token similarity exceeds a threshold.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .models import Internship

_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gh_src", "lever-source", "ref", "src", "source", "referrer", "trk",
}

_ROLE_STOPWORDS = {
    "intern", "internship", "summer", "2026", "2027", "2028",
    "co-op", "coop", "program", "the", "a", "an", "of", "and", "-",
}


def canonicalize_url(url: str) -> str:
    """Normalize a URL so cosmetic variants compare equal."""
    parts = urlsplit(url.strip())
    netloc = parts.netloc.lower().removeprefix("www.")
    path = re.sub(r"/{2,}", "/", parts.path).rstrip("/")
    query = urlencode(
        sorted((k, v) for k, v in parse_qsl(parts.query) if k.lower() not in _TRACKING_PARAMS)
    )
    return urlunsplit(("https", netloc, path, query, ""))


def _stem(token: str) -> str:
    """Very light stemming so 'engineer'/'engineering' and plurals compare equal."""
    changed = True
    while changed:
        changed = False
        for suffix in ("ing", "ers", "er", "s"):
            if token.endswith(suffix) and len(token) - len(suffix) >= 4:
                token = token[: -len(suffix)]
                changed = True
                break
    return token


def _role_tokens(role: str) -> frozenset[str]:
    tokens = re.findall(r"[a-z0-9+#]+", role.lower())
    return frozenset(_stem(t) for t in tokens if t not in _ROLE_STOPWORDS)


def role_similarity(a: str, b: str) -> float:
    """Jaccard similarity of meaningful role tokens, in [0, 1]."""
    ta, tb = _role_tokens(a), _role_tokens(b)
    if not ta or not tb:
        return 1.0 if ta == tb else 0.0
    return len(ta & tb) / len(ta | tb)


@dataclass(frozen=True)
class Duplicate:
    kind: str            # "url" | "fuzzy-role"
    left_id: str
    right_id: str
    detail: str

    def __str__(self) -> str:
        return f"possible duplicate ({self.kind}): {self.left_id} ↔ {self.right_id} — {self.detail}"


def find_duplicates(listings: list[Internship], fuzzy_threshold: float = 0.85) -> list[Duplicate]:
    duplicates: list[Duplicate] = []

    by_url: dict[str, Internship] = {}
    for listing in listings:
        canon = canonicalize_url(str(listing.apply_url))
        if (other := by_url.get(canon)) is not None and other.id != listing.id:
            duplicates.append(Duplicate("url", other.id, listing.id, f"both point at {canon}"))
        else:
            by_url[canon] = listing

    by_company_year: dict[tuple[str, int], list[Internship]] = {}
    for listing in listings:
        by_company_year.setdefault((listing.company.slug, listing.year), []).append(listing)

    for group in by_company_year.values():
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                if a.category != b.category:
                    continue
                sim = role_similarity(a.role, b.role)
                if sim >= fuzzy_threshold:
                    duplicates.append(
                        Duplicate("fuzzy-role", a.id, b.id,
                                  f"role titles are {sim:.0%} similar "
                                  f"({a.role!r} vs {b.role!r})")
                    )
    return duplicates
