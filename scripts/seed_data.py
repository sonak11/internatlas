"""Create the initial seed dataset.

Seed listings are deliberately marked ``status: unverified`` and point at each
company's public careers page rather than a specific requisition — real posting
URLs churn constantly, and this repo's model is that the community verifies and
upgrades listings via PRs. Run once: ``python scripts/seed_data.py``.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from internatlas.loader import write_listing  # noqa: E402
from internatlas.models import (  # noqa: E402
    ApplicationStatus, Category, CompanyInfo, CompanySize, CompanyType,
    Compensation, Dates, DegreeLevel, Eligibility, Industry, InterviewProcess,
    Internship, Location, Season, TechProfile, VisaSponsorship, WorkMode,
)

TODAY = date(2026, 7, 16)
NOTE = "Seed example — details unverified; confirm on the careers page and PR corrections."


def L(**kw) -> Internship:
    kw.setdefault("season", Season.SUMMER)
    kw.setdefault("year", 2027)
    kw.setdefault("status", ApplicationStatus.UNVERIFIED)
    kw.setdefault("dates", Dates(discovered=TODAY))
    kw.setdefault("notes", NOTE)
    return Internship(**kw)


SEEDS: list[Internship] = [
    L(
        id="google-software-engineering-intern-2027",
        company=CompanyInfo(name="Google", slug="google",
                            career_page="https://www.google.com/about/careers/applications/",
                            size=CompanySize.ENTERPRISE, industry=Industry.BIG_TECH,
                            company_type=CompanyType.PUBLIC, fortune_500=True),
        role="Software Engineering Intern", category=Category.SOFTWARE_ENGINEERING,
        subcategory="generalist",
        apply_url="https://www.google.com/about/careers/applications/jobs/results/?q=software%20engineering%20intern",
        work_mode=WorkMode.ONSITE,
        locations=[Location(city="Mountain View", state="CA", country="USA"),
                   Location(city="New York", state="NY", country="USA")],
        eligibility=Eligibility(degree_levels=[DegreeLevel.SOPHOMORE, DegreeLevel.JUNIOR,
                                               DegreeLevel.SENIOR],
                                graduation_years=[2028, 2029],
                                visa_sponsorship=VisaSponsorship.YES),
        interview=InterviewProcess(online_assessment=True, technical=True, behavioral=True,
                                   rounds=3),
        tech=TechProfile(languages=["Python", "C++", "Java", "Go"],
                         required_skills=["Data Structures", "Algorithms"]),
        recruiting_timeline="Applications historically open late summer; interviews through fall.",
    ),
    L(
        id="google-step-intern-2027",
        company=CompanyInfo(name="Google", slug="google",
                            career_page="https://www.google.com/about/careers/applications/",
                            size=CompanySize.ENTERPRISE, industry=Industry.BIG_TECH,
                            company_type=CompanyType.PUBLIC, fortune_500=True),
        role="STEP Intern (First & Second Year)", category=Category.SOFTWARE_ENGINEERING,
        subcategory="early-career",
        apply_url="https://www.google.com/about/careers/applications/jobs/results/?q=step%20intern",
        work_mode=WorkMode.ONSITE,
        locations=[Location(city="Mountain View", state="CA", country="USA")],
        eligibility=Eligibility(degree_levels=[DegreeLevel.FRESHMAN, DegreeLevel.SOPHOMORE],
                                graduation_years=[2029, 2030],
                                visa_sponsorship=VisaSponsorship.YES),
        interview=InterviewProcess(technical=True, behavioral=True, rounds=2),
        tech=TechProfile(languages=["Python", "Java", "C++"]),
        tags=["freshman-friendly"],
    ),
    L(
        id="jane-street-quantitative-trading-intern-2027",
        company=CompanyInfo(name="Jane Street", slug="jane-street",
                            career_page="https://www.janestreet.com/join-jane-street/open-roles/",
                            size=CompanySize.SMALL, industry=Industry.QUANT_TRADING,
                            company_type=CompanyType.PRIVATE),
        role="Quantitative Trading Intern", category=Category.QUANT,
        subcategory="trading",
        apply_url="https://www.janestreet.com/join-jane-street/open-roles/",
        work_mode=WorkMode.ONSITE,
        locations=[Location(city="New York", state="NY", country="USA")],
        compensation=Compensation(hourly_min=100, hourly_max=125, housing_stipend=True),
        eligibility=Eligibility(degree_levels=[DegreeLevel.SOPHOMORE, DegreeLevel.JUNIOR,
                                               DegreeLevel.SENIOR, DegreeLevel.MASTERS,
                                               DegreeLevel.PHD],
                                visa_sponsorship=VisaSponsorship.YES),
        interview=InterviewProcess(behavioral=True, technical=True, rounds=4,
                                   notes="Probability and mental-math heavy phone rounds."),
        tech=TechProfile(required_skills=["Probability", "Statistics", "Mental Math"],
                         languages=["Python", "OCaml"]),
        recruiting_timeline="Quant recruiting opens very early — often 12+ months ahead.",
    ),
    L(
        id="citadel-software-engineering-intern-2027",
        company=CompanyInfo(name="Citadel", slug="citadel",
                            career_page="https://www.citadel.com/careers/open-opportunities/students/",
                            size=CompanySize.MID, industry=Industry.QUANT_TRADING,
                            company_type=CompanyType.PRIVATE),
        role="Software Engineering Intern", category=Category.SOFTWARE_ENGINEERING,
        subcategory="trading-systems",
        apply_url="https://www.citadel.com/careers/open-opportunities/students/",
        work_mode=WorkMode.ONSITE,
        locations=[Location(city="Chicago", state="IL", country="USA"),
                   Location(city="New York", state="NY", country="USA")],
        compensation=Compensation(hourly_min=95, hourly_max=120, housing_stipend=True,
                                  relocation_assistance=True),
        eligibility=Eligibility(visa_sponsorship=VisaSponsorship.YES,
                                degree_levels=[DegreeLevel.JUNIOR, DegreeLevel.SENIOR,
                                               DegreeLevel.MASTERS]),
        interview=InterviewProcess(online_assessment=True, technical=True, behavioral=True,
                                   rounds=4),
        tech=TechProfile(languages=["C++", "Python"],
                         required_skills=["Data Structures", "Algorithms", "Systems"]),
    ),
    L(
        id="openai-research-intern-2027",
        company=CompanyInfo(name="OpenAI", slug="openai",
                            career_page="https://openai.com/careers/",
                            size=CompanySize.MID, industry=Industry.BIG_TECH,
                            company_type=CompanyType.PRIVATE),
        role="Research Intern", category=Category.RESEARCH, subcategory="ml-research",
        apply_url="https://openai.com/careers/",
        work_mode=WorkMode.ONSITE,
        locations=[Location(city="San Francisco", state="CA", country="USA")],
        eligibility=Eligibility(degree_levels=[DegreeLevel.PHD],
                                visa_sponsorship=VisaSponsorship.YES),
        interview=InterviewProcess(technical=True, behavioral=True),
        tech=TechProfile(languages=["Python"], frameworks=["PyTorch"],
                         required_skills=["Deep Learning", "Research Publications"]),
        tags=["phd"],
    ),
    L(
        id="nvidia-machine-learning-intern-2027",
        company=CompanyInfo(name="NVIDIA", slug="nvidia",
                            career_page="https://www.nvidia.com/en-us/about-nvidia/careers/university-recruiting/",
                            size=CompanySize.LARGE, industry=Industry.SEMICONDUCTORS,
                            company_type=CompanyType.PUBLIC, fortune_500=True),
        role="Machine Learning Intern", category=Category.MACHINE_LEARNING,
        subcategory="deep-learning",
        apply_url="https://www.nvidia.com/en-us/about-nvidia/careers/university-recruiting/",
        work_mode=WorkMode.HYBRID,
        locations=[Location(city="Santa Clara", state="CA", country="USA")],
        eligibility=Eligibility(degree_levels=[DegreeLevel.JUNIOR, DegreeLevel.SENIOR,
                                               DegreeLevel.MASTERS, DegreeLevel.PHD],
                                visa_sponsorship=VisaSponsorship.YES),
        interview=InterviewProcess(technical=True, behavioral=True, rounds=3),
        tech=TechProfile(languages=["Python", "C++", "CUDA"], frameworks=["PyTorch", "TensorRT"],
                         cloud_platforms=["AWS"], required_skills=["Deep Learning", "GPU Computing"]),
    ),
    L(
        id="stripe-software-engineering-intern-2027",
        company=CompanyInfo(name="Stripe", slug="stripe",
                            career_page="https://stripe.com/jobs/university",
                            size=CompanySize.MID, industry=Industry.BIG_TECH,
                            company_type=CompanyType.PRIVATE),
        role="Software Engineering Intern", category=Category.SOFTWARE_ENGINEERING,
        subcategory="backend",
        apply_url="https://stripe.com/jobs/university",
        work_mode=WorkMode.HYBRID,
        locations=[Location(city="South San Francisco", state="CA", country="USA"),
                   Location(city="Seattle", state="WA", country="USA")],
        eligibility=Eligibility(visa_sponsorship=VisaSponsorship.YES,
                                degree_levels=[DegreeLevel.SOPHOMORE, DegreeLevel.JUNIOR,
                                               DegreeLevel.SENIOR]),
        interview=InterviewProcess(technical=True, behavioral=True, rounds=3,
                                   notes="Practical coding in your own editor; no trick puzzles."),
        tech=TechProfile(languages=["Ruby", "Java", "Go", "Python"],
                         required_skills=["APIs", "Distributed Systems"]),
    ),
    L(
        id="lockheed-martin-embedded-software-intern-2027",
        company=CompanyInfo(name="Lockheed Martin", slug="lockheed-martin",
                            career_page="https://www.lockheedmartinjobs.com/students-early-careers",
                            size=CompanySize.LARGE, industry=Industry.DEFENSE,
                            company_type=CompanyType.PUBLIC, fortune_500=True),
        role="Embedded Software Intern", category=Category.EMBEDDED,
        subcategory="avionics",
        apply_url="https://www.lockheedmartinjobs.com/students-early-careers",
        work_mode=WorkMode.ONSITE,
        locations=[Location(city="Fort Worth", state="TX", country="USA")],
        eligibility=Eligibility(citizenship_required=True, security_clearance_required=True,
                                visa_sponsorship=VisaSponsorship.NO,
                                degree_levels=[DegreeLevel.SOPHOMORE, DegreeLevel.JUNIOR,
                                               DegreeLevel.SENIOR]),
        interview=InterviewProcess(behavioral=True, technical=True, rounds=2),
        tech=TechProfile(languages=["C", "C++"], required_skills=["RTOS", "Embedded Systems"]),
        tags=["defense", "clearance"],
    ),
    L(
        id="capital-one-data-science-intern-2027",
        company=CompanyInfo(name="Capital One", slug="capital-one",
                            career_page="https://www.capitalonecareers.com/students-and-grads",
                            size=CompanySize.LARGE, industry=Industry.FINANCE,
                            company_type=CompanyType.PUBLIC, fortune_500=True),
        role="Data Science Intern", category=Category.DATA_SCIENCE,
        apply_url="https://www.capitalonecareers.com/students-and-grads",
        work_mode=WorkMode.HYBRID,
        locations=[Location(city="McLean", state="VA", country="USA")],
        eligibility=Eligibility(citizenship_required=False,
                                visa_sponsorship=VisaSponsorship.NO,
                                degree_levels=[DegreeLevel.JUNIOR, DegreeLevel.SENIOR,
                                               DegreeLevel.MASTERS]),
        interview=InterviewProcess(online_assessment=True, behavioral=True, technical=True,
                                   rounds=3),
        tech=TechProfile(languages=["Python", "SQL", "R"], cloud_platforms=["AWS"],
                         required_skills=["Machine Learning", "Statistics"]),
    ),
    L(
        id="cloudflare-security-engineering-intern-2027",
        company=CompanyInfo(name="Cloudflare", slug="cloudflare",
                            career_page="https://www.cloudflare.com/careers/early-talent/",
                            size=CompanySize.MID, industry=Industry.BIG_TECH,
                            company_type=CompanyType.PUBLIC),
        role="Security Engineering Intern", category=Category.SECURITY,
        apply_url="https://www.cloudflare.com/careers/early-talent/",
        work_mode=WorkMode.REMOTE,
        eligibility=Eligibility(visa_sponsorship=VisaSponsorship.CASE_BY_CASE,
                                degree_levels=[DegreeLevel.SOPHOMORE, DegreeLevel.JUNIOR,
                                               DegreeLevel.SENIOR]),
        interview=InterviewProcess(technical=True, behavioral=True, rounds=3),
        tech=TechProfile(languages=["Go", "Rust", "Python"],
                         required_skills=["Networking", "Application Security"]),
        tags=["remote"],
    ),
    L(
        id="microsoft-explore-intern-2027",
        company=CompanyInfo(name="Microsoft", slug="microsoft",
                            career_page="https://careers.microsoft.com/v2/global/en/students",
                            size=CompanySize.ENTERPRISE, industry=Industry.BIG_TECH,
                            company_type=CompanyType.PUBLIC, fortune_500=True),
        role="Explore Intern (First & Second Year)", category=Category.SOFTWARE_ENGINEERING,
        subcategory="early-career",
        apply_url="https://careers.microsoft.com/v2/global/en/students",
        work_mode=WorkMode.ONSITE,
        locations=[Location(city="Redmond", state="WA", country="USA")],
        eligibility=Eligibility(degree_levels=[DegreeLevel.FRESHMAN, DegreeLevel.SOPHOMORE],
                                graduation_years=[2029, 2030],
                                visa_sponsorship=VisaSponsorship.YES),
        interview=InterviewProcess(behavioral=True, technical=True, rounds=2),
        tech=TechProfile(languages=["Python", "C#", "Java"]),
        tags=["freshman-friendly"],
    ),
    L(
        id="databricks-data-engineering-intern-2027",
        company=CompanyInfo(name="Databricks", slug="databricks",
                            career_page="https://www.databricks.com/company/careers/university-recruiting",
                            size=CompanySize.MID, industry=Industry.BIG_TECH,
                            company_type=CompanyType.PRIVATE),
        role="Software Engineering Intern — Data Platform", category=Category.DATA_ENGINEERING,
        apply_url="https://www.databricks.com/company/careers/university-recruiting",
        work_mode=WorkMode.ONSITE,
        locations=[Location(city="San Francisco", state="CA", country="USA")],
        eligibility=Eligibility(visa_sponsorship=VisaSponsorship.YES,
                                degree_levels=[DegreeLevel.JUNIOR, DegreeLevel.SENIOR,
                                               DegreeLevel.MASTERS]),
        interview=InterviewProcess(online_assessment=True, technical=True, rounds=3),
        tech=TechProfile(languages=["Scala", "Java", "Python"], frameworks=["Spark"],
                         cloud_platforms=["AWS", "Azure", "GCP"]),
    ),
]


def main() -> None:
    for listing in SEEDS:
        path = write_listing(ROOT, listing)
        print(f"✓ {path.relative_to(ROOT)}")
    print(f"\nSeeded {len(SEEDS)} example listings.")


if __name__ == "__main__":
    main()
