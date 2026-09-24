"""Источники кандидатов, которые можно перезапускать для другой страны.

    python sources.py ukgc Cyprus          -> лицензиаты UKGC с адресом в стране
    python sources.py casino_groups Zypern -> казино-группы с юрлицом в стране (casino-groups.com, нем.)

Результат — JSON-список кандидатов в stdout; дальше их прогоняет classify.py.
"""
import io, json, re, subprocess, sys, zipfile, concurrent.futures as cf
from collections import defaultdict

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"


def curl(url: str) -> bytes:
    return subprocess.run(["curl", "-sL", "-m", "40", "-A", UA, url], capture_output=True).stdout


def ukgc(country: str) -> list[dict]:
    """Реестр UK Gambling Commission: xlsx с листом Addresses."""
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(curl(
        "https://www.gamblingcommission.gov.uk/downloads/business-licence-register.xlsx")), read_only=True)
    sheets = {ws.title: list(ws.iter_rows(values_only=True))[1:] for ws in wb}
    names = {r[0]: r[1] for r in sheets["Businesses"]}
    lic, dom = defaultdict(set), defaultdict(list)
    for r in sheets["Licences"]:
        lic[r[0]].add(r[4])
    for r in sheets["DomainNames"]:
        dom[r[0]].append(r[1])
    out = []
    for r in sheets["Addresses"]:
        if r[5] and country.lower() in str(r[5]).lower():
            out.append({"name": names.get(r[0]), "city": r[3], "source": "UKGC",
                        "activities": sorted(x for x in lic[r[0]] if x), "domains": dom[r[0]][:10]})
    return out


def casino_groups(country_word: str) -> list[dict]:
    """casino-groups.com: страницы групп, где упомянуто юрлицо в стране (напр. 'Zypern')."""
    from bs4 import BeautifulSoup
    idx = BeautifulSoup(curl("https://www.casino-groups.com/seitenverzeichnis/"), "lxml")
    links = sorted({a["href"] for a in idx.find_all("a", href=True)
                    if re.search(r"casino-groups\.com/[^/]+-casinos/?$", a["href"])})

    def one(url):
        text = BeautifulSoup(curl(url), "lxml").get_text(" ", strip=True)
        hits = [text[max(0, m.start() - 200): m.start() + 80] for m in re.finditer(country_word, text)]
        return {"name": url.rstrip("/").split("/")[-1], "url": url, "evidence": hits[:2],
                "source": "casino-groups.com"} if hits else None

    with cf.ThreadPoolExecutor(6) as ex:
        return [r for r in ex.map(one, links) if r]


if __name__ == "__main__":
    fn = {"ukgc": ukgc, "casino_groups": casino_groups}[sys.argv[1]]
    json.dump(fn(sys.argv[2]), sys.stdout, ensure_ascii=False, indent=1, default=str)
