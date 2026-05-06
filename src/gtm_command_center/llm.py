from __future__ import annotations

import json
import os
import re
import urllib.request
from abc import ABC, abstractmethod
from typing import Any

from .models import AccountResearch
from .prompts import SYSTEM_PROMPT, build_account_prompt
from .utils import clean_text, priority_from_score


class LLMError(RuntimeError):
    pass


class LLMProvider(ABC):
    @abstractmethod
    def synthesize(self, research: AccountResearch, sender_persona: str) -> dict[str, Any]:
        raise NotImplementedError


def extract_json_object(text: str) -> dict[str, Any]:
    value = text.strip()
    if value.startswith("```"):
        value = re.sub(r"^```(?:json)?", "", value, flags=re.IGNORECASE).strip()
        value = re.sub(r"```$", "", value).strip()
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", value, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


class MockProvider(LLMProvider):
    """Deterministic provider for portfolio demos, tests, and no-key runs."""

    def synthesize(self, research: AccountResearch, sender_persona: str) -> dict[str, Any]:
        account = research.account
        evidence = " ".join([account.segment, account.notes, research.website_summary]).lower()
        score = 50
        if any(term in evidence for term in ["seed", "series a", "founder-led", "b2b", "saas"]):
            score += 18
        if any(term in evidence for term in ["ai", "llm", "agent", "devtools", "automation"]):
            score += 12
        if any(term in evidence for term in ["revenue", "pipeline", "cac", "activation", "outbound", "sales", "gtm"]):
            score += 16
        if any(term in evidence for term in ["manual", "messy", "ops", "support", "hiring", "crm", "reporting"]):
            score += 8
        score = max(0, min(96, score))

        role = account.target_role or "founder"
        person = account.target_person or role
        company = account.company
        segment = account.segment or "growth-stage"

        pain_hypotheses = [
            f"{company} likely has account research and founder-led follow-up scattered across manual tools.",
            f"Given the {segment} context, the team probably needs cleaner prioritization before adding more GTM headcount.",
            "A weekly operating view could expose which accounts, conversations, and follow-ups deserve founder attention.",
        ]
        if account.notes:
            pain_hypotheses.append(f"Operator note to validate: {clean_text(account.notes, 130)}")

        personalization = [
            f"Reference {company}'s {segment} context.",
            "Lead with a practical workflow, not a generic AI pitch.",
        ]
        if research.public_sources:
            personalization.append(f"Use the public website as the primary source: {research.public_sources[0].url}")

        subject = f"{company} GTM workflow idea"
        body = (
            f"Hi {person},\n\n"
            f"I was looking at {company} and had a practical GTM ops thought. "
            "For AI startups, the painful part is usually not writing one good email; "
            "it is keeping account research, fit scoring, proof points, follow-ups, and next actions in one operating loop.\n\n"
            "I built an open-source AI GTM Command Center that turns a target-account CSV into a scored draft queue "
            "with source-backed personalization and follow-up notes for founder approval.\n\n"
            "If useful, I can share the repo and also build a 10-account pilot around your ICP.\n\n"
            "Best,\n"
            "Shubham\n"
            "https://linkedin.com/in/shubham9616"
        )
        follow_up = (
            f"Hi {person}, quick follow-up.\n\n"
            "The useful part is the operating loop: each account gets research, a fit score, draft copy, "
            "and a next action without turning outreach into an uncontrolled email bot.\n\n"
            "Happy to share the open-source repo or build a small pilot using your target-account list."
        )

        return {
            "fit_score": score,
            "priority": priority_from_score(score),
            "score_rationale": (
                f"{company} looks like a {priority_from_score(score).lower()}-priority account because the available "
                "signals suggest founder-led GTM work where lightweight AI operations can save time."
            ),
            "pain_hypotheses": pain_hypotheses[:5],
            "personalization_points": personalization[:4],
            "suggested_offer_angle": (
                "Open-source AI GTM workflow plus a small Founder's Office pilot: source-backed account research, "
                "fit scoring, and approved outreach drafts."
            ),
            "cold_email_subject": subject,
            "cold_email_body": body,
            "follow_up_subject": f"Re: {subject}",
            "follow_up_body": follow_up,
            "likely_objections": [
                "We already use a CRM or sales engagement tool.",
                "AI-generated outreach may sound generic.",
                "This is useful, but we do not want another dashboard.",
            ],
            "talk_track": [
                "Start with the founder's current target-account workflow and where follow-up breaks.",
                "Show the draft queue and explain why sending stays human-approved.",
                "Offer a 10-account pilot with before/after time saved and reply-quality review.",
            ],
        }


class GeminiProvider(LLMProvider):
    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise LLMError("GEMINI_API_KEY is not set.")

    def synthesize(self, research: AccountResearch, sender_persona: str) -> dict[str, Any]:
        try:
            from google import genai  # type: ignore
        except ImportError as exc:
            raise LLMError("Install Gemini support with: pip install -e '.[gemini]'") from exc

        client = genai.Client(api_key=self.api_key)
        prompt = build_account_prompt(research, sender_persona)
        response = client.models.generate_content(
            model=self.model,
            contents=f"{SYSTEM_PROMPT}\n\n{prompt}",
            config={"response_mime_type": "application/json"},
        )
        return extract_json_object(response.text or "{}")


class GroqProvider(LLMProvider):
    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise LLMError("GROQ_API_KEY is not set.")

    def synthesize(self, research: AccountResearch, sender_persona: str) -> dict[str, Any]:
        prompt = build_account_prompt(research, sender_persona)
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            raise LLMError(f"Groq request failed: {exc}") from exc

        content = data["choices"][0]["message"]["content"]
        return extract_json_object(content)


def get_provider(name: str) -> LLMProvider:
    normalized = name.lower().strip()
    if normalized == "mock":
        return MockProvider()
    if normalized == "gemini":
        return GeminiProvider()
    if normalized == "groq":
        return GroqProvider()
    raise ValueError(f"Unknown provider: {name}. Use mock, gemini, or groq.")
