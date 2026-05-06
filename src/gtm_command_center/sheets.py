from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .models import GTMRecommendation
from .reporting import DRAFT_QUEUE_FIELDNAMES


class SheetsSyncError(RuntimeError):
    pass


def build_sheet_values(recommendations: list[GTMRecommendation]) -> list[list[Any]]:
    rows: list[list[Any]] = [DRAFT_QUEUE_FIELDNAMES]
    for recommendation in recommendations:
        flat = recommendation.as_flat_row()
        rows.append([flat.get(field, "") for field in DRAFT_QUEUE_FIELDNAMES])
    return rows


def sync_to_google_sheets(
    recommendations: list[GTMRecommendation],
    spreadsheet_id: str,
    worksheet_name: str = "Draft Queue",
    service_account_json: Path | None = None,
) -> str:
    try:
        import gspread  # type: ignore
    except ImportError as exc:
        raise SheetsSyncError("Install Google Sheets support with: pip install -e '.[sheets]'") from exc

    credentials_path = service_account_json or _env_service_account_path()
    if not credentials_path:
        raise SheetsSyncError(
            "Set --service-account-json or GOOGLE_SERVICE_ACCOUNT_JSON to a Google service account JSON file."
        )
    if not credentials_path.exists():
        raise SheetsSyncError(f"Google service account JSON file was not found: {credentials_path}")

    client = gspread.service_account(filename=str(credentials_path))
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = _get_or_create_worksheet(spreadsheet, worksheet_name, row_count=max(len(recommendations) + 5, 20))
    values = build_sheet_values(recommendations)
    worksheet.clear()
    worksheet.update(values=values, range_name="A1", value_input_option="USER_ENTERED")
    _format_sheet(worksheet, len(values), len(DRAFT_QUEUE_FIELDNAMES))
    return worksheet.url


def _env_service_account_path() -> Path | None:
    value = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    return Path(value).expanduser() if value else None


def _get_or_create_worksheet(spreadsheet: Any, name: str, row_count: int) -> Any:
    try:
        return spreadsheet.worksheet(name)
    except Exception:  # noqa: BLE001 - gspread raises library-specific exceptions.
        return spreadsheet.add_worksheet(title=name, rows=row_count, cols=len(DRAFT_QUEUE_FIELDNAMES))


def _format_sheet(worksheet: Any, row_count: int, col_count: int) -> None:
    try:
        worksheet.freeze(rows=1)
        worksheet.format("1:1", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.9, "green": 0.95, "blue": 1}})
        worksheet.resize(rows=max(row_count, 20), cols=col_count)
    except Exception:
        return
