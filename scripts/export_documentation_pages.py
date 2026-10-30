#!/usr/bin/env python3
"""Pre-render QuantTerminal_Project_Documentation.pdf into PNG pages + extracted text.

The Project Documentation page serves these committed files, so it does not need
PyMuPDF or a browser PDF viewer at runtime. Re-run after the PDF changes:

    python scripts/export_documentation_pages.py
"""
import json
import os

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "QuantTerminal_Project_Documentation.pdf")
OUT = os.path.join(ROOT, "docs", "project_documentation")
DPI = 150


def main():
    os.makedirs(OUT, exist_ok=True)
    for name in os.listdir(OUT):
        if name.startswith("page_") and name.endswith(".png"):
            os.remove(os.path.join(OUT, name))
    text = {}
    with pymupdf.open(PDF) as doc:
        for i, page in enumerate(doc, start=1):
            page.get_pixmap(dpi=DPI).save(os.path.join(OUT, f"page_{i:02d}.png"))
            text[str(i)] = page.get_text()
    with open(os.path.join(OUT, "text.json"), "w", encoding="utf-8") as fh:
        json.dump({"pages": len(text), "text": text}, fh, ensure_ascii=False)
    print(f"Exported {len(text)} pages to {OUT}")


if __name__ == "__main__":
    main()
