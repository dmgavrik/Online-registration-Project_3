"""BFS по публичным страницам компаний LinkedIn через блок «похожие страницы»."""
import json, re, subprocess, sys, time, os, random
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
OUT = os.path.join(os.path.dirname(__file__), "li_db.json")
SLUG_RE = re.compile(r"https://(?:[a-z]{2,3}|www)\.linkedin\.com/company/([A-Za-z0-9\-_%.]+)")
CY_WORDS = ("Cyprus", "Limassol", "Lemesos", "Nicosia", "Lefkosia", "Larnaca", "Larnaka", "Paphos", "Pafos",
            "Famagusta", "Ayia Napa", "Kyrenia", "Girne", "Strovolos", "Germasogeia", "Mesa Geitonia", "Agios Athanasios")
GAMBLING_IND = ("Gambling", "Casino")


def fetch(slug):
    r = subprocess.run(["curl", "-s", "-m", "25", "-A", UA, "-L", "-w", "\n%{http_code}",
                        f"https://{random.choice(['www','cy','uk','mt'])}.linkedin.com/company/{slug}"], capture_output=True, text=True)
    body, _, code = r.stdout.rpartition("\n")
    return code, body


def parse(slug, html):
    s = BeautifulSoup(html, "lxml")
    d = {"slug": slug, "url": f"https://www.linkedin.com/company/{slug}"}
    t = s.find("title")
    d["name"] = t.get_text(strip=True).replace(" | LinkedIn", "") if t else slug
    for dt in s.select("dl dt"):
        dd = dt.find_next("dd")
        if dd:
            d[dt.get_text(strip=True)] = dd.get_text(" ", strip=True).replace("External link for " + d["name"], "").strip()
    m = s.find("meta", attrs={"name": "description"})
    d["description"] = m["content"][:400] if m else ""
    fol = re.search(r"([\d,]+) followers", html)
    d["followers"] = fol.group(1) if fol else ""
    for sc in s.find_all("script", type="application/ld+json"):
        try:
            j = json.loads(sc.string)
        except Exception:
            continue
        for node in j.get("@graph", [j]):
            if node.get("@type") == "Organization" and node.get("address"):
                a = node["address"]
                d["country"] = a.get("addressCountry", "")
                d["locality"] = a.get("addressLocality", "")
    d["similar"] = sorted({x for x in SLUG_RE.findall(html) if x != slug})
    return d


def is_cy(d):
    blob = " ".join([d.get("country", ""), d.get("locality", ""), d.get("Headquarters", "")])
    return d.get("country", "") == "CY" or any(w.lower() in blob.lower() for w in CY_WORDS)


def is_gambling(d):
    return any(w in d.get("Industry", "") for w in GAMBLING_IND)


def main(seeds, max_pages):
    db = json.load(open(OUT)) if os.path.exists(OUT) else {}
    queue = [s for s in seeds if s not in db]
    # продолжаем обход от уже найденных кипрских gambling-страниц
    for d in db.values():
        if d.get("ok") and is_cy(d) and is_gambling(d):
            queue += [x for x in d["similar"] if x not in db]
    seen = set(db) | set(queue)
    n = 0
    while queue and n < max_pages:
        slug = queue.pop(0)
        code, html = fetch(slug)
        n += 1
        if code in ("999", "429", "000"):
            queue.append(slug); n -= 1
            print("rate limited, sleeping", file=sys.stderr); time.sleep(90)
            continue
        if code != "200":
            db[slug] = {"slug": slug, "ok": False, "code": code}
            continue
        d = parse(slug, html); d["ok"] = True
        db[slug] = d
        if is_cy(d) and is_gambling(d):
            for x in d["similar"]:
                if x not in seen:
                    seen.add(x); queue.append(x)
        if n % 20 == 0:
            json.dump(db, open(OUT, "w"), ensure_ascii=False)
            cy = sum(1 for v in db.values() if v.get("ok") and is_cy(v) and is_gambling(v))
            print(f"{n} fetched, queue {len(queue)}, CY gambling {cy}", file=sys.stderr)
        time.sleep(random.uniform(3, 6))
    json.dump(db, open(OUT, "w"), ensure_ascii=False)


if __name__ == "__main__":
    main([l.strip() for l in open(sys.argv[1]) if l.strip()], int(sys.argv[2]))
