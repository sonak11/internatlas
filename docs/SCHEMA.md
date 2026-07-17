# Listing Schema Reference

One internship = one JSON file at `data/internships/<company-slug>/<id>.json`.
The machine-readable schema is [`schemas/internship.schema.json`](../schemas/internship.schema.json)
(auto-exported from `src/internatlas/models.py` — the Pydantic models are canonical).

## Required fields

| Field | Type | Notes |
|---|---|---|
| `id` | slug | `<company-slug>-<role-slug>-<year>`; must match filename |
| `company.name` | string | Display name |
| `company.slug` | slug | Directory name; kebab-case |
| `role` | string | Official role title |
| `category` | enum | `software-engineering`, `machine-learning`, `ai`, `data-science`, `data-engineering`, `quant`, `hardware`, `embedded`, `security`, `cloud`, `product`, `design`, `research`, `finance`, `consulting` |
| `apply_url` | URL | Direct application link |
| `work_mode` | enum | `remote` \| `hybrid` \| `onsite` |
| `year` | int | Internship year (e.g. 2027) |
| `dates.discovered` | date | When the listing was added here |
| `locations[]` | list | Required unless `work_mode: remote`; each has `country` (required), `city`, `state` |

## Optional fields (add what you know)

- **Role context** — `subcategory`, `team`, `department`, `business_unit`, `season`, `length_weeks`, `tags`, `notes`, `recruiting_timeline`
- **Company** — `company.career_page`, `company.size` (`startup`/`small`/`mid`/`large`/`enterprise`), `company.industry`, `company.company_type` (`public`/`private`/`nonprofit`/`government`), `company.fortune_500`
- **Compensation** — `compensation.hourly_min`, `hourly_max`, `monthly`, `currency`, `housing_stipend`, `relocation_assistance`
- **Eligibility** — `eligibility.graduation_years`, `degree_levels` (`freshman`…`phd`), `min_gpa`, `citizenship_required`, `security_clearance_required`, `visa_sponsorship` (`yes`/`no`/`case-by-case`/`unknown`)
- **Interview** — `interview.online_assessment`, `behavioral`, `technical`, `system_design`, `rounds`, `notes`
- **Tech** — `tech.required_skills`, `preferred_skills`, `languages`, `frameworks`, `cloud_platforms`, `resume_keywords`
- **Dates** — `dates.posted`, `dates.deadline` (omit for rolling), `dates.last_verified`
- **Status** — `status`: `open` / `closed` / `not-yet-open` / `unverified` (default)
- **Contact** — `recruiter_contact` (publicly listed recruiting contacts only)

## Business rules enforced by CI

1. `id` must start with `company.slug` and match the filename.
2. Non-remote listings need ≥ 1 location.
3. `hourly_min ≤ hourly_max`; `posted ≤ deadline`.
4. Unknown fields are rejected (typo protection).
5. Cross-file: no duplicate ids, no duplicate canonical apply URLs, fuzzy
   role-title duplicates within a company+year are flagged.
