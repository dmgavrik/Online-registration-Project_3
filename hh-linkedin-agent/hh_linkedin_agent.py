"""Агент: ищет на hh.ru вакансии, в описании которых встречается слово «linkedin»,
и находит LinkedIn-профиль компании-работодателя.

Порядок поиска профиля компании:
  1. ссылка linkedin.com/company/... прямо в тексте вакансии;
  2. ссылка на LinkedIn на сайте компании (из карточки работодателя hh.ru);
  3. веб-поиск «<компания> site:linkedin.com/company».

Результат сохраняется в CSV и (опционально) в Google Таблицу.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import html
import json
import logging
import os
import re
import sys
import time
from dataclasses import asdict, dataclass, fields
from typing import Iterable, Iterator
from urllib.parse import unquote, urlparse

import requests

log = logging.getLogger("hh_linkedin_agent")

HH_BASE = "https://hh.ru"
HH_MAX_RESULTS = 2000  # hh.ru не отдаёт больше 2000 результатов на один поиск
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)
STATE_RE = re.compile(
    r'<template[^>]*id="HH-Lux-InitialState"[^>]*>(.*?)</template>', re.S
)
LINKEDIN_COMPANY_RE = re.compile(
    r"https?://(?:[a-z]{2,3}\.|www\.)?linkedin\.com/(?:company|school|showcase)/"
    r"[A-Za-z0-9\-_.%]+",
    re.I,
)
TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class Result:
    vacancy_id: int
    vacancy_url: str
    vacancy_name: str
    published: str
    area: str
    company_id: str
    company_name: str
    hh_company_url: str
    company_site: str
    linkedin_url: str
    linkedin_source: str  # description | company_site | web_search | not_found
    linkedin_candidates: str
    mention: str  # фрагмент описания вокруг слова linkedin


COLUMNS = [f.name for f in fields(Result)]


# ---------------------------------------------------------------- HTTP / hh.ru


class Http:
    def __init__(self, delay: float = 1.0, timeout: float = 30.0, retries: int = 3):
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": USER_AGENT, "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"}
        )
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self._last = 0.0

    def get(self, url: str, **kwargs) -> requests.Response:
        for attempt in range(1, self.retries + 1):
            wait = self.delay - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            try:
                resp = self.session.get(url, timeout=self.timeout, **kwargs)
                if resp.status_code in (429, 500, 502, 503, 504):
                    raise requests.HTTPError(f"HTTP {resp.status_code}")
                return resp
            except requests.RequestException as exc:
                if attempt == self.retries:
                    raise
                backoff = 2**attempt
                log.warning("GET %s: %s, повтор через %sс", url, exc, backoff)
                time.sleep(backoff)
        raise AssertionError("unreachable")


def parse_state(page_html: str) -> dict:
    """Достаёт JSON-состояние, которое hh.ru встраивает в каждую страницу."""
    m = STATE_RE.search(page_html)
    if not m:
        raise ValueError("на странице hh.ru не найден блок HH-Lux-InitialState")
    return json.loads(html.unescape(m.group(1)))


def search_vacancy_ids(http: Http, query: str, limit: int | None) -> Iterator[int]:
    page = 0
    seen: set[int] = set()  # премиум-вакансии повторяются на разных страницах
    while True:
        resp = http.get(
            f"{HH_BASE}/search/vacancy",
            params={
                "text": query,
                "search_field": "description",
                "items_on_page": 100,
                "page": page,
            },
        )
        resp.raise_for_status()
        result = parse_state(resp.text)["vacancySearchResult"]
        if page == 0:
            total = result.get("totalResults", 0)
            log.info("hh.ru: найдено вакансий: %s", total)
            if total > HH_MAX_RESULTS:
                log.warning(
                    "hh.ru отдаёт не больше %s результатов, остальные будут пропущены",
                    HH_MAX_RESULTS,
                )
        vacancies = result.get("vacancies") or []
        for v in vacancies:
            vid = int(v["vacancyId"])
            if vid in seen:
                continue
            seen.add(vid)
            yield vid
            if limit and len(seen) >= limit:
                return
        nxt = (result.get("paging") or {}).get("next") or {}
        if not vacancies or nxt.get("disabled", True):
            return
        page += 1


def fetch_vacancy(http: Http, vacancy_id: int) -> dict:
    resp = http.get(f"{HH_BASE}/vacancy/{vacancy_id}")
    resp.raise_for_status()
    return parse_state(resp.text)["vacancyView"]


# ----------------------------------------------------------------- LinkedIn


def html_to_text(fragment: str) -> str:
    text = TAG_RE.sub(" ", fragment or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def mention_snippet(text: str, word: str = "linkedin", width: int = 120) -> str:
    i = text.lower().find(word)
    if i < 0:
        return ""
    start, end = max(0, i - width), min(len(text), i + len(word) + width)
    return ("…" if start else "") + text[start:end] + ("…" if end < len(text) else "")


def normalize_linkedin(url: str) -> str:
    """https://uk.linkedin.com/company/foo/?trk=x -> https://www.linkedin.com/company/foo"""
    p = urlparse(url.strip())
    parts = [s for s in p.path.split("/") if s]
    if len(parts) < 2:
        return ""
    return f"https://www.linkedin.com/{parts[0].lower()}/{parts[1]}"


def extract_linkedin_urls(text: str) -> list[str]:
    out: list[str] = []
    for m in LINKEDIN_COMPANY_RE.finditer(html.unescape(text or "")):
        url = normalize_linkedin(m.group(0))
        if url and url not in out:
            out.append(url)
    return out


def linkedin_from_site(http: Http, site_url: str) -> list[str]:
    if not site_url:
        return []
    p = urlparse(site_url if "://" in site_url else f"https://{site_url}")
    homepage = f"{p.scheme or 'https'}://{p.netloc}/"
    urls: list[str] = []
    for url in dict.fromkeys([site_url, homepage]):
        try:
            resp = http.get(url, allow_redirects=True)
        except requests.RequestException as exc:
            log.info("сайт компании %s недоступен: %s", url, exc)
            continue
        if resp.ok:
            urls += [u for u in extract_linkedin_urls(resp.text) if u not in urls]
        if urls:
            break
    return urls


TRANSLIT = dict(zip(
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o",
     "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e",
     "yu", "ya"],
))
STOPWORDS = {
    "ооо", "ао", "пао", "зао", "оао", "ип", "гк", "группа", "компаний", "компания",
    "llc", "ltd", "inc", "gmbh", "group", "company", "the", "co",
}


def _norm_name(name: str) -> str:
    name = re.sub(r"\(.*?\)", " ", unquote(name).lower())
    words = re.sub(r"[^\w]+", " ", name).split()
    return " ".join(w for w in words if w not in STOPWORDS)


def clean_company_name(name: str) -> str:
    """«А1.Начало карьеры (Специалист…)» -> «А1.Начало карьеры»."""
    return re.sub(r"\s+", " ", re.sub(r"\(.*?\)", " ", name)).strip()


def _translit(text: str) -> str:
    return "".join(TRANSLIT.get(ch, ch) for ch in text)


def site_domain(site_url: str) -> str:
    if not site_url:
        return ""
    netloc = urlparse(site_url if "://" in site_url else f"https://{site_url}").netloc
    return netloc.lower().removeprefix("www.")


def rank_candidates(
    company: str, site_url: str, hits: Iterable[dict]
) -> list[tuple[float, str]]:
    """Оценивает результаты поиска: похожесть названия + совпадение домена сайта."""
    domain = site_domain(site_url)
    brand = domain.split(".")[0] if domain else ""
    targets = {_norm_name(company), _translit(_norm_name(company))} - {""}
    scored: dict[str, float] = {}
    for hit in hits:
        url = normalize_linkedin(hit.get("url", ""))
        if not url or "/company/" not in url:
            continue
        title = re.split(r"\s[|\-–]\s", hit.get("title", ""))[0]
        slug = _norm_name(url.rsplit("/", 1)[-1].replace("-", " "))
        names = {_norm_name(title), slug, _translit(_norm_name(title)), _translit(slug)}
        score = max(
            (difflib.SequenceMatcher(None, t, n).ratio() for t in targets for n in names),
            default=0.0,
        )
        blob = f"{title} {hit.get('snippet', '')} {slug}".lower().replace(" ", "")
        if domain and (domain in blob or (len(brand) >= 4 and brand in blob)):
            score += 0.3
        scored[url] = max(score, scored.get(url, 0.0))
    return sorted(((s, u) for u, s in scored.items()), reverse=True)


# --------------------------------------------------------------- web search


class WebSearch:
    """Веб-поиск. provider: ddg (без ключа), serpapi (SERPAPI_KEY), brave (BRAVE_API_KEY)."""

    def __init__(self, provider: str, http: Http):
        self.provider = provider
        self.http = http

    def search(self, query: str, n: int = 8) -> list[dict]:
        try:
            return getattr(self, f"_{self.provider}")(query, n)
        except Exception as exc:  # поиск не должен ронять весь прогон
            log.warning("веб-поиск (%s) «%s»: %s", self.provider, query, exc)
            return []

    def _ddg(self, query: str, n: int) -> list[dict]:
        from ddgs import DDGS
        from ddgs.exceptions import DDGSException

        time.sleep(self.http.delay)
        try:
            rows = DDGS().text(query, max_results=n)
        except DDGSException as exc:
            if "No results" in str(exc):
                return []
            raise
        return [
            {"url": r.get("href", ""), "title": r.get("title", ""), "snippet": r.get("body", "")}
            for r in rows
        ]

    def _serpapi(self, query: str, n: int) -> list[dict]:
        resp = self.http.get(
            "https://serpapi.com/search.json",
            params={"q": query, "num": n, "api_key": os.environ["SERPAPI_KEY"]},
        )
        resp.raise_for_status()
        return [
            {"url": r.get("link", ""), "title": r.get("title", ""), "snippet": r.get("snippet", "")}
            for r in resp.json().get("organic_results", [])
        ]

    def _brave(self, query: str, n: int) -> list[dict]:
        resp = self.http.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": n},
            headers={"X-Subscription-Token": os.environ["BRAVE_API_KEY"]},
        )
        resp.raise_for_status()
        return [
            {"url": r.get("url", ""), "title": r.get("title", ""), "snippet": r.get("description", "")}
            for r in resp.json().get("web", {}).get("results", [])
        ]


# -------------------------------------------------------------------- agent


class Agent:
    def __init__(self, http: Http, web: WebSearch, min_score: float = 0.75):
        self.http = http
        self.web = web
        self.min_score = min_score
        self._company_cache: dict[str, tuple[str, str, str]] = {}

    def find_company_linkedin(
        self, company_id: str, name: str, site: str
    ) -> tuple[str, str, str]:
        """-> (url, source, candidates). Кэшируется по работодателю."""
        key = company_id or name
        if key in self._company_cache:
            return self._company_cache[key]
        result = ("", "not_found", "")
        urls = linkedin_from_site(self.http, site)
        if urls:
            result = (urls[0], "company_site", " ".join(urls))
        elif name:
            hits = self.web.search(f"{clean_company_name(name)} site:linkedin.com/company")
            domain = site_domain(site)
            if domain:
                hits += self.web.search(f'"{domain}" site:linkedin.com/company')
            ranked = rank_candidates(name, site, hits)
            if ranked:
                cands = " ".join(f"{u} ({s:.2f})" for s, u in ranked[:3])
                best_score, best_url = ranked[0]
                if best_score >= self.min_score:
                    result = (best_url, "web_search", cands)
                else:
                    result = ("", "not_found", cands)
        self._company_cache[key] = result
        return result

    def process(self, vacancy_id: int) -> Result | None:
        v = fetch_vacancy(self.http, vacancy_id)
        description = v.get("description") or ""
        text = html_to_text(description)
        if "linkedin" not in text.lower():
            log.info("вакансия %s: слова linkedin в описании нет, пропуск", vacancy_id)
            return None

        company = v.get("company") or {}
        company_id = str(company.get("id") or "")
        name = company.get("visibleName") or company.get("name") or ""
        site = company.get("companySiteUrl") or ""

        in_desc = extract_linkedin_urls(description)
        if in_desc:
            url, source, cands = in_desc[0], "description", " ".join(in_desc)
        else:
            url, source, cands = self.find_company_linkedin(company_id, name, site)

        return Result(
            vacancy_id=vacancy_id,
            vacancy_url=f"{HH_BASE}/vacancy/{vacancy_id}",
            vacancy_name=v.get("name", ""),
            published=v.get("publicationDate", ""),
            area=(v.get("area") or {}).get("name", ""),
            company_id=company_id,
            company_name=name,
            hh_company_url=f"{HH_BASE}/employer/{company_id}" if company_id else "",
            company_site=site,
            linkedin_url=url,
            linkedin_source=source,
            linkedin_candidates=cands,
            mention=mention_snippet(text),
        )


# ------------------------------------------------------------------- output


def write_csv(path: str, results: list[Result]) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(asdict(r) for r in results)


def write_google_sheet(
    sheet_id: str, worksheet: str, credentials_file: str, results: list[Result]
) -> str:
    import gspread

    gc = gspread.service_account(filename=credentials_file)
    sh = gc.open_by_key(sheet_id)
    try:
        ws = sh.worksheet(worksheet)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet, rows=len(results) + 1, cols=len(COLUMNS))
    rows = [COLUMNS] + [[str(getattr(r, c)) for c in COLUMNS] for r in results]
    ws.clear()
    ws.update(values=rows, range_name="A1")
    return sh.url


# --------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--query", default="linkedin", help="слово для поиска в описании")
    ap.add_argument("--limit", type=int, default=None, help="максимум вакансий")
    ap.add_argument("--csv", default="results.csv", help="путь к CSV")
    ap.add_argument(
        "--search-provider",
        choices=["ddg", "serpapi", "brave", "none"],
        default=os.environ.get("SEARCH_PROVIDER", "ddg"),
    )
    ap.add_argument("--min-score", type=float, default=0.75,
                    help="порог уверенности для результата веб-поиска (0..1.3)")
    ap.add_argument("--delay", type=float, default=1.0, help="пауза между запросами, с")
    ap.add_argument("--sheet-id", default=os.environ.get("GOOGLE_SHEET_ID"),
                    help="ID Google Таблицы (из её URL)")
    ap.add_argument("--worksheet", default="hh_linkedin")
    ap.add_argument("--google-credentials",
                    default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
                    help="JSON-ключ сервисного аккаунта Google")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    if args.sheet_id and not args.google_credentials:
        ap.error("для Google Таблицы нужен --google-credentials")

    http = Http(delay=args.delay)
    web = WebSearch(args.search_provider, http)
    if args.search_provider == "none":
        web.search = lambda *a, **k: []  # type: ignore[method-assign]
    agent = Agent(http, web, min_score=args.min_score)

    results: list[Result] = []
    for i, vid in enumerate(search_vacancy_ids(http, args.query, args.limit), 1):
        try:
            r = agent.process(vid)
        except Exception as exc:
            log.error("вакансия %s: %s", vid, exc)
            continue
        if r:
            results.append(r)
            print(f"[{i}] {r.company_name} — {r.linkedin_url or 'не найден'} "
                  f"({r.linkedin_source})", file=sys.stderr)

    write_csv(args.csv, results)
    found = sum(1 for r in results if r.linkedin_url)
    print(f"Вакансий: {len(results)}, LinkedIn найден: {found}. CSV: {args.csv}")
    if args.sheet_id:
        url = write_google_sheet(args.sheet_id, args.worksheet, args.google_credentials, results)
        print(f"Google Таблица: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
