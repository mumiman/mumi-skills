#!/usr/bin/env python3
"""
Build a Word .docx tutorial from a steps.json spec.

The .docx structure is:
  - Title (large, bold)
  - Brief intro paragraph
  - For each step:
      - "Step N" heading (or "ขั้นตอนที่ N" for Thai)
      - Caption text (14pt)
      - Annotated screenshot (centered, fit to ~6 inches wide)
      - Spacer

Usage:
    python build_docx.py --spec steps.json --output tutorial.docx
"""
import argparse
import json
from io import BytesIO
import zipfile
from spec import load_spec, localized, report, SpecError
from media import prepare_image
from pathlib import Path

from PIL import Image
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


def font_for_language(language: str) -> str:
    """Pick a default font that renders the given language correctly."""
    if (language or "").lower() in ("thai", "th"):
        # TH Sarabun New is the standard for Thai documents (incl. Thai government
        # standard). Most Thai Windows / Word installations have it; if not, Word
        # will substitute a similar Thai font.
        return "TH Sarabun New"
    return "Calibri"


def sizes_for_language(language: str) -> dict:
    """
    Per-language point sizes. TH Sarabun New renders visually smaller than
    Calibri at the same point size, so Thai needs larger numbers to match
    the visual weight (and to align with the standard Thai government
    document sizing — 16pt body in TH Sarabun New).
    """
    if (language or "").lower() in ("thai", "th"):
        return {
            "title":        28,
            "intro":        16,
            "step_heading": 20,
            "caption":      18,
        }
    return {
        "title":        24,
        "intro":        12,
        "step_heading": 16,
        "caption":      14,
    }


def step_label(language: str) -> str:
    if (language or "").lower() in ("thai", "th"):
        return "ขั้นตอนที่"
    return "Step"


def apply_font_to_paragraph(paragraph, font_name: str, size_pt: float = None,
                            bold: bool = None) -> None:
    """
    Force a font name onto every run in the paragraph, including the complex-script
    (Thai) and east-Asian font slots — otherwise Word may pick a default Thai font
    that doesn't match.
    """
    for run in paragraph.runs:
        run.font.name = font_name
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.insert(0, rFonts)
        rFonts.set(qn("w:ascii"), font_name)
        rFonts.set(qn("w:hAnsi"), font_name)
        rFonts.set(qn("w:cs"), font_name)
        rFonts.set(qn("w:eastAsia"), font_name)
        if size_pt is not None:
            run.font.size = Pt(size_pt)
            # Also set complex-script size for Thai
            sz_cs = rPr.find(qn("w:szCs"))
            if sz_cs is None:
                sz_cs = OxmlElement("w:szCs")
                rPr.append(sz_cs)
            sz_cs.set(qn("w:val"), str(int(size_pt * 2)))
        if bold is not None:
            run.font.bold = bold


def add_styled_paragraph(doc, text: str, font: str, size_pt: float,
                         bold: bool = False,
                         align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    p.alignment = align
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size_pt)
    apply_font_to_paragraph(p, font, size_pt=size_pt, bold=bold)
    return p


def build_docx(spec_path: str, output_path: str, asset_root=None) -> None:
    spec, warnings = load_spec(spec_path)
    language = spec['language']
    font = spec['render'].get('document_font', font_for_language(language))
    sizes = sizes_for_language(language)
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Inches(8.27), Inches(11.69)
    section.top_margin = section.bottom_margin = Inches(.75)
    section.left_margin = section.right_margin = Inches(.75)
    doc.core_properties.author = ''
    doc.core_properties.last_modified_by = ''
    doc.core_properties.title = spec['title']
    normal = doc.styles['Normal']
    normal.font.name, normal.font.size = font, Pt(sizes['intro'])
    normal.paragraph_format.space_after = Pt(6)
    if spec.get('logo'):
        data, dimensions = prepare_image({'path': spec['logo']}, spec_path, 1, spec['render']['accent'], asset_root)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        picture = p.add_run().add_picture(BytesIO(data), width=Inches(min(2.4, 1.2 * dimensions[0]/dimensions[1])))
        picture._inline.docPr.set('descr', 'Logo')
    title = add_styled_paragraph(doc, spec['title'], font, sizes['title'], bold=True)
    title.style = doc.styles['Title']
    if spec.get('intro'):
        add_styled_paragraph(doc, spec['intro'], font, sizes['intro'])
    if spec.get('prerequisites'):
        add_styled_paragraph(doc, 'ก่อนเริ่มใช้งาน' if language == 'th' else 'Before you start', font, sizes['step_heading'], bold=True)
        for value in spec['prerequisites']:
            add_styled_paragraph(doc, '• ' + value, font, sizes['intro'])
    label = step_label(language)
    for index, step in enumerate(spec['steps'], 1):
        heading = f"{label} {index}" + (': ' + localized(spec, step, 'title') if localized(spec, step, 'title') else '')
        h = add_styled_paragraph(doc, heading, font, sizes['step_heading'], bold=True)
        h.style = doc.styles['Heading 1']
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.keep_with_next = True
        caption = add_styled_paragraph(doc, localized(spec, step, 'instruction'), font, sizes['caption'])
        if step.get('screenshot'):
            caption.paragraph_format.keep_with_next = True
            shot = step['screenshot']
            if not shot.get('privacy_reviewed'):
                warnings.append(f"{step['id']}: screenshot privacy review required before sharing")
            data, (width, height) = prepare_image(shot, spec_path, index, spec['render']['accent'], asset_root)
            # No minimum width: tall images must never exceed the usable height.
            width_in = min(6.5, 5.7 * width / height)
            if width_in < 2:
                warnings.append(f"{step['id']}: tall screenshot may be unreadable; crop into task-specific regions")
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            picture = p.add_run().add_picture(BytesIO(data), width=Inches(width_in))
            picture._inline.docPr.set('descr', shot.get('alt') or localized(spec, step, 'instruction'))
        else:
            warnings.append(f"{step['id']}: text-only step; screenshot unavailable")
        for key, th, en in [('expected_result','ผลที่คาดหวัง','Expected result'),('troubleshooting','เมื่อพบปัญหา','Troubleshooting')]:
            value = localized(spec, step, key)
            if value:
                add_styled_paragraph(doc, (th if language == 'th' else en) + ': ' + value, font, sizes['intro'])
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    with zipfile.ZipFile(output_path) as archive:
        if archive.testzip(): raise SpecError('DOCX archive integrity failed')
    report(str(output_path)+'.qa.json', [
        {'name':'schema_and_media','status':'passed'},
        {'name':'docx_archive_and_numbering','status':'passed'},
        {'name':'rendered_layout_fonts_annotations','status':'not_run','reason':'Render with Word/LibreOffice and inspect every page before release.'}
    ], warnings)
    print(f'Saved -> {output_path}')


def main() -> None:
    p = argparse.ArgumentParser(description="Build a .docx tutorial from steps.json.")
    p.add_argument("--spec", required=True, help="Path to steps.json")
    p.add_argument("--output", required=True, help="Path to write the .docx")
    p.add_argument("--asset-root", help="Explicitly approved directory for external images")
    args = p.parse_args()
    try:
        build_docx(args.spec, args.output, args.asset_root)
    except (SpecError, OSError, ValueError) as exc:
        p.exit(2, f"Cannot build document: {exc}\n")


if __name__ == "__main__":
    main()
