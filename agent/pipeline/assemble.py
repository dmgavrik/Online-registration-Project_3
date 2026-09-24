import csv, json, re
from final_list import ROWS

db = json.load(open("li_db.json"))
OUT = "../results/cyprus_igaming_operators.csv"


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def pick(row):
    name = row[1]
    for s in row[4]:
        d = db.get(s, {})
        if not d.get("ok"):
            continue
        # страница должна называться похоже на компанию/бренд
        page = norm(d.get("name", ""))
        keys = [norm(w) for w in re.split(r"[ /()–-]+", name + " " + row[2]) if len(norm(w)) >= 3]
        if any(k in page or page in k for k in keys if k):
            return d
    return None


hdr = ["Категория", "Компания", "Бренды / юрлицо / лицензия", "Сайт", "LinkedIn", "HQ по LinkedIn",
       "Сотрудников (LinkedIn)", "Отрасль (LinkedIn)", "Источники", "Уверенность", "Заметки"]
FALLBACK = {  # найдены в поисковой выдаче, но гостевой просмотр LinkedIn отдаёт 404
    "in2bet": "https://cy.linkedin.com/company/in2bet",
    "BetWinner": "https://www.linkedin.com/company/betwinner",
    "PIN-UP Global (RedCore)": "https://cy.linkedin.com/company/pin-up-global",
    "Mostbet": "https://www.linkedin.com/company/mostbet",
    "TLF Entertainment": "https://cy.linkedin.com/company/tlf-mng",
}
out = []
for r in ROWS:
    d = pick(r)
    if not d and r[1] in FALLBACK:
        d = {"url": FALLBACK[r[1]], "search_only": True}
    out.append([r[0], r[1], r[2], r[3],
                d["url"] if d else "",
                (d.get("Headquarters") or d.get("locality", "")) if d else "",
                d.get("Company size", "").replace(" employees", "") if d else "",
                d.get("Industry", "") if d else "",
                r[5] + ("; LinkedIn — из поисковой выдачи" if d and d.get("search_only") else ""), r[6], r[7] if d else (r[7] + "; LinkedIn не найден").strip("; ")])
out.sort(key=lambda x: (x[0], {"high": 0, "medium": 1, "low": 2}[x[9]], x[1].lower()))
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(hdr); w.writerows(out)
print(len(out), "rows;", sum(1 for x in out if x[4]), "with LinkedIn")
