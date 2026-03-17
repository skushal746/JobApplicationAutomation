"""
convert_md.py — Markdown/plain-text → PDF using reportlab (pure Python, no system deps).
Called by convert.sh when no LaTeX engine is available.

Usage:
    python convert_md.py <input.txt> <output.pdf>
"""

import sys
import os
import re

from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem, Image, PageBreak
)

from reportlab.lib.enums import TA_LEFT


def parse_and_build(text: str) -> list:
    """
    Parse Markdown-ish text line by line into reportlab Flowables.
    Handles: # headings, **bold**, bullet lists (- / *), horizontal rules (---), blank lines.
    """
    styles = getSampleStyleSheet()

    # Custom styles
    h1 = ParagraphStyle("H1", parent=styles["Normal"],
                        fontSize=18, leading=22, fontName="Helvetica-Bold",
                        spaceBefore=8, spaceAfter=4, textColor=colors.HexColor("#0d1b2a"))
    h2 = ParagraphStyle("H2", parent=styles["Normal"],
                        fontSize=12, leading=15, fontName="Helvetica-Bold",
                        spaceBefore=10, spaceAfter=3, textColor=colors.HexColor("#1565c0"),
                        borderPadding=(0, 0, 2, 0))
    h3 = ParagraphStyle("H3", parent=styles["Normal"],
                        fontSize=11, leading=14, fontName="Helvetica-Bold",
                        spaceBefore=6, spaceAfter=2)
    body = ParagraphStyle("Body", parent=styles["Normal"],
                          fontSize=10.5, leading=15, fontName="Helvetica",
                          spaceBefore=2, spaceAfter=2)
    bullet_style = ParagraphStyle("Bullet", parent=body, leftIndent=12)

    story = []
    lines = text.splitlines()
    bullet_buffer = []  # accumulate consecutive bullet lines

    def flush_bullets():
        if bullet_buffer:
            items = [ListItem(Paragraph(_inline(b), bullet_style), bulletColor=colors.HexColor("#1565c0"))
                     for b in bullet_buffer]
            story.append(ListFlowable(items, bulletType="bullet", start="•",
                                       leftIndent=16, bulletFontSize=10))
            story.append(Spacer(1, 3))
            bullet_buffer.clear()

    for line in lines:
        stripped = line.strip()

        # Horizontal rule or Page break
        if stripped == "---page---":
            flush_bullets()
            story.append(PageBreak())
            continue
            
        if re.fullmatch(r"-{3,}|={3,}", stripped):
            flush_bullets()
            story.append(HRFlowable(width="100%", thickness=0.8,
                                    color=colors.HexColor("#c5d8f5"), spaceAfter=4))
            continue


        # Headings
        if stripped.startswith("### "):
            flush_bullets()
            story.append(Paragraph(_inline(stripped[4:]), h3))
            continue
        if stripped.startswith("## "):
            flush_bullets()
            story.append(Paragraph(_inline(stripped[3:]), h2))
            story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=colors.HexColor("#c5d8f5"), spaceAfter=2))
            continue
        if stripped.startswith("# "):
            flush_bullets()
            story.append(Paragraph(_inline(stripped[2:]), h1))
            continue

        # Bullet lines
        if re.match(r"^[-*]\s+", stripped):
            bullet_buffer.append(re.sub(r"^[-*]\s+", "", stripped))
            continue

        # Images: ![caption](path)
        img_match = re.match(r"!\[(.*?)\]\((.*?)\)", stripped)
        if img_match:
            flush_bullets()
            caption = img_match.group(1)
            img_path = img_match.group(2)
            
            # Resolve relative paths if needed
            if not os.path.isabs(img_path):
                # Try relative to project root
                proj_root = "/Users/kushalsharma/Documents/Projects2026/JobApplicationAutomation/CoverLetterResumeMaking"
                full_img_path = os.path.join(proj_root, img_path)
            else:
                full_img_path = img_path
                
            if os.path.exists(full_img_path):
                try:
                    # Scale image to fit page width (LETTER is 8.5x11 inches)
                    # Content width is approx 6.7 inches (8.5 - 2*0.9)
                    max_w = 6.5 * inch
                    max_h = 4.0 * inch # allow space for other things
                    
                    img = Image(full_img_path)
                    img_w, img_h = img.drawWidth, img.drawHeight
                    
                    aspect = img_h / float(img_w)
                    if img_w > max_w:
                        img_w = max_w
                        img_h = img_w * aspect
                    if img_h > max_h:
                        img_h = max_h
                        img_w = img_h / aspect
                    
                    img.drawWidth = img_w
                    img.drawHeight = img_h
                    img.hAlign = 'CENTER'
                    
                    story.append(img)
                    if caption:
                        story.append(Paragraph(f"<i>{caption}</i>", body))
                    story.append(Spacer(1, 10))
                except Exception as e:
                    story.append(Paragraph(f"[Error loading image {img_path}: {e}]", body))
            else:
                story.append(Paragraph(f"[Image not found: {img_path}]", body))
            continue

        # Blank line
        if not stripped:
            flush_bullets()
            story.append(Spacer(1, 5))
            continue


        # Normal paragraph
        flush_bullets()
        story.append(Paragraph(_inline(stripped), body))

    flush_bullets()
    return story


def _inline(text: str) -> str:
    """Convert inline Markdown (**bold**, *italic*, [link](url)) to reportlab XML."""
    # Escape bare & first (before adding any XML tags)
    text = re.sub(r"&(?!amp;|lt;|gt;|nbsp;)", "&amp;", text)
    # Bold: **text** or __text__
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
    # Italic: *text* or _text_
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"_(.+?)_", r"<i>\1</i>", text)
    # Links: [text](url) → clickable blue underlined hyperlink
    text = re.sub(
        r"\[(.+?)\]\((https?://[^\)]+)\)",
        r'<a href="\2" color="blue"><u>\1</u></a>',
        text,
    )
    return text


def convert(input_path: str, output_path: str) -> None:
    raw = Path(input_path).read_text(encoding="utf-8")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=LETTER,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
    )

    story = parse_and_build(raw)
    doc.build(story)
    print(f"  ✓ PDF saved → {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_md.py <input.txt> <output.pdf>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
