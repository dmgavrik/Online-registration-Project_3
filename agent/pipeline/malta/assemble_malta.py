"""Собирает таблицу операторов Мальты (реестр MGA, B2C + CRP-операторы) и помечает цветом
пересечения с уже отработанными листами Cyprus / SIGMA файла пользователя.
Вход (scratchpad): mga/licensees.json, mga/det.json, mga/ents.json, li_db.json, userfile/done.json"""
import csv, json, re, sys
from xml.sax.saxutils import escape
S = sys.argv[1]
OUT = "/home/user/Online-registration-Project_3/agent/results/malta_operators"
L = json.load(open(S + "/mga/licensees.json")); D = json.load(open(S + "/mga/det.json"))
E = json.load(open(S + "/mga/ents.json")); db = json.load(open(S + "/li_db.json"))
done = json.load(open(S + "/userfile/done.json"))
sys.path.insert(0, "/home/user/Online-registration-Project_3/agent/pipeline/malta")
from mga_map import BRAND

# проверенные вручную LinkedIn-страницы (юрлицо -> slug)
PICK = {
 "Bet-at-home.com Internet Limited": "bet-at-home", "Betway Limited": "supergroupholdingcompany",
 "bwin Holdings (Malta) Limited": "entain", "Chilling Cheetah Limited": "chilling-cheetah", "Chimera Gaming Limited": "wildzgroup",
 "Clobet LTD": "clobet", "Fairload Limited": "lvbet", "FavBet Limited": "favbet", "GGN Europe Ltd": "ggpoker", "NSUS Malta Limited": "ggpoker",
 "GIPS Limited": "betsson-group", "GM Gaming Limited": "gm-gaming-limited", "Hillside (Sports) ENC": "bet365",
 "IZI Interactive Limited": "izigroup-ltd", "Kaizen Gaming International Limited": "kaizen-gaming", "Kserol P.L.C.": "FDJUNITED",
 "LeoVegas Gaming plc": "leovegasgroup", "Lopoca Gaming Limited": "lopoca", "Merkur Bets Malta Limited": "merkurbets",
 "Mill of Magic Limited": "casumo", "Mr Green Limited": "evokeplc", "NetBet Enterprises Limited": "netbet", "PinBet Malta Limited": "pinbet",
 "Play North Limited": "play-north", "PPB Counterparty Services Limited": "flutter-entertainment", "SBG Sports Limited": "flutter-entertainment",
 "Prima Networks Limited": "prima-networks", "Pro Xenon Mediathek Limited": "kajot", "Probe Investments Limited": "energy-casino",
 "Progressplay Limited": "progressplay", "Rizk Nordic Limited": "rizk", "Rootz Ltd": "wildzgroup", "Shuffle Up Ltd": "shuffleup",
 "Skill On Net Limited": "skillonnet", "Smarkets (Malta) Limited": "smarkets", "Star Stake Limited": "starstake",
 "Thelivering Ltd.": "themilladventure", "TSG Interactive Gaming Europe Limited": "pokerstars", "Tumas Gaming Limited": "tumas-gaming",
 "VGW Games Limited": "virtual-gaming-worlds", "White Hat Gaming Limited": "white-hat-gaming", "Tipico Co. Ltd": "tipico-co-ltd",
 "Tipico Games Ltd": "tipico-co-ltd", "Tipico Karlsruhe Ltd": "tipico-co-ltd", "Mozzartbet Malta Limited": "mozzart-bet",
 "Aspire Global International Limited": "aspireglobal", "Glitnor Services Limited": "glitnor", "Tipwin Limited": "tipwin-limited",
 "Level Up Interactive Limited": "level-up-interactive", "P2P Entertainment Limited": "igamingadvisors", "True Flip Gaming Ltd": "igamingadvisors",
}
NOTE = {
 "Aspire Global International Limited": "Гибрид: в основном white-label B2B (бренд Karamba — B2C)",
 "Prima Networks Limited": "По описанию в LinkedIn — софт-сервисы для операторов (скорее B2B)",
 "Star Stake Limited": "По описанию в LinkedIn — платформа лояльности (скорее B2B)",
 "Thelivering Ltd.": "The Mill Adventure — платформа gaming-as-a-service (гибрид)",
 "Level Up Interactive Limited": "В LinkedIn описана как маркетинг в iGaming — проверить",
 "Progressplay Limited": "Гибрид: white-label + свои бренды", "White Hat Gaming Limited": "Гибрид: white-label + свои бренды",
 "Clobet LTD": "Бренд Lottofy (лотерейные ставки)", "Glitnor Services Limited": "Glitnor Group переименована в LCKY Group",
 "P2P Entertainment Limited": "Лицензия приостановлена (добровольно); LinkedIn консультанта IGA Group",
 "True Flip Gaming Ltd": "Email лицензии — консультант IGA Group; LinkedIn бренда не найден",
 "Kserol P.L.C.": "Kindred (Unibet) теперь в составе FDJ United", "Pro Xenon Mediathek Limited": "Kajot Casino",
}
if "P2P Entertainment Limited" in PICK: PICK.pop("P2P Entertainment Limited"); PICK.pop("True Flip Gaming Ltd")

# найдено через Lusha (companies_search, превью без раскрытия): юрлицо -> (LinkedIn, HQ, сотрудников, заметка)
LUSHA = {
 "Meridian Gaming Limited": ("https://www.linkedin.com/company/meridian-sports", "Limassol, Cyprus", "11-50", "LinkedIn кипрского юрлица Meridian Gaming (CY)"),
 "Avento MT Limited": ("https://www.linkedin.com/company/aventogroup", "Ta' Xbiex, Malta", "51-200", "Avento Group"),
 "Bestbet Limited": ("https://www.linkedin.com/company/bestbet-com-ltd", "London, UK", "1-10", ""),
 "Rebels Gaming Limited": ("https://www.linkedin.com/company/rebels-gaming-ltd", "Malta", "1-10", ""),
 "Buddybet Malta Limited": ("https://www.linkedin.com/company/buddybet-australia", "Melbourne, Australia", "51-200", "Buddybet Group"),
 "Dialmedia Limited": ("https://www.linkedin.com/company/full-force-gaming-group", "Larnaca, Cyprus", "51-200", "Full Force Gaming Group"),
 "Dragonara Gaming Limited": ("https://www.linkedin.com/company/dragonaracasino", "St Julian's, Malta", "51-200", ""),
 "FairBet Limited": ("https://www.linkedin.com/company/fairbet.org", "Malta", "1-10", "FairBet.org"),
 "Interwetten Gaming Limited": ("https://www.linkedin.com/company/interwetten-group", "Sliema, Malta", "51-200", "Interwetten Group"),
 "One Casino Limited": ("https://www.linkedin.com/company/one-casino", "Ta' Xbiex, Malta", "11-50", ""),
 "Palasino Malta Limited": ("https://www.linkedin.com/company/trans-world-hotels-entertainment-a-s-", "Česká Kubice, Czechia", "501-1,000", "Материнская Palasino Group (TWHE)"),
 "Realm Entertainment Limited": ("https://www.linkedin.com/company/realmentertainment", "Sliema, Malta", "11-50", ""),
 "Stanleybet Malta Limited": ("https://www.linkedin.com/company/stanleybet-limited", "Liverpool, UK", "1-10", "Страница британского юрлица Stanleybet — проверить"),
 "TV GLOBAL ENTERPRISES LTD": ("https://www.linkedin.com/company/tvglobaltnterprises", "Ta' Xbiex, Malta", "1-10", ""),
}

def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())
user_slugs, user_names = {}, {}
for sheet, rows in done.items():
    for name, li, site in rows:
        m = re.search(r"/company/([^/?#]+)", li)
        if m: user_slugs.setdefault(m.group(1).lower(), (sheet, name))
        for tok in re.split(r"[/();,]| — ", name):
            k = norm(re.sub(r"(?i)casino|sportsbook|group|limited|ltd", "", tok))
            if len(k) >= 4: user_names.setdefault(k, (sheet, name))

groups = {}
for n, reg, auth, typ in L:
    if n not in E: continue
    b = BRAND.get(n)
    brand = b[0] if b else n
    kind = {"К": "Онлайн-казино", "С": "Ставки на спорт", "К+С": "Казино + ставки", "Покер": "Покер",
            "К+Покер": "Казино + покер", "С (биржа)": "Беттинг-биржа"}.get(b[1], b[1]) if b else (
            "Казино + ставки" if "Type 2" in typ and "Type 1" in typ else "Ставки на спорт" if "Type 2" in typ else "Онлайн-казино")
    g = groups.setdefault(brand, {"ents": [], "auth": [], "kind": kind, "slug": None, "emails": set(), "status": set(), "notes": []})
    g["ents"].append(n); g["auth"].append(auth)
    d = D.get(n, {}); e = d.get("email", "")
    if "@" in e: g["emails"].add(e.split("@")[-1].lower())
    if d.get("status"): g["status"].add(d["status"])
    if PICK.get(n): g["slug"] = g["slug"] or PICK[n]
    if n in LUSHA and not g.get("lusha"): g["lusha"] = LUSHA[n]
    for x in (b[3] if b else "", NOTE.get(n, "")):
        if x and x not in g["notes"]: g["notes"].append(x)

out = []
for brand, g in groups.items():
    d = db.get(g["slug"], {}) if g["slug"] else {}
    lu = None if g["slug"] else g.get("lusha")
    hit = None
    if g["slug"] and g["slug"].lower() in user_slugs: hit = user_slugs[g["slug"].lower()]
    if not hit:
        for tok in re.split(r"[/();,]", brand):
            k = norm(re.sub(r"(?i)casino|sportsbook|group|limited|ltd|\(.*", "", tok))
            if len(k) >= 4 and k in user_names: hit = user_names[k]; break
    out.append({"Бренд / группа": brand, "Юрлицо в реестре MGA": "; ".join(dict.fromkeys(g["ents"])),
        "Лицензия MGA": "; ".join(dict.fromkeys(g["auth"])), "Вертикаль": g["kind"],
        "Статус лицензии": ", ".join(sorted(g["status"])) or "Licensed", "Домен из email (MGA)": ", ".join(sorted(g["emails"] - {"n/a"})),
        "LinkedIn": "https://www.linkedin.com/company/" + g["slug"] if g["slug"] else (lu[0] if lu else ""),
        "HQ по LinkedIn": d.get("Headquarters") or d.get("locality") or (lu[1] if lu else ""),
        "Сотрудников": (d.get("Company size") or "").replace(" employees", "") or (lu[2] if lu else ""),
        "Отрасль (LinkedIn)": d.get("Industry") or "",
        "Уже в вашем файле": f"да — лист {hit[0]} ({hit[1]})" if hit else "",
        "Заметки": "; ".join(g["notes"] + ([x for x in (lu[3], "LinkedIn — из Lusha") if x] if lu else []))})
out.sort(key=lambda r: (r["Уже в вашем файле"] == "", r["LinkedIn"] == "", r["Бренд / группа"].lower()))
hdr = list(out[0])
with open(OUT + ".csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, hdr); w.writeheader(); w.writerows(out)
# XML Spreadsheet 2003: Google Drive конвертирует в Google Sheets с сохранением заливки
cell = lambda v, st="": f'<Cell{st}><Data ss:Type="String">{escape(str(v))}</Data></Cell>'
x = ['<?xml version="1.0"?>', '<?mso-application progid="Excel.Sheet"?>',
     '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">',
     '<Styles><Style ss:ID="h"><Font ss:Bold="1"/><Interior ss:Color="#D9E2F3" ss:Pattern="Solid"/></Style>'
     '<Style ss:ID="y"><Interior ss:Color="#FFE699" ss:Pattern="Solid"/></Style></Styles>',
     '<Worksheet ss:Name="Malta"><Table>', "<Row>" + "".join(cell(h, ' ss:StyleID="h"') for h in hdr) + "</Row>"]
for r in out:
    st = ' ss:StyleID="y"' if r["Уже в вашем файле"] else ""
    cells, skip = [], False
    for i, h in enumerate(hdr, 1):
        if not r[h]: skip = True; continue
        cells.append(cell(r[h], f' ss:Index="{i}"' if skip else "")); skip = False
    x.append(f"<Row{st}>" + "".join(cells) + "</Row>")
x += ["</Table></Worksheet></Workbook>"]
open(OUT + ".xml", "w", encoding="utf-8").write("\n".join(x))
print(len(out), "brands;", sum(1 for r in out if r["LinkedIn"]), "LinkedIn;", sum(1 for r in out if r["Уже в вашем файле"]), "overlap")
for r in out:
    if r["Уже в вашем файле"]: print("  ", r["Бренд / группа"], "->", r["Уже в вашем файле"])
