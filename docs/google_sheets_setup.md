# Google Sheets Setup

This workflow is optional. The command center works without Google credentials and always writes local CSV, Markdown, JSON, and HTML outputs.

Use Sheets sync when you want a founder-style draft queue that can be reviewed, assigned, filtered, and handed off.

## Why Sheets, Not Gmail Sending

For a Founder's Office portfolio project, Google Sheets is the stronger default:

- It is free-tier friendly.
- It preserves human approval before outreach.
- It looks like an operating system, not a spam bot.
- It can be reviewed by founders, GTM teams, or assistants without running Python.

## Setup

1. Create a Google Cloud project.
2. Enable the Google Sheets API.
3. Create a service account.
4. Download the service account JSON key.
5. Create a Google Sheet.
6. Share the Sheet with the service account email, usually ending in `iam.gserviceaccount.com`.
7. Copy `.env.example` to `.env`.
8. Add:

```bash
GOOGLE_SHEET_ID=your_google_sheet_id
GOOGLE_SERVICE_ACCOUNT_JSON=/absolute/path/to/service-account.json
GOOGLE_WORKSHEET_NAME=Draft Queue
```

Install the optional dependency:

```bash
python -m pip install -e '.[sheets]'
```

Run:

```bash
python -m gtm_command_center run \
  --targets examples/target_accounts.csv \
  --persona examples/persona.md \
  --provider mock \
  --offline \
  --sync-sheets
```

## What Gets Synced

The worksheet receives the same fields as `outputs/<run>/draft_queue.csv`:

- account name and website
- fit score and priority
- score rationale
- offer angle
- draft email and follow-up
- pain hypotheses
- personalization points
- likely objections
- call talk track
- source links and warnings

## Free-Tier Notes

This sync does not use paid LLM calls. Google Sheets API quotas are more than enough for small founder-facing demos and weekly workflows.

