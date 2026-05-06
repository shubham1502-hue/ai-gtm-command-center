from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gtm_command_center.models import GTMRecommendation
from gtm_command_center.reporting import DRAFT_QUEUE_FIELDNAMES
from gtm_command_center.sheets import build_sheet_values


class SheetsTests(unittest.TestCase):
    def test_build_sheet_values_uses_draft_queue_columns(self) -> None:
        recommendation = GTMRecommendation(
            company="ContextLayer AI",
            website="https://example.com",
            target_person="Aarav Mehta",
            target_role="Founder",
            linkedin_url="https://linkedin.com/in/example",
            industry="AI SaaS",
            funding_stage="Seed",
            fit_score=96,
            priority="High",
            score_rationale="Strong AI startup fit.",
            industry_context="Seed AI SaaS target.",
            approach_strategy="Open LinkedIn manually and validate recent posts.",
            pain_hypotheses=["Founder-led sales needs structure."],
            personalization_points=["AI support workflow"],
            manual_research_checklist=["Check recent posts"],
            suggested_offer_angle="Open-source GTM workflow plus pilot.",
            linkedin_connection_note="Hi Aarav, open to connect?",
            linkedin_dm_body="Thanks for connecting. Useful repo for GTM ops.",
            linkedin_follow_up_body="Quick follow-up.",
            cold_email_subject="GTM workflow idea",
            cold_email_body="Draft body",
            follow_up_subject="Re: GTM workflow idea",
            follow_up_body="Follow-up body",
            likely_objections=["Already have CRM"],
            talk_track=["Show draft queue"],
            sources=[],
        )

        values = build_sheet_values([recommendation])

        self.assertEqual(values[0], DRAFT_QUEUE_FIELDNAMES)
        self.assertEqual(values[1][0], "ContextLayer AI")
        self.assertEqual(values[1][7], 96)


if __name__ == "__main__":
    unittest.main()
