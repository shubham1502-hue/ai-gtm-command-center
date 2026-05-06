import unittest

from gtm_command_center.fundraising_scout import (
    choose_repo_angle,
    extract_amount,
    extract_company,
    extract_round,
    infer_industry,
)


class FundraisingScoutTests(unittest.TestCase):
    def test_extract_company_amount_and_round(self) -> None:
        headline = "Acme AI raises $5 million in seed funding"

        self.assertEqual(extract_company(headline), "Acme AI")
        self.assertEqual(extract_amount(headline), "$5 million")
        self.assertEqual(extract_round(headline), "Seed")

    def test_extract_company_from_startup_headline(self) -> None:
        self.assertEqual(extract_company("Exclusive: AI grocery startup Vori raises $22 million"), "Vori")
        self.assertEqual(extract_company("Silo founder raises €25m for quantum computing"), "Silo")

    def test_infer_industry_and_repo_angle(self) -> None:
        industry = infer_industry("Fintech startup raises Series A for lending infrastructure")
        repo_angle, dm_angle = choose_repo_angle(industry, "lending infrastructure")

        self.assertEqual(industry, "Fintech")
        self.assertIn("Collections", repo_angle)
        self.assertIn("risk", dm_angle)


if __name__ == "__main__":
    unittest.main()
