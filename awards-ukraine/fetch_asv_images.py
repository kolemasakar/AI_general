"""Retrieve identifiable award depictions from Ukrainian armed forces academy official portal."""
from pathlib import Path
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import csv,io,requests
from bs4 import BeautifulSoup
from PIL import Image
root=Path(__file__).resolve().parent
out=root/"images";out.mkdir(exist_ok=True)
site="https://asv.mil.gov.ua"
records={
1:["/awards/orden-zolota-zirka-vidznaky-prezydenta-ukrayiny-heroy-ukrayiny"],
8:["/awards/orden-bohdana-khmelnytskoho-i-stupenya","/awards/orden-bohdana-khmelnytskoho-ii-stupenya","/awards/orden-bohdana-khmelnytskoho-iii-stupenya"],
10:["/awards/orden-za-muzhnist-i-stupenya","/awards/orden-za-muzhnist-ii-stupenya","/awards/orden-za-muzhnist-iii-stupenya"],
12:["/awards/orden-danyla-halytskoho"],
15:["/awards/medal-za-viyskovu-sluzhbu-ukrayini"],
16:["/awards/medal-za-bezdohannu-sluzhbu-iii-stupenya"],
17:["/awards/medal-zakhysnyku-vitchyzny"],
}
names=[l.strip() for l in (root/"catalog_names.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
def run(pair):
 no,paths=pair
 record=[]
 for path in paths:
  url=urljoin(site,path)
  try:
   r=requests.get(url,timeout=20);r.raise_for_status()
   soup=BeautifulSoup(r.text,"html.parser")
   # Direct official award gallery image path, not portraits or decorative site graphics.
   imgs=[t for t in soup.select("img") if "/awards/" in (t.get("src") or "") and "/sites/default/files/awards/" in (t.get("src") or "")]
   if not imgs:
    imgs=[t for t in soup.select("img") if "/sites/default/files/awards/" in (t.get("src") or "")]
   if not imgs:continue
   src=urljoin(site,imgs[0].get("src"))
   rr=requests.get(src,timeout=20);rr.raise_for_status()
   with Image.open(io.BytesIO(rr.content)) as im:
    if im.width<45 or im.height<45:continue
    result=out/f"asv_{no:03d}_{len(record)+1}.png"
    im.convert("RGBA").save(result)
   record.append([no,names[no-1],url,src,result.name,"FOUND"])
  except Exception as e:record.append([no,names[no-1],url,"","",f"ERROR_{type(e).__name__}"])
 return record
with ThreadPoolExecutor(max_workers=5) as pool:
 rows=[x for group in pool.map(run,records.items()) for x in group]
with (root/"image_sources_asv.csv").open("w",encoding="utf-8",newline="") as f:
 w=csv.writer(f);w.writerow(["catalog_number","award","official_page","image_url","file","status"]);w.writerows(rows)
print("ASV_FOUND",sum(r[-1]=="FOUND" for r in rows),"ROWS",len(rows))
