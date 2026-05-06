from __future__ import annotations

import argparse
import os
from pathlib import Path

from .llm import LLMError, get_provider
from .pipeline import load_persona, load_targets, recommend_accounts
from .reporting import write_outputs
from .sheets import SheetsSyncError, sync_to_google_sheets
from .utils import utc_run_id


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gtm-command-center",
        description="Run AI-native GTM account research, scoring, and draft generation.",
    )
    parser.add_argument(
        "run",
        nargs="?",
        default="run",
        help="Command to run. Currently only 'run' is supported.",
    )
    parser.add_argument("--targets", required=True, type=Path, help="CSV with company and website columns.")
    parser.add_argument("--persona", type=Path, help="Markdown file describing the sender persona and offer.")
    parser.add_argument("--out", type=Path, help="Output directory. Defaults to outputs/<timestamp>.")
    parser.add_argument("--provider", default="mock", choices=["mock", "gemini", "groq"], help="LLM provider.")
    parser.add_argument("--offline", action="store_true", help="Skip live web/news fetches and use CSV notes only.")
    parser.add_argument("--news-limit", type=int, default=3, help="Maximum Google News RSS items per account.")
    parser.add_argument("--env-file", type=Path, default=Path(".env"), help="Optional env file path.")
    parser.add_argument("--sync-sheets", action="store_true", help="Sync the draft queue to Google Sheets.")
    parser.add_argument("--sheet-id", default="", help="Google spreadsheet ID for --sync-sheets.")
    parser.add_argument("--worksheet", default="", help="Worksheet name for --sync-sheets.")
    parser.add_argument("--service-account-json", type=Path, help="Google service account JSON for Sheets sync.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.run != "run":
        parser.error("Only the 'run' command is supported.")

    load_env(args.env_file)

    out_dir = args.out or Path("outputs") / utc_run_id()
    try:
        accounts = load_targets(args.targets)
        persona = load_persona(args.persona)
        provider = get_provider(args.provider)
        recommendations = recommend_accounts(
            accounts=accounts,
            provider=provider,
            sender_persona=persona,
            offline=args.offline,
            news_limit=args.news_limit,
        )
        write_outputs(recommendations, out_dir)
        sheet_url = ""
        if args.sync_sheets:
            sheet_id = args.sheet_id or os.getenv("GOOGLE_SHEET_ID", "")
            worksheet = args.worksheet or os.getenv("GOOGLE_WORKSHEET_NAME", "Draft Queue")
            if not sheet_id:
                raise SheetsSyncError("Set --sheet-id or GOOGLE_SHEET_ID to sync Google Sheets.")
            sheet_url = sync_to_google_sheets(
                recommendations=recommendations,
                spreadsheet_id=sheet_id,
                worksheet_name=worksheet,
                service_account_json=args.service_account_json,
            )
    except (OSError, ValueError, LLMError, SheetsSyncError) as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Processed {len(recommendations)} accounts.")
    print(f"Draft queue: {out_dir / 'draft_queue.csv'}")
    print(f"LinkedIn DM queue: {out_dir / 'linkedin_dm_queue.csv'}")
    print(f"Tracker import: {out_dir / 'founder_outreach_tracker_import.csv'}")
    print(f"Brief: {out_dir / 'gtm_brief.md'}")
    print(f"HTML report: {out_dir / 'gtm_report.html'}")
    if sheet_url:
        print(f"Google Sheet: {sheet_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
