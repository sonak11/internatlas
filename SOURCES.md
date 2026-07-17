# Data sources & attribution

InternAtlas aggregates **factual job-posting information** — company, role,
location, posting date, and the direct application URL — that companies publish
themselves. Nothing here is scraped from behind a login, and no descriptions,
prose, or proprietary content is copied. The listing data is refreshed
automatically every hour by `internatlas sync`.

Every auto-ingested listing carries a `src:<label>` tag recording where the
sync found it, so provenance is always visible in the JSON and in the README's
["Where this data comes from"](README.md#-where-this-data-comes-from) table.

## Primary source — company ATS boards

The sync's first-class source is each company's own applicant-tracking system,
queried through its public, keyless JSON API:

| ATS | Endpoint | Tag |
|---|---|---|
| Greenhouse | `https://boards-api.greenhouse.io/v1/boards/<token>/jobs` | `src:ats` |
| Lever | `https://api.lever.co/v0/postings/<token>?mode=json` | `src:ats` |
| Ashby | `https://api.ashbyhq.com/posting-api/job-board/<token>` | `src:ats` |

These are the same endpoints that power the companies' own careers pages, so an
ATS-sourced listing links straight to the live posting and closes automatically
when the company takes it down. Boards are declared in
[`automation/sources.yaml`](automation/sources.yaml).

## Secondary sources — community feeds

Many large employers use systems with no public API (Workday, Taleo, in-house
portals). To cover them, the sync also reads the structured `listings.json`
files published by community-maintained internship repositories. **Thank you to
their maintainers and contributors** — this project would have far thinner
coverage without their work.

| Feed | Repository | Tag |
|---|---|---|
| SimplifyJobs / Summer Internships | https://github.com/SimplifyJobs/Summer2026-Internships | `src:simplify` |
| vanshb03 / Summer 2027 Internships | https://github.com/vanshb03/Summer2027-Internships | `src:vanshb03` |

Only entries a feed marks **active and visible** are ingested; the sync
normalizes them into the InternAtlas schema, keeps the feed's direct
application URL, and tags each one with the feed's label. Live per-feed counts
are shown in the README.

### How feed data is treated

- **Factual data only.** We ingest company, title, location, posting timestamp,
  sponsorship flag, and the application URL — the factual coordinates of a job
  opening, not anyone's editorial content.
- **Attribution, always.** Each feed is credited by name with a link in this
  file and in the README, and every listing keeps its `src:` tag.
- **No re-hosting of prose.** We don't copy descriptions or any written content
  from the feeds or the postings.

If you maintain one of these feeds and would like the attribution changed, or
would prefer InternAtlas not read your feed at all, please see *Removal &
corrections* below — we'll act on it promptly. If you'd like your project
**added**, a PR editing `automation/sources.yaml` is very welcome.

## Removal & corrections

- **A specific listing is wrong, stale, or shouldn't be here** — open a PR
  editing (or deleting) the JSON file under `data/internships/`, or open an
  issue with the *listing-report* template. The next hourly sync also closes
  anything that has vanished upstream.
- **You're a source maintainer and want your feed removed** — open an issue or
  PR removing the entry from `automation/sources.yaml`; we'll merge it quickly.
  Ping the maintainer in the issue if you'd like a faster response.
- **You're an employer** and want a posting delisted here — note that the live
  posting lives on your own ATS; removing it there makes it drop out of
  InternAtlas automatically on the next sync. We're also happy to remove it by
  request in the meantime.

## A note on accuracy

InternAtlas is a **map, not the territory**. Postings change and close
constantly. Every listing links to the official application page and carries a
`last_verified` date — always confirm details on the company's own page before
applying.
