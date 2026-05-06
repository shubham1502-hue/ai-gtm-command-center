from __future__ import annotations

import csv
import html
from pathlib import Path

from .models import GTMRecommendation
from .pipeline import write_json
from .utils import ensure_dir


DRAFT_QUEUE_FIELDNAMES = [
    "company",
    "website",
    "target_person",
    "target_role",
    "linkedin_url",
    "industry",
    "funding_stage",
    "fit_score",
    "priority",
    "score_rationale",
    "industry_context",
    "approach_strategy",
    "suggested_offer_angle",
    "linkedin_connection_note",
    "linkedin_dm_body",
    "linkedin_follow_up_body",
    "cold_email_subject",
    "cold_email_body",
    "follow_up_subject",
    "follow_up_body",
    "pain_hypotheses",
    "personalization_points",
    "manual_research_checklist",
    "likely_objections",
    "talk_track",
    "sources",
    "warnings",
]


def write_outputs(recommendations: list[GTMRecommendation], out_dir: Path) -> None:
    ensure_dir(out_dir)
    write_draft_queue(recommendations, out_dir / "draft_queue.csv")
    write_linkedin_dm_queue(recommendations, out_dir / "linkedin_dm_queue.csv")
    write_tracker_import(recommendations, out_dir / "founder_outreach_tracker_import.csv")
    write_brief(recommendations, out_dir / "gtm_brief.md")
    write_html_report(recommendations, out_dir / "gtm_report.html")
    write_json(out_dir / "recommendations.json", [item.as_flat_row() for item in recommendations])


def write_draft_queue(recommendations: list[GTMRecommendation], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DRAFT_QUEUE_FIELDNAMES)
        writer.writeheader()
        for recommendation in recommendations:
            writer.writerow(recommendation.as_flat_row())


def write_linkedin_dm_queue(recommendations: list[GTMRecommendation], path: Path) -> None:
    fieldnames = [
        "priority",
        "fit_score",
        "target_person",
        "target_role",
        "company",
        "industry",
        "funding_stage",
        "linkedin_url",
        "website",
        "approach_strategy",
        "linkedin_connection_note",
        "linkedin_dm_body",
        "linkedin_follow_up_body",
        "manual_research_checklist",
        "suggested_offer_angle",
        "sources",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in recommendations:
            row = item.as_flat_row()
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_tracker_import(recommendations: list[GTMRecommendation], path: Path) -> None:
    fieldnames = [
        "No.",
        "Contact Name",
        "Company",
        "Role / Title",
        "LinkedIn URL",
        "Message Type",
        "Stage",
        "Fit Score (1-5)",
        "Date Added",
        "Message Sent Date",
        "Last Activity Date",
        "Follow-up Due",
        "Source",
        "Notes",
        "Next Action",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index, item in enumerate(recommendations, start=1):
            writer.writerow(
                {
                    "No.": index,
                    "Contact Name": item.target_person,
                    "Company": item.company,
                    "Role / Title": item.target_role,
                    "LinkedIn URL": item.linkedin_url,
                    "Message Type": "Manual LinkedIn DM",
                    "Stage": "Research Complete",
                    "Fit Score (1-5)": max(1, min(5, round(item.fit_score / 20))),
                    "Date Added": "",
                    "Message Sent Date": "",
                    "Last Activity Date": "",
                    "Follow-up Due": "",
                    "Source": "AI GTM Command Center",
                    "Notes": item.score_rationale,
                    "Next Action": "Open LinkedIn manually, validate checklist, send or edit the drafted note.",
                }
            )


def write_brief(recommendations: list[GTMRecommendation], path: Path) -> None:
    lines = [
        "# AI GTM Command Center Brief",
        "",
        "This report is draft-only. Review every recommendation before using it in real outreach.",
        "",
        "## Priority Accounts",
        "",
    ]
    for item in recommendations:
        lines.extend(
            [
                f"### {item.company} - {item.fit_score}/100 ({item.priority})",
                "",
                f"**Why this account:** {item.score_rationale}",
                "",
                f"**Industry context:** {item.industry_context}",
                "",
                f"**Manual approach strategy:** {item.approach_strategy}",
                "",
                f"**Offer angle:** {item.suggested_offer_angle}",
                "",
                "**Manual LinkedIn research checklist:**",
                *[f"- {value}" for value in item.manual_research_checklist],
                "",
                "**LinkedIn connection note:**",
                "",
                item.linkedin_connection_note,
                "",
                "**LinkedIn DM draft:**",
                "",
                item.linkedin_dm_body,
                "",
                "**LinkedIn follow-up draft:**",
                "",
                item.linkedin_follow_up_body,
                "",
                "**Pain hypotheses:**",
                *[f"- {value}" for value in item.pain_hypotheses],
                "",
                "**Personalization points:**",
                *[f"- {value}" for value in item.personalization_points],
                "",
                "**Draft email:**",
                "",
                f"Subject: {item.cold_email_subject}",
                "",
                item.cold_email_body,
                "",
                "**Follow-up:**",
                "",
                f"Subject: {item.follow_up_subject}",
                "",
                item.follow_up_body,
                "",
                "**Founder call talk track:**",
                *[f"- {value}" for value in item.talk_track],
                "",
            ]
        )
        if item.sources:
            lines.append("**Sources:**")
            lines.extend(f"- {source.get('label', 'source')}: {source.get('url', '')}" for source in item.sources)
            lines.append("")
        if item.warnings:
            lines.append("**Warnings:**")
            lines.extend(f"- {warning}" for warning in item.warnings)
            lines.append("")
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def write_html_report(recommendations: list[GTMRecommendation], path: Path) -> None:
    cards = []
    for item in recommendations:
        pains = "".join(f"<li>{html.escape(value)}</li>" for value in item.pain_hypotheses)
        points = "".join(f"<li>{html.escape(value)}</li>" for value in item.personalization_points)
        sources = "".join(
            f'<li><a href="{html.escape(source.get("url", ""))}">{html.escape(source.get("label", "source"))}</a></li>'
            for source in item.sources
            if source.get("url")
        )
        email_body = html.escape(item.cold_email_body)
        linkedin_body = html.escape(item.linkedin_dm_body)
        checklist = "".join(f"<li>{html.escape(value)}</li>" for value in item.manual_research_checklist)
        cards.append(
            f"""
            <article class="account">
              <div class="account-header">
                <div>
                  <h2>{html.escape(item.company)}</h2>
                  <a href="{html.escape(item.website)}">{html.escape(item.website)}</a>
                </div>
                <div class="score {item.priority.lower()}">
                  <span>{item.fit_score}</span>
                  <small>{html.escape(item.priority)}</small>
                </div>
              </div>
              <p class="rationale">{html.escape(item.score_rationale)}</p>
              <div class="grid">
                <section>
                  <h3>Pain Hypotheses</h3>
                  <ul>{pains}</ul>
                </section>
                <section>
                  <h3>Personalization</h3>
                  <ul>{points}</ul>
                </section>
              </div>
                <section>
                  <h3>Offer Angle</h3>
                  <p>{html.escape(item.suggested_offer_angle)}</p>
                </section>
              <section>
                <h3>Manual LinkedIn Checklist</h3>
                <ul>{checklist}</ul>
              </section>
              <section class="email">
                <h3>Manual LinkedIn DM</h3>
                <strong>Connection note: {html.escape(item.linkedin_connection_note)}</strong>
                <pre>{linkedin_body}</pre>
              </section>
              <section class="email">
                <h3>Draft Email</h3>
                <strong>Subject: {html.escape(item.cold_email_subject)}</strong>
                <pre>{email_body}</pre>
              </section>
              <section>
                <h3>Sources</h3>
                <ul>{sources or "<li>Operator notes only</li>"}</ul>
              </section>
            </article>
            """
        )

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI GTM Command Center Report</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172026;
      --muted: #64717c;
      --line: #d9e1e7;
      --bg: #f7f9fb;
      --panel: #ffffff;
      --accent: #0f766e;
      --high: #166534;
      --medium: #9a5b00;
      --low: #9f1239;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.5;
    }}
    header {{
      padding: 40px 32px 20px;
      border-bottom: 1px solid var(--line);
      background: #fff;
    }}
    header h1 {{
      margin: 0 0 8px;
      font-size: clamp(28px, 4vw, 44px);
      letter-spacing: 0;
    }}
    header p {{
      margin: 0;
      max-width: 780px;
      color: var(--muted);
      font-size: 17px;
    }}
    main {{
      width: min(1120px, calc(100% - 32px));
      margin: 24px auto 48px;
      display: grid;
      gap: 18px;
    }}
    .account {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 22px;
    }}
    .account-header {{
      display: flex;
      align-items: start;
      justify-content: space-between;
      gap: 16px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 14px;
      margin-bottom: 14px;
    }}
    h2, h3 {{ letter-spacing: 0; }}
    h2 {{ margin: 0; font-size: 24px; }}
    h3 {{ margin: 0 0 8px; font-size: 14px; text-transform: uppercase; color: var(--muted); }}
    a {{ color: var(--accent); overflow-wrap: anywhere; }}
    .score {{
      min-width: 76px;
      min-height: 76px;
      border: 1px solid var(--line);
      border-radius: 8px;
      display: grid;
      place-items: center;
      padding: 8px;
      background: #f8fbfa;
    }}
    .score span {{ font-size: 28px; font-weight: 750; line-height: 1; }}
    .score small {{ color: var(--muted); }}
    .score.high span {{ color: var(--high); }}
    .score.medium span {{ color: var(--medium); }}
    .score.low span {{ color: var(--low); }}
    .rationale {{ font-size: 16px; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
      margin: 18px 0;
    }}
    ul {{ margin: 0; padding-left: 18px; }}
    li + li {{ margin-top: 6px; }}
    section {{ margin-top: 18px; }}
    pre {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: #fbfcfd;
      font: inherit;
    }}
    @media (max-width: 760px) {{
      header {{ padding: 30px 18px 18px; }}
      .account-header {{ flex-direction: column; }}
      .grid {{ grid-template-columns: 1fr; }}
      .score {{ width: 100%; min-height: 58px; grid-template-columns: auto auto; justify-content: center; column-gap: 8px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>AI GTM Command Center</h1>
    <p>Source-backed account research, ICP scoring, and human-approved outreach drafts for founder-led GTM.</p>
  </header>
  <main>
    {''.join(cards)}
  </main>
</body>
</html>
"""
    path.write_text(document, encoding="utf-8")
