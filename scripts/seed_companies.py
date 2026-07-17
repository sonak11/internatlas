"""Expand the seed dataset to 100+ listings.

Honesty policy: these seeds are a *directory*, not verified postings. Each one
points at the company's official careers/university portal, carries
``status: unverified``, and omits pay/deadline/eligibility details we can't
confirm. The hourly ATS sync and community PRs upgrade them into verified,
detail-rich listings over time.

Run once: ``python scripts/seed_companies.py``
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from internatlas.loader import load_all, write_listing  # noqa: E402
from internatlas.models import (ApplicationStatus, Category, CompanyInfo,  # noqa: E402
                                CompanySize, CompanyType, Dates, Industry,
                                Internship, Location, WorkMode, make_slug)

TODAY = date(2026, 7, 16)
NOTE = ("Seed listing — points at the official careers portal; role details "
        "unverified. Confirm on the company site and PR corrections/enrichment.")

C = Category
I = Industry
S = CompanySize
T = CompanyType

# (company, careers_url, category, industry, size, type, fortune500, hq_city, hq_state, country, role_override)
SEEDS: list[tuple] = [
    # ── Big tech / large public software ────────────────────────────────────
    ("Meta", "https://www.metacareers.com/jobs", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.ENTERPRISE, T.PUBLIC, True, "Menlo Park", "CA", "USA", None),
    ("Apple", "https://www.apple.com/careers/us/students.html", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.ENTERPRISE, T.PUBLIC, True, "Cupertino", "CA", "USA", None),
    ("Amazon", "https://www.amazon.jobs/en/teams/internships-for-students", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.ENTERPRISE, T.PUBLIC, True, "Seattle", "WA", "USA", None),
    ("Netflix", "https://jobs.netflix.com/", C.SOFTWARE_ENGINEERING, I.MEDIA, S.LARGE, T.PUBLIC, True, "Los Gatos", "CA", "USA", None),
    ("Adobe", "https://careers.adobe.com/us/en/university", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.LARGE, T.PUBLIC, True, "San Jose", "CA", "USA", None),
    ("Salesforce", "https://careers.salesforce.com/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.LARGE, T.PUBLIC, True, "San Francisco", "CA", "USA", None),
    ("Oracle", "https://www.oracle.com/careers/students-grads/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.ENTERPRISE, T.PUBLIC, True, "Austin", "TX", "USA", None),
    ("IBM", "https://www.ibm.com/careers", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.ENTERPRISE, T.PUBLIC, True, "Armonk", "NY", "USA", None),
    ("Intel", "https://jobs.intel.com/en/students", C.HARDWARE, I.SEMICONDUCTORS, S.ENTERPRISE, T.PUBLIC, True, "Santa Clara", "CA", "USA", None),
    ("Qualcomm", "https://www.qualcomm.com/company/careers/students", C.HARDWARE, I.SEMICONDUCTORS, S.LARGE, T.PUBLIC, True, "San Diego", "CA", "USA", None),
    ("AMD", "https://careers.amd.com/", C.HARDWARE, I.SEMICONDUCTORS, S.LARGE, T.PUBLIC, True, "Santa Clara", "CA", "USA", None),
    ("Cisco", "https://jobs.cisco.com/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.LARGE, T.PUBLIC, True, "San Jose", "CA", "USA", None),
    ("Uber", "https://www.uber.com/us/en/careers/teams/university/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.LARGE, T.PUBLIC, True, "San Francisco", "CA", "USA", None),
    ("Lyft", "https://www.lyft.com/careers", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.MID, T.PUBLIC, False, "San Francisco", "CA", "USA", None),
    ("Airbnb", "https://careers.airbnb.com/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.MID, T.PUBLIC, True, "San Francisco", "CA", "USA", None),
    ("DoorDash", "https://careersatdoordash.com/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.MID, T.PUBLIC, True, "San Francisco", "CA", "USA", None),
    ("Pinterest", "https://www.pinterestcareers.com/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.MID, T.PUBLIC, False, "San Francisco", "CA", "USA", None),
    ("Snap", "https://careers.snap.com/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.MID, T.PUBLIC, False, "Santa Monica", "CA", "USA", None),
    ("TikTok", "https://careers.tiktok.com/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.ENTERPRISE, T.PRIVATE, False, "San Jose", "CA", "USA", None),
    ("LinkedIn", "https://careers.linkedin.com/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.LARGE, T.PUBLIC, False, "Sunnyvale", "CA", "USA", None),
    ("Dropbox", "https://jobs.dropbox.com/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.MID, T.PUBLIC, False, "San Francisco", "CA", "USA", None),
    ("Atlassian", "https://www.atlassian.com/company/careers/students", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.MID, T.PUBLIC, False, "San Francisco", "CA", "USA", None),
    ("Twilio", "https://www.twilio.com/en-us/company/jobs", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.MID, T.PUBLIC, False, "San Francisco", "CA", "USA", None),
    ("Snowflake", "https://careers.snowflake.com/", C.DATA_ENGINEERING, I.BIG_TECH, S.MID, T.PUBLIC, False, "Bozeman", "MT", "USA", None),
    ("ServiceNow", "https://careers.servicenow.com/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.LARGE, T.PUBLIC, True, "Santa Clara", "CA", "USA", None),
    ("Intuit", "https://www.intuit.com/careers/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.LARGE, T.PUBLIC, True, "Mountain View", "CA", "USA", None),
    ("SAP", "https://jobs.sap.com/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.ENTERPRISE, T.PUBLIC, False, "Newtown Square", "PA", "USA", None),
    ("PayPal", "https://careers.pypl.com/", C.SOFTWARE_ENGINEERING, I.FINANCE, S.LARGE, T.PUBLIC, True, "San Jose", "CA", "USA", None),
    ("Mastercard", "https://careers.mastercard.com/", C.SOFTWARE_ENGINEERING, I.FINANCE, S.LARGE, T.PUBLIC, True, "Purchase", "NY", "USA", None),
    ("Shopify", "https://www.shopify.com/careers", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.MID, T.PUBLIC, False, "Ottawa", "ON", "Canada", None),
    ("Block", "https://block.xyz/careers", C.SOFTWARE_ENGINEERING, I.FINANCE, S.MID, T.PUBLIC, True, "Oakland", "CA", "USA", None),
    # ── High-growth private / startups ───────────────────────────────────────
    ("Anthropic", "https://www.anthropic.com/careers", C.RESEARCH, I.BIG_TECH, S.MID, T.PRIVATE, False, "San Francisco", "CA", "USA", "Research / Engineering Intern"),
    ("Scale AI", "https://scale.com/careers", C.MACHINE_LEARNING, I.STARTUP, S.SMALL, T.PRIVATE, False, "San Francisco", "CA", "USA", None),
    ("Notion", "https://www.notion.so/careers", C.SOFTWARE_ENGINEERING, I.STARTUP, S.SMALL, T.PRIVATE, False, "San Francisco", "CA", "USA", None),
    ("Discord", "https://discord.com/careers", C.SOFTWARE_ENGINEERING, I.STARTUP, S.SMALL, T.PRIVATE, False, "San Francisco", "CA", "USA", None),
    ("Plaid", "https://plaid.com/careers/", C.SOFTWARE_ENGINEERING, I.STARTUP, S.SMALL, T.PRIVATE, False, "San Francisco", "CA", "USA", None),
    ("Ramp", "https://ramp.com/careers", C.SOFTWARE_ENGINEERING, I.STARTUP, S.SMALL, T.PRIVATE, False, "New York", "NY", "USA", None),
    ("Figma", "https://www.figma.com/careers/", C.SOFTWARE_ENGINEERING, I.STARTUP, S.SMALL, T.PRIVATE, False, "San Francisco", "CA", "USA", None),
    ("Roblox", "https://careers.roblox.com/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.MID, T.PUBLIC, False, "San Mateo", "CA", "USA", None),
    ("Duolingo", "https://careers.duolingo.com/", C.SOFTWARE_ENGINEERING, I.STARTUP, S.SMALL, T.PUBLIC, False, "Pittsburgh", "PA", "USA", None),
    ("Robinhood", "https://careers.robinhood.com/", C.SOFTWARE_ENGINEERING, I.FINANCE, S.MID, T.PUBLIC, False, "Menlo Park", "CA", "USA", None),
    ("Coinbase", "https://www.coinbase.com/careers", C.SOFTWARE_ENGINEERING, I.FINANCE, S.MID, T.PUBLIC, False, "San Francisco", "CA", "USA", None),
    ("Palantir", "https://www.palantir.com/careers/", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.MID, T.PUBLIC, False, "Denver", "CO", "USA", None),
    ("Datadog", "https://careers.datadoghq.com/", C.CLOUD, I.BIG_TECH, S.MID, T.PUBLIC, False, "New York", "NY", "USA", None),
    ("MongoDB", "https://www.mongodb.com/company/careers", C.SOFTWARE_ENGINEERING, I.BIG_TECH, S.MID, T.PUBLIC, False, "New York", "NY", "USA", None),
    ("Waymo", "https://waymo.com/careers/", C.MACHINE_LEARNING, I.AUTOMOTIVE, S.MID, T.PRIVATE, False, "Mountain View", "CA", "USA", None),
    ("Cohere", "https://cohere.com/careers", C.MACHINE_LEARNING, I.STARTUP, S.SMALL, T.PRIVATE, False, "Toronto", "ON", "Canada", None),
    # ── Quant / trading ──────────────────────────────────────────────────────
    ("Citadel Securities", "https://www.citadelsecurities.com/careers/", C.QUANT, I.QUANT_TRADING, S.SMALL, T.PRIVATE, False, "Miami", "FL", "USA", None),
    ("Two Sigma", "https://careers.twosigma.com/", C.QUANT, I.QUANT_TRADING, S.SMALL, T.PRIVATE, False, "New York", "NY", "USA", None),
    ("Hudson River Trading", "https://www.hudsonrivertrading.com/careers/", C.QUANT, I.QUANT_TRADING, S.SMALL, T.PRIVATE, False, "New York", "NY", "USA", None),
    ("Jump Trading", "https://www.jumptrading.com/careers/", C.QUANT, I.QUANT_TRADING, S.SMALL, T.PRIVATE, False, "Chicago", "IL", "USA", None),
    ("DRW", "https://www.drw.com/work-at-drw", C.QUANT, I.QUANT_TRADING, S.SMALL, T.PRIVATE, False, "Chicago", "IL", "USA", None),
    ("IMC Trading", "https://careers.imc.com/", C.QUANT, I.QUANT_TRADING, S.SMALL, T.PRIVATE, False, "Chicago", "IL", "USA", None),
    ("Optiver", "https://optiver.com/working-at-optiver/", C.QUANT, I.QUANT_TRADING, S.SMALL, T.PRIVATE, False, "Chicago", "IL", "USA", None),
    ("SIG (Susquehanna)", "https://careers.sig.com/", C.QUANT, I.QUANT_TRADING, S.SMALL, T.PRIVATE, False, "Bala Cynwyd", "PA", "USA", None),
    ("Akuna Capital", "https://akunacapital.com/careers", C.QUANT, I.QUANT_TRADING, S.STARTUP, T.PRIVATE, False, "Chicago", "IL", "USA", None),
    ("Tower Research Capital", "https://www.tower-research.com/", C.QUANT, I.QUANT_TRADING, S.STARTUP, T.PRIVATE, False, "New York", "NY", "USA", None),
    ("D. E. Shaw", "https://www.deshaw.com/careers", C.QUANT, I.QUANT_TRADING, S.SMALL, T.PRIVATE, False, "New York", "NY", "USA", None),
    ("Point72", "https://careers.point72.com/", C.QUANT, I.FINANCE, S.SMALL, T.PRIVATE, False, "Stamford", "CT", "USA", None),
    ("Millennium", "https://www.mlp.com/careers/", C.QUANT, I.FINANCE, S.SMALL, T.PRIVATE, False, "New York", "NY", "USA", None),
    ("Virtu Financial", "https://www.virtu.com/careers/", C.QUANT, I.QUANT_TRADING, S.STARTUP, T.PUBLIC, False, "New York", "NY", "USA", None),
    ("Flow Traders", "https://www.flowtraders.com/careers", C.QUANT, I.QUANT_TRADING, S.STARTUP, T.PUBLIC, False, "New York", "NY", "USA", None),
    # ── Banks & asset managers ───────────────────────────────────────────────
    ("Goldman Sachs", "https://www.goldmansachs.com/careers/students", C.FINANCE, I.FINANCE, S.LARGE, T.PUBLIC, True, "New York", "NY", "USA", "Summer Analyst (Engineering)"),
    ("J.P. Morgan", "https://careers.jpmorgan.com/us/en/students", C.FINANCE, I.FINANCE, S.ENTERPRISE, T.PUBLIC, True, "New York", "NY", "USA", "Software Engineer Program Summer Analyst"),
    ("Morgan Stanley", "https://www.morganstanley.com/careers/students-graduates", C.FINANCE, I.FINANCE, S.LARGE, T.PUBLIC, True, "New York", "NY", "USA", "Technology Summer Analyst"),
    ("Bank of America", "https://careers.bankofamerica.com/en-us/students", C.FINANCE, I.FINANCE, S.ENTERPRISE, T.PUBLIC, True, "Charlotte", "NC", "USA", "Global Technology Summer Analyst"),
    ("BlackRock", "https://careers.blackrock.com/", C.FINANCE, I.FINANCE, S.LARGE, T.PUBLIC, True, "New York", "NY", "USA", "Summer Analyst (Aladdin Engineering)"),
    ("Bloomberg", "https://www.bloomberg.com/careers", C.SOFTWARE_ENGINEERING, I.FINANCE, S.LARGE, T.PRIVATE, False, "New York", "NY", "USA", None),
    ("Fidelity", "https://jobs.fidelity.com/", C.SOFTWARE_ENGINEERING, I.FINANCE, S.LARGE, T.PRIVATE, False, "Boston", "MA", "USA", None),
    ("Vanguard", "https://www.vanguardjobs.com/", C.SOFTWARE_ENGINEERING, I.FINANCE, S.LARGE, T.PRIVATE, False, "Malvern", "PA", "USA", None),
    ("American Express", "https://www.americanexpress.com/en-us/careers/", C.SOFTWARE_ENGINEERING, I.FINANCE, S.LARGE, T.PUBLIC, True, "New York", "NY", "USA", None),
    # ── Defense / aerospace / gov ────────────────────────────────────────────
    ("Northrop Grumman", "https://www.northropgrumman.com/careers/", C.EMBEDDED, I.DEFENSE, S.LARGE, T.PUBLIC, True, "Falls Church", "VA", "USA", None),
    ("RTX (Raytheon)", "https://careers.rtx.com/", C.EMBEDDED, I.DEFENSE, S.ENTERPRISE, T.PUBLIC, True, "Arlington", "VA", "USA", None),
    ("Boeing", "https://jobs.boeing.com/", C.EMBEDDED, I.AEROSPACE, S.ENTERPRISE, T.PUBLIC, True, "Arlington", "VA", "USA", None),
    ("SpaceX", "https://www.spacex.com/careers/", C.EMBEDDED, I.AEROSPACE, S.MID, T.PRIVATE, False, "Hawthorne", "CA", "USA", None),
    ("Blue Origin", "https://www.blueorigin.com/careers", C.EMBEDDED, I.AEROSPACE, S.MID, T.PRIVATE, False, "Kent", "WA", "USA", None),
    ("Anduril", "https://www.anduril.com/careers/", C.EMBEDDED, I.DEFENSE, S.SMALL, T.PRIVATE, False, "Costa Mesa", "CA", "USA", None),
    ("L3Harris", "https://careers.l3harris.com/", C.EMBEDDED, I.DEFENSE, S.LARGE, T.PUBLIC, True, "Melbourne", "FL", "USA", None),
    ("MITRE", "https://careers.mitre.org/", C.RESEARCH, I.GOVERNMENT, S.MID, T.NONPROFIT, False, "McLean", "VA", "USA", None),
    ("NASA", "https://intern.nasa.gov/", C.RESEARCH, I.GOVERNMENT, S.LARGE, T.GOVERNMENT, False, "Washington", "DC", "USA", "NASA Internship Program"),
    ("Sandia National Laboratories", "https://www.sandia.gov/careers/", C.RESEARCH, I.GOVERNMENT, S.MID, T.GOVERNMENT, False, "Albuquerque", "NM", "USA", None),
    # ── Hardware / semis / auto ──────────────────────────────────────────────
    ("Texas Instruments", "https://careers.ti.com/", C.HARDWARE, I.SEMICONDUCTORS, S.LARGE, T.PUBLIC, True, "Dallas", "TX", "USA", None),
    ("Analog Devices", "https://www.analog.com/en/about-adi/careers.html", C.HARDWARE, I.SEMICONDUCTORS, S.LARGE, T.PUBLIC, True, "Wilmington", "MA", "USA", None),
    ("Micron", "https://careers.micron.com/", C.HARDWARE, I.SEMICONDUCTORS, S.LARGE, T.PUBLIC, True, "Boise", "ID", "USA", None),
    ("Arm", "https://careers.arm.com/", C.HARDWARE, I.SEMICONDUCTORS, S.MID, T.PUBLIC, False, "Austin", "TX", "USA", None),
    ("ASML", "https://www.asml.com/en/careers", C.HARDWARE, I.SEMICONDUCTORS, S.LARGE, T.PUBLIC, False, "Wilton", "CT", "USA", None),
    ("Tesla", "https://www.tesla.com/careers", C.EMBEDDED, I.AUTOMOTIVE, S.ENTERPRISE, T.PUBLIC, True, "Austin", "TX", "USA", None),
    ("Rivian", "https://rivian.com/careers", C.EMBEDDED, I.AUTOMOTIVE, S.MID, T.PUBLIC, True, "Irvine", "CA", "USA", None),
    # ── Healthcare / enterprise ──────────────────────────────────────────────
    ("Epic Systems", "https://careers.epic.com/", C.SOFTWARE_ENGINEERING, I.HEALTHCARE, S.MID, T.PRIVATE, False, "Verona", "WI", "USA", None),
    ("Johnson & Johnson", "https://www.careers.jnj.com/", C.DATA_SCIENCE, I.HEALTHCARE, S.ENTERPRISE, T.PUBLIC, True, "New Brunswick", "NJ", "USA", None),
    ("UnitedHealth Group / Optum", "https://careers.unitedhealthgroup.com/", C.SOFTWARE_ENGINEERING, I.HEALTHCARE, S.ENTERPRISE, T.PUBLIC, True, "Minnetonka", "MN", "USA", None),
    # ── Consulting ───────────────────────────────────────────────────────────
    ("McKinsey & Company", "https://www.mckinsey.com/careers", C.CONSULTING, I.CONSULTING, S.LARGE, T.PRIVATE, False, "New York", "NY", "USA", "Summer Business Analyst"),
    ("Boston Consulting Group", "https://careers.bcg.com/", C.CONSULTING, I.CONSULTING, S.LARGE, T.PRIVATE, False, "Boston", "MA", "USA", "Summer Associate"),
    ("Bain & Company", "https://www.bain.com/careers/", C.CONSULTING, I.CONSULTING, S.LARGE, T.PRIVATE, False, "Boston", "MA", "USA", "Associate Consultant Intern"),
    ("Accenture", "https://www.accenture.com/us-en/careers", C.CONSULTING, I.CONSULTING, S.ENTERPRISE, T.PUBLIC, True, "Chicago", "IL", "USA", None),
]

DEFAULT_ROLES: dict[Category, str] = {
    C.SOFTWARE_ENGINEERING: "Software Engineering Intern",
    C.MACHINE_LEARNING: "Machine Learning Intern",
    C.AI: "AI Intern",
    C.DATA_SCIENCE: "Data Science Intern",
    C.DATA_ENGINEERING: "Data Engineering Intern",
    C.QUANT: "Quantitative Trading / Research Intern",
    C.HARDWARE: "Hardware Engineering Intern",
    C.EMBEDDED: "Embedded Software Intern",
    C.SECURITY: "Security Engineering Intern",
    C.CLOUD: "Cloud / Infrastructure Intern",
    C.PRODUCT: "Product Management Intern",
    C.DESIGN: "Product Design Intern",
    C.RESEARCH: "Research Intern",
    C.FINANCE: "Technology Summer Analyst",
    C.CONSULTING: "Summer Intern",
}


def main() -> None:
    existing = {l.company.slug for l in load_all(ROOT).listings}
    created = skipped = 0
    for (name, url, cat, industry, size, ctype, f500, city, state, country, role) in SEEDS:
        slug = make_slug(name)
        if slug in existing:
            skipped += 1
            continue
        role = role or DEFAULT_ROLES[cat]
        listing = Internship(
            id=f"{slug}-{make_slug(role)}-2027",
            company=CompanyInfo(name=name, slug=slug, career_page=url,  # type: ignore[arg-type]
                                size=size, industry=industry, company_type=ctype,
                                fortune_500=f500 or None),
            role=role,
            category=cat,
            apply_url=url,  # type: ignore[arg-type]
            work_mode=WorkMode.ONSITE,
            locations=[Location(city=city, state=state, country=country)],
            year=2027,
            dates=Dates(discovered=TODAY),
            status=ApplicationStatus.UNVERIFIED,
            notes=NOTE,
        )
        write_listing(ROOT, listing)
        created += 1
    total = len(load_all(ROOT).listings)
    print(f"✓ Created {created} listings ({skipped} companies already present). Total: {total}")


if __name__ == "__main__":
    main()
