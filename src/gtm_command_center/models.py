from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TargetAccount:
    company: str
    website: str
    segment: str = ""
    target_person: str = ""
    target_role: str = ""
    email: str = ""
    notes: str = ""

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "TargetAccount":
        return cls(
            company=(row.get("company") or "").strip(),
            website=(row.get("website") or "").strip(),
            segment=(row.get("segment") or "").strip(),
            target_person=(row.get("target_person") or "").strip(),
            target_role=(row.get("target_role") or "").strip(),
            email=(row.get("email") or "").strip(),
            notes=(row.get("notes") or "").strip(),
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
    fit_score: int
    priority: str
    score_rationale: str
    pain_hypotheses: list[str]
    personalization_points: list[str]
    suggested_offer_angle: str
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
            "fit_score": self.fit_score,
            "priority": self.priority,
            "score_rationale": self.score_rationale,
            "suggested_offer_angle": self.suggested_offer_angle,
            "cold_email_subject": self.cold_email_subject,
            "cold_email_body": self.cold_email_body,
            "follow_up_subject": self.follow_up_subject,
            "follow_up_body": self.follow_up_body,
            "pain_hypotheses": " | ".join(self.pain_hypotheses),
            "personalization_points": " | ".join(self.personalization_points),
            "likely_objections": " | ".join(self.likely_objections),
            "talk_track": " | ".join(self.talk_track),
            "sources": " | ".join(source.get("url", "") for source in self.sources),
            "warnings": " | ".join(self.warnings),
        }

