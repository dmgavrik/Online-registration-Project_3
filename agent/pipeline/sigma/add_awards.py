"""Добавляет в SiGMA-таблицу операторов из победителей/шорт-листов SiGMA Awards 2023–2026
и помечает уже имеющиеся бренды, которые там фигурировали (= были на выставке)."""
import csv, json, sys
sys.path.insert(0, "..")
from li_crawl import is_cy
db = json.load(open("../li_db.json"))
OUT = "/home/user/Online-registration-Project_3/agent/results/sigma_operators.csv"
PICK = {"Roman Casino": "roman-casino", "VBET": "vbet-official", "ArenaPlus": "arenaplus-ph", "Betiton": "betiton",
        "Vegas Legends": "vegas-legends", "Gamdom": "gamdom-com", "Nine Casino": "nine-casino", "Highbet": "highbet",
        "PariPesa": "paripesa", "Roobet": "roobet-com", "Balkan Bet": "balkan-bet", "Brazino777": "brazino777",
        "Izibet": "izibet", "Kaizen Gaming (Betano)": "kaizen-gaming", "RocketPlay Casino": "rocketplay-casino",
        "Flutter (PokerStars, FanDuel)": "flutter-entertainment", "Betclic": "betclicgroup"}  # kindred, meridian-tech — ложные совпадения
NOTE = {"Roman Casino": "HQ в LinkedIn указан Сиэтл — проверить, та ли компания",
        "Brazino777": "Найдена страница Brazino777 BELARUS",
        "Izibet": "Страница LinkedIn почти пустая",
        "Flutter (PokerStars, FanDuel)": "Группа; отдельная страница PokerStars: linkedin.com/company/pokerstars",
        "Unibet (Kindred / FDJ)": "LinkedIn группы Kindred", "Meridianbet": "LinkedIn группы Meridian Tech",
        "Kaizen Gaming (Betano)": "Отдельная страница бренда: linkedin.com/company/betano",
        "BingoPlus": "Оператор DigiPlus Interactive (Филиппины)"}
SEEN = {  # бренды из таблицы, упомянутые в наградах SiGMA
 "1xBet": "Победитель SiGMA Awards 2024–2026 (Euro-Med, Americas, Europe, Africa, South Asia)",
 "22Bet": "SiGMA East Europe 2024 — Best Casino Operator; Central Europe 2025 — Best Sportsbook",
 "22Bet Sportsbook": "SiGMA Central Europe 2025 — Best Sportsbook; Europe 2026 — шорт-лист",
 "MegaPari Sportsbook": "SiGMA Europe B2C 2023/2024 — Best Online Sportsbook", "MelBet": "SiGMA Africa 2025 — Best Casino Operator",
 "Bet365": "SiGMA Euro-Med 2025 — Best Online Sportsbook; Europe 2026", "BC Game Casino": "SiGMA Central Europe 2025 — Best Crypto Casino",
 "Betsson": "SiGMA Central Europe 2025 — Regulated Markets Champion", "Casumo": "SiGMA Europe 2026 — Best Casino Operator",
 "N1 Casino": "SiGMA Europe 2026 — шорт-лист Best Casino Operator", "WEEZYBET": "SiGMA Europe 2026 — шорт-лист Best Casino Operator",
 "WINWIN Partners": "WinWinBet — шорт-лист Best Casino Operator (Euro-Med 2025, Europe 2026)",
 "Netwin": "SiGMA Central Europe 2025 — Italian Market Rising Star", "Dragon Money": "SiGMA Central Europe 2025 — Best Community Engagement",
 "Parimatch": "SiGMA Asia 2025 — Breakthrough Sportsbook Operator", "BetWinner": "SiGMA Europe 2026 — шорт-лист",
 "Pin-Up Casino": "SiGMA Balkans — Best Online Casino", "Videoslots": "SiGMA Europe 2026 — шорт-лист",
 "Novibet": "SiGMA Europe 2026 — шорт-лист", "Bethard": "SiGMA Europe 2026 — шорт-лист",
 "KNG Partners": "SiGMA Central Europe 2025 — Best Mobile Casino (бренд KNG)", "Rocks Partners": "SiGMA Euro-Med 2025 — Industry Rising Star",
 "Thewolfpartners": "SiGMA Europe 2026 — шорт-лист", "888Casino": "888poker — SiGMA Europe B2C 2023/2024",
 "Betway": "Super Group — шорт-лист SiGMA Europe 2026", "GG.BET": "", }
rows = list(csv.reader(open(OUT, encoding="utf-8")))
have = {r[0] for r in rows[1:]}
for r in rows[1:]:
    if SEEN.get(r[0]) and "SiGMA Awards" not in r[9]:
        r[9] += "; SiGMA Awards"
        r[10] = "; ".join(x for x in [r[10], SEEN[r[0]]] if x)
add = 0
for n, t, src, _ in json.load(open("awards.json")):
    if n in have:
        continue
    d = db.get(PICK.get(n, ""), {}) if n in PICK else {}
    cy = "да — HQ на Кипре по LinkedIn" if d.get("ok") and is_cy(d) else ""
    note = "; ".join(x for x in [src, NOTE.get(n, ""), "" if n in PICK else "LinkedIn не найден автоматически"] if x)
    rows.append([n, t, "", "", d.get("url", "https://www.linkedin.com/company/" + PICK[n]) if n in PICK else "",
                 (d.get("Headquarters") or d.get("locality", "")) if d else "", d.get("Company size", "").replace(" employees", ""),
                 d.get("Industry", ""), cy, "SiGMA Awards (победители / шорт-листы)", note])
    add += 1
with open(OUT, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(rows)
b = rows[1:]
print(add, "added;", len(b), "rows;", sum(1 for r in b if r[4]), "LinkedIn;", sum(1 for r in b if r[8]), "Cyprus;",
      sum(1 for r in b if "SiGMA Awards" in r[9]), "with awards evidence")
