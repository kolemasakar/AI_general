from pathlib import Path
import csv, re
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

root = Path(__file__).resolve().parent
names = [line.strip() for line in (root / "catalog_names.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
sources = {}
manifest = root / "image_sources.csv"
if manifest.exists():
    with manifest.open(encoding="utf-8",newline="") as f:
        for item in csv.DictReader(f):
            if item["quality_status"].startswith("ACCEPTED_"):
                key = re.sub(r"\\W+", "", item["award"].casefold())
                png = root / "images" / (Path(item["file"]).stem + ".png")
                if png.exists(): sources.setdefault(key,png)
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
    key = re.sub(r"\\W+", "", name.casefold())
    if key in sources:
        cells[2].paragraphs[0].add_run().add_picture(str(sources[key]), width=Cm(4))
    else:
        cells[2].text = "—"
    for c in cells: c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
for row in table.rows:
    row.cells[0].width = Cm(1.5)
    row.cells[1].width = Cm(10.3)
    row.cells[2].width = Cm(4.7)
d.save(root / "Каталог_нагород_України_чернетка.docx")
(root / "build_count.txt").write_text(str(len(names)) + "\n", encoding="utf-8")
print("Records:", len(names))
