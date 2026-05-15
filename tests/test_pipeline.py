from pathlib import Path
import csv
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gtm_command_center.llm import MockProvider, extract_json_object
from gtm_command_center.models import TargetAccount
from gtm_command_center.pipeline import load_targets, recommend_accounts
from gtm_command_center.reporting import write_outputs


class PipelineTests(unittest.TestCase):
    def test_extract_json_from_fenced_response(self) -> None:
        parsed = extract_json_object('```json\n{"fit_score": 80, "priority": "High"}\n```')
        self.assertEqual(parsed["fit_score"], 80)

    def test_load_targets_requires_company_and_website(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "targets.csv"
            path.write_text("company,website\nAcme,https://example.com\n", encoding="utf-8")
            accounts = load_targets(path)
        self.assertEqual(accounts[0].company, "Acme")

    def test_mock_provider_generates_ranked_recommendation(self) -> None:
        accounts = [
            TargetAccount(
                company="Acme",
                website="https://example.com",
                segment="B2B SaaS",
                industry="Revenue Operations",
                funding_stage="Seed",
                target_person="Asha Rao",
                target_role="Founder",
                linkedin_url="https://linkedin.com/in/example",
                notes="Seed founder-led revenue pipeline with manual follow-up.",
                linkedin_notes="Recent post about pipeline hygiene.",
            )
        ]
        recommendations = recommend_accounts(
            accounts,
            provider=MockProvider(),
            sender_persona="AI founder office operator",
            offline=True,
        )
        self.assertEqual(len(recommendations), 1)
        self.assertGreaterEqual(recommendations[0].fit_score, 75)
        self.assertIn("draft queue", recommendations[0].cold_email_body.lower())
        self.assertIn("Open the LinkedIn profile manually", recommendations[0].approach_strategy)
        self.assertLessEqual(len(recommendations[0].linkedin_connection_note), 200)
        self.assertIn("thanks for connecting", recommendations[0].linkedin_dm_body.lower())
        self.assertEqual(recommendations[0].segment, "B2B SaaS")

    def test_write_outputs_includes_crm_import(self) -> None:
        accounts = [
            TargetAccount(
                company="Acme",
                website="https://example.com",
                segment="B2B SaaS",
                industry="Revenue Operations",
                funding_stage="Seed",
                target_person="Asha Rao",
                target_role="Founder",
                email="asha@example.com",
                linkedin_url="https://linkedin.com/in/example",
                notes="Seed founder-led revenue pipeline with manual follow-up.",
            )
        ]
        recommendations = recommend_accounts(
            accounts,
            provider=MockProvider(),
            sender_persona="AI founder office operator",
            offline=True,
        )

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            write_outputs(recommendations, out_dir)
            with (out_dir / "crm_import.csv").open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["company"], "Acme")
        self.assertEqual(rows[0]["contact"], "Asha Rao")
        self.assertEqual(rows[0]["email"], "asha@example.com")
        self.assertEqual(rows[0]["segment"], "B2B SaaS")
        self.assertEqual(rows[0]["score"], str(recommendations[0].fit_score))
        self.assertIn("Open the LinkedIn profile manually", rows[0]["next_action"])
        self.assertIn("owner", rows[0])


if __name__ == "__main__":
    unittest.main()
