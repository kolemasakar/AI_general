"""Find pictures of unillustrated Ukrainian decorations via Ukrainian Wikipedia award articles.
Avoid recipient portraits and ribbon-only images; preserve image source URLs.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
import csv, io, re, unicodedata, requests

ROOT=Path(__file__).resolve().parent
IMAGES=ROOT/"images"
IMAGES.mkdir(exist_ok=True)
names=[s.strip() for s in (ROOT/"catalog_names.txt").read_text(encoding="utf-8").splitlines() if s.strip()]
mod=ROOT/"image_sources.csv"
commons=ROOT/"image_sources_commons.csv"
existing=set()
def norm(v):
    v=unicodedata.normalize("NFC",v.lower())
    return re.sub(r"[^а-яіїєґa-z0-9]+","",v)
def core(s):
    qs=re.findall(r"«([^»]+)»",s)
    return (qs[-1] if qs else s.split("—")[-1]).strip()
def comparable(s):
    return norm(core(s))
if mod.exists():
    with mod.open(encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f):
            if row["file"] and (IMAGES/(Path(row["file"]).stem+".png")).exists():
                existing.add(comparable(row["award"]))
if commons.exists():
    with commons.open(encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f):
            if row["status"].startswith("FOUND_") and (IMAGES/f"commons_{int(row['catalog_number']):03d}.png").exists():
                existing.add(comparable(row["award"]))
API="https://uk.wikipedia.org/w/api.php"
HEADERS={"User-Agent":"UkrainianAwardsCatalog/0.2 (public reference; source attribution)"}
BAD=["ribbon","стрічк","планк","portrait","портрет","герб","логотип","emblem","значок"]
def process(item):
    i,name=item
    if comparable(name) in existing:return None
    target=core(name)
    query=name.replace(" I, II, III, IV, V ступенів","").replace(" I, II, III ступенів","").replace(" I, II ступенів","")
    query=query.replace(" I, II класу","").replace(" I, II, III","")
    try:
        s=requests.get(API,params={"action":"query","format":"json","list":"search","srsearch":query,"srlimit":6},headers=HEADERS,timeout=10)
        s.raise_for_status()
        hits=s.json().get("query",{}).get("search",[])
    except Exception:
        return [i,name,"","","","SEARCH_ERROR"]
    choices=[]
    for hit in hits:
        title=hit["title"]
        overlap=SequenceMatcher(None,comparable(name),comparable(title)).ratio()
        if comparable(name) not in comparable(title) and comparable(title) not in comparable(name) and overlap<0.62:
            continue
        choices.append((overlap,title))
    if not choices:return [i,name,"","","","NOT_FOUND"]
    choices.sort(reverse=True)
    for overlap,title in choices[:2]:
        try:
            p=requests.get(API,params={"action":"query","format":"json","titles":title,"prop":"pageimages","piprop":"thumbnail|original","pithumbsize":1000},headers=HEADERS,timeout=10)
            p.raise_for_status()
            page=next(iter(p.json().get("query",{}).get("pages",{}).values()))
            link=page.get("thumbnail",{}).get("source","") or page.get("original",{}).get("source","")
            if not link or any(b in link.lower() for b in BAD):continue
            image=requests.get(link,headers=HEADERS,timeout=12);image.raise_for_status()
            with Image.open(io.BytesIO(image.content)) as im:
                if im.width<60 or im.height<60:continue
                im.convert("RGBA").save(IMAGES/f"wiki_{i:03d}.png")
            return [i,name,title,link,"https://uk.wikipedia.org/wiki/"+title.replace(" ","_"),f"FOUND_SCORE_{overlap:.2f}"]
        except Exception:
            continue
    return [i,name,"","","","NO_AWARD_IMAGE"]
from PIL import Image
with ThreadPoolExecutor(max_workers=6) as pool:
    results=[r for r in pool.map(process,enumerate(names,1)) if r is not None]
with (ROOT/"image_sources_wikipedia.csv").open("w",encoding="utf-8",newline="") as f:
    w=csv.writer(f);w.writerow(["catalog_number","award","article","image_url","source_url","status"]);w.writerows(results)
print("Wikipedia pictures:",sum(x[-1].startswith("FOUND") for x in results),"of",len(results))
