"""Official presidential insignia artwork linked directly from president.gov.ua decrees."""
from pathlib import Path
import requests, io, csv
from PIL import Image
root=Path(__file__).resolve().parent; dest=root/"images";dest.mkdir(exist_ok=True)
items=[
(6,"Орден Європи","https://www.president.gov.ua/documents/5992026-60357","https://www.president.gov.ua/storage/j-image-storage/59/52/77/3c0a197159e841143ad675d0c90be7c7_1784102808_wysiwyg.png"),
]
rows=[]
for no,name,page,url in items:
 try:
  resp=requests.get(url,headers={"User-Agent":"Mozilla/5.0","Referer":page},timeout=20);resp.raise_for_status()
  with Image.open(io.BytesIO(resp.content)) as im:
   destpath=dest/f"president_{no:03d}.png"
   im.convert("RGBA").save(destpath)
  status="FOUND"
 except Exception as e:status=f"ERROR_{type(e).__name__}"
 rows.append([no,name,page,url,status])
with (root/"image_sources_president.csv").open("w",encoding="utf-8",newline="") as f:
 w=csv.writer(f);w.writerow(["catalog_number","award","official_decree","image_url","status"]);w.writerows(rows)
print(rows)
