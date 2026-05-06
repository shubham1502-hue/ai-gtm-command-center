from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gtm_command_center.llm import MockProvider, extract_json_object
from gtm_command_center.models import TargetAccount
from gtm_command_center.pipeline import load_targets, recommend_accounts


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
                notes="Seed founder-led revenue pipeline with manual follow-up.",
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


if __name__ == "__main__":
    unittest.main()
