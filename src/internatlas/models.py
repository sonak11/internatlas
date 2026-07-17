"""Core data model for InternAtlas.

This module is the **single source of truth** for the internship schema.
``schemas/internship.schema.json`` is exported from these models via
``python -m internatlas schema`` — never edit that file by hand.
"""

from __future__ import annotations

import re
from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

SCHEMA_VERSION = "1.0"


# ──────────────────────────────────────────────────────────────────────────────
# Controlled vocabularies
# ──────────────────────────────────────────────────────────────────────────────

class Category(str, Enum):
    SOFTWARE_ENGINEERING = "software-engineering"
    MACHINE_LEARNING = "machine-learning"
    AI = "ai"
    DATA_SCIENCE = "data-science"
    DATA_ENGINEERING = "data-engineering"
    QUANT = "quant"
    HARDWARE = "hardware"
    EMBEDDED = "embedded"
    SECURITY = "security"
    CLOUD = "cloud"
    PRODUCT = "product"
    DESIGN = "design"
    RESEARCH = "research"
    FINANCE = "finance"
    CONSULTING = "consulting"


class WorkMode(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class VisaSponsorship(str, Enum):
    YES = "yes"
    NO = "no"
    CASE_BY_CASE = "case-by-case"
    UNKNOWN = "unknown"


class ApplicationStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    NOT_YET_OPEN = "not-yet-open"
    UNVERIFIED = "unverified"


class Season(str, Enum):
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"
    SPRING = "spring"


class CompanyType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"


class CompanySize(str, Enum):
    STARTUP = "startup"          # < 100
    SMALL = "small"              # 100 – 1,000
    MID = "mid"                  # 1,000 – 10,000
    LARGE = "large"              # 10,000 – 100,000
    ENTERPRISE = "enterprise"    # 100,000+


class Industry(str, Enum):
    BIG_TECH = "big-tech"
    FINANCE = "finance"
    QUANT_TRADING = "quant-trading"
    STARTUP = "startup"
    DEFENSE = "defense"
    HEALTHCARE = "healthcare"
    GOVERNMENT = "government"
    CONSULTING = "consulting"
    SEMICONDUCTORS = "semiconductors"
    AEROSPACE = "aerospace"
    AUTOMOTIVE = "automotive"
    RETAIL = "retail"
    MEDIA = "media"
    ENERGY = "energy"
    EDUCATION = "education"
    OTHER = "other"


class DegreeLevel(str, Enum):
    FRESHMAN = "freshman"
    SOPHOMORE = "sophomore"
    JUNIOR = "junior"
    SENIOR = "senior"
    MASTERS = "masters"
    PHD = "phd"


# ──────────────────────────────────────────────────────────────────────────────
# Nested models
# ──────────────────────────────────────────────────────────────────────────────

class Location(BaseModel):
    """A physical location for the role. Omit for fully-remote roles."""
    model_config = ConfigDict(extra="forbid")

    city: Optional[str] = None
    state: Optional[str] = Field(None, description="State / province / region")
    country: str = Field(..., min_length=2, examples=["USA", "UK", "Canada"])


class Compensation(BaseModel):
    """All money fields are in USD unless ``currency`` says otherwise."""
    model_config = ConfigDict(extra="forbid")

    currency: str = "USD"
    hourly_min: Optional[float] = Field(None, ge=0)
    hourly_max: Optional[float] = Field(None, ge=0)
    monthly: Optional[float] = Field(None, ge=0, description="Monthly salary if quoted that way")
    housing_stipend: bool = False
    relocation_assistance: bool = False

    @model_validator(mode="after")
    def _range_ok(self) -> "Compensation":
        if self.hourly_min is not None and self.hourly_max is not None:
            if self.hourly_min > self.hourly_max:
                raise ValueError("hourly_min cannot exceed hourly_max")
        return self

    @property
    def hourly_midpoint(self) -> Optional[float]:
        vals = [v for v in (self.hourly_min, self.hourly_max) if v is not None]
        return sum(vals) / len(vals) if vals else None


class Eligibility(BaseModel):
    model_config = ConfigDict(extra="forbid")

    graduation_years: list[int] = Field(default_factory=list, examples=[[2028, 2029]])
    degree_levels: list[DegreeLevel] = Field(default_factory=list)
    min_gpa: Optional[float] = Field(None, ge=0, le=4.3)
    citizenship_required: bool = False
    security_clearance_required: bool = False
    visa_sponsorship: VisaSponsorship = VisaSponsorship.UNKNOWN

    @property
    def freshman_friendly(self) -> bool:
        return DegreeLevel.FRESHMAN in self.degree_levels

    @property
    def sophomore_friendly(self) -> bool:
        return DegreeLevel.SOPHOMORE in self.degree_levels

    @property
    def international_friendly(self) -> bool:
        return (
            self.visa_sponsorship in (VisaSponsorship.YES, VisaSponsorship.CASE_BY_CASE)
            and not self.citizenship_required
        )


class InterviewProcess(BaseModel):
    model_config = ConfigDict(extra="forbid")

    online_assessment: Optional[bool] = None
    behavioral: Optional[bool] = None
    technical: Optional[bool] = None
    system_design: Optional[bool] = None
    rounds: Optional[int] = Field(None, ge=1, le=15)
    notes: Optional[str] = None


class TechProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list, examples=[["Python", "C++"]])
    frameworks: list[str] = Field(default_factory=list, examples=[["PyTorch", "React"]])
    cloud_platforms: list[str] = Field(default_factory=list, examples=[["AWS", "GCP"]])
    resume_keywords: list[str] = Field(default_factory=list)


class CompanyInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    slug: str = Field(..., pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    career_page: Optional[HttpUrl] = None
    size: Optional[CompanySize] = None
    industry: Optional[Industry] = None
    company_type: Optional[CompanyType] = None
    fortune_500: Optional[bool] = None


class Dates(BaseModel):
    model_config = ConfigDict(extra="forbid")

    posted: Optional[date] = None
    discovered: date
    deadline: Optional[date] = Field(None, description="Omit for rolling deadlines")
    last_verified: Optional[date] = None

    @model_validator(mode="after")
    def _ordering(self) -> "Dates":
        if self.posted and self.deadline and self.posted > self.deadline:
            raise ValueError("posted date is after the deadline")
        return self


# ──────────────────────────────────────────────────────────────────────────────
# Root model
# ──────────────────────────────────────────────────────────────────────────────

_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class Internship(BaseModel):
    """One internship listing == one JSON file in ``data/internships/``."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    schema_version: str = SCHEMA_VERSION
    id: str = Field(
        ...,
        pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$",
        description="Globally unique slug, conventionally <company>-<role>-<year>",
        examples=["acme-swe-intern-2027"],
    )
    company: CompanyInfo
    role: str = Field(..., min_length=2)
    category: Category
    subcategory: Optional[str] = Field(None, examples=["backend", "nlp", "trading-systems"])
    team: Optional[str] = None
    department: Optional[str] = None
    business_unit: Optional[str] = None

    apply_url: HttpUrl
    recruiter_contact: Optional[str] = Field(None, description="Public contact only — never scrape private emails")

    season: Season = Season.SUMMER
    year: int = Field(..., ge=2024, le=2035)
    length_weeks: Optional[int] = Field(None, ge=1, le=52)

    work_mode: WorkMode
    locations: list[Location] = Field(default_factory=list)

    compensation: Compensation = Field(default_factory=Compensation)
    eligibility: Eligibility = Field(default_factory=Eligibility)
    interview: InterviewProcess = Field(default_factory=InterviewProcess)
    tech: TechProfile = Field(default_factory=TechProfile)
    dates: Dates
    status: ApplicationStatus = ApplicationStatus.UNVERIFIED
    recruiting_timeline: Optional[str] = Field(
        None, description="Free-text summary, e.g. 'Apps open Aug, OAs Sept, superdays Oct'"
    )
    tags: list[str] = Field(default_factory=list, examples=[["big-tech", "returning-program"]])
    notes: Optional[str] = None

    # ── business rules ────────────────────────────────────────────────────────
    @model_validator(mode="after")
    def _remote_or_located(self) -> "Internship":
        if self.work_mode is not WorkMode.REMOTE and not self.locations:
            raise ValueError("non-remote listings must include at least one location")
        return self

    @field_validator("id")
    @classmethod
    def _id_slug(cls, v: str) -> str:
        if not _SLUG_RE.match(v):
            raise ValueError("id must be a lowercase kebab-case slug")
        return v

    @model_validator(mode="after")
    def _id_prefix(self) -> "Internship":
        if not self.id.startswith(self.company.slug):
            raise ValueError(f"id {self.id!r} must start with company slug {self.company.slug!r}")
        return self

    # ── convenience ───────────────────────────────────────────────────────────
    @property
    def primary_location(self) -> str:
        if self.work_mode is WorkMode.REMOTE and not self.locations:
            return "Remote"
        if not self.locations:
            return "—"
        loc = self.locations[0]
        parts = [p for p in (loc.city, loc.state) if p]
        label = ", ".join(parts) if parts else loc.country
        extra = f" +{len(self.locations) - 1}" if len(self.locations) > 1 else ""
        return label + extra

    @property
    def is_open(self) -> bool:
        return self.status is ApplicationStatus.OPEN


def make_slug(text: str) -> str:
    """Convert arbitrary text into a valid kebab-case slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)
