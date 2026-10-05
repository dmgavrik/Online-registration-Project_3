import csv, json, re, sys
sys.path.insert(0, "/tmp/claude-0/-home-user-Online-registration-Project-3/8407209d-11b8-5e11-bf15-397f68bfebaa/scratchpad")
from li_crawl import is_cy

items = json.load(open(__file__.rsplit("/",1)[0]+"/items.json"))
db = json.load(open("/tmp/claude-0/-home-user-Online-registration-Project-3/8407209d-11b8-5e11-bf15-397f68bfebaa/scratchpad/li_db.json"))
cy_rows = list(csv.reader(open("/home/user/Online-registration-Project_3/agent/results/cyprus_igaming_operators.csv", encoding="utf-8")))[1:]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


cy_names = {norm(r[1]): r[0] for r in cy_rows}
cy_li = {}
for r in cy_rows:
    for k in [norm(r[1])] + [norm(x) for x in re.split(r"[;,/()]", r[1])]:
        if len(k) >= 4 and r[4]: cy_li.setdefault(k, r)
cy_brands = {}
for r in cy_rows:
    for b in re.split(r"[;,/()]", r[1] + ";" + r[2] + ";" + r[10]):
        k = norm(re.sub(r"(?i)бренды:|и др\.?|casino", "", b))
        if len(k) >= 4:
            cy_brands.setdefault(k, r[1])

BAD = {"boss","bruno","days","planet","comeon","greenspin","joker","sol","ultra","unique","west","twin","zaza","yoju","pinup","royal","n1","dolcevita","allwins","superpartners","mrgreen","pinnacle","king-billy","titans","oshi","winz","karamba","duelz","yabo","ggbet","leovegas","888casino","coinsgame","fairspin","netwin-official","dragon-money","starcrown","blaze-official"}
AFF = re.compile(r"partners|affiliat", re.I)


def pick(it):
    base = norm(re.sub(r"(?i)\b(casino|sportsbook)\b", "", it["name"]))
    for s in it["slugs"]:
        d = db.get(s, {})
        if not d.get("ok"):
            continue
        page = norm(d.get("name", ""))
        if base and (base in page or page in base):
            ind = d.get("Industry", "")
            okind = any(w in ind for w in ("Gambling", "Casino", "Entertainment", "Spectator Sports", "Computer Games", "Online Audio", "Technology, Information"))
            if ind and not okind:
                continue
            if not ind and len(s) < 7 and not re.search(r"bet|casino|play|game|spin", s):
                continue
            if s in BAD:
                continue
            return d
    return None


rows = []
for it in items:
    d = pick(it)
    hq = (d.get("Headquarters") or d.get("locality", "")) if d else ""
    k = norm(re.sub(r"(?i)\b(casino|sportsbook)\b", "", it["name"]))
    in_cy = cy_names.get(k) or cy_brands.get(k)
    notes = []
    if it["cat"] == "shot":
        typ = it.get("type", "")
        src = "Ваш список (скрин)"
        if typ.startswith("Оператор") and AFF.search(it["name"] + " " + it.get("site", "") + " " + it.get("email", "")):
            notes.append("Это партнёрская (аффилиат) программа оператора — ЛПР искать у самого бренда")
        if it["name"] in ("Tornike Okson", "Vincenzo Wrofino"):
            notes.append("В колонке «Компания» указан человек; компания по email: " + it.get("site", ""))
    else:
        typ = "Онлайн-казино" if it["cat"] == "C" else "Букмекер / ставки на спорт"
        src = "sigma.world (ваш список)"
    if d and AFF.search(d.get("name", "")):
        notes.append("Найдена партнёрская страница LinkedIn")
    if not d and in_cy:
        cr = cy_li.get(k) or next((r for r in cy_rows if r[1] == in_cy and r[4]), None)
        if cr:
            d = {"url": cr[4], "Headquarters": cr[5], "Company size": cr[6], "Industry": cr[7], "from_cy": True}
            hq = cr[5]
    cyprus = "да — есть в кипрской базе" if in_cy else ("да — HQ на Кипре по LinkedIn" if d and is_cy(d) else "")
    rows.append([it["name"], typ, it.get("email", ""), it.get("site", ""),
                 d["url"] if d else "", hq, (d.get("Company size", "") if d else "").replace(" employees", ""),
                 d.get("Industry", "") if d else "", cyprus, src,
                 "; ".join(notes) or ("" if d else "LinkedIn не найден автоматически")])

rows.sort(key=lambda r: (r[9] != "Ваш список (скрин)", r[1], r[0].lower()))
hdr = ["Компания / бренд", "Тип", "Email (из вашего списка)", "Сайт", "LinkedIn", "HQ по LinkedIn",
       "Сотрудников", "Отрасль (LinkedIn)", "Кипр", "Источник", "Заметки"]
out = "/home/user/Online-registration-Project_3/agent/results/sigma_operators.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(hdr); w.writerows(rows)
print(len(rows), "rows;", sum(1 for r in rows if r[4]), "LinkedIn;", sum(1 for r in rows if r[8]), "Cyprus")
