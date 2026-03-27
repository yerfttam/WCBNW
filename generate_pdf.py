#!/usr/bin/env python3
"""Generate WCBNW-Website-Guide.pdf from HANDOFF.md"""

import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, Preformatted, KeepTogether, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import Flowable

# Color palette
NAVY = colors.HexColor('#293b4e')
BROWN = colors.HexColor('#6b452e')
SAGE = colors.HexColor('#b5b8a3')
CREAM = colors.HexColor('#f6efe5')
LIGHT_GRAY = colors.HexColor('#f0f0f0')
MED_GRAY = colors.HexColor('#e0e0e0')
DARK_GRAY = colors.HexColor('#555555')
CODE_BG = colors.HexColor('#f4f4f4')
SAGE_LIGHT = colors.HexColor('#d8ddd0')

PAGE_WIDTH, PAGE_HEIGHT = letter
LEFT_MARGIN = 0.85 * inch
RIGHT_MARGIN = 0.85 * inch
TOP_MARGIN = 0.9 * inch
BOTTOM_MARGIN = 0.85 * inch

def make_styles():
    styles = {}

    styles['h1'] = ParagraphStyle(
        'H1',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=NAVY,
        spaceBefore=18,
        spaceAfter=4,
        leading=20,
    )
    styles['h2'] = ParagraphStyle(
        'H2',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=NAVY,
        spaceBefore=14,
        spaceAfter=3,
        leading=16,
    )
    styles['h3'] = ParagraphStyle(
        'H3',
        fontName='Helvetica-BoldOblique',
        fontSize=10,
        textColor=BROWN,
        spaceBefore=10,
        spaceAfter=2,
        leading=14,
    )
    styles['body'] = ParagraphStyle(
        'Body',
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.black,
        spaceBefore=3,
        spaceAfter=3,
        leading=15,
    )
    styles['blockquote'] = ParagraphStyle(
        'Blockquote',
        fontName='Helvetica-Oblique',
        fontSize=10,
        textColor=DARK_GRAY,
        spaceBefore=6,
        spaceAfter=6,
        leading=15,
        leftIndent=18,
        rightIndent=10,
    )
    styles['code_inline'] = ParagraphStyle(
        'CodeInline',
        fontName='Courier',
        fontSize=9,
        textColor=colors.black,
        spaceBefore=0,
        spaceAfter=0,
        leading=14,
    )
    styles['list_item'] = ParagraphStyle(
        'ListItem',
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.black,
        spaceBefore=2,
        spaceAfter=2,
        leading=15,
        leftIndent=16,
    )
    styles['list_item_numbered'] = ParagraphStyle(
        'ListItemNumbered',
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.black,
        spaceBefore=2,
        spaceAfter=2,
        leading=15,
        leftIndent=16,
    )
    styles['subtitle'] = ParagraphStyle(
        'Subtitle',
        fontName='Helvetica',
        fontSize=12,
        textColor=SAGE,
        spaceBefore=4,
        spaceAfter=6,
        leading=16,
        alignment=TA_CENTER,
    )
    styles['title_main'] = ParagraphStyle(
        'TitleMain',
        fontName='Helvetica-Bold',
        fontSize=28,
        textColor=NAVY,
        spaceBefore=0,
        spaceAfter=6,
        leading=34,
        alignment=TA_CENTER,
    )
    styles['footer_note'] = ParagraphStyle(
        'FooterNote',
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=DARK_GRAY,
        spaceBefore=0,
        spaceAfter=0,
        leading=11,
    )

    return styles


class SageBar(Flowable):
    """Left sage bar for blockquotes"""
    def __init__(self, content_flowable, width, bar_color=SAGE):
        Flowable.__init__(self)
        self._content = content_flowable
        self._width = width
        self._bar_color = bar_color
        self.width = width
        self.height = 0

    def wrap(self, availWidth, availHeight):
        w, h = self._content.wrap(availWidth - 14, availHeight)
        self.height = h + 8
        self.width = availWidth
        return availWidth, self.height

    def draw(self):
        self.canv.setFillColor(self._bar_color)
        self.canv.rect(0, 4, 4, self.height - 8, fill=1, stroke=0)
        self._content.drawOn(self.canv, 14, 4)


class CodeBlock(Flowable):
    """Gray rounded-rectangle code block"""
    def __init__(self, text, width=None):
        Flowable.__init__(self)
        self.code_text = text
        self._width = width
        self.height = 0

    def wrap(self, availWidth, availHeight):
        self._avail_width = availWidth
        lines = self.code_text.split('\n')
        # Estimate height: ~12pt per line + padding
        self.height = len(lines) * 12 + 16
        return availWidth, self.height

    def draw(self):
        canv = self.canv
        w = self._avail_width
        h = self.height
        r = 5

        # Background
        canv.setFillColor(CODE_BG)
        canv.setStrokeColor(MED_GRAY)
        canv.roundRect(0, 0, w, h, r, fill=1, stroke=1)

        # Text
        canv.setFillColor(colors.black)
        canv.setFont('Courier', 8.5)
        lines = self.code_text.split('\n')
        y = h - 10
        for line in lines:
            canv.drawString(8, y, line)
            y -= 12


def add_footer(canvas, doc):
    canvas.saveState()
    page_width, page_height = letter
    footer_y = 0.55 * inch

    canvas.setStrokeColor(SAGE)
    canvas.setLineWidth(0.75)
    canvas.line(LEFT_MARGIN, footer_y + 14, page_width - RIGHT_MARGIN, footer_y + 14)

    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(DARK_GRAY)
    canvas.drawString(LEFT_MARGIN, footer_y, 'WCBNW Website Guide')
    canvas.drawRightString(page_width - RIGHT_MARGIN, footer_y, f'Page {doc.page}')

    canvas.restoreState()


def escape_xml(text):
    """Escape XML special characters."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


def inline_format(text):
    """Convert markdown inline formatting to ReportLab XML."""
    # We need to process segments carefully to avoid double-escaping.
    # Strategy: extract code spans first (they need literal content),
    # then escape remaining text, then apply bold/italic/link.

    # Step 1: Extract inline code spans and replace with placeholders
    code_spans = []
    def save_code(m):
        idx = len(code_spans)
        # Escape the code content for XML
        content = escape_xml(m.group(1))
        code_spans.append(f'<font face="Courier" size="8.5">{content}</font>')
        return f'\x00CODE{idx}\x00'
    text = re.sub(r'`([^`]+)`', save_code, text)

    # Step 2: Escape remaining XML special chars
    text = escape_xml(text)

    # Step 3: Apply bold **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

    # Step 4: Italic *text* (single asterisk, not part of **)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)

    # Step 5: Links [text](url) — show as bold text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'<b>\1</b>', text)

    # Step 6: Restore code spans
    for idx, code in enumerate(code_spans):
        text = text.replace(f'\x00CODE{idx}\x00', code)

    return text


def parse_table(lines):
    """Parse a markdown table into a list of rows."""
    rows = []
    for line in lines:
        if re.match(r'^\s*\|[-: |]+\|\s*$', line):
            continue  # separator row
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)
    return rows


def build_story(md_text, styles):
    story = []

    # Title block
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph('WCBNW Website Guide', styles['title_main']))
    story.append(Paragraph('Whiskey Creek Beach NW &mdash; Port Angeles, WA', styles['subtitle']))
    story.append(HRFlowable(width='100%', thickness=2, color=NAVY, spaceAfter=16))

    lines = md_text.split('\n')
    i = 0

    # Skip the first H1 (already in title block)
    while i < len(lines) and not lines[i].startswith('# '):
        i += 1
    if i < len(lines) and lines[i].startswith('# '):
        i += 1  # skip it

    def peek_next_nonempty(idx):
        j = idx
        while j < len(lines) and lines[j].strip() == '':
            j += 1
        return j

    while i < len(lines):
        line = lines[i]

        # Blank line
        if line.strip() == '':
            i += 1
            continue

        # Horizontal rule ---
        if re.match(r'^---+\s*$', line):
            story.append(HRFlowable(width='100%', thickness=0.5, color=MED_GRAY,
                                     spaceBefore=6, spaceAfter=6))
            i += 1
            continue

        # H1
        if line.startswith('# ') and not line.startswith('## '):
            heading = inline_format(line[2:].strip())
            story.append(Spacer(1, 6))
            story.append(Paragraph(heading, styles['h1']))
            story.append(HRFlowable(width='100%', thickness=1, color=NAVY,
                                     spaceBefore=2, spaceAfter=6))
            i += 1
            continue

        # H2
        if line.startswith('## ') and not line.startswith('### '):
            heading = inline_format(line[3:].strip())
            story.append(Paragraph(heading, styles['h2']))
            i += 1
            continue

        # H3
        if line.startswith('### '):
            heading = inline_format(line[4:].strip())
            story.append(Paragraph(heading, styles['h3']))
            i += 1
            continue

        # H4 (treat like h3 but smaller)
        if line.startswith('#### '):
            heading = inline_format(line[5:].strip())
            story.append(Paragraph(heading, styles['h3']))
            i += 1
            continue

        # Code block ```
        if line.strip().startswith('```'):
            lang = line.strip()[3:].strip()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            code_text = '\n'.join(code_lines)
            story.append(Spacer(1, 4))
            story.append(CodeBlock(code_text))
            story.append(Spacer(1, 4))
            continue

        # Blockquote >
        if line.startswith('> '):
            bq_lines = []
            while i < len(lines) and lines[i].startswith('> '):
                bq_lines.append(lines[i][2:].strip())
                i += 1
            bq_text = ' '.join(bq_lines)
            bq_text = inline_format(bq_text)
            p = Paragraph(bq_text, styles['blockquote'])
            bar = SageBar(p, PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN)
            story.append(Spacer(1, 4))
            story.append(bar)
            story.append(Spacer(1, 4))
            continue

        # Table
        if line.strip().startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            rows = parse_table(table_lines)
            if rows:
                # Convert cells
                table_data = []
                for r_idx, row in enumerate(rows):
                    table_row = []
                    for cell in row:
                        cell_text = inline_format(cell)
                        if r_idx == 0:
                            p = Paragraph(f'<b>{cell_text}</b>', ParagraphStyle(
                                'TableHeader',
                                fontName='Helvetica-Bold',
                                fontSize=9,
                                textColor=colors.white,
                                leading=13,
                            ))
                        else:
                            p = Paragraph(cell_text, ParagraphStyle(
                                'TableCell',
                                fontName='Helvetica',
                                fontSize=9,
                                textColor=colors.black,
                                leading=13,
                            ))
                        table_row.append(p)
                    table_data.append(table_row)

                col_count = max(len(r) for r in table_data)
                avail_width = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
                col_width = avail_width / col_count

                t = Table(table_data, colWidths=[col_width] * col_count,
                          repeatRows=1)

                ts = TableStyle([
                    # Header row
                    ('BACKGROUND', (0, 0), (-1, 0), NAVY),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('ROWBACKGROUND', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, MED_GRAY),
                    ('LINEBELOW', (0, 0), (-1, 0), 1, NAVY),
                ])
                t.setStyle(ts)
                story.append(Spacer(1, 4))
                story.append(t)
                story.append(Spacer(1, 6))
            continue

        # Unordered list item
        if re.match(r'^(\s*)[-*+] ', line):
            # Collect consecutive list items
            items = []
            while i < len(lines) and re.match(r'^(\s*)[-*+] ', lines[i]):
                indent_match = re.match(r'^(\s*)[-*+] (.*)', lines[i])
                indent = len(indent_match.group(1))
                content = inline_format(indent_match.group(2).strip())
                items.append((indent, content))
                i += 1
            for (indent, content) in items:
                bullet_style = ParagraphStyle(
                    'BulletItem',
                    parent=styles['list_item'],
                    leftIndent=16 + indent * 8,
                    bulletIndent=4 + indent * 8,
                )
                story.append(Paragraph(f'&bull;&nbsp;&nbsp;{content}', bullet_style))
            continue

        # Ordered list item
        if re.match(r'^\d+\. ', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                m = re.match(r'^(\d+)\. (.*)', lines[i])
                num = m.group(1)
                content = inline_format(m.group(2).strip())
                items.append((num, content))
                i += 1
            for (num, content) in items:
                story.append(Paragraph(
                    f'<b>{num}.</b>&nbsp;&nbsp;{content}',
                    styles['list_item_numbered']
                ))
            continue

        # Regular paragraph
        text = inline_format(line.strip())
        if text:
            story.append(Paragraph(text, styles['body']))
        i += 1

    return story


def main():
    md_path = '/Users/matthewfrey/Projects/WCBNW/HANDOFF.md'
    pdf_path = '/Users/matthewfrey/Projects/WCBNW/WCBNW-Website-Guide.pdf'

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title='WCBNW Website Guide',
        author='Whiskey Creek Beach NW',
        subject='Website Operations Guide',
    )

    styles = make_styles()
    story = build_story(md_text, styles)

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    print(f'PDF generated: {pdf_path}')


if __name__ == '__main__':
    main()
