# Recent Fundraising Founder Outreach Workflow

This workflow finds public fundraising signals, turns them into founder research rows, and keeps LinkedIn outreach manual.

It does not scrape LinkedIn, bypass paywalls, or send automated DMs.

## Why Recently Funded Founders

Recent fundraising creates operating pressure:

- new investors expect better updates
- hiring and GTM motion accelerate
- founders need sharper weekly operating cadence
- messy CRM, metrics, and reporting workflows start breaking
- teams need systems before they hire full BizOps, RevOps, or Founder Office capacity

That is why your repos are relevant if the message maps one funding signal to one operating problem.

## Step 1: Run The Scout

```bash
python -m gtm_command_center.fundraising_scout \
  --days 45 \
  --out outputs/fundraising-scout
```

Outputs:

- `fundraising_leads.csv`: company, source, amount, round, industry, repo angle
- `target_accounts_from_fundraising.csv`: starter CSV for GTM Command Center
- `founder_outreach_tracker_import.csv`: starter rows for the outreach tracker

## Step 2: Manually Verify The Founder

For each company:

1. Open the funding source.
2. Confirm the company actually raised recently.
3. Find the founder manually on LinkedIn.
4. Copy the founder profile URL into `target_accounts_from_fundraising.csv`.
5. Add 1-2 notes from public LinkedIn posts.
6. Add the company website if the scout did not capture it.

Do not scrape LinkedIn. Do not use private data.

## Step 3: Generate DM Drafts

```bash
python -m gtm_command_center run \
  --targets outputs/fundraising-scout/target_accounts_from_fundraising.csv \
  --persona examples/persona.md \
  --provider mock \
  --offline \
  --out outputs/funding-dm-drafts
```

Open:

- `linkedin_dm_queue.csv`
- `gtm_brief.md`
- `founder_outreach_tracker_import.csv`

## Step 4: Message Manually

Use this structure:

```text
Hi {Name}, congrats on the recent {round/raise} at {Company}.

Usually after a raise, the operating pressure shifts to {specific system: GTM cadence, investor updates, RevOps, metrics, ops visibility}.

I built a forkable {repo name} for that exact workflow.
Open to me sending it for feedback?
```

Keep it short. Do not attach five repos. Send one artifact.

## Step 5: Track In The Sheet

Use the `fundraising-prospects` tab for leads you have not messaged yet.

Move the founder into `sheet-template` once you send or draft the message.

Recommended status values:

- Funding lead found
- Founder profile needed
- Draft ready
- Connection note sent
- Message sent
- Follow-up draft ready
- Replied
- Closed

## Good Repo Mapping

| Funding Signal | Likely Pain | Repo To Share |
|---|---|---|
| AI/SaaS seed round | founder-led GTM, account research, follow-up discipline | AI GTM Command Center |
| Board/investor-heavy raise | investor reporting, metric narrative | Board Pack / Investor Update Agent |
| Scaling GTM team | CRM, pipeline, reporting, handoffs | RevOps Infrastructure Playbook |
| Fintech/lending raise | risk, collections, repayment visibility | Collections Strategy Engine |
| Payments raise | monitoring, fraud signals, business KPIs | Payments Monitoring / Payments Business Management |
| D2C/consumer raise | pricing, retention, ops cadence | D2C Pricing Strategy Framework |
| Any early-stage raise | weekly cadence, risks, priorities, investor-safe updates | Founder Weekly Operating Review Agent |
