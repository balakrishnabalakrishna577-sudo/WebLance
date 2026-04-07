"""
PDF Generator for Weblance Agreement Letters — strict 2-page layout
"""
import io
import qrcode
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ── Fonts ──────────────────────────────────────────────────────────
_FONTS_DIR = 'C:/Windows/Fonts'
try:
    pdfmetrics.registerFont(TTFont('Arial',      os.path.join(_FONTS_DIR, 'arial.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(_FONTS_DIR, 'arialbd.ttf')))
    _F  = 'Arial'
    _FB = 'Arial-Bold'
except Exception:
    _F  = 'Helvetica'
    _FB = 'Helvetica-Bold'

RS    = '\u20b9'
GREEN = colors.HexColor('#00cc6a')
DARK  = colors.HexColor('#0d0d0d')
GRAY  = colors.HexColor('#555555')
LGRAY = colors.HexColor('#f5f7fa')
MGRAY = colors.HexColor('#e8ecf0')
WHITE = colors.white


# ── Compact styles (all sizes reduced for 2-page fit) ──────────────
def S(name):
    return {
        'brand':    ParagraphStyle('brand',    fontName=_FB, fontSize=18, textColor=DARK, leading=22),
        'contact':  ParagraphStyle('contact',  fontName=_F,  fontSize=7,  textColor=GRAY, alignment=TA_RIGHT, leading=10),
        'title':    ParagraphStyle('title',    fontName=_FB, fontSize=14, textColor=DARK, alignment=TA_CENTER, leading=18, spaceAfter=2),
        'sub':      ParagraphStyle('sub',      fontName=_F,  fontSize=8,  textColor=GRAY, alignment=TA_CENTER, leading=11, spaceAfter=2),
        'ref':      ParagraphStyle('ref',      fontName=_FB, fontSize=8,  textColor=GREEN, alignment=TA_CENTER, spaceAfter=8),
        'section':  ParagraphStyle('section',  fontName=_FB, fontSize=9,  textColor=GREEN, spaceBefore=6, spaceAfter=3, leading=12),
        'body':     ParagraphStyle('body',     fontName=_F,  fontSize=8,  textColor=DARK, leading=11, alignment=TA_JUSTIFY, spaceAfter=2),
        'cell':     ParagraphStyle('cell',     fontName=_F,  fontSize=7.5,textColor=DARK, leading=10),
        'cell_b':   ParagraphStyle('cell_b',   fontName=_FB, fontSize=7.5,textColor=DARK, leading=10),
        'clause':   ParagraphStyle('clause',   fontName=_F,  fontSize=7,  textColor=DARK, leading=9,  spaceAfter=1),
        'small':    ParagraphStyle('small',    fontName=_F,  fontSize=7,  textColor=GRAY, leading=10, spaceAfter=1),
        'footer':   ParagraphStyle('footer',   fontName=_F,  fontSize=6.5,textColor=GRAY, alignment=TA_CENTER),
        'qr_lbl':   ParagraphStyle('qr_lbl',   fontName=_F,  fontSize=6,  textColor=GRAY, alignment=TA_CENTER),
    }[name]


def _clean(val, fallback='—'):
    if val and str(val).strip().lower() not in ('none', ''):
        return str(val).strip()
    return fallback


def _qr_image(data: str, size_mm: int = 20) -> Image:
    qr = qrcode.QRCode(version=1, box_size=4, border=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    sz = size_mm * mm
    return Image(buf, width=sz, height=sz)


def _ts(cmds):
    return TableStyle(cmds)


def generate_agreement_pdf(agreement, base_url: str = 'https://weblance.onrender.com') -> bytes:
    buf = io.BytesIO()
    _verify_url = f'{base_url.rstrip("/")}/agreement/verify/{agreement.ref_id}/'

    # Tight margins to maximise usable space
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=14*mm, rightMargin=14*mm,
        topMargin=10*mm, bottomMargin=10*mm,
        title=f'Agreement {agreement.short_ref}',
        author='Weblance',
    )
    W = A4[0] - 28*mm
    story = []

    # ── HEADER ────────────────────────────────────────────────────────
    hdr = Table([[
        Paragraph('<font color="#00cc6a">WEB</font>LANCE', S('brand')),
        Paragraph(
            'Devanahalli, Karnataka, India<br/>'
            '+91 7892934437 | infoweblance01@gmail.com | weblance.onrender.com',
            S('contact')
        ),
    ]], colWidths=[W*0.4, W*0.6])
    hdr.setStyle(_ts([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.append(hdr)
    story.append(HRFlowable(width='100%', thickness=2, color=GREEN, spaceAfter=6))

    # ── TITLE ─────────────────────────────────────────────────────────
    story.append(Paragraph('SERVICE AGREEMENT LETTER', S('title')))
    story.append(Paragraph('Web Development &amp; Digital Services', S('sub')))
    story.append(Paragraph(f'Ref: <b>{agreement.short_ref}</b> &nbsp;|&nbsp; Date: {date.today().strftime("%d %B %Y")} &nbsp;|&nbsp; Type: {agreement.get_project_type_display()} &nbsp;|&nbsp; Status: {agreement.get_status_display()}', S('ref')))

    # ── PARTIES (side by side, compact) ───────────────────────────────
    client_lines = [f'<b>{agreement.client_name}</b>']
    if _clean(agreement.company_name) != '—': client_lines.append(_clean(agreement.company_name))
    if _clean(agreement.client_address) != '—':
        for ln in agreement.client_address.strip().splitlines():
            if ln.strip(): client_lines.append(ln.strip())
    if _clean(agreement.client_phone) != '—': client_lines.append(f'Ph: {agreement.client_phone}')
    client_lines.append(f'Email: {agreement.client_email}')

    parties = Table([
        [Paragraph('SERVICE PROVIDER', S('cell_b')), Paragraph('CLIENT', S('cell_b'))],
        [
            Paragraph('<br/>'.join(['<b>Weblance</b>', 'Devanahalli, Karnataka', 'Ph: +91 7892934437', 'infoweblance01@gmail.com']), S('cell')),
            Paragraph('<br/>'.join(client_lines), S('cell')),
        ],
    ], colWidths=[W/2, W/2])
    parties.setStyle(_ts([
        ('BACKGROUND',(0,0),(-1,0),GREEN),('TEXTCOLOR',(0,0),(-1,0),WHITE),
        ('FONTNAME',(0,0),(-1,0),_FB),('FONTSIZE',(0,0),(-1,-1),7.5),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.3,MGRAY),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
    ]))
    story.append(parties)
    story.append(Spacer(1, 4))

    # ── INTRODUCTION (one line) ────────────────────────────────────────
    co = f' of <b>{_clean(agreement.company_name)}</b>' if _clean(agreement.company_name) != '—' else ''
    story.append(Paragraph('1. INTRODUCTION', S('section')))
    story.append(Paragraph(
        f'This Agreement is entered into as of <b>{agreement.start_date.strftime("%d %B %Y")}</b> between '
        f'<b>Weblance</b> (Service Provider) and <b>{agreement.client_name}</b>{co} (Client) for '
        f'<b>{agreement.get_project_type_display()}</b> services as described herein.',
        S('body')
    ))

    # ── SCOPE + TIMELINE + PAYMENT on page 1 ─────────────────────────
    duration = (agreement.end_date - agreement.start_date).days
    desc_lines = [ln.strip() for ln in agreement.description.strip().splitlines() if ln.strip()]
    desc_text = '<br/>'.join(desc_lines[:8])  # max 8 lines to fit page 1

    # Scope section
    story.append(Paragraph('2. SCOPE OF WORK', S('section')))
    story.append(Paragraph(f'<b>{agreement.project_title}</b>', S('body')))
    story.append(Paragraph(desc_text, S('body')))
    story.append(Spacer(1, 3))

    # Timeline + Payment side by side
    tl_data = [
        [Paragraph('<b>Start</b>', S('cell_b')), Paragraph(agreement.start_date.strftime('%d %b %Y'), S('cell')),
         Paragraph('<b>End</b>',   S('cell_b')), Paragraph(agreement.end_date.strftime('%d %b %Y'),   S('cell')),
         Paragraph('<b>Days</b>',  S('cell_b')), Paragraph(f'{duration}', S('cell'))],
    ]
    tl_tbl = Table(tl_data, colWidths=[W*0.08, W*0.2, W*0.06, W*0.2, W*0.07, W*0.12])
    tl_tbl.setStyle(_ts([
        ('FONTSIZE',(0,0),(-1,-1),7.5),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('GRID',(0,0),(-1,-1),0.3,MGRAY),('BACKGROUND',(0,0),(-1,-1),LGRAY),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),5),
    ]))
    story.append(KeepTogether([Paragraph('3. PROJECT TIMELINE', S('section')), tl_tbl, Spacer(1,3)]))

    # Payment
    pay_rows = [
        [Paragraph('<b>Description</b>', S('cell_b')), Paragraph('<b>Amount</b>', S('cell_b'))],
        [Paragraph('Total Project Cost', S('cell')),   Paragraph(f'{RS}{agreement.total_cost:,.2f}', S('cell'))],
        [Paragraph(f'Advance ({agreement.advance_percent}%)', S('cell')), Paragraph(f'{RS}{agreement.advance_amount:,.2f}', S('cell'))],
        [Paragraph(f'Balance on Delivery ({100-agreement.advance_percent}%)', S('cell_b')), Paragraph(f'{RS}{agreement.balance_amount:,.2f}', S('cell_b'))],
    ]
    if _clean(agreement.payment_terms) != '—':
        for ln in agreement.payment_terms.strip().splitlines():
            if ln.strip():
                pay_rows.append([Paragraph(f'• {ln.strip()}', S('clause')), Paragraph('', S('clause'))])

    pay_tbl = Table(pay_rows, colWidths=[W*0.65, W*0.35])
    pay_tbl.setStyle(_ts([
        ('BACKGROUND',(0,0),(-1,0),DARK),('TEXTCOLOR',(0,0),(-1,0),WHITE),
        ('FONTNAME',(0,0),(-1,0),_FB),('FONTNAME',(0,1),(-1,-1),_F),
        ('FONTSIZE',(0,0),(-1,-1),7.5),('ALIGN',(1,0),(1,-1),'RIGHT'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('GRID',(0,0),(-1,-1),0.3,MGRAY),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(1,0),(1,-1),6),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[LGRAY,WHITE,LGRAY]),
        ('TEXTCOLOR',(1,-1),(1,-1),GREEN),
        ('BACKGROUND',(0,-1),(-1,-1),colors.HexColor('#edfaf3')),
    ]))
    story.append(KeepTogether([Paragraph('4. PAYMENT TERMS', S('section')), pay_tbl, Spacer(1,3)]))

    # ── T&C (compact 2-col) ───────────────────────────────────────────
    clauses = [
        ('<b>Revisions:</b> Up to 3 rounds included. Extra revisions at ₹500/hr.',
         '<b>IP:</b> Full ownership transfers to Client on complete payment.'),
        ('<b>Confidentiality:</b> Both parties keep all project info strictly confidential.',
         '<b>Delays:</b> Weblance not liable for delays due to late content/approvals.'),
        ('<b>Termination:</b> 7 days written notice. Advance non-refundable after work begins.',
         '<b>Warranty:</b> 30 days free bug-fix support. New features quoted separately.'),
        ('<b>Governing Law:</b> Indian law. Disputes in Bangalore courts.', ''),
    ]
    tc_tbl = Table(
        [[Paragraph(a, S('clause')), Paragraph(b, S('clause'))] for a, b in clauses],
        colWidths=[W/2, W/2]
    )
    tc_tbl.setStyle(_ts([
        ('FONTSIZE',(0,0),(-1,-1),7),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('GRID',(0,0),(-1,-1),0.3,MGRAY),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[LGRAY,WHITE,LGRAY,WHITE]),
    ]))

    # ── ADDITIONAL TERMS ──────────────────────────────────────────────
    add_block = []
    if _clean(agreement.additional_terms) != '—':
        add_block.append(Paragraph('6. ADDITIONAL TERMS', S('section')))
        for ln in agreement.additional_terms.strip().splitlines():
            if ln.strip():
                add_block.append(Paragraph(ln.strip(), S('body')))

    # ── SIGNATURES ────────────────────────────────────────────────────
    qr_img = _qr_image(_verify_url, size_mm=20)
    w_date = 'Signed' if agreement.weblance_signed else '___________'
    c_date = f'Signed: {agreement.client_signed_at.strftime("%d %b %Y")}' if agreement.client_signed and agreement.client_signed_at else '___________'
    c_co   = _clean(agreement.company_name)
    sig_num = '7.' if _clean(agreement.additional_terms) != '—' else '6.'

    sig_tbl = Table([
        [Paragraph('<b>For Weblance</b>', S('cell_b')),
         Paragraph('<b>Client Signature</b>', S('cell_b')),
         Paragraph('<b>QR Verify</b>', S('cell_b'))],
        [
            Paragraph(f'<br/><br/>__________________________<br/><b>Balakrishna</b><br/>Lead Developer<br/>Date: {w_date}', S('small')),
            Paragraph(f'<br/><br/>__________________________<br/><b>{agreement.client_name}</b><br/>{c_co + "<br/>" if c_co != "—" else ""}Date: {c_date}', S('small')),
            Table([[qr_img],[Paragraph(f'Scan to verify<br/><b>{agreement.short_ref}</b>', S('qr_lbl'))]], colWidths=[W*0.24]),
        ],
    ], colWidths=[W*0.38, W*0.38, W*0.24])
    sig_tbl.setStyle(_ts([
        ('VALIGN',(0,0),(-1,-1),'TOP'),('ALIGN',(2,1),(2,1),'CENTER'),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),
        ('BACKGROUND',(0,0),(-1,0),LGRAY),
        ('TOPPADDING',(0,0),(-1,0),5),('BOTTOMPADDING',(0,0),(-1,0),5),
        ('LINEBELOW',(0,0),(-1,0),0.4,MGRAY),
        ('LINEAFTER',(0,0),(1,-1),0.3,MGRAY),
    ]))

    # ── ALL REMAINING CONTENT IN ONE BLOCK ────────────────────────────
    final = [
        Paragraph('5. TERMS &amp; CONDITIONS', S('section')),
        tc_tbl,
    ] + add_block + [
        Spacer(1, 4),
        HRFlowable(width='100%', thickness=0.8, color=MGRAY, spaceAfter=3),
        Paragraph(f'{sig_num} SIGNATURES', S('section')),
        Paragraph('By signing below, both parties confirm they have read and agreed to all terms in this Agreement.', S('body')),
        Spacer(1, 4),
        sig_tbl,
        Spacer(1, 4),
        HRFlowable(width='100%', thickness=1.5, color=GREEN, spaceAfter=3),
        Paragraph(
            f'Legally binding agreement &nbsp;|&nbsp; ID: <b>{agreement.short_ref}</b> &nbsp;|&nbsp; '
            f'Generated: {date.today().strftime("%d %B %Y")} &nbsp;|&nbsp; weblance.onrender.com',
            S('footer')
        ),
    ]
    story.append(KeepTogether(final))

    doc.build(story)
    return buf.getvalue()


RS    = '\u20b9'
GREEN = colors.HexColor('#00cc6a')
DARK  = colors.HexColor('#0d0d0d')
GRAY  = colors.HexColor('#555555')
LGRAY = colors.HexColor('#f5f7fa')
MGRAY = colors.HexColor('#e8ecf0')
WHITE = colors.white


def S(name):
    return {
        'brand': ParagraphStyle('brand', fontName=_FB, fontSize=20, textColor=DARK, leading=24),
        'contact': ParagraphStyle('contact', fontName=_F, fontSize=7.5, textColor=GRAY, alignment=TA_RIGHT, leading=12),
        'doc_title': ParagraphStyle('doc_title', fontName=_FB, fontSize=16, textColor=DARK, alignment=TA_CENTER, leading=20, spaceAfter=3),
        'doc_sub': ParagraphStyle('doc_sub', fontName=_F, fontSize=9, textColor=GRAY, alignment=TA_CENTER, leading=13, spaceAfter=3),
        'ref': ParagraphStyle('ref', fontName=_FB, fontSize=8.5, textColor=GREEN, alignment=TA_CENTER, spaceAfter=10),
        'section': ParagraphStyle('section', fontName=_FB, fontSize=10, textColor=GREEN, spaceBefore=8, spaceAfter=4, leading=14),
        'body': ParagraphStyle('body', fontName=_F, fontSize=9, textColor=DARK, leading=13, alignment=TA_JUSTIFY, spaceAfter=3),
        'cell': ParagraphStyle('cell', fontName=_F, fontSize=8.5, textColor=DARK, leading=12),
        'cell_bold': ParagraphStyle('cell_bold', fontName=_FB, fontSize=8.5, textColor=DARK, leading=12),
        'clause': ParagraphStyle('clause', fontName=_F, fontSize=8, textColor=DARK, leading=11, spaceAfter=2),
        'small': ParagraphStyle('small', fontName=_F, fontSize=8, textColor=GRAY, leading=12, spaceAfter=2),
        'footer': ParagraphStyle('footer', fontName=_F, fontSize=7, textColor=GRAY, alignment=TA_CENTER),
        'qr_lbl': ParagraphStyle('qr_lbl', fontName=_F, fontSize=6.5, textColor=GRAY, alignment=TA_CENTER),
    }[name]


def _clean(val, fallback='—'):
    if val and str(val).strip().lower() not in ('none', ''):
        return str(val).strip()
    return fallback


def _qr_image(data: str, size_mm: int = 24) -> Image:
    qr = qrcode.QRCode(version=1, box_size=5, border=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    sz = size_mm * mm
    return Image(buf, width=sz, height=sz)


def _tbl_style(header_bg=None, row_bgs=None, grid=True):
    cmds = [
        ('FONTSIZE',      (0,0), (-1,-1), 8.5),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
    ]
    if header_bg:
        cmds += [
            ('BACKGROUND', (0,0), (-1,0), header_bg),
            ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
            ('FONTNAME',   (0,0), (-1,0), _FB),
            ('FONTNAME',   (0,1), (-1,-1), _F),
        ]
    if row_bgs:
        cmds.append(('ROWBACKGROUNDS', (0,1), (-1,-1), row_bgs))
    if grid:
        cmds.append(('GRID', (0,0), (-1,-1), 0.4, MGRAY))
    return TableStyle(cmds)


def generate_agreement_pdf(agreement, base_url: str = 'https://weblance.onrender.com') -> bytes:
    buf = io.BytesIO()
    _verify_url = f'{base_url.rstrip("/")}/agreement/verify/{agreement.ref_id}/'

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=14*mm, bottomMargin=14*mm,
        title=f'Agreement {agreement.short_ref}',
        author='Weblance',
    )
    W = A4[0] - 36*mm
    story = []

    # ── HEADER ────────────────────────────────────────────────────────
    hdr = Table([[
        Paragraph('<font color="#00cc6a">WEB</font>LANCE', S('brand')),
        Paragraph(
            'Devanahalli, Karnataka, India<br/>'
            '+91 7892934437 &nbsp;|&nbsp; infoweblance01@gmail.com<br/>'
            'weblance.onrender.com',
            S('contact')
        ),
    ]], colWidths=[W * 0.45, W * 0.55])
    hdr.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(hdr)
    story.append(HRFlowable(width='100%', thickness=2.5, color=GREEN, spaceAfter=10))

    # ── TITLE ─────────────────────────────────────────────────────────
    story.append(Paragraph('SERVICE AGREEMENT LETTER', S('doc_title')))
    story.append(Paragraph('Web Development &amp; Digital Services', S('doc_sub')))
    story.append(Paragraph(f'Reference No: <b>{agreement.short_ref}</b>', S('ref')))

    # ── META ──────────────────────────────────────────────────────────
    meta_tbl = Table([
        [Paragraph('<b>Date Issued:</b>', S('cell_bold')), Paragraph(date.today().strftime('%d %B %Y'), S('cell')),
         Paragraph('<b>Agreement ID:</b>', S('cell_bold')), Paragraph(agreement.short_ref, S('cell'))],
        [Paragraph('<b>Status:</b>', S('cell_bold')), Paragraph(agreement.get_status_display(), S('cell')),
         Paragraph('<b>Project Type:</b>', S('cell_bold')), Paragraph(agreement.get_project_type_display(), S('cell'))],
    ], colWidths=[28*mm, 52*mm, 30*mm, 52*mm])
    meta_tbl.setStyle(_tbl_style(row_bgs=[LGRAY, WHITE]))
    story.append(meta_tbl)
    story.append(Spacer(1, 8))

    # ── 1. PARTIES ────────────────────────────────────────────────────
    story.append(Paragraph('1. PARTIES TO THIS AGREEMENT', S('section')))
    client_lines = [f'<b>{agreement.client_name}</b>']
    if _clean(agreement.company_name) != '—':
        client_lines.append(_clean(agreement.company_name))
    if _clean(agreement.client_address) != '—':
        for ln in agreement.client_address.strip().splitlines():
            if ln.strip(): client_lines.append(ln.strip())
    if _clean(agreement.client_phone) != '—':
        client_lines.append(f'Phone: {agreement.client_phone}')
    client_lines.append(f'Email: {agreement.client_email}')

    parties_tbl = Table([
        [Paragraph('SERVICE PROVIDER', S('cell_bold')), Paragraph('CLIENT', S('cell_bold'))],
        [
            Paragraph('<br/>'.join(['<b>Weblance</b>', 'Devanahalli, Karnataka, India',
                                    'Phone: +91 7892934437', 'Email: infoweblance01@gmail.com',
                                    'Web: weblance.onrender.com']), S('cell')),
            Paragraph('<br/>'.join(client_lines), S('cell')),
        ],
    ], colWidths=[W/2, W/2])
    parties_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), GREEN),
        ('TEXTCOLOR',     (0,0), (-1,0), WHITE),
        ('FONTNAME',      (0,0), (-1,0), _FB),
        ('FONTNAME',      (0,1), (-1,-1), _F),
        ('FONTSIZE',      (0,0), (-1,-1), 8.5),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('GRID',          (0,0), (-1,-1), 0.4, MGRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
    ]))
    story.append(parties_tbl)
    story.append(Spacer(1, 6))

    # ── 2. INTRODUCTION ───────────────────────────────────────────────
    story.append(Paragraph('2. INTRODUCTION', S('section')))
    co = f' of <b>{_clean(agreement.company_name)}</b>' if _clean(agreement.company_name) != '—' else ''
    story.append(Paragraph(
        f'This Service Agreement is entered into as of <b>{agreement.start_date.strftime("%d %B %Y")}</b> '
        f'between <b>Weblance</b> ("Service Provider"), Devanahalli, Karnataka, India, and '
        f'<b>{agreement.client_name}</b>{co} ("Client"). This Agreement governs the provision of '
        f'<b>{agreement.get_project_type_display()}</b> services as described herein.',
        S('body')
    ))

    # ── 3. SCOPE OF WORK ──────────────────────────────────────────────
    story.append(Paragraph('3. SCOPE OF WORK', S('section')))
    story.append(Paragraph(f'<b>Project Title:</b> {agreement.project_title}', S('body')))
    for line in agreement.description.strip().splitlines():
        if line.strip():
            story.append(Paragraph(line.strip(), S('body')))

    # ── 4. TIMELINE ───────────────────────────────────────────────────
    duration = (agreement.end_date - agreement.start_date).days
    tl_tbl = Table([
        [Paragraph('<b>Start Date</b>', S('cell_bold')),
         Paragraph('<b>End Date</b>', S('cell_bold')),
         Paragraph('<b>Duration</b>', S('cell_bold'))],
        [Paragraph(agreement.start_date.strftime('%d %B %Y'), S('cell')),
         Paragraph(agreement.end_date.strftime('%d %B %Y'), S('cell')),
         Paragraph(f'{duration} days', S('cell'))],
    ], colWidths=[W/3, W/3, W/3])
    tl_tbl.setStyle(_tbl_style(header_bg=GREEN, row_bgs=[LGRAY]))
    tl_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), GREEN),
        ('TEXTCOLOR',     (0,0), (-1,0), WHITE),
        ('FONTNAME',      (0,0), (-1,0), _FB),
        ('FONTNAME',      (0,1), (-1,-1), _F),
        ('FONTSIZE',      (0,0), (-1,-1), 8.5),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',          (0,0), (-1,-1), 0.4, MGRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [LGRAY]),
    ]))
    story.append(KeepTogether([Paragraph('4. PROJECT TIMELINE', S('section')), tl_tbl, Spacer(1, 6)]))

    # ── 5. PAYMENT TERMS ──────────────────────────────────────────────
    pay_tbl = Table([
        [Paragraph('<b>Description</b>', S('cell_bold')), Paragraph('<b>Amount (INR)</b>', S('cell_bold'))],
        [Paragraph('Total Project Cost', S('cell')), Paragraph(f'{RS}{agreement.total_cost:,.2f}', S('cell'))],
        [Paragraph(f'Advance Payment ({agreement.advance_percent}%)', S('cell')),
         Paragraph(f'{RS}{agreement.advance_amount:,.2f}', S('cell'))],
        [Paragraph(f'Balance on Delivery ({100 - agreement.advance_percent}%)', S('cell_bold')),
         Paragraph(f'{RS}{agreement.balance_amount:,.2f}', S('cell_bold'))],
    ], colWidths=[W * 0.65, W * 0.35])
    pay_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), GREEN),
        ('TEXTCOLOR',     (0,0), (-1,0), WHITE),
        ('FONTNAME',      (0,0), (-1,0), _FB),
        ('FONTNAME',      (0,1), (-1,-1), _F),
        ('FONTSIZE',      (0,0), (-1,-1), 8.5),
        ('ALIGN',         (1,0), (1,-1), 'RIGHT'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',          (0,0), (-1,-1), 0.4, MGRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (1,0), (1,-1), 8),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [LGRAY, WHITE, LGRAY]),
        ('TEXTCOLOR',     (1,-1), (1,-1), GREEN),
        ('BACKGROUND',    (0,-1), (-1,-1), colors.HexColor('#edfaf3')),
    ]))
    pay_block = [Paragraph('5. PAYMENT TERMS', S('section')), pay_tbl]
    if _clean(agreement.payment_terms) != '—':
        pay_block.append(Spacer(1, 4))
        for line in agreement.payment_terms.strip().splitlines():
            if line.strip():
                pay_block.append(Paragraph(line.strip(), S('body')))
    story.append(KeepTogether(pay_block))

    # ── 6. TERMS & CONDITIONS (compact 2-column table) ────────────────
    clauses = [
        ('<b>Revisions:</b> Up to 3 rounds included. Additional revisions billed at ₹500/hour.',
         '<b>Intellectual Property:</b> Full ownership transfers to Client upon complete payment.'),
        ('<b>Confidentiality:</b> Both parties agree to keep all project information strictly confidential.',
         '<b>Delays:</b> Weblance is not liable for delays caused by late content or approvals from Client.'),
        ('<b>Termination:</b> Either party may terminate with 7 days written notice. Advance is non-refundable after work begins.',
         '<b>Warranty:</b> 30 days free bug-fix support after delivery. New features quoted separately.'),
        ('<b>Governing Law:</b> This Agreement is governed by Indian law. Disputes resolved in Bangalore courts.',
         ''),
    ]
    tc_rows = [[Paragraph(a, S('clause')), Paragraph(b, S('clause'))] for a, b in clauses]
    tc_tbl = Table(tc_rows, colWidths=[W/2, W/2])
    tc_tbl.setStyle(TableStyle([
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('GRID',          (0,0), (-1,-1), 0.3, MGRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 7),
        ('RIGHTPADDING',  (0,0), (-1,-1), 7),
        ('ROWBACKGROUNDS',(0,0), (-1,-1), [LGRAY, WHITE, LGRAY, WHITE]),
    ]))
    # ── 6. T&C + 7. ADDITIONAL TERMS + 8. SIGNATURES + FOOTER (one block) ──
    sig_num = '8.' if _clean(agreement.additional_terms) != '—' else '7.'
    final_block = [
        Paragraph('6. TERMS &amp; CONDITIONS', S('section')),
        tc_tbl,
    ]

    if _clean(agreement.additional_terms) != '—':
        final_block.append(Paragraph('7. ADDITIONAL TERMS', S('section')))
        for line in agreement.additional_terms.strip().splitlines():
            if line.strip():
                final_block.append(Paragraph(line.strip(), S('body')))
    # Signature table
    qr_img = _qr_image(_verify_url, size_mm=22)
    weblance_date = 'Signed' if agreement.weblance_signed else '_______________'
    client_date = (
        f'Signed: {agreement.client_signed_at.strftime("%d %b %Y")}'
        if agreement.client_signed and agreement.client_signed_at else '_______________'
    )
    client_co = _clean(agreement.company_name)

    sig_tbl = Table([
        [Paragraph('<b>For Weblance</b>', S('cell_bold')),
         Paragraph('<b>Client Signature</b>', S('cell_bold')),
         Paragraph('<b>QR Verification</b>', S('cell_bold'))],
        [
            Paragraph(
                '<br/><br/>'
                '__________________________<br/>'
                f'<b>Balakrishna</b><br/>Lead Developer, Weblance<br/>Date: {weblance_date}',
                S('small')
            ),
            Paragraph(
                '<br/><br/>'
                '__________________________<br/>'
                f'<b>{agreement.client_name}</b><br/>'
                f'{client_co + "<br/>" if client_co != "—" else ""}'
                f'Date: {client_date}',
                S('small')
            ),
            Table(
                [[qr_img],
                 [Paragraph(f'Scan to verify<br/><b>{agreement.short_ref}</b>', S('qr_lbl'))]],
                colWidths=[W * 0.26]
            ),
        ],
    ], colWidths=[W * 0.37, W * 0.37, W * 0.26])
    sig_tbl.setStyle(TableStyle([
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('ALIGN',         (2,1), (2,1),   'CENTER'),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 4),
        ('RIGHTPADDING',  (0,0), (-1,-1), 4),
        ('BACKGROUND',    (0,0), (-1,0),  LGRAY),
        ('TOPPADDING',    (0,0), (-1,0),  6),
        ('BOTTOMPADDING', (0,0), (-1,0),  6),
        ('LINEBELOW',     (0,0), (-1,0),  0.5, MGRAY),
        ('LINEAFTER',     (0,0), (1,-1),  0.4, MGRAY),
    ]))

    final_block += [
        Spacer(1, 6),
        HRFlowable(width='100%', thickness=0.8, color=MGRAY, spaceAfter=4),
        Paragraph(f'{sig_num} SIGNATURES', S('section')),
        Paragraph(
            'By signing below, both parties confirm they have read and agreed to all terms in this Agreement.',
            S('body')
        ),
        Spacer(1, 6),
        sig_tbl,
        Spacer(1, 6),
        HRFlowable(width='100%', thickness=1.5, color=GREEN, spaceAfter=4),
        Paragraph(
            f'This is a legally binding agreement. &nbsp;|&nbsp; '
            f'Agreement ID: <b>{agreement.short_ref}</b> &nbsp;|&nbsp; '
            f'Generated: {date.today().strftime("%d %B %Y")} &nbsp;|&nbsp; weblance.onrender.com',
            S('footer')
        ),
    ]
    story.append(KeepTogether(final_block))

    doc.build(story)
    return buf.getvalue()
