<div align="center">

# 🗺️ InternAtlas

### The open-source data platform for Summer 2027 internships

Not another markdown table. Every listing is structured JSON — validated by CI,
deduplicated automatically, rendered into browsable pages, and exportable to
CSV, calendars, and RSS.

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

## 📋 All internships ({{LISTING_COUNT}})

Everything, right here — grouped by category, open roles and earliest deadlines
first. Dates marked `*` are the date we discovered the listing (official posting
date unknown).

{{LISTINGS_BY_CATEGORY}}

> Data is community-maintained and refreshed **every hour** by the sync
> pipeline. Listings marked ⚪ Unverified point at the company's official
> careers portal and haven't been individually confirmed — always verify on the
> official page, and PR corrections!

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
- [ ] GitHub Pages site with client-side search
- [ ] Historical salary trends across seasons
- [ ] Auto-ingest suggestions from ATS boards (Greenhouse/Lever) as draft PRs
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
Yes — it's MIT licensed. <code>generated/exports/internships.json</code> is a
stable machine-readable snapshot rebuilt on every merge.
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
