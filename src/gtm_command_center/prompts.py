from __future__ import annotations

import json

from .models import AccountResearch


SYSTEM_PROMPT = """You are an AI-native founder's office GTM operator.
Your job is to turn sparse account research into a practical, human-approved outbound draft.

Rules:
- Be specific and source-aware. Do not invent facts not present in the input.
- If evidence is weak, say so and use hypotheses.
- Keep the email concise and useful.
- Do not claim a prior relationship.
- Do not include manipulative urgency.
- Return valid JSON only.
"""


def build_account_prompt(research: AccountResearch, sender_persona: str) -> str:
    account = research.account
    payload = {
        "sender_persona": sender_persona,
        "target_account": {
            "company": account.company,
            "website": account.website,
            "segment": account.segment,
            "target_person": account.target_person,
            "target_role": account.target_role,
            "notes": account.notes,
        },
        "research": {
            "website_summary": research.website_summary,
            "news": [source.as_dict() for source in research.news],
            "public_sources": [source.as_dict() for source in research.public_sources],
            "warnings": research.warnings,
        },
    }

    schema = {
        "fit_score": "integer 0-100",
        "priority": "High, Medium, or Low",
        "score_rationale": "one concise paragraph",
        "pain_hypotheses": ["3-5 evidence-backed hypotheses"],
        "personalization_points": ["2-4 details that can safely appear in outreach"],
        "suggested_offer_angle": "one specific offer angle",
        "cold_email_subject": "short subject line",
        "cold_email_body": "plain-text email under 140 words",
        "follow_up_subject": "short subject line",
        "follow_up_body": "plain-text follow-up under 100 words",
        "likely_objections": ["2-4 objections"],
        "talk_track": ["3 bullets for a founder call"],
    }

    return (
        "Analyze this target account and return JSON matching the schema.\n\n"
        f"INPUT:\n{json.dumps(payload, indent=2)}\n\n"
        f"OUTPUT_SCHEMA:\n{json.dumps(schema, indent=2)}"
    )

