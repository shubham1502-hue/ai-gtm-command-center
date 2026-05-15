from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TargetAccount:
    company: str
    website: str
    segment: str = ""
    industry: str = ""
    funding_stage: str = ""
    target_person: str = ""
    target_role: str = ""
    linkedin_url: str = ""
    email: str = ""
    notes: str = ""
    linkedin_notes: str = ""
    industry_notes: str = ""

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "TargetAccount":
        return cls(
            company=(row.get("company") or "").strip(),
            website=(row.get("website") or "").strip(),
            segment=(row.get("segment") or "").strip(),
            industry=(row.get("industry") or "").strip(),
            funding_stage=(row.get("funding_stage") or "").strip(),
            target_person=(row.get("target_person") or "").strip(),
            target_role=(row.get("target_role") or "").strip(),
            linkedin_url=(row.get("linkedin_url") or "").strip(),
            email=(row.get("email") or "").strip(),
            notes=(row.get("notes") or "").strip(),
            linkedin_notes=(row.get("linkedin_notes") or "").strip(),
            industry_notes=(row.get("industry_notes") or "").strip(),
        )


@dataclass
class ResearchSource:
    label: str
    url: str
    summary: str

    def as_dict(self) -> dict[str, str]:
        return {"label": self.label, "url": self.url, "summary": self.summary}


@dataclass
class AccountResearch:
    account: TargetAccount
    website_summary: str = ""
    news: list[ResearchSource] = field(default_factory=list)
    public_sources: list[ResearchSource] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def source_dicts(self) -> list[dict[str, str]]:
        sources = [source.as_dict() for source in self.public_sources]
        sources.extend(source.as_dict() for source in self.news)
        return sources


@dataclass
class GTMRecommendation:
    company: str
    website: str
    segment: str
    target_person: str
    target_role: str
    email: str
    linkedin_url: str
    industry: str
    funding_stage: str
    fit_score: int
    priority: str
    score_rationale: str
    industry_context: str
    approach_strategy: str
    pain_hypotheses: list[str]
    personalization_points: list[str]
    manual_research_checklist: list[str]
    suggested_offer_angle: str
    linkedin_connection_note: str
    linkedin_dm_body: str
    linkedin_follow_up_body: str
    cold_email_subject: str
    cold_email_body: str
    follow_up_subject: str
    follow_up_body: str
    likely_objections: list[str]
    talk_track: list[str]
    sources: list[dict[str, str]]
    warnings: list[str] = field(default_factory=list)
    raw_model_output: dict[str, Any] = field(default_factory=dict)

    def as_flat_row(self) -> dict[str, Any]:
        return {
            "company": self.company,
            "website": self.website,
            "segment": self.segment,
            "target_person": self.target_person,
            "target_role": self.target_role,
            "email": self.email,
            "linkedin_url": self.linkedin_url,
            "industry": self.industry,
            "funding_stage": self.funding_stage,
            "fit_score": self.fit_score,
            "priority": self.priority,
            "score_rationale": self.score_rationale,
            "industry_context": self.industry_context,
            "approach_strategy": self.approach_strategy,
            "suggested_offer_angle": self.suggested_offer_angle,
            "linkedin_connection_note": self.linkedin_connection_note,
            "linkedin_dm_body": self.linkedin_dm_body,
            "linkedin_follow_up_body": self.linkedin_follow_up_body,
            "cold_email_subject": self.cold_email_subject,
            "cold_email_body": self.cold_email_body,
            "follow_up_subject": self.follow_up_subject,
            "follow_up_body": self.follow_up_body,
            "pain_hypotheses": " | ".join(self.pain_hypotheses),
            "personalization_points": " | ".join(self.personalization_points),
            "manual_research_checklist": " | ".join(self.manual_research_checklist),
            "likely_objections": " | ".join(self.likely_objections),
            "talk_track": " | ".join(self.talk_track),
            "sources": " | ".join(source.get("url", "") for source in self.sources),
            "warnings": " | ".join(self.warnings),
        }
