import csv, json, sys
sys.path.insert(0, "..")
from li_crawl import is_cy
db = json.load(open("../li_db.json"))
OUT = "/home/user/Online-registration-Project_3/agent/results/sigma_operators.csv"
# компания -> (slug LinkedIn, заметка); найдено через Apollo (бесплатный lookup) + сайт компании + проверка страницы LinkedIn
PICK = {
 "TITANS": ("titansnet", ""), "Vincenzo Wrofino": ("codere-online", ""),
 "Kawaii Partners": ("kawaii-partners", "Найдена партнёрская страница LinkedIn"),
 "KNG Partners": ("thekngpartners", "Найдена партнёрская страница LinkedIn"),
 "STARCROWN": ("starcrown-partners", "Найдена партнёрская страница LinkedIn"),
 "Thewolfpartners": ("the-wolf-partners", "Найдена партнёрская страница LinkedIn"),
 "v.partners": ("v-partners-casino-affiliate-program", "Найдена партнёрская страница LinkedIn"),
 "BetAndYou": ("betandyoupartners", "LinkedIn — партнёрская программа BetAndYou"),
 "Betway": ("supergroupholdingcompany", "LinkedIn материнской группы Super Group (SGHC)"),
 "Bwin": ("entain", "LinkedIn материнской группы Entain"),
 "Ladbrokes": ("entain", "LinkedIn материнской группы Entain"),
 "888Casino": ("evokeplc", "LinkedIn материнской группы evoke (бывш. 888 Holdings)"),
 "Conquestador Sportsbook": ("conquestador-affiliates", "LinkedIn — партнёрская программа Conquestador"),
 "Intertops": ("intertops-gmbh", "Страница LinkedIn почти пустая"),
 "ComeOn!": ("comeon-group", "LinkedIn группы ComeOn Group"),
 "Cosmolot": ("cosmolot", ""), "Fairspin": ("fairspin", ""), "GreenSpin": ("greenspin-bet", ""),
 "Jackpotjoy": ("jackpotjoy-operations", ""), "LeoVegas": ("leovegasgroup", "LinkedIn группы LeoVegas Group"),
 "Pin-Up Casino": ("pin-up-global", "LinkedIn группы PIN-UP Global (RedCore) из кипрской базы"),
 "Queen Vegas": ("queen-vegas-casino", "Страница LinkedIn почти пустая"),
 "Wildz": ("wildzgroup", "LinkedIn группы Wildz Group (Rootz)"), "Winbet": ("casino-solutions-ltd", ""),
 "Zaza": ("zaza-casino", ""),
}
rows = list(csv.reader(open(OUT, encoding="utf-8")))
n = 0
for r in rows[1:]:
    if r[0] not in PICK or r[4]:
        continue
    slug, note = PICK[r[0]]
    d = db.get(slug, {})
    r[4] = "https://www.linkedin.com/company/" + slug
    r[5] = d.get("Headquarters") or d.get("locality", "")
    r[6] = d.get("Company size", "").replace(" employees", "")
    r[7] = d.get("Industry", "")
    if not r[8] and d.get("ok") and is_cy(d):
        r[8] = "да — HQ на Кипре по LinkedIn"
    r[9] += "; Apollo"
    notes = [x for x in r[10].split("; ") if x and x != "LinkedIn не найден автоматически"]
    r[10] = "; ".join(dict.fromkeys(notes + ([note] if note else [])))
    n += 1
with open(OUT, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(rows)
print(n, "updated;", sum(1 for r in rows[1:] if r[4]), "with LinkedIn;", sum(1 for r in rows[1:] if r[8]), "Cyprus")
