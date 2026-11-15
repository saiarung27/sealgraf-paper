"""Render sealgraf-paper.pdf from paper.md (title page + body).

    python build_pdf.py [rendered-on date, e.g. "15 November 2026"]

Needs pandoc and Playwright's Chromium. The Markdown source is the
canonical text; this script only lays it out.
"""

import datetime
import pathlib
import re
import subprocess
import sys


HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "paper.md"
OUT = HERE / "sealgraf-paper.pdf"

CSS = """
@page { size: Letter; margin: 0.9in 0.95in; }
html { font-family: "Noto Serif", "DejaVu Serif", Georgia, serif; font-size: 10.5pt; line-height: 1.45; color: #111; }
h1, h2, h3, h4 { font-family: "DejaVu Sans", Arial, sans-serif; line-height: 1.25; break-after: avoid; }
h1 { font-size: 22pt; margin: 0 0 18pt; }
h2 { font-size: 14pt; margin: 22pt 0 8pt; }
h3 { font-size: 11.5pt; margin: 16pt 0 6pt; }
p, li { orphans: 3; widows: 3; }
code, pre { font-family: "DejaVu Sans Mono", monospace; font-size: 8.6pt; }
pre { background: #f5f5f3; padding: 8pt 10pt; white-space: pre-wrap; break-inside: avoid; }
blockquote { margin: 8pt 0 8pt 14pt; padding-left: 10pt; border-left: 2pt solid #bbb; color: #333; }
table { border-collapse: collapse; font-size: 9pt; }
th, td { border: 0.5pt solid #bbb; padding: 3pt 5pt; vertical-align: top; }
a { color: #0b4fbf; text-decoration: none; }
.title-page { break-after: page; padding-top: 1.6in; }
.title-page h1 { font-size: 26pt; }
.title-page .author { font-family: "DejaVu Sans", Arial, sans-serif; font-size: 13pt; margin: 0; }
.title-page .affil { font-family: "DejaVu Sans", Arial, sans-serif; margin: 2pt 0 28pt; }
.title-page .note { font-size: 9.5pt; color: #333; }
"""


def set_metadata(title: str, author: str) -> None:
    from pypdf import PdfReader, PdfWriter
    writer = PdfWriter()
    writer.append(PdfReader(str(OUT)))
    writer.add_metadata({
        "/Title": title, "/Author": author, "/Creator": "Sealgraf",
        "/Keywords": "agent payments, approval evidence, mandates, receipts, Sealgraf",
    })
    with open(OUT, "wb") as fh:
        writer.write(fh)


def _title_author() -> tuple[str, str]:
    head = SRC.read_text(encoding="utf-8").split("\n## Abstract", 1)[0]
    return (re.search(r"^# (.+)$", head, re.M).group(1).strip(),
            re.search(r"^\*\*(.+?)\*\*", head, re.M).group(1).strip())


def main() -> None:
    if sys.argv[1:] == ["--meta-only"]:
        # For environments where pypdf and Playwright live apart.
        set_metadata(*_title_author())
        return
    rendered_on = sys.argv[1] if len(sys.argv) > 1 else (
        datetime.date.today().strftime("%-d %B %Y"))
    md = SRC.read_text(encoding="utf-8")
    # Front matter: the title, the author block and the italic note,
    # up to the Abstract heading.
    head, body = md.split("\n## Abstract", 1)
    title = re.search(r"^# (.+)$", head, re.M).group(1).strip()
    author = re.search(r"^\*\*(.+?)\*\*", head, re.M).group(1).strip()
    affil = re.search(r"^\*\*.+?\*\*\s*\n(.+)$", head, re.M).group(1).strip()
    note = re.search(r"^\*(Technical paper.+?)\*\s*$", head, re.M | re.S).group(1)
    note = " ".join(note.split())
    body_html = subprocess.run(
        ["pandoc", "--from", "gfm", "--to", "html5"],
        input="## Abstract" + body, capture_output=True, text=True, check=True).stdout
    title_html = title.replace(": ", ":<br>", 1)
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{title}</title><style>{CSS}</style></head><body>
<section class="title-page">
<h1>{title_html}</h1>
<p class="author">{author}</p>
<p class="affil">{affil}</p>
<p class="note">{note}</p>
<p class="note">License: Creative Commons Attribution 4.0 International (CC BY 4.0).
Canonical text: Sealgraf. This PDF was rendered from the canonical Markdown
source (paper.md) on {rendered_on}.</p>
</section>
{body_html}
</body></html>"""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="load")
        page.pdf(path=str(OUT), format="Letter", print_background=True,
                 display_header_footer=True,
                 header_template="<span></span>",
                 footer_template=('<div style="width:100%;text-align:center;'
                                  'font-size:8pt;color:#666;font-family:DejaVu Sans,Arial">'
                                  '<span class="pageNumber"></span></div>'),
                 margin={"top": "0.85in", "bottom": "0.85in",
                         "left": "0.95in", "right": "0.95in"})
        browser.close()
    try:
        set_metadata(title, author)
    except ImportError:
        print("pypdf not found: run `python build_pdf.py --meta-only` where it is")

if __name__ == "__main__":
    main()
