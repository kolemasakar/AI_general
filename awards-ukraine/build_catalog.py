from pathlib import Path
import csv, re, unicodedata
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def norm(value):
    value = re.sub(r"^(нагрудний знак|медаль)\s+", "", value.casefold())
    found = re.findall(r"«([^»]+)»", value)
    if found: value = found[0]
    value = unicodedata.normalize("NFC",value)
    return re.sub(r"\W+", "", value)

root = Path(__file__).resolve().parent
names = [line.strip() for line in (root / "catalog_names.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
sources = {}
manifest = root / "image_sources.csv"
if manifest.exists():
    with manifest.open(encoding="utf-8",newline="") as f:
        for item in csv.DictReader(f):
            if item["quality_status"].startswith(("ACCEPTED_", "FOUND_")):
                key = norm(item["award"])
                png = root / "images" / (Path(item["file"]).stem + ".png")
                if png.exists(): sources.setdefault(key,png)
commons = {}
commons_manifest = root / "image_sources_commons.csv"
if commons_manifest.exists():
    with commons_manifest.open(encoding="utf-8", newline="") as f:
        for item in csv.DictReader(f):
            if item["status"].startswith("FOUND_"):
                p = root / "images" / f"commons_{int(item['catalog_number']):03d}.png"
                if p.exists(): commons[int(item["catalog_number"])] = p
wiki = {}
wiki_manifest = root / "image_sources_wikipedia.csv"
if wiki_manifest.exists():
    with wiki_manifest.open(encoding="utf-8", newline="") as f:
        for item in csv.DictReader(f):
            if item["status"].startswith("FOUND_"):
                p = root / "images" / f"wiki_{int(item['catalog_number']):03d}.png"
                if p.exists(): wiki[int(item["catalog_number"])] = p
english = {}
english_manifest = root / "image_sources_english.csv"
if english_manifest.exists():
    with english_manifest.open(encoding="utf-8", newline="") as f:
        for item in csv.DictReader(f):
            if item["status"].startswith("FOUND_"):
                p = root / "images" / f"english_{int(item['catalog_number']):03d}.png"
                if p.exists(): english[int(item["catalog_number"])] = p
nas={}
nas_manifest=root/"image_sources_nas.csv"
if nas_manifest.exists():
    with nas_manifest.open(encoding="utf-8",newline="") as f:
        for item in csv.DictReader(f):
            if item["status"].startswith("FOUND_"):
                pic=root/"images"/f"nas_{int(item['catalog_number']):03d}.png"
                if pic.exists():nas[int(item["catalog_number"])]=pic
asv={}
asv_manifest=root/"image_sources_asv.csv"
if asv_manifest.exists():
    with asv_manifest.open(encoding="utf-8",newline="") as f:
        for item in csv.DictReader(f):
            if item["status"]=="FOUND":
                pic=root/"images"/item["file"]
                if pic.exists():asv.setdefault(int(item["catalog_number"]),pic)
d = Document()
section = d.sections[0]
section.top_margin, section.bottom_margin = Cm(1.5), Cm(1.5)
section.left_margin, section.right_margin = Cm(1.7), Cm(1.7)
style = d.styles["Normal"]
style.font.name = "Arial"
style.font.size = Pt(10)
p = d.add_paragraph("КАТАЛОГ НАГОРОД УКРАЇНИ")
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.runs[0].bold = True
p.runs[0].font.size = Pt(15)
table = d.add_table(rows=1, cols=3)
table.style = "Table Grid"
for c, title in zip(table.rows[0].cells, ["№ з/п", "Назва нагороди", "Зображення нагороди"]):
    c.text = title
    for r in c.paragraphs[0].runs: r.bold = True
trPr = table.rows[0]._tr.get_or_add_trPr()
heading = OxmlElement("w:tblHeader")
heading.set(qn("w:val"), "true")
trPr.append(heading)
for no, name in enumerate(names, 1):
    cells = table.add_row().cells
    cells[0].text = str(no)
    cells[1].text = name
    key = norm(name)
    image = nas.get(no) or asv.get(no) or sources.get(key) or english.get(no) or commons.get(no) or wiki.get(no)
    if image:
        cells[2].paragraphs[0].add_run().add_picture(str(image), width=Cm(4))
    else:
        cells[2].text = "—"
    for c in cells: c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
for row in table.rows:
    row.cells[0].width = Cm(1.5)
    row.cells[1].width = Cm(10.3)
    row.cells[2].width = Cm(4.7)
d.save(root / "Каталог_нагород_України_чернетка.docx")
(root / "build_count.txt").write_text(str(len(names)) + "\n", encoding="utf-8")
(root / "image_coverage.txt").write_text(f"total={len(names)}\nwith_image={sum(1 for i,n in enumerate(names,1) if (norm(n) in sources or i in commons or i in wiki or i in english or i in nas or i in asv))}\n",encoding="utf-8")
print("Records:", len(names))
