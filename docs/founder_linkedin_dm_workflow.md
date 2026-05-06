# Founder LinkedIn DM Workflow

This workflow is for research and drafting only. It does not scrape LinkedIn, automate connection requests, or send DMs.

LinkedIn's user agreement restricts bots, scraping, and automated messaging. Treat this repo as the operating system before the send button: research, prioritization, draft quality, and follow-up discipline.

## Workflow

### 1. Define the founder segment

Start with one narrow segment for each batch.

Good examples:

- Seed-stage AI SaaS founders hiring their first GTM/operator.
- Fintech founders with payments, collections, or risk workflows.
- EdTech founders with RevOps, reporting, or sales handoff problems.
- B2B SaaS founders posting about pipeline quality, activation, churn, or investor reporting.

Bad examples:

- Any founder.
- Any startup.
- Anyone hiring.

Narrow segments make your message sharper and make it easier to choose the right repo to share.

### 2. Build the target CSV manually

Use `examples/target_accounts.csv` as the shape.

Recommended columns:

```csv
company,website,segment,industry,funding_stage,target_person,target_role,linkedin_url,email,notes,linkedin_notes,industry_notes
```

How to fill it:

- `company`: company name
- `website`: company website, not LinkedIn
- `segment`: short operating segment, for example AI SaaS or Fintech Payments
- `industry`: specific industry context
- `funding_stage`: bootstrapped, pre-seed, seed, Series A, etc.
- `target_person`: founder name
- `target_role`: founder, CEO, COO, chief of staff, etc.
- `linkedin_url`: manually copied LinkedIn profile URL
- `notes`: why this company could benefit from your toolkit
- `linkedin_notes`: public details you manually observed on the profile or posts
- `industry_notes`: what the industry likely cares about

Do not use private, sensitive, or scraped data.

### 3. Run the workflow

Offline, using only your CSV notes:

```bash
python -m gtm_command_center run \
  --targets examples/target_accounts.csv \
  --persona examples/persona.md \
  --provider mock \
  --offline \
  --out outputs/founder-dm-demo
```

With public website and Google News RSS research:

```bash
python -m gtm_command_center run \
  --targets examples/target_accounts.csv \
  --persona examples/persona.md \
  --provider mock \
  --out outputs/founder-dm-demo
```

Outputs:

- `linkedin_dm_queue.csv`: manual LinkedIn connection note, DM, follow-up, checklist
- `founder_outreach_tracker_import.csv`: import-ready rows for `founder-outreach-tracker`
- `draft_queue.csv`: full account scoring and outreach detail
- `gtm_brief.md`: human-readable review brief
- `gtm_report.html`: browser-friendly review report

### 4. Review before sending

For every founder, manually verify:

- latest LinkedIn posts
- current hiring or fundraising signals
- company ICP and product category
- one specific problem your repo maps to
- whether your message sounds like a useful operator, not a seller

If the message could be sent to 50 founders unchanged, it is not specific enough.

### 5. Send manually

Use the generated connection note only after editing it.

LinkedIn's help currently describes a limited number of personalized connection notes for free accounts and a 200-character limit. Check the current UI before sending because product limits can change.

After the founder accepts or if DMs are open, send the generated DM only if it passes this test:

> Would I send this if I were optimizing for long-term reputation, not short-term replies?

### 6. Track follow-ups

Import `founder_outreach_tracker_import.csv` into the `founder-outreach-tracker` sheet.

After you manually send a DM, update:

- `Stage` -> `Message Sent`
- `Message Sent Date` -> today's date
- `Last Activity Date` -> today's date
- `Next Action` -> expected follow-up action

The tracker can then remind you when follow-up is due.

## Message Patterns

### Connection note

Use this shape:

```text
Hi {Name}, liked how {Company} is building in {specific space}. I build founder-ops tools and made a forkable {relevant workflow}. Open to connect?
```

### First DM after connection

Use this shape:

```text
Thanks for connecting, {Name}.

I was looking at {Company} and noticed {specific operating context}. I built a forkable repo that helps with {problem}. It is not a pitch deck or generic automation; it is a working template founders can adapt.

Open to me sending the repo for feedback?
```

### Follow-up

Use this shape:

```text
Quick follow-up, {Name}. The useful part is the operating loop, not the code itself. If {problem} is on your plate, happy to send the repo most relevant to it.
```

## Scoring Rule

Prioritize founders where at least three are true:

- founder is active on LinkedIn
- company is in a segment your repos directly serve
- there is a current operating pain signal
- the founder is hiring, fundraising, launching, or scaling GTM
- you can map one repo to one specific problem
- you can write a non-generic first sentence

Skip founders where:

- the company context is unclear
- the only reason is "startup founder"
- your message would be mostly about you needing a job
- you cannot name the problem your repo helps solve
