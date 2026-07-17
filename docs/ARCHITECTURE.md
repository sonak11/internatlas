# Architecture

InternAtlas is a **git-native data platform**. The repository itself is the database;
GitHub Actions is the compute layer; generated Markdown is the read-optimized view layer.

```
┌─────────────────────────────────────────────────────────────────┐
│                        WRITE PATH                               │
│  Contributor PR ──► data/internships/<company>/<slug>.json      │
│                        │                                        │
│                        ▼                                        │
│        CI: schema validation ► duplicate detection ► lint       │
└─────────────────────────────────────────────────────────────────┘
                             │  merge to main
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BUILD PATH (GitHub Actions)              │
│  internatlas generate                                           │
│    ├── README.md            (top-level tables + badges)         │
│    ├── generated/companies/ (one page per company)              │
│    ├── generated/categories/(one page per category)             │
│    ├── generated/stats/     (analytics, leaderboards)           │
│    ├── generated/indexes/   (visa, remote, timeline, deadlines) │
│    └── exports/             (csv, json, ics, rss, digest)       │
└─────────────────────────────────────────────────────────────────┘
                             │  bot commit
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        READ PATH                                │
│  Students browse README / pages, or run the CLI:                │
│    python -m internatlas search --category quant --visa yes     │
└─────────────────────────────────────────────────────────────────┘
```

## Design principles

1. **One listing = one JSON file.** `data/internships/<company>/<slug>.json`.
   - Merge conflicts become nearly impossible (contributors touch different files).
   - Git history *is* the audit log for every listing.
   - Scales linearly to 10,000+ files; the loader streams the tree.
2. **Humans write JSON, machines write Markdown.** Nothing in `README.md` or
   `generated/` is hand-edited — CI regenerates all of it on every merge.
   A guard workflow fails PRs that hand-edit generated files.
3. **Schema as code.** `src/internatlas/models.py` (Pydantic v2) is the single
   source of truth. `schemas/internship.schema.json` is *exported from it*, so
   editor autocompletion, CI validation, and Python code can never drift apart.
4. **Controlled vocabularies.** Categories, work modes, statuses, and seasons are
   enums. Free text is confined to fields like `notes` — everything filterable is typed.
5. **Deterministic builds.** Generators sort all output; running the pipeline twice
   produces byte-identical files, so bot commits are clean diffs.
6. **Lifecycle, not deletion.** Closed listings move to `archive/` with status
   `closed`, preserving hiring-history analytics forever.

## Package layout

```
src/internatlas/
├── models.py        # Pydantic models + enums (source of truth)
├── loader.py        # stream/load listings from the data tree
├── validate.py      # schema + business-rule validation
├── dedupe.py        # duplicate detection (URL canon + fuzzy title match)
├── linkcheck.py     # dead-link checker with retry/backoff
├── stats.py         # pure analytics functions (no I/O)
├── search.py        # CLI search engine
├── generate/        # markdown/view generators (readme, companies, categories, indexes)
├── exports/         # csv, json, ics calendar, rss, weekly digest
└── cli.py           # `python -m internatlas <command>` entry point
```

Generators depend on `loader` + `stats` only. Analytics functions are pure
(listings in → dataclasses out) so they are trivially unit-testable.

## Why no database?

- Zero hosting cost, zero ops, infinite free reads via GitHub's CDN.
- Every change is reviewed (PR), attributed (commit), and reversible (revert).
- Contributors need no credentials — just a fork.
- 10k JSON files ≈ 20 MB. Git and the loader handle this comfortably; if it ever
  doesn't, `loader.py` is the single seam where a SQLite build cache would slot in.
