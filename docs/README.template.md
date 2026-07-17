<div align="center">

# 🗺️ InternAtlas

### The open-source data platform for Summer 2027 internships

Not another markdown table. Every listing is structured JSON — **synced every
hour** from company ATS boards and community feeds, validated by CI,
deduplicated automatically, and rendered right here in the README. Each role
links **straight to the live application page**, with its posting date shown.

{{BADGES}}

[**Browse by category**](#-browse-by-category) ·
[**Deadline timeline**](generated/indexes/timeline.md) ·
[**Visa sponsors**](generated/indexes/visa-sponsorship.md) ·
[**Remote roles**](generated/indexes/remote.md) ·
[**Stats**](generated/stats/README.md) ·
[**Add a listing**](CONTRIBUTING.md)

</div>

---

{{DEADLINE_ALERT}}

## 📈 At a glance

{{QUICK_STATS}}

## 🧭 Browse by category

{{CATEGORY_NAV}}

**More views:**
[🌍 Visa sponsorship](generated/indexes/visa-sponsorship.md) ·
[🛂 International students](generated/indexes/international-students.md) ·
[🏠 Remote](generated/indexes/remote.md) ·
[🐣 Freshman-friendly](generated/indexes/freshman.md) ·
[🌱 Sophomore-friendly](generated/indexes/sophomore.md) ·
[🎓 Masters](generated/indexes/masters.md) ·
[🔬 PhD](generated/indexes/phd.md) ·
[🏢 All companies](generated/indexes/companies.md) ·
[📅 Timeline](generated/indexes/timeline.md)

## ⚡ Why this repo is different

| Typical internship repo | InternAtlas |
|---|---|
| Hand-edited markdown table | **Structured JSON, one file per listing** |
| Updated when someone remembers | **Auto-synced every hour** via GitHub Actions |
| Links to generic careers pages | **Direct links to the live posting**, with posting dates |
| Merge conflicts on every PR | Conflict-free — contributors touch different files |
| Company + link + location | **40+ fields**: pay, visa, eligibility, interview process, tech stack |
| Links rot silently | **Scheduled dead-link checker** flags stale postings |
| No filtering | **CLI search**, category pages, visa/remote/level indexes |
| No history | Closed roles are **archived**, powering hiring-history pages |
| No exports | **CSV · JSON · .ics calendar · RSS · weekly digest** |

## 🔎 Search from your terminal

```bash
git clone <this-repo> && cd <this-repo>
pip install -e .

internatlas search --category quant --visa yes
internatlas search --remote --min-pay 50
internatlas search --level sophomore --grad-year 2029
internatlas search --company stripe --json
```

## 📅 Never miss a deadline

- **Calendar** — import [`generated/exports/deadlines.ics`](generated/exports/deadlines.ics) into Google/Apple Calendar. Every deadline becomes an all-day event.
- **RSS** — subscribe to [`generated/exports/feed.xml`](generated/exports/feed.xml) for new listings.
- **Weekly digest** — [`generated/exports/digest.md`](generated/exports/digest.md), rebuilt every Monday.
- **Spreadsheet** — point Google Sheets `IMPORTDATA()` at the raw URL of [`generated/exports/internships.csv`](generated/exports/internships.csv).

## 🎒 Application toolkit

Tracker templates to organize your own search — copy into your fork or a spreadsheet:

- [Application tracker](templates/application-tracker.md)
- [Interview tracker](templates/interview-tracker.md)
- [Offer tracker](templates/offer-tracker.md)
- [Resume version tracker](templates/resume-tracker.md)

## ☀️ Summer 2027 internships ({{LISTING_COUNT}})

Every Summer 2027 listing, right here — grouped by category, **open roles and
newest postings first**. The **Posted** column shows each role's official
posting date; a `*` means the date shown is when the sync first discovered it
(the upstream source didn't expose a posting date). Every **Role** link goes
straight to the live application page.

{{LISTINGS_BY_CATEGORY}}

## 🗓 Other open terms ({{OFFSEASON_COUNT}})

Live postings the sync found for **other terms** — Fall 2026, Winter 2027,
Spring 2027 co-ops and off-cycle internships. These are real, currently-open
roles; they're just not Summer 2027, so they live in their own section to keep
the headline list clean.

<details>
<summary><b>Show other open terms ({{OFFSEASON_COUNT}})</b></summary>

{{OFFSEASON_LISTINGS}}

</details>

## 🔗 Where this data comes from

Listings are pulled automatically every hour. Direct company ATS boards
(Greenhouse, Lever, Ashby) are the primary source; community-maintained feeds
fill in companies whose systems have no public API. Full provenance,
per-listing source tags, and a removal-on-request process are in
[SOURCES.md](SOURCES.md).

{{DATA_SOURCES}}

> Every listing links to the live posting and carries a `last_verified` date.
> Roles that disappear upstream are automatically marked 🔴 Closed on the next
> hourly run. The company's official page is always the source of truth — if
> you spot something off, [PR a correction](CONTRIBUTING.md)!

## 🤝 Contributing

Adding a listing takes ~2 minutes:

1. Copy [`templates/listing-template.json`](templates/listing-template.json) to
   `data/internships/<company-slug>/<id>.json`
2. Fill in what you know — most fields are optional
3. Run `internatlas validate` (CI runs it too)
4. Open a PR 🎉

Full guide: [CONTRIBUTING.md](CONTRIBUTING.md) · Schema reference: [docs/SCHEMA.md](docs/SCHEMA.md)

## 🗺 Roadmap

- [x] Structured data model + CI validation
- [x] Auto-generated README, company, category, index & stats pages
- [x] CLI search · CSV/JSON/ICS/RSS exports · weekly digest
- [x] Hourly auto-sync from ATS boards (Greenhouse/Lever/Ashby) + community feeds
- [ ] GitHub Pages site with client-side search
- [ ] Historical salary trends across seasons
- [ ] Browser extension: "Add to InternAtlas" from any posting

## ❓ FAQ

<details>
<summary><b>How accurate is the data?</b></summary>
Every listing carries a <code>last_verified</code> date and a status badge. CI
link-checks postings on a schedule, but the source of truth is always the
company's official page — treat this repo as a map, not the territory.
</details>

<details>
<summary><b>Why JSON instead of a simple table?</b></summary>
Structure is what enables everything else: filtering, dedup detection, salary
stats, calendar exports, and pages that regenerate themselves. Markdown tables
can't do any of that.
</details>

<details>
<summary><b>Can I use this data in my own project?</b></summary>
The InternAtlas <i>code</i> is MIT licensed.
<code>generated/exports/internships.json</code> is a stable machine-readable
snapshot rebuilt on every sync. The <i>listing data</i> is aggregated factual
job-posting information from company ATS boards and community feeds — see
<a href="SOURCES.md">SOURCES.md</a> for provenance and attribution before you
redistribute it.
</details>

<details>
<summary><b>A listing is wrong/dead. What do I do?</b></summary>
Open a PR editing the JSON file (set <code>status</code> to <code>closed</code>
to archive it), or open an issue with the <i>listing-report</i> template.
</details>

---

<div align="center">
<sub>⭐ Star the repo to bookmark it — and to help other students find it.</sub>
</div>
