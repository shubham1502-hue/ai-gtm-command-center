from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from .llm import LLMProvider
from .models import AccountResearch, GTMRecommendation, TargetAccount
from .research import CompanyResearcher
from .utils import priority_from_score, safe_int


REQUIRED_COLUMNS = {"company", "website"}


def load_targets(path: Path) -> list[TargetAccount]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Missing required columns in {path}: {', '.join(sorted(missing))}")
        accounts = [TargetAccount.from_row(row) for row in reader]
    return [account for account in accounts if account.company and account.website]


def load_persona(path: Path | None) -> str:
    if not path:
        return (
            "Founder office operator who builds practical AI systems for GTM, revenue operations, "
            "market intelligence, and founder-led sales follow-up."
        )
    return path.read_text(encoding="utf-8")


def normalize_recommendation(research: AccountResearch, raw: dict) -> GTMRecommendation:
    score = max(0, min(100, safe_int(raw.get("fit_score"), 0)))
    priority = str(raw.get("priority") or priority_from_score(score)).title()
    if priority not in {"High", "Medium", "Low"}:
        priority = priority_from_score(score)

    def as_list(key: str) -> list[str]:
        value = raw.get(key)
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    account = research.account
    return GTMRecommendation(
        company=account.company,
        website=account.website,
        segment=account.segment,
        target_person=account.target_person,
        target_role=account.target_role,
        email=account.email,
        linkedin_url=account.linkedin_url,
        industry=account.industry,
        funding_stage=account.funding_stage,
        fit_score=score,
        priority=priority,
        score_rationale=str(raw.get("score_rationale") or "No rationale returned.").strip(),
        industry_context=str(raw.get("industry_context") or "").strip(),
        approach_strategy=str(raw.get("approach_strategy") or "").strip(),
        pain_hypotheses=as_list("pain_hypotheses"),
        personalization_points=as_list("personalization_points"),
        manual_research_checklist=as_list("manual_research_checklist"),
        suggested_offer_angle=str(raw.get("suggested_offer_angle") or "").strip(),
        linkedin_connection_note=str(raw.get("linkedin_connection_note") or "").strip()[:200],
        linkedin_dm_body=str(raw.get("linkedin_dm_body") or "").strip(),
        linkedin_follow_up_body=str(raw.get("linkedin_follow_up_body") or "").strip(),
        cold_email_subject=str(raw.get("cold_email_subject") or f"{account.company} GTM idea").strip(),
        cold_email_body=str(raw.get("cold_email_body") or "").strip(),
        follow_up_subject=str(raw.get("follow_up_subject") or "Quick follow-up").strip(),
        follow_up_body=str(raw.get("follow_up_body") or "").strip(),
        likely_objections=as_list("likely_objections"),
        talk_track=as_list("talk_track"),
        sources=research.source_dicts(),
        warnings=research.warnings,
        raw_model_output=raw,
    )


def recommend_accounts(
    accounts: Iterable[TargetAccount],
    provider: LLMProvider,
    sender_persona: str,
    offline: bool = False,
    news_limit: int = 3,
) -> list[GTMRecommendation]:
    researcher = CompanyResearcher(offline=offline, news_limit=news_limit)
    recommendations: list[GTMRecommendation] = []
    for account in accounts:
        research = researcher.gather(account)
        raw = provider.synthesize(research, sender_persona)
        recommendations.append(normalize_recommendation(research, raw))
    recommendations.sort(key=lambda item: item.fit_score, reverse=True)
    return recommendations


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
