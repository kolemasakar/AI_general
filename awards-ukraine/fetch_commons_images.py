"""Best-effort Commons image retrieval for awards missing from official MOD pages.
Only a file whose title semantically matches the award is accepted.
Images are not resized or promoted as authentic when the match is uncertain.
"""
from pathlib import Path
from difflib import SequenceMatcher
import csv, io, re, time, unicodedata
from concurrent.futures import ThreadPoolExecutor
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "images"
IMAGES.mkdir(exist_ok=True)
NAMES = [v.strip() for v in (ROOT / "catalog_names.txt").read_text(encoding="utf-8").splitlines() if v.strip()]
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "UkrainianAwardsCatalog/0.2 (public research archive; image attribution in CSV)"})
API = "https://commons.wikimedia.org/w/api.php"
MAP = ROOT / "image_sources_commons.csv"
EXCLUDE = {"диплом","certificate","свідоцтво","посвідчення","документ","собака","dog","ribbon","ribbons","bar","ribbonbar","стрічка","планка","планки","сертифікат","посвідчення","portrait","портрет","герб","герби"}
STOP = {"орден","медаль","відзнака","нагородний","нагрудний","знак","україни","українська","президента","звання","років","ступенів","ступеня","класу","моу","збройних","сил","і","та","за","для","iii","ii","iv","v","i"}

def norm(s):
    s=unicodedata.normalize("NFKC",s).lower().replace("’","'").replace("ʼ","'")
    return re.sub(r"[^0-9a-zа-яіїєґ]+"," ",s).strip()

def tokens(s):
    return {w for w in norm(s).split() if w not in STOP and len(w)>2}

def core(s):
    parts=re.findall(r"«([^»]+)»",s)
    return (parts[-1] if parts else s.split("—")[-1]).strip()

def score(name, title):
    base=tokens(core(name)); t=tokens(title)
    if not base:return 0
    overlap=len(base&t)/len(base)
    if len(base)==1 and overlap==1 and len(t)>5:
        overlap*=0.65
    bad=EXCLUDE & t
    if bad:return 0
    if "холодна зброя" in name.casefold() and "гур" not in norm(title):return 0
    return overlap*0.85 + SequenceMatcher(None,norm(core(name)),norm(title)).ratio()*0.15

def get(params):
    for attempt in range(1):
        try:
            r=SESSION.get(API,params=params,timeout=8);r.raise_for_status()
            return r.json()
        except Exception:
            if attempt==0: time.sleep(1)
    return {}

def search(name):
    query=core(name)
    variants=[f'intitle:"{query}"',query]
    if query==name and len(query)>55:variants=[query[:55]]
    seen=set()
    candidates=[]
    for q in variants:
        data=get({"action":"query","format":"json","list":"search","srnamespace":6,"srlimit":12,"srsearch":q})
        for item in data.get("query",{}).get("search",[]):
            title=item.get("title","")
            if title in seen:continue
            seen.add(title)
            candidates.append((score(name,title),title))
        if any(sc>=0.79 for sc,_ in candidates):break
    candidates.sort(reverse=True)
    if not candidates or candidates[0][0]<0.74:return None
    bestscore,besttitle=candidates[0]
    data=get({"action":"query","format":"json","titles":besttitle,"prop":"imageinfo","iiprop":"url|mime|extmetadata","iiurlwidth":900})
    pages=list(data.get("query",{}).get("pages",{}).values())
    if not pages:return None
    info=(pages[0].get("imageinfo") or [{}])[0]
    url=info.get("thumburl") or info.get("url")
    if not url or info.get("mime") not in ("image/jpeg","image/png","image/webp"):return None
    return bestscore,besttitle,url,info.get("descriptionurl","")

def key(s):
    return norm(core(s))

# Index direct MOD images by official source labels, which sometimes differ in case or prefix.
already=set()
p=ROOT/"image_sources.csv"
if p.exists():
    with p.open(encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f):
            if row.get("file") and (IMAGES / (Path(row["file"]).stem + ".png")).exists():
                already.add(key(row["award"]))
def process(entry):
    i,name=entry
    if key(name) in already:
        return None
    result=search(name)
    if not result:
        return [i,name,"","","","NOT_FOUND"]
    confidence,title,url,source=result
    target=IMAGES/f"commons_{i:03d}.png"
    try:
        resp=requests.get(url,headers={"User-Agent":"UkrainianAwardsCatalog/0.2 (public research reference)"},timeout=10);resp.raise_for_status()
        with Image.open(io.BytesIO(resp.content)) as im:
            if im.width<60 or im.height<60: raise ValueError("tiny thumbnail")
            im.convert("RGBA").save(target)
        return [i,name,title,url,source,f"FOUND_SCORE_{confidence:.2f}"]
    except Exception as err:
        return [i,name,title,url,source,f"DOWNLOAD_ERROR_{type(err).__name__}"]
with ThreadPoolExecutor(max_workers=6) as pool:
    rows=[r for r in pool.map(process,enumerate(NAMES,1)) if r is not None]
with MAP.open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f);w.writerow(["catalog_number","award","commons_file","image_url","description_url","status"]);w.writerows(rows)
print("Commons downloaded:",sum(x[-1].startswith("FOUND") for x in rows),"of",len(rows))
