import json, time, random
from li_crawl import fetch, parse
from final_list import ROWS

db = json.load(open("li_db.json"))
todo = [s for r in ROWS if not any(db.get(x, {}).get("ok") for x in r[4]) for s in r[4] if s not in db]
print(len(todo), flush=True)
i = 0
while i < len(todo):
    s = todo[i]
    code, html = fetch(s)
    if code in ("999", "429", "000"):
        print("rl", flush=True); time.sleep(75); continue
    db[s] = (parse(s, html) | {"ok": True}) if code == "200" else {"slug": s, "ok": False, "code": code}
    print(s, code, db[s].get("name", ""), db[s].get("Headquarters", ""), flush=True)
    json.dump(db, open("li_db.json", "w"), ensure_ascii=False)
    i += 1
    time.sleep(random.uniform(3, 5))
