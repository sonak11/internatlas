<!-- ⚠️ AUTO-GENERATED FILE — do not edit by hand.
     Edit JSON in data/internships/ and run `python -m internatlas generate`. -->
<div align="center">

# 🗺️ InternAtlas

### The open-source data platform for Summer 2027 internships

Not another markdown table. Every listing is structured JSON — validated by CI,
deduplicated automatically, rendered into browsable pages, and exportable to
CSV, calendars, and RSS.

![internships](https://img.shields.io/badge/internships-12-blue?style=for-the-badge) ![open now](https://img.shields.io/badge/open%20now-0-brightgreen?style=for-the-badge) ![companies](https://img.shields.io/badge/companies-11-purple?style=for-the-badge) ![visa sponsors](https://img.shields.io/badge/visa%20sponsors-8-orange?style=for-the-badge) ![remote roles](https://img.shields.io/badge/remote%20roles-1-teal?style=for-the-badge) ![updated](https://img.shields.io/badge/updated-2026--07--17-lightgrey?style=for-the-badge)

[**Browse by category**](#-browse-by-category) ·
[**Deadline timeline**](generated/indexes/timeline.md) ·
[**Visa sponsors**](generated/indexes/visa-sponsorship.md) ·
[**Remote roles**](generated/indexes/remote.md) ·
[**Stats**](generated/stats/README.md) ·
[**Add a listing**](CONTRIBUTING.md)

</div>

---



## 📈 At a glance

| Metric | Value |
|---|---|
| Total tracked | **12** |
| Currently open | **0** |
| Companies | **11** |
| Average hourly (reported) | **$110.00** |
| Median hourly (reported) | **$110.00** |
| Most requested languages | Python, C++, Java |

## 🧭 Browse by category

| [💻 Software Engineering](generated/categories/software-engineering.md) | [🧠 Machine Learning](generated/categories/machine-learning.md) | [🤖 AI](generated/categories/ai.md) | [📊 Data Science](generated/categories/data-science.md) | [🛠 Data Engineering](generated/categories/data-engineering.md) |
|---|---|---|---|---|
| [📈 Quant](generated/categories/quant.md) | [🔩 Hardware](generated/categories/hardware.md) | [⚙️ Embedded](generated/categories/embedded.md) | [🔐 Security](generated/categories/security.md) | [☁️ Cloud](generated/categories/cloud.md) |
| [🧭 Product](generated/categories/product.md) | [🎨 Design](generated/categories/design.md) | [🔬 Research](generated/categories/research.md) | [💰 Finance](generated/categories/finance.md) | [🤝 Consulting](generated/categories/consulting.md) |

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

## 📋 All tracked internships (12)

<details>
<summary><b>Click to expand the full table</b></summary>

| Company | Role | Location | Mode | Pay | Visa | Deadline | Status |
|---|---|---|---|---|---|---|---|
| [Capital One](generated/companies/capital-one.md) | [Data Science Intern](https://www.capitalonecareers.com/students-and-grads) | McLean, VA | Hybrid | — | ❌ | Rolling | ⚪ Unverified |
| [Citadel](generated/companies/citadel.md) | [Software Engineering Intern](https://www.citadel.com/careers/open-opportunities/students/) | Chicago, IL +1 | Onsite | $95–120/hr | ✅ | Rolling | ⚪ Unverified |
| [Cloudflare](generated/companies/cloudflare.md) | [Security Engineering Intern](https://www.cloudflare.com/careers/early-talent/) | Remote | Remote | — | 🔶 | Rolling | ⚪ Unverified |
| [Databricks](generated/companies/databricks.md) | [Software Engineering Intern — Data Platform](https://www.databricks.com/company/careers/university-recruiting) | San Francisco, CA | Onsite | — | ✅ | Rolling | ⚪ Unverified |
| [Google](generated/companies/google.md) | [Software Engineering Intern](https://www.google.com/about/careers/applications/jobs/results/?q=software%20engineering%20intern) | Mountain View, CA +1 | Onsite | — | ✅ | Rolling | ⚪ Unverified |
| [Google](generated/companies/google.md) | [STEP Intern (First & Second Year)](https://www.google.com/about/careers/applications/jobs/results/?q=step%20intern) | Mountain View, CA | Onsite | — | ✅ | Rolling | ⚪ Unverified |
| [Jane Street](generated/companies/jane-street.md) | [Quantitative Trading Intern](https://www.janestreet.com/join-jane-street/open-roles/) | New York, NY | Onsite | $100–125/hr | ✅ | Rolling | ⚪ Unverified |
| [Lockheed Martin](generated/companies/lockheed-martin.md) | [Embedded Software Intern](https://www.lockheedmartinjobs.com/students-early-careers) | Fort Worth, TX | Onsite | — | ❌ | Rolling | ⚪ Unverified |
| [Microsoft](generated/companies/microsoft.md) | [Explore Intern (First & Second Year)](https://careers.microsoft.com/v2/global/en/students) | Redmond, WA | Onsite | — | ✅ | Rolling | ⚪ Unverified |
| [NVIDIA](generated/companies/nvidia.md) | [Machine Learning Intern](https://www.nvidia.com/en-us/about-nvidia/careers/university-recruiting/) | Santa Clara, CA | Hybrid | — | ✅ | Rolling | ⚪ Unverified |
| [OpenAI](generated/companies/openai.md) | [Research Intern](https://openai.com/careers/) | San Francisco, CA | Onsite | — | ✅ | Rolling | ⚪ Unverified |
| [Stripe](generated/companies/stripe.md) | [Software Engineering Intern](https://stripe.com/jobs/university) | South San Francisco, CA +1 | Hybrid | — | ✅ | Rolling | ⚪ Unverified |

</details>

> Data is community-maintained. Listings marked ⚪ Unverified haven't been
> confirmed recently — always check the official posting, and PR corrections!

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
