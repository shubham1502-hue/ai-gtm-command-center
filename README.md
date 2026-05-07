# AI GTM Command Center

Pre-call GTM command center for founder-led account research, ICP scoring, outreach drafts, and call prep.

<!-- FOUNDER_OS_STANDARD_README -->

## The founder problem

Founders often run outbound from browser tabs, CRM notes, LinkedIn profiles, and half-written drafts. They do not need more activity. They need a repeatable workflow that turns account context into clear research, call prep, and human-approved outreach.

## What this repo does

- scores target accounts against ICP signals
- generates account briefs and pain hypotheses
- creates reviewable email and LinkedIn draft queues
- exports tracker-ready CSVs
- keeps optional AI providers separate from the deterministic demo path

## What a founder gets in 10 minutes

- ranked account list
- GTM brief
- draft outreach queue
- LinkedIn DM queue
- founder outreach tracker import
- HTML report and JSON recommendations

## Before and after

Before:

- target accounts spread across sheets and tabs
- unclear ICP fit
- outreach drafts written from scratch
- call prep dependent on founder memory

After:

- scored account workflow
- founder-ready briefs
- human-approved draft queue
- tracker-ready follow-up artifacts

## Who this is for

- early-stage founders
- GTM operators
- Founder's Office teams
- RevOps operators
- startup generalists
- AI-native startup teams

## Quick start

- Run `python -m pip install -e .`.
- Run `python -m gtm_command_center run --targets examples/target_accounts.csv --persona examples/persona.md --out docs/demo_output --offline`.
- Open `docs/demo_output/gtm_brief.md` first.
- Review `docs/demo_output/draft_queue.csv` before sending anything.

## How to fork and use this for your company

1. Click Fork.
2. Rename the repo if needed.
3. Replace `examples/target_accounts.csv` with your own accounts.
4. Keep optional API keys in `.env`, never in committed files.
5. Run the demo path first before connecting Gemini, Groq, or Google Sheets.
6. Move approved outputs into HubSpot, Pipedrive, Attio, Airtable, Google Sheets, or your outreach tracker.

### Non-technical path

- Replace one file: `examples/target_accounts.csv`.
- Run one command from the Quick start section.
- Read one memo first: `docs/demo_output/gtm_brief.md`.
- Send nothing until a human reviews the drafts.

## Input format

- target account CSV with company, website, segment, use case, funding stage, contact fields, notes, and evidence
- optional provider settings in `.env`
- founder-approved ICP and messaging assumptions

The default sample data and examples are synthetic, anonymized, or template-only unless the repo explicitly documents a public source. Keep private customer, prospect, employee, investor, borrower, merchant, payment, or company data out of public forks.

## Output files

- `docs/demo_output/gtm_brief.md`: founder call-prep brief
- `docs/demo_output/draft_queue.csv`: outbound drafts for review
- `docs/demo_output/linkedin_dm_queue.csv`: LinkedIn DM drafts
- `docs/demo_output/founder_outreach_tracker_import.csv`: tracker import file
- `docs/demo_output/gtm_report.html`: reviewable report
- `docs/demo_output/recommendations.json`: structured recommendations

## Example founder workflow

- Monday: add target accounts.
- Tuesday: run the command center.
- Wednesday: review account briefs and draft queues.
- Thursday: move approved actions into CRM or tracker.
- Friday: compare replies and update ICP assumptions.

## Customization guide

Customize these before using the repo for a real company:

- ICP scoring signals
- target account fields
- outreach tone
- LLM provider choice
- Google Sheets sync
- CRM import columns

## Where this fits in the Founder OS

`ai-gtm-command-center` sits before `founder-led-sales-call-os`. Use it for pre-call research and outreach. Use `founder-led-sales-call-os` after calls. Connect both to `founder-outreach-tracker` and `founder-os-revenue-engine` for follow-up and revenue diagnosis.

## Why this matters

This is not an outreach spam generator. It is a founder-controlled GTM workflow for preparing better conversations and tracking the next action.

## Roadmap

- HubSpot, Pipedrive, and Attio sync
- Google Sheets two-way updates
- Notion account brief export
- Slack review queue
- weekly GTM review integration

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) if present. Practical improvements are welcome when they make the workflow easier to fork, run, or adapt.

## License

MIT License. See [LICENSE](LICENSE).

## Built by

Built by Shubham Singh, a founder-facing operator focused on RevOps, GTM systems, startup metrics, AI workflows, and operating systems for early-stage teams.

## Use this in your company

Fork it, replace the sample inputs with your company context, and run the workflow. Start with the main output listed in the Quick Start section. Keep private data out of public forks.

## If you are a Founder's Office candidate

Use this repo to understand how a founder-facing operator turns messy inputs into decisions, cadence, and execution artifacts. Fork it, adapt it to a real company example, and write a short case note explaining what changed.

---

## Detailed implementation notes

The founder-facing guide above is the fastest path. The original repo-specific notes are preserved below for deeper implementation context.

## Problem This Solves

Early-stage founders often run GTM from scattered CSVs, browser tabs, notes, and half-written follow-ups. The problem is not just writing outreach. It is turning messy account context into a repeatable founder-approved sales workflow.

## How It Helps

- Turns a target-account CSV into scored account briefs, pain hypotheses, talk tracks, email drafts, follow-ups, and reviewable outputs.
- Keeps the workflow human-approved so founders get leverage without turning their brand into a spam machine.
- Runs offline with a mock provider for demos, then upgrades to Gemini, Groq, and optional Google Sheets sync.

## When To Fork This

- Fork this if you are a founder, founder's office hire, RevOps operator, or GTM analyst building a first outbound operating system.
- Fork it when your account research, ICP scoring, and follow-up discipline are living in too many places.
- Customize the persona, target CSV columns, scoring rubric, prompt, and Google Sheet output around your own ICP.

I built this because most early-stage AI founders do not have their GTM work in one clean place.

The account list is in a CSV. Research is in browser tabs. Follow-ups are in someone's head. ICP judgment is partly intuition. Email drafts are written from scratch every time. By the time the founder sits down to sell, the actual operating system is still missing.

This repo is how I would start fixing that.

## Use This In Your Company

This repo is designed to be forked into an internal company workflow. Fork it, replace the sample inputs with your company context, and keep only the parts that match your operating cadence. No permission request or sales call is needed before using it; the repo is the handoff. Check the license if you plan to redistribute your version.

- Use it as a founder-approved GTM research queue before any outreach is sent.
- Keep the pipeline: target CSV -> research -> fit score -> founder call notes -> manual DM/email draft -> tracker import.
- Replace only the target accounts, sender persona, and repo/offer angle for your company.

## Minimum Edits To Make It Yours

Change these first:

| Edit | Where | Why |
|---|---|---|
| Replace the target account list. | `examples/target_accounts.csv` | This is the core input; every account score, brief, and outreach draft depends on it. |
| Rewrite the sender/company context. | `examples/persona.md` | Makes the output sound like your founder, product, market, and offer. |
| Tune the ICP and scoring assumptions. | `src/gtm_command_center/prompts.py` | Changes what the system considers a high-fit account. |
| Add your tracker destination only if needed. | `.env` / Google Sheets setup | Keeps the first run simple if you only want local CSV outputs. |

You can leave the report templates, mock provider, provider integrations, and LinkedIn-safety guardrails alone on the first fork. Start with offline output, review the drafts manually, then connect Sheets or an LLM provider.

## What This Does

AI GTM Command Center takes a CSV of target accounts and turns it into a founder-ready GTM workbench.

For each company, it creates:

- account research
- ICP fit score
- priority level
- pain hypotheses
- personalization points
- founder-call talk track
- likely objections
- cold email draft
- follow-up draft
- source links and warnings

It is intentionally draft-only. I do not want this to be a spam bot. I want it to be the system before the send button: research, judgment, prioritization, and clean follow-up discipline.

## After the sales call

Use AI GTM Command Center before calls to research accounts, prepare outreach, and build founder-call briefs. After calls, use [Founder-Led Sales Call OS](https://github.com/shubham1502-hue/founder-led-sales-call-os) to extract objections, deal risks, follow-up priorities, and narrative experiments from actual sales conversations.

If GTM work is becoming repetitive or ops-heavy, use [Founder AI Workflow ROI OS](https://github.com/shubham1502-hue/founder-ai-workflow-roi-os) to decide which research, follow-up, CRM hygiene, or reporting workflows are worth automating.

## Why I Built This

I approached this as a Founder's Office candidate, not as someone trying to ship another generic AI wrapper.

At STEMpedia, I built RevOps infrastructure from scratch inside a founder-led startup: CRM workflows, reporting, handoffs, automations, and weekly CEO visibility. That taught me something simple: founders do not just need analysis. They need systems that reduce the number of things they personally have to remember.

This project is built from that lens.

If I were working with an AI startup founder, this is the kind of workflow I would want to build in week one: take a messy GTM motion, make the work visible, use AI where it saves time, and keep the final judgment with the human.

## Example Output

Demo files are committed in [docs/demo_output](docs/demo_output):

- [GTM brief](docs/demo_output/gtm_brief.md)
- [HTML GTM report](docs/demo_output/gtm_report.html)
- [Founder approval draft queue](docs/demo_output/draft_queue.csv)
- [Structured recommendations JSON](docs/demo_output/recommendations.json)

```text
ContextLayer AI - 96/100 (High)

Why this account:
ContextLayer AI looks like a high-priority account because the available signals suggest founder-led GTM work where lightweight AI operations can save time.

Offer angle:
Open-source AI GTM workflow plus a small Founder's Office pilot: source-backed account research, fit scoring, and approved outreach drafts.

Draft email:
Subject: ContextLayer AI GTM workflow idea

Hi Aarav Mehta,

I was looking at ContextLayer AI and had a practical GTM ops thought. For AI startups,
the painful part is usually not writing one good email; it is keeping account research,
fit scoring, proof points, follow-ups, and next actions in one operating loop.

I built an open-source AI GTM Command Center that turns a target-account CSV into a scored
draft queue with source-backed personalization and follow-up notes for founder approval.

If useful, I can share the repo and also build a 10-account pilot around your ICP.
```

## How It Works

```mermaid
flowchart LR
  CSV["Target accounts CSV"] --> Research["Research collector"]
  Research --> Sources["Homepage + Google News RSS + operator notes"]
  Sources --> Prompt["GTM reasoning prompt"]
  Persona["Sender positioning"] --> Prompt
  Prompt --> LLM["Gemini / Groq / Mock provider"]
  LLM --> Normalize["Structured recommendation"]
  Normalize --> Outputs["CSV + Markdown + JSON + HTML"]
  Normalize --> Sheets["Optional Google Sheets draft queue"]
```

The system is deliberately simple:

1. Start with a CSV of target accounts.
2. Pull lightweight public context from the company website and Google News RSS.
3. Combine that with operator notes.
4. Ask the LLM to reason through fit, pain, personalization, objections, and outreach.
5. Export everything into files a founder or GTM team can actually review.
6. Optionally sync the draft queue to Google Sheets.

## Why This Is AI-Native

I am not using AI here as a novelty layer.

The LLM is doing the work that is usually slow, repetitive, and judgment-heavy:

- turning messy context into a structured account brief
- generating a first-pass outreach angle
- identifying what should be validated before a founder reaches out
- keeping the output in a format that can move into an operating workflow

The important part is not the model name. It can run with Gemini, Groq, or a deterministic mock provider. The important part is the operating loop around the model.

## What Founders Can Use This For

- Build a first-pass outbound list for founder-led sales.
- Score which accounts deserve attention first.
- Create a human-approved draft queue.
- Give an intern, analyst, or founder's office hire a cleaner GTM workflow.
- Turn scattered account research into a weekly operating habit.

This is especially useful for early AI startups where the founder is still close to sales, positioning, product feedback, and investor narrative.

## Stack

- Python
- Gemini API or Groq API
- Google News RSS
- Robots-aware website fetching
- CSV, Markdown, JSON, and HTML outputs
- Optional Google Sheets sync

The default demo runs with no API key.

## Quickstart

Run the demo:

```bash
python -m pip install -e .

python -m gtm_command_center run \
 --targets examples/target_accounts.csv \
 --persona examples/persona.md \
 --provider mock \
 --offline \
 --out outputs/demo
```

Then open:

- `outputs/demo/gtm_report.html`
- `outputs/demo/gtm_brief.md`
- `outputs/demo/draft_queue.csv`
- `outputs/demo/linkedin_dm_queue.csv`
- `outputs/demo/founder_outreach_tracker_import.csv`

## Manual LinkedIn Founder DM Workflow

This repo now supports a LinkedIn-safe founder research workflow:

1. Manually collect founder and company context into `examples/target_accounts.csv`.
2. Run the command center to score accounts and draft outreach.
3. Open `linkedin_dm_queue.csv` to review connection notes, first DMs, follow-ups, and the manual research checklist.
4. Manually open LinkedIn, validate the founder's current context, edit the draft, and send yourself.
5. Import `founder_outreach_tracker_import.csv` into [founder-outreach-tracker](https://github.com/shubham1502-hue/founder-outreach-tracker) after sending so follow-ups do not slip.

Full workflow: [docs/founder_linkedin_dm_workflow.md](docs/founder_linkedin_dm_workflow.md)

## Recent Fundraising Scout

You can also find public fundraising signals and convert them into outreach research rows:

```bash
python -m gtm_command_center.fundraising_scout \
 --days 45 \
 --out outputs/fundraising-scout
```

This writes:

- `fundraising_leads.csv`
- `target_accounts_from_fundraising.csv`
- `founder_outreach_tracker_import.csv`

Full workflow: [docs/recent_fundraising_outreach_workflow.md](docs/recent_fundraising_outreach_workflow.md)

## Using Gemini

Gemini is the easiest free-tier-first option for this project.

```bash
python -m pip install -e '.[gemini]'
cp .env.example .env
# Add GEMINI_API_KEY to .env

python -m gtm_command_center run \
 --targets examples/target_accounts.csv \
 --persona examples/persona.md \
 --provider gemini \
 --out outputs/gemini-run
```

## Using Groq

Groq is useful as a fast fallback provider.

```bash
cp .env.example .env
# Add GROQ_API_KEY to .env

python -m gtm_command_center run \
 --targets examples/target_accounts.csv \
 --persona examples/persona.md \
 --provider groq \
 --out outputs/groq-run
```

## Optional Google Sheets Sync

I added Google Sheets sync because it matches how founder teams actually work.

Not every founder wants to run Python. But every founder understands a sheet with account, score, rationale, draft, follow-up, and next action.

```bash
python -m pip install -e '.[sheets]'
cp .env.example .env
# Add GOOGLE_SHEET_ID and GOOGLE_SERVICE_ACCOUNT_JSON to .env
# Share the Google Sheet with the service-account email.

python -m gtm_command_center run \
 --targets examples/target_accounts.csv \
 --persona examples/persona.md \
 --provider mock \
 --offline \
 --sync-sheets
```

Setup notes: [docs/google_sheets_setup.md](docs/google_sheets_setup.md)

## Input Format

Minimum CSV:

```csv
company,website
Acme,https://example.com
```

Recommended CSV:

```csv
company,website,segment,industry,funding_stage,target_person,target_role,linkedin_url,email,notes,linkedin_notes,industry_notes
Acme,https://example.com,B2B SaaS,Revenue Operations,Seed,Asha Rao,Founder,https://linkedin.com/in/example,asha@example.com,"Seed-stage founder-led sales motion.","Recent post about pipeline hygiene.","B2B SaaS founders care about pipeline quality and activation."
```

## Safety Choices

I made a few opinionated choices on purpose:

- No LinkedIn scraping.
- No LinkedIn auto-DMs or connection automation.
- No automatic email sending.
- Drafts require human approval.
- Sources and warnings stay visible.
- The model is told not to invent facts or imply a prior relationship.

That matters because founder-facing automation should create leverage without creating reputational risk.

## Author Note

Built by Shubham Singh, focused on AI-native operating systems for early-stage founders.

I have built RevOps infrastructure from scratch at a founder-led startup, including CRM workflows, reporting, handoffs, automations, and weekly CEO visibility.

- LinkedIn: <https://linkedin.com/in/shubham9616>
- GitHub: <https://github.com/shubham1502-hue>
