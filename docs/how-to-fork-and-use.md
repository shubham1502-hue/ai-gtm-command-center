# How to fork and use AI GTM Command Center

This guide is for a founder or operator who wants to adapt the repo without turning it into a generic portfolio project.

## First pass

1. Fork the repo.
2. Rename it for your company or operating workflow.
3. Read the README Quick Start section.
4. Replace sample inputs, templates, or context files with your own company context.
5. Run the workflow if executable, or copy the first template if it is a playbook.
6. Open the main output listed in the README before changing deeper logic.

## Company fork path

1. Click Fork.
2. Rename the repo if needed.
3. Replace `examples/target_accounts.csv` with your own accounts.
4. Keep optional API keys in `.env`, never in committed files.
5. Run the demo path first before connecting Gemini, Groq, or Google Sheets.
6. Move approved outputs into HubSpot, Pipedrive, Attio, Airtable, Google Sheets, or your outreach tracker.

## Non-technical path

- Replace one file: `examples/target_accounts.csv`.
- Run one command from the Quick start section.
- Read one memo first: `docs/demo_output/gtm_brief.md`.
- Send nothing until a human reviews the drafts.

## Data safety

The included sample data is synthetic, anonymized, or template-only unless a public source is explicitly documented. Do not commit private customer, prospect, employee, investor, borrower, merchant, payment, or company data to a public fork.

## Tools to connect later

Start with files first. After the workflow is useful, connect outputs to Google Sheets, Notion, Airtable, HubSpot, Pipedrive, Attio, Linear, Asana, ClickUp, Slack, or your internal ops tracker where relevant.
