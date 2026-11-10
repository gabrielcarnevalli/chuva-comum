"""Gera PDF de até 3 páginas a partir do texto editável, sem acessar a rede."""
import argparse
import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
INK = colors.black
MUTED = colors.black
LIGHT = colors.white


def rich(text):
    text = html.escape(text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return re.sub(r'\[([^\]]+)\]\((https://[^\s)]+)\)',
                  r'<link href="\2" color="#000000"><u>\1</u></link>', text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nome', default='PREENCHER NOME')
    parser.add_argument('--rm', default='PREENCHER')
    parser.add_argument('--turma', default='PREENCHER')
    args = parser.parse_args()
    font, bold = 'Helvetica', 'Helvetica-Bold'
    font_dir = Path('/usr/share/fonts/truetype/dejavu')
    if (font_dir / 'DejaVuSans.ttf').exists():
        pdfmetrics.registerFont(TTFont('Doc', str(font_dir / 'DejaVuSans.ttf')))
        pdfmetrics.registerFont(TTFont('Doc-Bold', str(font_dir / 'DejaVuSans-Bold.ttf')))
        pdfmetrics.registerFontFamily('Doc', normal='Doc', bold='Doc-Bold', italic='Doc', boldItalic='Doc-Bold')
        font, bold = 'Doc', 'Doc-Bold'
    body = ParagraphStyle('body', fontName=font, fontSize=9, leading=12.8,
                          textColor=INK, spaceAfter=8, alignment=TA_LEFT)
    styles = {
        0: body,
        1: ParagraphStyle('title', parent=body, fontName=bold, fontSize=29, leading=34, spaceAfter=5),
        2: ParagraphStyle('subtitle', parent=body, fontName=bold, fontSize=16, leading=21,
                          spaceBefore=3, spaceAfter=16, keepWithNext=True),
        3: ParagraphStyle('section', parent=body, fontName=bold, fontSize=10.6, leading=14,
                          spaceBefore=8, spaceAfter=7, keepWithNext=True),
    }
    small = ParagraphStyle('small', parent=body, fontSize=7.7, leading=10.5, spaceAfter=5)
    source = (ROOT / 'docs/RELATORIO.md').read_text(encoding='utf-8')
    for key, value in (('NOME', args.nome), ('RM', args.rm), ('TURMA', args.turma)):
        source = source.replace('{{' + key + '}}', value[:100])
    story, buffer, table_rows = [], [], []
    references = False

    def flush():
        if buffer:
            story.append(Paragraph(rich(' '.join(buffer)), small if references else body))
            buffer.clear()

    def flush_table():
        if table_rows:
            rows = [[Paragraph(rich(cell), small) for cell in row] for row in table_rows]
            table = Table(rows, colWidths=[146, A4[0] - 84 - 146], hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), LIGHT),
                ('LINEBELOW', (0, 0), (-1, -1), .4, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 7),
                ('RIGHTPADDING', (0, 0), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.extend([table, Spacer(1, 9)])
            table_rows.clear()

    for line in source.splitlines():
        if line.startswith('|'):
            flush()
            table_rows.append([cell.strip() for cell in line.strip('|').split('|')])
            continue
        flush_table()
        if line.strip() == '<!-- PAGEBREAK -->':
            flush()
            story.append(PageBreak())
        elif line.startswith('#'):
            flush()
            level = len(line) - len(line.lstrip('#'))
            title = line[level:].strip()
            if title.startswith('Referências'):
                references = True
            story.append(Paragraph(rich(title), styles.get(level, styles[3])))
        elif not line.strip():
            flush()
        else:
            buffer.append(line.strip())
    flush()
    flush_table()
    page_count = [0]

    def frame(canvas, doc):
        page_count[0] = doc.page
        canvas.saveState()
        width, height = A4
        canvas.setFillColor(INK)
        canvas.rect(0, height - 8, width, 8, fill=1, stroke=0)
        canvas.setFont(bold, 8)
        canvas.drawString(42, height - 32, 'CHUVACOMUM / CITIZENTECH')
        canvas.setFillColor(MUTED)
        canvas.setFont(font, 7)
        canvas.drawRightString(width - 42, height - 32, 'GLOBAL SOLUTION · CODING FOR SECURITY')
        canvas.setStrokeColor(colors.black)
        canvas.line(42, 36, width - 42, 36)
        canvas.drawString(42, 23, 'Protótipo acadêmico · Dados fictícios ou abertos · Uso de IA declarado')
        canvas.drawRightString(width - 42, 23, f'{doc.page} / 3')
        canvas.restoreState()

    output = ROOT / 'docs/relatorio.pdf'
    doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=42, rightMargin=42,
                            topMargin=56, bottomMargin=47, title='ChuvaComum — Relatório CitizenTech',
                            author=args.nome, subject='Global Solution — Coding for Security')
    doc.build(story, onFirstPage=frame, onLaterPages=frame)
    if page_count[0] != 3:
        raise SystemExit(f'Revise a diagramação: PDF gerou {page_count[0]} páginas; esperado: 3.')
    print('docs/relatorio.pdf gerado: 3 páginas. Confira identificação, texto e declaração de IA.')


if __name__ == '__main__':
    main()
