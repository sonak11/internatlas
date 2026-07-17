# Contributing to InternAtlas

Thanks for helping students find internships! Every contribution — a new
listing, a corrected deadline, a dead-link report — makes the map better.

> **Most listings arrive automatically.** An hourly GitHub Action pulls live
> postings from company ATS boards and community feeds (see
> [SOURCES.md](SOURCES.md)). Auto-ingested files are tagged `auto-ingested` and
> are managed by the sync — the best way to add coverage in bulk is to add a
> company's board token to [`automation/sources.yaml`](automation/sources.yaml).
> Hand-curated listings you add below are **never** touched by the sync.

## Add a listing (~2 minutes)

1. **Fork** the repo.
2. **Copy** [`templates/listing-template.json`](templates/listing-template.json) to
   `data/internships/<company-slug>/<id>.json` where:
   - `<company-slug>` is lowercase kebab-case, e.g. `jane-street`
   - `<id>` is `<company-slug>-<role-slug>-<year>`, e.g. `jane-street-swe-intern-2027`
   - The filename must be `<id>.json`
3. **Fill in what you know.** Only these fields are required:
   `id`, `company.name`, `company.slug`, `role`, `category`, `apply_url`,
   `work_mode`, `year`, `dates.discovered`, and at least one location for
   non-remote roles. Everything else is optional — partial data beats no data.
4. **Validate locally** (optional; CI runs it anyway):
   ```bash
   pip install -e . && internatlas validate
   ```
   Or scaffold interactively: `internatlas new`
5. **Open a PR.** CI validates the schema, checks for duplicates, and — once
   merged — regenerates every page automatically.

## Update or close a listing

- Wrong info? Edit the JSON and bump `dates.last_verified`.
- Posting closed? Set `"status": "closed"` — a maintainer will move the file to
  `archive/`, which keeps it powering the company's hiring-history page.
- Dead link? Open an issue with the **listing report** template if you can't PR.

## Ground rules for data

- **Public information only.** Link official postings/career pages. Never add
  personal contact details that aren't publicly listed by the company for
  recruiting purposes.
- **No speculation as fact.** If pay is unconfirmed, leave it out — don't guess.
- **One listing per role per year.** Different offices of the same posting are
  one listing with multiple `locations`.

## What you must NOT edit

`README.md` and everything under `generated/` are machine-owned; CI will reject
PRs that touch them. Edit the JSON (or `docs/README.template.md` for prose) instead.

## Code contributions

- Source lives in `src/internatlas/`; read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) first.
- Type hints everywhere, `ruff` clean, tests for new behavior (`pytest -q`).
- Schema changes: edit `models.py`, run `internatlas schema`, commit both, and
  bump `SCHEMA_VERSION` for breaking changes.

## Field vocabulary quick reference

See [`docs/SCHEMA.md`](docs/SCHEMA.md) for every field, or let your editor
autocomplete via the JSON Schema: the template already includes a `$schema` key.
