from __future__ import annotations

import html
import socket
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

from .models import AccountResearch, ResearchSource, TargetAccount
from .utils import clean_text


USER_AGENT = "AI-GTM-Command-Center/0.1 (+https://github.com/shubham1502-hue/ai-gtm-command-center)"


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._chunks: list[str] = []
        self._title: list[str] = []
        self._in_title = False
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        value = html.unescape(data).strip()
        if not value:
            return
        if self._in_title:
            self._title.append(value)
        self._chunks.append(value)

    @property
    def title(self) -> str:
        return clean_text(" ".join(self._title), 180)

    @property
    def text(self) -> str:
        return clean_text(" ".join(self._chunks), 6000)


def fetch_text(url: str, timeout: int = 10) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            return ""
        raw = response.read(750_000)
    return raw.decode("utf-8", errors="replace")


def robots_allowed(url: str) -> tuple[bool, str | None]:
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return False, "Invalid website URL."

    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except (OSError, socket.timeout):
        return True, "Could not read robots.txt; fetched only the provided homepage."
    return parser.can_fetch(USER_AGENT, url), None


def summarize_homepage(account: TargetAccount, offline: bool = False) -> tuple[str, list[ResearchSource], list[str]]:
    warnings: list[str] = []
    sources: list[ResearchSource] = []

    if offline:
        summary = (
            f"{account.company} is listed as a {account.segment or 'target'} account. "
            f"Notes from the operator: {account.notes or 'No notes provided.'}"
        )
        sources.append(ResearchSource("operator notes", account.website, clean_text(summary, 280)))
        return summary, sources, warnings

    allowed, robots_warning = robots_allowed(account.website)
    if robots_warning:
        warnings.append(robots_warning)
    if not allowed:
        warning = f"Skipped homepage fetch because robots.txt disallows automated access: {account.website}"
        warnings.append(warning)
        return account.notes, sources, warnings

    try:
        raw_html = fetch_text(account.website)
    except Exception as exc:  # noqa: BLE001 - network failures should not stop the run.
        warnings.append(f"Could not fetch homepage: {exc}")
        return account.notes, sources, warnings

    parser = VisibleTextParser()
    parser.feed(raw_html)
    title = parser.title or account.company
    text = parser.text
    summary = clean_text(f"{title}. {text}", 2200)
    if account.notes:
        summary = clean_text(f"{summary} Operator notes: {account.notes}", 2600)
    sources.append(ResearchSource("homepage", account.website, clean_text(summary, 320)))
    return summary, sources, warnings


def fetch_google_news(company: str, offline: bool = False, limit: int = 3) -> tuple[list[ResearchSource], list[str]]:
    if offline:
        return [], []

    query = urllib.parse.quote_plus(f'"{company}" startup funding product pricing')
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    warnings: list[str] = []
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            xml_bytes = response.read(300_000)
    except Exception as exc:  # noqa: BLE001
        return [], [f"Could not fetch Google News RSS: {exc}"]

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        return [], [f"Could not parse Google News RSS: {exc}"]

    items: list[ResearchSource] = []
    for item in root.findall("./channel/item")[:limit]:
        title = clean_text(item.findtext("title") or "", 180)
        link = clean_text(item.findtext("link") or "", 500)
        published = clean_text(item.findtext("pubDate") or "", 80)
        if title and link:
            items.append(ResearchSource("news", link, clean_text(f"{title}. {published}", 260)))
    return items, warnings


class CompanyResearcher:
    def __init__(self, offline: bool = False, news_limit: int = 3) -> None:
        self.offline = offline
        self.news_limit = news_limit

    def gather(self, account: TargetAccount) -> AccountResearch:
        website_summary, public_sources, warnings = summarize_homepage(account, offline=self.offline)
        news, news_warnings = fetch_google_news(account.company, offline=self.offline, limit=self.news_limit)
        warnings.extend(news_warnings)
        return AccountResearch(
            account=account,
            website_summary=website_summary,
            news=news,
            public_sources=public_sources,
            warnings=warnings,
        )
