"""Targeted Commons queries for national Ukrainian decorations; conservative title checks."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import csv, io, re, requests
from PIL import Image

ROOT=Path(__file__).resolve().parent
IMAGES=ROOT/"images"
IMAGES.mkdir(exist_ok=True)
NAMES=[s.strip() for s in (ROOT/"catalog_names.txt").read_text(encoding="utf-8").splitlines() if s.strip()]
# Indexed by stable row number in catalog_names.txt; never alter ordering.
ALIASES={
1:"Hero of Ukraine Gold Star medal",
2:"Hero of Ukraine Order of the State",
3:"Cross of Military Merit Ukraine",
4:"Order of Freedom Ukraine",
5:"Order of Prince Yaroslav the Wise Ukraine",
7:"Order of Merit Ukraine",
8:"Order of Bohdan Khmelnytsky Ukraine",
9:"Order of the Heavenly Hundred Heroes",
10:"Order for Courage Ukraine",
11:"Order of Princess Olga Ukraine",
12:"Order of Danylo Halytsky Ukraine",
13:"Order for Valiant Miner Labour Ukraine",
14:"Cross of Ivan Mazepa Ukraine",
15:"Medal for Military Service to Ukraine",
16:"Medal for Irreproachable Service Ukraine",
17:"Defender of the Fatherland medal Ukraine",
18:"Medal for Saving Life Ukraine",
19:"Medal for Labour and Valour Ukraine",
20:"20 years Independence of Ukraine medal",
21:"25 years Independence of Ukraine medal",
22:"25 years withdrawal of troops Afghanistan Ukraine medal",
23:"Medal for participation in anti terrorist operation Ukraine",
24:"Medal for humanitarian participation ATO Ukraine",
25:"Named firearms distinction Ukraine",
26:"For the Defence of Ukraine presidential decoration",
27:"National Legend of Ukraine medal",
28:"Cross of Saint Archangel Michael Ukraine",
29:"Iron Cross Winter Campaign Ukrainian People's Republic",
30:"Symon Petliura Cross Ukraine",
31:"Golden Cross of Military Merit Ukrainian Insurgent Army",
32:"Silver Cross of Military Merit Ukrainian Insurgent Army",
33:"Bronze Cross of Military Merit Ukrainian Insurgent Army",
34:"Golden Cross of Merit Ukrainian Insurgent Army",
35:"Silver Cross of Merit Ukrainian Insurgent Army",
36:"Bronze Cross of Merit Ukrainian Insurgent Army",
37:"Medal for Struggle in Especially Difficult Conditions Ukraine",
38:"For Military Valour Ministry of Defence Ukraine badge",
39:"Valour and Honour Ministry of Defence Ukraine badge",
53:"Badge of Honour Ministry of Defence of Ukraine",
54:"Medal for development of military cooperation Ukraine",
55:"Medal for exemplary service Ministry Defence Ukraine",
56:"Medal for personal achievements Ministry Defence Ukraine",
57:"Medal for assistance to armed forces Ukraine",
62:"10th anniversary of Armed Forces of Ukraine medal",
63:"15th anniversary of Armed Forces of Ukraine medal",
}
API="https://commons.wikimedia.org/w/api.php"
HEADERS={"User-Agent":"UkrainianAwardsCatalog/0.3 (documentation and source attribution)"}
STOP={"of","the","a","for","and","to","in","ukraine","ukrainian","medal","order","badge","cross","award","decoration","years","year","ministry","defence","military","armed","forces"}
BAD={"dog","собака","diploma","диплом","certificate","awardee","portrait","ribbon","ribbons","bar","insignia bar","sheet","poster","collage","document","documentary","flag"}
def words(s):
    return {x for x in re.findall(r"[a-z]{3,}",s.lower()) if x not in STOP}
def candidate_score(alias,title):
    t=title.lower()
    if any(b in t for b in BAD):return 0
    a=words(alias); b=words(title)
    if not a:return 0
    hit=len(a & b)
    # Require at least two distinctive words and 70 percent query coverage.
    if hit<min(2,len(a)):return 0
    return hit/len(a)
def get(q):
    try:
        r=requests.get(API,params=q,headers=HEADERS,timeout=12);r.raise_for_status()
        return r.json()
    except Exception:return {}
def process(pair):
    idx,alias=pair
    query=alias.replace(" Ukraine","")
    data=get({"action":"query","format":"json","list":"search","srnamespace":6,"srsearch":query,"srlimit":30})
    choices=[]
    for p in data.get("query",{}).get("search",[]):
        title=p.get("title","")
        score=candidate_score(alias,title)
        if score>=0.72:choices.append((score,title))
    choices.sort(reverse=True)
    for score,title in choices[:3]:
        data=get({"action":"query","format":"json","titles":title,"prop":"imageinfo","iiprop":"url|mime","iiurlwidth":900})
        pages=list(data.get("query",{}).get("pages",{}).values())
        if not pages:continue
        info=(pages[0].get("imageinfo") or [{}])[0]
        if info.get("mime") not in ("image/jpeg","image/png","image/webp"):continue
        url=info.get("thumburl") or info.get("url")
        if not url:continue
        try:
            r=requests.get(url,headers=HEADERS,timeout=12);r.raise_for_status()
            with Image.open(io.BytesIO(r.content)) as im:
                if im.width<60 or im.height<60:continue
                im.convert("RGBA").save(IMAGES/f"english_{idx:03d}.png")
            return [idx,NAMES[idx-1],alias,title,url,f"FOUND_SCORE_{score:.2f}"]
        except Exception:continue
    return [idx,NAMES[idx-1],alias,"","","NOT_FOUND"]
with ThreadPoolExecutor(max_workers=5) as ex:
    rows=list(ex.map(process,ALIASES.items()))
with (ROOT/"image_sources_english.csv").open("w",encoding="utf-8",newline="") as f:
    w=csv.writer(f);w.writerow(["catalog_number","award","english_search","file_title","image_url","status"]);w.writerows(rows)
print("English Commons images",sum(r[-1].startswith("FOUND") for r in rows),"/",len(rows))
