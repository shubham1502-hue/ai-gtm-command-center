from __future__ import annotations

import argparse
import csv
import email.utils
import re
import ssl
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .utils import clean_text, ensure_dir, utc_run_id


USER_AGENT = "AI-GTM-Command-Center/0.1 (+https://github.com/shubham1502-hue/ai-gtm-command-center)"

DEFAULT_QUERIES = [
    '"raises" "seed funding" startup founder India',
    '"raises" "Series A" startup founder India',
    '"secures" funding startup founder India',
    '"bags" funding startup founder India',
    '"raises" funding "AI startup" founder',
    '"raises" funding fintech startup founder India',
    '"raises" funding SaaS startup founder India',
]


@dataclass(frozen=True)
class FundingLead:
    company: str
    funding_date: str
    amount: str
    round: str
    industry: str
    title: str
    source_name: str
    source_url: str
    query: str
    repo_angle: str
    dm_angle: str


def fetch_url(url: str, timeout: int = 20) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read(500_000)
    except (ssl.SSLCertVerificationError, urllib.error.URLError) as exc:
        if isinstance(exc, urllib.error.URLError) and not isinstance(exc.reason, ssl.SSLCertVerificationError):
            raise
        # Some local Python installs miss CA roots. Keep this limited to public RSS reads.
        context = ssl._create_unverified_context()  # noqa: SLF001
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            return response.read(500_000)


def parse_pub_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def source_from_title(title: str) -> tuple[str, str]:
    if " - " not in title:
        return title.strip(), ""
    headline, source = title.rsplit(" - ", 1)
    return headline.strip(), source.strip()


def extract_company(headline: str) -> str:
    cleaned = re.sub(r"^[\"'\u201c\u201d]+|[\"'\u201c\u201d]+$", "", headline.strip())
    cleaned = re.sub(r"^(?:exclusive|analysis|funding alert)\s*:\s*", "", cleaned, flags=re.IGNORECASE)
    startup_match = re.search(
        r"(?:AI|deep-tech|fintech|SaaS|grocery|climate|healthtech|edtech)?\s*startup\s+([A-Z][A-Za-z0-9&.'-]+)\s+"
        r"(?:raises|raised|secures|secured|bags|bagged|lands|landed|closes|closed|gets|got)\b",
        cleaned,
        flags=re.IGNORECASE,
    )
    if startup_match:
        return clean_text(startup_match.group(1).strip(" -:|"), 80)
    founder_match = re.search(
        r"^(.+?)\s+founder\s+(?:raises|raised|secures|secured|bags|bagged|lands|landed|closes|closed|gets|got)\b",
        cleaned,
        flags=re.IGNORECASE,
    )
    if founder_match:
        return clean_text(founder_match.group(1).strip(" -:|"), 80)
    possessive_match = re.search(
        r"^[A-Z][A-Za-z .'-]+['\u2019]s\s+([A-Z][A-Za-z0-9&.'-]+)\s+"
        r"(?:raises|raised|secures|secured|bags|bagged|lands|landed|closes|closed|gets|got)\b",
        cleaned,
        flags=re.IGNORECASE,
    )
    if possessive_match:
        return clean_text(possessive_match.group(1).strip(" -:|"), 80)
    patterns = [
        r"^(.+?)\s+(?:raises|raised|secures|secured|bags|bagged|lands|landed|closes|closed|gets|got)\b",
        r"^(.+?)\s+(?:announces|announced)\s+.+?\s+(?:funding|round)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, cleaned, flags=re.IGNORECASE)
        if match:
            return clean_text(match.group(1).strip(" -:|"), 80)
    return clean_text(cleaned.split(":")[0], 80)


def extract_amount(headline: str) -> str:
    pattern = (
        r"(?:(?:\$|US\$|USD|₹|INR|Rs\.?)\s?[\d,.]+(?:\s?(?:million|mn|m|crore|cr|billion|bn|lakh))?)"
        r"|(?:[\d,.]+\s?(?:million|mn|m|crore|cr|billion|bn|lakh)\s?(?:dollars|rupees|USD|INR)?)"
    )
    match = re.search(pattern, headline, flags=re.IGNORECASE)
    return clean_text(match.group(0), 40) if match else ""


def extract_round(headline: str) -> str:
    rounds = [
        "pre-seed",
        "seed",
        "series a",
        "series b",
        "series c",
        "series d",
        "angel",
        "bridge",
        "debt",
        "pre-series a",
    ]
    lower = headline.lower()
    for value in rounds:
        if value in lower:
            return value.title().replace("Pre-", "Pre-").replace("Series", "Series")
    return ""


def infer_industry(text: str) -> str:
    lower = text.lower()
    checks = [
        ("AI", ["ai ", "artificial intelligence", "llm", "agent", "genai"]),
        ("Fintech", ["fintech", "lending", "credit", "payments", "wealth", "banking"]),
        ("SaaS", ["saas", "software", "enterprise", "b2b"]),
        ("Healthtech", ["health", "clinic", "doctor", "medical", "pharma"]),
        ("EdTech", ["edtech", "education", "learning", "student"]),
        ("D2C / Consumer", ["d2c", "consumer", "brand", "commerce", "retail"]),
        ("Climate", ["climate", "energy", "ev", "carbon", "sustainability"]),
        ("Logistics", ["logistics", "supply chain", "delivery", "freight"]),
    ]
    for label, terms in checks:
        if any(term in lower for term in terms):
            return label
    return "Startup"


def choose_repo_angle(industry: str, headline: str) -> tuple[str, str]:
    lower = f"{industry} {headline}".lower()
    if any(term in lower for term in ["fintech", "lending", "credit", "payments"]):
        return (
            "Collections Strategy Engine / Payments Monitoring",
            "recent funding usually creates pressure to tighten risk, payments, collections, and operating visibility.",
        )
    if any(term in lower for term in ["consumer", "d2c", "commerce", "retail"]):
        return (
            "D2C Pricing Strategy Framework / Operations KPI Automation",
            "recent funding usually creates pressure around pricing, retention, channel mix, and ops cadence.",
        )
    if any(term in lower for term in ["saas", "ai", "llm", "agent", "enterprise", "b2b"]):
        return (
            "AI GTM Command Center / Founder Weekly Operating Review Agent",
            "recent funding usually creates pressure to turn founder-led GTM into a repeatable operating rhythm.",
        )
    return (
        "Founder Weekly Operating Review Agent",
        "recent funding usually creates pressure to turn goals, metrics, risks, and investor updates into a weekly cadence.",
    )


def google_news_url(query: str) -> str:
    encoded = urllib.parse.quote_plus(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"


def fetch_funding_leads(queries: list[str], days: int, per_query: int) -> list[FundingLead]:
    cutoff = datetime.now(UTC) - timedelta(days=days)
    seen: set[str] = set()
    leads: list[FundingLead] = []

    for query in queries:
        root = ET.fromstring(fetch_url(google_news_url(query)))
        for item in root.findall("./channel/item")[:per_query]:
            title = clean_text(item.findtext("title") or "", 240)
            link = clean_text(item.findtext("link") or "", 500)
            published = parse_pub_date(item.findtext("pubDate") or "")
            if not title or not link or not published or published < cutoff:
                continue

            headline, source_name = source_from_title(title)
            if not re.search(r"\b(raises|raised|secures|secured|bags|bagged|funding|round)\b", headline, re.I):
                continue

            company = extract_company(headline)
            key = company.lower()
            if not company or key in seen:
                continue
            seen.add(key)

            industry = infer_industry(headline)
            repo_angle, dm_angle = choose_repo_angle(industry, headline)
            leads.append(
                FundingLead(
                    company=company,
                    funding_date=published.date().isoformat(),
                    amount=extract_amount(headline),
                    round=extract_round(headline),
                    industry=industry,
                    title=headline,
                    source_name=source_name,
                    source_url=link,
                    query=query,
                    repo_angle=repo_angle,
                    dm_angle=dm_angle,
                )
            )
    return leads


def write_funding_leads(leads: list[FundingLead], path: Path) -> None:
    fieldnames = [
        "company",
        "funding_date",
        "amount",
        "round",
        "industry",
        "title",
        "source_name",
        "source_url",
        "repo_angle",
        "dm_angle",
        "query",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for lead in leads:
            writer.writerow(lead.__dict__)


def write_target_accounts(leads: list[FundingLead], path: Path) -> None:
    fieldnames = [
        "company",
        "website",
        "segment",
        "industry",
        "funding_stage",
        "target_person",
        "target_role",
        "linkedin_url",
        "email",
        "notes",
        "linkedin_notes",
        "industry_notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for lead in leads:
            writer.writerow(
                {
                    "company": lead.company,
                    "website": "",
                    "segment": f"{lead.industry} recently funded startup",
                    "industry": lead.industry,
                    "funding_stage": lead.round,
                    "target_person": "",
                    "target_role": "Founder",
                    "linkedin_url": "",
                    "email": "",
                    "notes": f"{lead.title}. Funding source: {lead.source_url}. Repo angle: {lead.repo_angle}.",
                    "linkedin_notes": "Manually inspect founder profile before messaging. Do not scrape LinkedIn.",
                    "industry_notes": lead.dm_angle,
                }
            )


def write_tracker_import(leads: list[FundingLead], path: Path) -> None:
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
    today = datetime.now(UTC).date().isoformat()
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index, lead in enumerate(leads, start=1):
            writer.writerow(
                {
                    "No.": index,
                    "Contact Name": "",
                    "Company": lead.company,
                    "Role / Title": "Founder",
                    "LinkedIn URL": "",
                    "Message Type": "Manual LinkedIn DM",
                    "Stage": "Funding lead found; founder profile needed",
                    "Fit Score (1-5)": "4",
                    "Date Added": today,
                    "Message Sent Date": "",
                    "Last Activity Date": today,
                    "Follow-up Due": "",
                    "Source": lead.source_name or "Google News RSS",
                    "Notes": f"{lead.title}. Amount: {lead.amount}. Round: {lead.round}. Repo angle: {lead.repo_angle}. Source: {lead.source_url}",
                    "Next Action": "Find founder manually on LinkedIn, verify fit, then move into AI GTM Command Center target CSV.",
                }
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Find recent public fundraising signals for manual founder outreach.")
    parser.add_argument("--days", type=int, default=45, help="Lookback window in days.")
    parser.add_argument("--per-query", type=int, default=20, help="Maximum RSS items to inspect per query.")
    parser.add_argument("--query", action="append", default=[], help="Additional Google News RSS query.")
    parser.add_argument("--out", type=Path, help="Output directory. Defaults to outputs/fundraising-<timestamp>.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    queries = DEFAULT_QUERIES + args.query
    out_dir = args.out or Path("outputs") / f"fundraising-{utc_run_id()}"
    ensure_dir(out_dir)
    leads = fetch_funding_leads(queries=queries, days=args.days, per_query=args.per_query)
    leads = sorted(leads, key=lambda item: item.funding_date, reverse=True)
    write_funding_leads(leads, out_dir / "fundraising_leads.csv")
    write_target_accounts(leads, out_dir / "target_accounts_from_fundraising.csv")
    write_tracker_import(leads, out_dir / "founder_outreach_tracker_import.csv")

    print(f"Found {len(leads)} funding leads.")
    print(f"Funding leads: {out_dir / 'fundraising_leads.csv'}")
    print(f"Target account draft: {out_dir / 'target_accounts_from_fundraising.csv'}")
    print(f"Tracker import: {out_dir / 'founder_outreach_tracker_import.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
