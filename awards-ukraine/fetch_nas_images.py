"""Retrieve properly labeled award images from government academy's gallery."""
from pathlib import Path
from urllib.parse import urljoin
import csv, io, re, unicodedata, requests
from bs4 import BeautifulSoup
from PIL import Image

ROOT=Path(__file__).resolve().parent; IMG=ROOT/"images";IMG.mkdir(exist_ok=True)
URL="https://www.nas.gov.ua/derzavni-nagorodi"
names=[s.strip() for s in (ROOT/"catalog_names.txt").read_text(encoding="utf-8").splitlines() if s.strip()]
S=requests.Session();S.headers["User-Agent"]="Mozilla/5.0 (Public Ukrainian awards catalog research)"
def norm(s):return re.sub(r"[^a-zа-яіїєґ0-9]+","",unicodedata.normalize("NFC",s.casefold()))
def key(s):
    chunks=re.findall("«([^»]+)»",s)
    if chunks:s=chunks[-1]
    return norm(s)
def match(label,name):
    a=norm(label);b=norm(name)
    if "геройукраїни" in a and name.startswith("Звання «Герой України»") and "Золота Зірка" in name:return True
    if "ордендержави" in a and name.startswith("Звання «Герой України»") and "Держави" in name:return True
    for p in ["князяярославамудрого","за заслуги","княгиніольги","замужність","богданахмельницького","орденсвободи","данилагалицького","запрацюізвитягу","25роківнезалежності"]:
        token=norm(p)
        if token in a and token in b:return True
    return False
rows=[]
try:
    r=S.get(URL,timeout=35);r.raise_for_status()
    soup=BeautifulSoup(r.text,"html.parser")
    # Many gallery images carry a descriptive alt string. Other cards have a heading/anchor adjacent.
    image_tags=soup.find_all("img")
    print("Gallery img tags",len(image_tags))
    seen=set()
    for tag in image_tags:
        alt=tag.get("alt","").strip()
        nearest=tag.find_parent(["a","div","li"])
        label=alt or ((nearest.get_text(" ",strip=True) if nearest else "")[:130])
        if not label or len(label)>160:continue
        target=next(((i,n) for i,n in enumerate(names,1) if match(label,n)),None)
        if target is None:continue
        i,name=target
        if i in seen:continue
        src=tag.get("data-src") or tag.get("src") or ""
        if not src:continue
        options=[urljoin(URL,src)]
        for d in ["80x80/","200x200/","400x400/"]:
            if d in src:
                options.insert(0,urljoin(URL,src.replace(d,"")))
        saved=False
        for candidate in options:
            try:
                pic=S.get(candidate,timeout=18);pic.raise_for_status()
                with Image.open(io.BytesIO(pic.content)) as im:
                    if im.width<50:continue
                    path=IMG/f"nas_{i:03d}.png"
                    im.convert("RGBA").save(path)
                    rows.append([i,name,label,candidate,f"FOUND_{im.width}x{im.height}"])
                    seen.add(i);saved=True;break
            except Exception:continue
        if saved:print(i,label)
except Exception as ex:print("NAS_ERROR",repr(ex))
with (ROOT/"image_sources_nas.csv").open("w",encoding="utf-8",newline="") as f:
    w=csv.writer(f);w.writerow(["catalog_number","award","image_label","source_url","status"]);w.writerows(rows)
print("NAS_FOUND",len(rows))
