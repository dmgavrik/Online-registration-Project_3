import subprocess,re,json,time,urllib.parse
from bs4 import BeautifulSoup
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
kws=["igaming","casino","betting","sportsbook","gambling","online casino","casino CRM","VIP manager casino","bookmaker","slots","affiliate igaming","payments igaming","risk betting","trader sportsbook"]
comp={}
for kw in kws:
    for start in range(0,250,25):
        u="https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"+urllib.parse.urlencode({"keywords":kw,"location":"Cyprus","start":start})
        h=subprocess.run(["curl","-s","-m","25","-A",UA,u],capture_output=True,text=True).stdout
        s=BeautifulSoup(h,"lxml")
        cards=s.select("div.base-card, li")
        got=0
        for c in s.select("h4.base-search-card__subtitle"):
            a=c.find("a"); name=c.get_text(" ",strip=True)
            slug=""
            if a and a.get("href"):
                m=re.search(r"linkedin\.com/company/([^?/]+)",a["href"]); slug=m.group(1) if m else ""
            title=c.find_previous("h3"); title=title.get_text(" ",strip=True) if title else ""
            e=comp.setdefault(name,{"slug":slug,"titles":set(),"kws":set()}); e["titles"].add(title); e["kws"].add(kw); got+=1
        if got==0: break
        time.sleep(1)
    print(kw,len(comp),flush=True)
json.dump({k:{"slug":v["slug"],"titles":sorted(v["titles"])[:6],"kws":sorted(v["kws"])} for k,v in comp.items()},open("jobs.json","w"),ensure_ascii=False,indent=0)
