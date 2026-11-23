from pathlib import Path
from urllib.parse import urljoin
import csv, re
import requests
from bs4 import BeautifulSoup
from PIL import Image

root=Path(__file__).resolve().parent
out=root / "images_reference"
out.mkdir(exist_ok=True)
final=root / "images"
final.mkdir(exist_ok=True)
sources=[
 ("mod","https://mod.gov.ua/explanation/zaohochuvalni-vidznaki-ministerstva-oboroni"),
 ("commander","https://mod.gov.ua/explanation/pochesni-nagrudni-znaki-golovnokomanduvacha-zbrojnih-sil-ukrayini"),
]
rows=[]
session=requests.Session()
session.headers["User-Agent"]="Mozilla/5.0 (catalog educational reference; github project)"
for group,url in sources:
 try:
  res=session.get(url,timeout=30); res.raise_for_status()
  soup=BeautifulSoup(res.text,"html.parser")
 except Exception as ex:
  rows.append([group,"",url,"","", "", "PAGE_ERROR: "+str(ex)])
  continue
 count=0
 for heading in soup.find_all(["h3","h4"]):
  name=heading.get_text(" ",strip=True)
  if not (name.startswith("Медаль") or name.startswith("Нагрудний") or name.startswith("«") or name.startswith("“")): continue
  image=heading.find_next(["img","h3","h4"])
  if image is None or image.name != "img": continue
  raw=image.get("src") or image.get("data-src") or ""
  if not raw and image.get("srcset"):raw=image["srcset"].split(",")[-1].strip().split(" ")[0]
  if not raw:continue
  src=urljoin(url,raw)
  count+=1
  suffix=".webp" if ".webp" in src.lower() else ".png" if ".png" in src.lower() else ".jpg"
  path=out / f"{group}_{count:02d}{suffix}"
  try:
   r=session.get(src,timeout=30);r.raise_for_status()
   path.write_bytes(r.content)
   with Image.open(path) as im:
    width,height=im.size
    status="SOURCE_ONLY; QUALITY_UNVERIFIED"
    if im.mode in ("RGBA","LA") and im.getextrema()[-1][0] < 255:
     rgba=im.convert("RGBA")
     bb=rgba.getchannel("A").getbbox()
     if bb and bb[2]-bb[0]>=945:
      cropped=rgba.crop(bb)
      cropped.save(final / f"{group}_{count:02d}.png",dpi=(600,600))
      status=f"ACCEPTED_VISIBLE_WIDTH_{cropped.width}"
     else:status=f"VISIBLE_WIDTH_BELOW_945_{bb[2]-bb[0] if bb else 0}"
    elif width<945:status="SOURCE_WIDTH_BELOW_945"
    else:status="OPAQUE_BACKGROUND; QUALITY_UNVERIFIED"
   rows.append([group,name,src,path.name,width,height,status])
  except Exception as ex:
   if path.exists():path.unlink()
   rows.append([group,name,src,"","","","DOWNLOAD_ERROR: "+str(ex)])
with (root / "image_sources.csv").open("w",encoding="utf-8",newline="") as file:
 writer=csv.writer(file);writer.writerow(["group","award","source_url","file","width_px","height_px","quality_status"]);writer.writerows(rows)
print("Images:",sum(bool(r[3]) for r in rows),"rows:",len(rows))
