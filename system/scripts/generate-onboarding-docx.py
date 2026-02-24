#!/usr/bin/env python3
"""
Generuje docs/output/onboarding.docx — interaktywny dokument onboardingowy
z klikalnymi checkboxami i obrazkami. Jeden dokument dla macOS i Windows.

Uruchomienie:
    python3 system/scripts/generate-onboarding-docx.py

Wymagania (instalowane automatycznie):
    python-docx, pillow
"""

import subprocess
import sys
import os
import time
import tempfile

# ── Auto-instalacja zależności ────────────────────────────────────────────────

def pip_install(package):
    print(f"Instaluję {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

try:
    from docx import Document
except ImportError:
    pip_install("python-docx")
    from docx import Document

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    pip_install("pillow")
    from PIL import Image, ImageDraw, ImageFont

from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ── Konfiguracja ──────────────────────────────────────────────────────────────

# True = robi realne screenshoty stron internetowych (otwiera przeglądarkę)
# False = pomija screenshoty, szybsze generowanie
TAKE_SCREENSHOTS = False

IMG_WIDTH_PX = 520    # szerokość obrazków w pikselach
IMG_WIDTH_IN  = 5.0   # szerokość obrazków w dokumencie Word (cale)

# ── Helpers: czcionki ─────────────────────────────────────────────────────────

def get_font(size=13, bold=False):
    """Próbuje załadować systemową czcionkę, fallback na domyślną."""
    candidates = [
        '/System/Library/Fonts/Helvetica.ttc',
        '/System/Library/Fonts/SFNSText.ttf',
        '/Library/Fonts/Arial.ttf',
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

def get_mono_font(size=13):
    """Próbuje załadować systemową czcionkę monospace."""
    candidates = [
        '/System/Library/Fonts/Menlo.ttc',
        '/System/Library/Fonts/Monaco.ttf',
        '/Library/Fonts/Courier New.ttf',
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

# ── Helpers: obrazki ─────────────────────────────────────────────────────────

_screenshot_cache = {}

def take_screenshot_of_url(url, wait=6):
    """
    Otwiera URL w przeglądarce, czeka na załadowanie, robi screenshot.
    Zwraca ścieżkę do przetworzonego PNG lub None jeśli się nie udało.
    """
    if not TAKE_SCREENSHOTS:
        return None
    if url in _screenshot_cache:
        return _screenshot_cache[url]

    try:
        print(f"  Otwieram przeglądarkę: {url}")
        subprocess.Popen(['open', url])
        print(f"  Czekam {wait}s na załadowanie strony...")
        time.sleep(wait)

        raw = tempfile.mktemp(suffix='.png')
        subprocess.run(['screencapture', '-x', raw], check=True, capture_output=True)

        img = Image.open(raw)

        # Na retina display screenshoty są 2x — przycinamy do rozsądnych rozmiarów.
        crop_h = int(img.height * 0.58)
        img = img.crop((0, 0, img.width, crop_h))

        ratio = IMG_WIDTH_PX / img.width
        img = img.resize((IMG_WIDTH_PX, int(img.height * ratio)), Image.LANCZOS)

        out = tempfile.mktemp(suffix='.png')
        img.save(out, 'PNG')
        os.unlink(raw)

        _screenshot_cache[url] = out
        return out

    except Exception as e:
        print(f"  Screenshot nie powiódł się ({e}) — pomijam obrazek")
        return None


def close_browser_tabs():
    """Zamyka ostatnie karty w Safari żeby nie śmiecić."""
    try:
        script = '''
        tell application "Safari"
            close current tab of window 1
        end tell
        '''
        subprocess.run(['osascript', '-e', script], capture_output=True, timeout=3)
    except Exception:
        pass


def annotate_image(img_path, text, bg_color=(220, 50, 50), text_color=(255, 255, 255)):
    """
    Dodaje czerwony baner z tekstem na dole obrazka.
    Zwraca ścieżkę do nowego pliku PNG.
    """
    try:
        img = Image.open(img_path)
        font = get_font(14)
        banner_h = 36
        new_img = Image.new('RGB', (img.width, img.height + banner_h), color=bg_color)
        new_img.paste(img, (0, 0))
        draw = ImageDraw.Draw(new_img)
        draw.rectangle([(0, img.height), (img.width, img.height + banner_h)], fill=bg_color)
        draw.text((12, img.height + 9), f"  {text}", font=font, fill=text_color)
        out = tempfile.mktemp(suffix='.png')
        new_img.save(out, 'PNG')
        return out
    except Exception:
        return img_path


def create_terminal_mockup(lines, width=IMG_WIDTH_PX):
    """
    Tworzy mockup okienka terminala (macOS) z podanymi liniami tekstu.
    Zwraca ścieżkę do PNG.
    """
    try:
        mono = get_mono_font(13)
        font = get_font(12)

        line_h = 22
        pad = 14
        title_h = 30
        height = title_h + pad + len(lines) * line_h + pad + 10

        img = Image.new('RGB', (width, height), (28, 28, 28))
        draw = ImageDraw.Draw(img)

        # Pasek tytułu
        draw.rectangle([(0, 0), (width, title_h)], fill=(55, 55, 55))
        colors_tl = [(255, 95, 86), (255, 189, 46), (39, 201, 63)]
        for i, c in enumerate(colors_tl):
            cx = 12 + i * 20
            draw.ellipse([(cx, 9), (cx + 12, 21)], fill=c)
        draw.text((width // 2 - 25, 8), "Terminal", font=font, fill=(180, 180, 180))

        y = title_h + pad
        for line in lines:
            if line.startswith('>>>'):
                draw.text((pad, y), line[3:].strip(), font=mono, fill=(130, 130, 130))
            elif line.startswith('#'):
                draw.text((pad, y), line, font=mono, fill=(95, 95, 95))
            else:
                draw.text((pad, y), f"$ {line}", font=mono, fill=(220, 220, 220))
            y += line_h

        # Kursor
        draw.rectangle([(pad, y), (pad + 9, y + 15)], fill=(200, 200, 200))

        out = tempfile.mktemp(suffix='.png')
        img.save(out, 'PNG')
        return out
    except Exception as e:
        print(f"  Mockup terminala nie powiódł się: {e}")
        return None


def create_windsurf_ide_mockup(width=IMG_WIDTH_PX):
    """
    Tworzy uproszczony mockup Windsurf pokazujący gdzie jest terminal (macOS).
    """
    try:
        font = get_font(12)
        font_sm = get_font(10)
        font_bold = get_font(14)

        height = 300
        editor_split = 175

        img = Image.new('RGB', (width, height), (30, 30, 30))
        draw = ImageDraw.Draw(img)

        # ── Menu bar ──
        draw.rectangle([(0, 0), (width, 26)], fill=(48, 48, 48))
        items = [('File', False), ('Edit', False), ('View', False),
                 ('Terminal', True), ('Help', False)]
        x = 8
        for label, highlight in items:
            color = (255, 215, 0) if highlight else (200, 200, 200)
            draw.text((x, 5), label, font=font, fill=color)
            x += len(label) * 7 + 18

        # ── Edytor (góra) ──
        draw.rectangle([(0, 26), (width, editor_split)], fill=(35, 35, 35))
        draw.text((16, 45), "# Twój kod będzie tutaj", font=font, fill=(70, 70, 70))
        draw.text((16, 70), "def hello():", font=font, fill=(80, 80, 80))
        draw.text((32, 92), 'print("Hello!")', font=font, fill=(80, 80, 80))

        # ── Separator ──
        draw.rectangle([(0, editor_split), (width, editor_split + 2)], fill=(80, 80, 80))

        # ── Panel terminala ──
        draw.rectangle([(0, editor_split + 2), (width, editor_split + 22)],
                        fill=(42, 42, 42))
        draw.text((10, editor_split + 5), "TERMINAL   PROBLEMS   OUTPUT",
                  font=font_sm, fill=(160, 160, 160))

        draw.rectangle([(10, editor_split + 20), (72, editor_split + 22)],
                        fill=(80, 180, 255))

        draw.rectangle([(0, editor_split + 22), (width, height)], fill=(28, 28, 28))
        draw.text((10, editor_split + 30), "pablo@Mac Onboarding %",
                  font=get_mono_font(12), fill=(80, 200, 120))
        draw.rectangle([(10, editor_split + 54), (18, editor_split + 68)],
                        fill=(200, 200, 200))

        # ── Strzałka ──
        ax = width - 20
        ay = editor_split + 55
        draw.polygon([(ax - 30, ay), (ax, ay - 14), (ax, ay + 14)],
                      fill=(255, 60, 60))
        draw.rectangle([(ax - 100, ay - 7), (ax - 30, ay + 7)], fill=(255, 60, 60))
        draw.text((ax - 190, ay - 26), "Tu wpisuj", font=font_bold, fill=(255, 60, 60))
        draw.text((ax - 190, ay - 8), "komendy!", font=font, fill=(255, 60, 60))

        draw.text((8, height - 38), "Jak otworzyć terminal:", font=font_sm,
                  fill=(180, 180, 180))
        draw.text((8, height - 22), "Terminal  →  New Terminal   (lub Ctrl + `)",
                  font=font_sm, fill=(255, 215, 0))

        out = tempfile.mktemp(suffix='.png')
        img.save(out, 'PNG')
        return out
    except Exception as e:
        print(f"  Mockup Windsurf nie powiódł się: {e}")
        return None


def create_powershell_mockup(lines, width=IMG_WIDTH_PX):
    """
    Tworzy mockup okienka PowerShell (Windows — niebieski motyw).
    Zwraca ścieżkę do PNG.
    """
    try:
        mono = get_mono_font(13)
        font = get_font(12)

        line_h = 22
        pad = 14
        title_h = 30
        height = title_h + pad + len(lines) * line_h + pad + 10

        # Ciemny niebieski motyw Windows Terminal
        img = Image.new('RGB', (width, height), (12, 12, 30))
        draw = ImageDraw.Draw(img)

        # Pasek tytułu — granatowy
        draw.rectangle([(0, 0), (width, title_h)], fill=(0, 50, 120))
        draw.text((width // 2 - 45, 8), "Windows PowerShell", font=font, fill=(180, 200, 255))

        # Przyciski tytułu (minimalizuj, maksymalizuj, zamknij)
        draw.text((width - 60, 8), "─  □  ✕", font=font, fill=(180, 200, 255))

        y = title_h + pad
        for line in lines:
            if line.startswith('>>>'):
                draw.text((pad, y), line[3:].strip(), font=mono, fill=(130, 160, 130))
            elif line.startswith('#'):
                draw.text((pad, y), line, font=mono, fill=(80, 100, 80))
            else:
                draw.text((pad, y), f"PS> {line}", font=mono, fill=(180, 220, 255))
            y += line_h

        # Kursor
        draw.rectangle([(pad, y), (pad + 9, y + 15)], fill=(180, 220, 255))

        out = tempfile.mktemp(suffix='.png')
        img.save(out, 'PNG')
        return out
    except Exception as e:
        print(f"  Mockup PowerShell nie powiódł się: {e}")
        return None


def create_windsurf_windows_mockup(width=IMG_WIDTH_PX):
    """
    Tworzy uproszczony mockup Windsurf na Windows z PowerShell w terminalu.
    """
    try:
        font = get_font(12)
        font_sm = get_font(10)
        font_bold = get_font(14)

        height = 300
        editor_split = 175

        img = Image.new('RGB', (width, height), (30, 30, 30))
        draw = ImageDraw.Draw(img)

        # ── Pasek tytułu Windows ──
        draw.rectangle([(0, 0), (width, 26)], fill=(32, 32, 32))
        items = [('File', False), ('Edit', False), ('View', False),
                 ('Terminal', True), ('Help', False)]
        x = 8
        for label, highlight in items:
            color = (0, 120, 212) if highlight else (200, 200, 200)
            draw.text((x, 5), label, font=font, fill=color)
            x += len(label) * 7 + 18
        # Przyciski okna Windows
        draw.text((width - 70, 5), "─  □  ✕", font=font, fill=(200, 200, 200))

        # ── Edytor (góra) ──
        draw.rectangle([(0, 26), (width, editor_split)], fill=(35, 35, 35))
        draw.text((16, 45), "# Twój kod będzie tutaj", font=font, fill=(70, 70, 70))
        draw.text((16, 70), "def hello():", font=font, fill=(80, 80, 80))
        draw.text((32, 92), 'print("Hello!")', font=font, fill=(80, 80, 80))

        # ── Separator ──
        draw.rectangle([(0, editor_split), (width, editor_split + 2)], fill=(80, 80, 80))

        # ── Panel terminala — niebieski motyw Windows ──
        draw.rectangle([(0, editor_split + 2), (width, editor_split + 22)],
                        fill=(42, 42, 42))
        draw.text((10, editor_split + 5), "TERMINAL   PROBLEMS   OUTPUT",
                  font=font_sm, fill=(160, 160, 160))
        draw.rectangle([(10, editor_split + 20), (72, editor_split + 22)],
                        fill=(0, 120, 212))

        draw.rectangle([(0, editor_split + 22), (width, height)], fill=(12, 12, 30))
        draw.text((10, editor_split + 30), "PS C:\\Users\\Jan\\Onboarding>",
                  font=get_mono_font(12), fill=(100, 160, 255))
        draw.rectangle([(10, editor_split + 54), (18, editor_split + 68)],
                        fill=(180, 220, 255))

        # ── Strzałka ──
        ax = width - 20
        ay = editor_split + 55
        draw.polygon([(ax - 30, ay), (ax, ay - 14), (ax, ay + 14)],
                      fill=(0, 120, 212))
        draw.rectangle([(ax - 100, ay - 7), (ax - 30, ay + 7)], fill=(0, 120, 212))
        draw.text((ax - 190, ay - 26), "Tu wpisuj", font=font_bold, fill=(0, 120, 212))
        draw.text((ax - 190, ay - 8), "komendy!", font=font, fill=(0, 120, 212))

        draw.text((8, height - 38), "Jak otworzyć terminal:", font=font_sm,
                  fill=(180, 180, 180))
        draw.text((8, height - 22), "Terminal  →  New Terminal   (lub Ctrl + `)",
                  font=font_sm, fill=(0, 120, 212))

        out = tempfile.mktemp(suffix='.png')
        img.save(out, 'PNG')
        return out
    except Exception as e:
        print(f"  Mockup Windsurf Windows nie powiódł się: {e}")
        return None


# ── Helpers: treść dokumentu ─────────────────────────────────────────────────

def set_font(run, name='Calibri', size=11, bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_formcheckbox(paragraph):
    """Dodaje klikalny checkbox (legacy FORMCHECKBOX)."""
    run = paragraph.add_run()
    fldChar_begin = OxmlElement('w:fldChar')
    fldChar_begin.set(qn('w:fldCharType'), 'begin')
    ffData = OxmlElement('w:ffData')
    for tag, attrs in [
        ('w:name', {'w:val': ''}),
        ('w:enabled', {}),
        ('w:calcOnExit', {'w:val': '0'}),
    ]:
        el = OxmlElement(tag)
        for k, v in attrs.items():
            el.set(qn(k), v)
        ffData.append(el)
    checkBox = OxmlElement('w:checkBox')
    for tag, attrs in [
        ('w:sizeAuto', {}),
        ('w:default', {'w:val': '0'}),
        ('w:checked', {'w:val': '0'}),
    ]:
        el = OxmlElement(tag)
        for k, v in attrs.items():
            el.set(qn(k), v)
        checkBox.append(el)
    ffData.append(checkBox)
    fldChar_begin.append(ffData)
    run._r.append(fldChar_begin)

    run2 = paragraph.add_run()
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = ' FORMCHECKBOX '
    run2._r.append(instrText)

    for ftype in ('separate', 'end'):
        r = paragraph.add_run()
        fc = OxmlElement('w:fldChar')
        fc.set(qn('w:fldCharType'), ftype)
        r._r.append(fc)


def add_section_heading(doc, text):
    doc.add_paragraph()
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    r = h.add_run(text)
    set_font(r, bold=True, size=14, color=(31, 73, 125))
    pPr = h._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    b = OxmlElement('w:bottom')
    b.set(qn('w:val'), 'single')
    b.set(qn('w:sz'), '6')
    b.set(qn('w:space'), '1')
    b.set(qn('w:color'), '1F497D')
    pBdr.append(b)
    pPr.append(pBdr)


def _set_cell_left_border(cell, color_hex):
    """Dodaje lewy border do komórki tabeli (bez innych bordów)."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for bname in ['top', 'bottom', 'right', 'insideV', 'insideH']:
        b = OxmlElement(f'w:{bname}')
        b.set(qn('w:val'), 'none')
        b.set(qn('w:sz'), '0')
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), 'auto')
        tcBorders.append(b)
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), '8')
    left.set(qn('w:space'), '6')
    left.set(qn('w:color'), color_hex)
    tcBorders.append(left)
    tcPr.append(tcBorders)


def _insert_image_in_cell(cell, image_path, caption, width_in=2.8):
    """Wstawia obrazek do komórki tabeli."""
    if image_path and os.path.exists(image_path):
        img_para = cell.add_paragraph()
        img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img_para.paragraph_format.space_before = Pt(4)
        img_para.paragraph_format.space_after = Pt(2)
        try:
            run = img_para.add_run()
            run.add_picture(image_path, width=Inches(width_in))
        except Exception as e:
            print(f"  Nie udało się wstawić obrazka: {e}")
    if caption:
        cap = cell.add_paragraph(f'  {caption}')
        cap.paragraph_format.space_before = Pt(2)
        cap.paragraph_format.space_after = Pt(4)
        for r in cap.runs:
            set_font(r, size=8, italic=True, color=(100, 100, 100))


def _add_screenshot_ph_to_cell(cell, description):
    """Dodaje szary placeholder na screenshot do komórki tabeli."""
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'F2F2F2')
    pPr.append(shd)
    pBdr = OxmlElement('w:pBdr')
    for side in ['top', 'bottom', 'left', 'right']:
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'), 'dashed')
        el.set(qn('w:sz'), '4')
        el.set(qn('w:space'), '4')
        el.set(qn('w:color'), 'AAAAAA')
        pBdr.append(el)
    pPr.append(pBdr)
    r = p.add_run(f'[ Miejsce na screenshot:\n{description} ]')
    set_font(r, size=8, italic=True, color=(120, 120, 120))


def add_screenshot_placeholder(doc, description, indent_cm=1.2):
    """Dodaje szary placeholder na screenshot (wspólny, pełna szerokość)."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(indent_cm)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'F2F2F2')
    pPr.append(shd)
    pBdr = OxmlElement('w:pBdr')
    for side in ['top', 'bottom', 'left', 'right']:
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'), 'dashed')
        el.set(qn('w:sz'), '4')
        el.set(qn('w:space'), '4')
        el.set(qn('w:color'), 'AAAAAA')
        pBdr.append(el)
    pPr.append(pBdr)
    r = p.add_run(f'[ Miejsce na screenshot: {description} ]')
    set_font(r, size=9, italic=True, color=(120, 120, 120))


def add_step(doc, number, title, description, sub_steps=None,
             mac_steps=None, win_steps=None,
             image_path=None, image_caption=None,
             mac_image=None, win_image=None,
             mac_image_caption=None, win_image_caption=None,
             mac_screenshot_desc=None, win_screenshot_desc=None,
             screenshot_desc=None):
    """
    Dodaje krok z checkboxem, opisem, pod-punktami i opcjonalnym obrazkiem.

    sub_steps  — wspólne pod-punkty (renderowane jako jedna lista)
    mac_steps  — pod-punkty specyficzne dla macOS
    win_steps  — pod-punkty specyficzne dla Windows

    Gdy mac_steps lub win_steps są podane, renderowane są w tabeli 2-kolumnowej
    obok siebie: lewa kolumna = Mac, prawa = Windows.

    image_path / image_caption      — wspólny obrazek (dla sub_steps)
    mac_image / win_image           — osobne obrazki per OS (w komórkach tabeli)
    mac_screenshot_desc             — opis placeholdera na screenshot (Mac)
    win_screenshot_desc             — opis placeholdera na screenshot (Windows)
    screenshot_desc                 — opis placeholdera na screenshot (wspólny)
    """
    # ── Tytuł z checkboxem ──
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(12)
    para.paragraph_format.space_after = Pt(3)
    add_formcheckbox(para)
    para.add_run('  ')
    title_run = para.add_run(f'Krok {number} — {title}')
    set_font(title_run, bold=True, size=12)

    # ── Krótki opis ──
    if description:
        d = doc.add_paragraph(description)
        d.paragraph_format.left_indent = Cm(1.2)
        d.paragraph_format.space_before = Pt(2)
        d.paragraph_format.space_after = Pt(4)
        for r in d.runs:
            set_font(r, size=10, color=(70, 70, 70))

    use_os_blocks = bool(mac_steps or win_steps)

    if use_os_blocks:
        # ── Tabela 2-kolumnowa: Mac | Windows obok siebie ──
        table = doc.add_table(rows=1, cols=2)

        # Usuń borders tabeli
        tbl = table._tbl
        tblPr = tbl.find(qn('w:tblPr'))
        if tblPr is None:
            tblPr = OxmlElement('w:tblPr')
            tbl.insert(0, tblPr)
        tblBorders = OxmlElement('w:tblBorders')
        for bname in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
            b = OxmlElement(f'w:{bname}')
            b.set(qn('w:val'), 'none')
            b.set(qn('w:sz'), '0')
            b.set(qn('w:space'), '0')
            b.set(qn('w:color'), 'auto')
            tblBorders.append(b)
        tblPr.append(tblBorders)

        mac_cell = table.cell(0, 0)
        win_cell = table.cell(0, 1)

        # ── Zawartość Mac (lewa kolumna) ──
        if mac_steps:
            _set_cell_left_border(mac_cell, '999999')
            p = mac_cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.left_indent = Cm(0.3)
            r = p.add_run('Na Macu:')
            set_font(r, bold=True, size=10, color=(80, 80, 80))
            for i, step_text in enumerate(mac_steps, start=1):
                sp = mac_cell.add_paragraph()
                sp.paragraph_format.left_indent = Cm(0.5)
                sp.paragraph_format.first_line_indent = Cm(-0.4)
                sp.paragraph_format.space_before = Pt(1)
                sp.paragraph_format.space_after = Pt(2)
                num_run = sp.add_run(f'{i}.  ')
                set_font(num_run, bold=True, size=10, color=(80, 80, 80))
                text_run = sp.add_run(step_text)
                set_font(text_run, size=10)
            actual_mac = mac_image or image_path
            if actual_mac and os.path.exists(actual_mac):
                _insert_image_in_cell(mac_cell, actual_mac,
                                      mac_image_caption or image_caption)
            elif mac_screenshot_desc:
                _add_screenshot_ph_to_cell(mac_cell, mac_screenshot_desc)

        # ── Zawartość Windows (prawa kolumna) ──
        if win_steps:
            _set_cell_left_border(win_cell, '0078D4')
            p = win_cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.left_indent = Cm(0.3)
            r = p.add_run('Na Windowsie:')
            set_font(r, bold=True, size=10, color=(0, 84, 166))
            for i, step_text in enumerate(win_steps, start=1):
                sp = win_cell.add_paragraph()
                sp.paragraph_format.left_indent = Cm(0.5)
                sp.paragraph_format.first_line_indent = Cm(-0.4)
                sp.paragraph_format.space_before = Pt(1)
                sp.paragraph_format.space_after = Pt(2)
                num_run = sp.add_run(f'{i}.  ')
                set_font(num_run, bold=True, size=10, color=(0, 84, 166))
                text_run = sp.add_run(step_text)
                set_font(text_run, size=10)
            if win_image and os.path.exists(win_image):
                _insert_image_in_cell(win_cell, win_image, win_image_caption)
            elif win_screenshot_desc:
                _add_screenshot_ph_to_cell(win_cell, win_screenshot_desc)

    else:
        # ── Wspólne pod-punkty ──
        if sub_steps:
            for i, step_text in enumerate(sub_steps, start=1):
                sp = doc.add_paragraph()
                sp.paragraph_format.left_indent = Cm(1.5)
                sp.paragraph_format.first_line_indent = Cm(-0.4)
                sp.paragraph_format.space_before = Pt(1)
                sp.paragraph_format.space_after = Pt(2)
                num_run = sp.add_run(f'{i}.  ')
                set_font(num_run, bold=True, size=10, color=(31, 73, 125))
                text_run = sp.add_run(step_text)
                set_font(text_run, size=10)

        # ── Obrazek wspólny lub placeholder ──
        if image_path:
            _insert_image(doc, image_path, image_caption)
        elif screenshot_desc:
            add_screenshot_placeholder(doc, screenshot_desc)


def _insert_image(doc, image_path, image_caption):
    """Pomocnicza: wstawia obrazek i jego podpis do dokumentu."""
    if image_path and os.path.exists(image_path):
        img_para = doc.add_paragraph()
        img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img_para.paragraph_format.left_indent = Cm(1.2)
        img_para.paragraph_format.space_before = Pt(6)
        img_para.paragraph_format.space_after = Pt(2)
        try:
            run = img_para.add_run()
            run.add_picture(image_path, width=Inches(IMG_WIDTH_IN))
        except Exception as e:
            print(f"  Nie udało się wstawić obrazka: {e}")

    if image_caption:
        cap = doc.add_paragraph(f'  {image_caption}')
        cap.paragraph_format.left_indent = Cm(1.2)
        cap.paragraph_format.space_before = Pt(2)
        cap.paragraph_format.space_after = Pt(6)
        for r in cap.runs:
            set_font(r, size=9, italic=True, color=(100, 100, 100))


def add_welcome_section(doc):
    """Dodaje przyjazny wstęp z korzyściami i szacunkiem czasu."""

    # ── Ramka "Który masz system?" ──
    sys_para = doc.add_paragraph()
    sys_para.paragraph_format.space_before = Pt(6)
    sys_para.paragraph_format.space_after = Pt(10)

    pPr = sys_para._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'FFF9E6')
    pPr.append(shd)
    pBdr = OxmlElement('w:pBdr')
    for side in ['top', 'bottom', 'left', 'right']:
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '6')
        el.set(qn('w:space'), '4')
        el.set(qn('w:color'), 'FFA000')
        pBdr.append(el)
    pPr.append(pBdr)

    r_label = sys_para.add_run('  Który masz system?   ')
    set_font(r_label, bold=True, size=10, color=(180, 80, 0))
    r_mac = sys_para.add_run('[Apple Mac]')
    set_font(r_mac, bold=True, size=10, color=(60, 60, 60))
    r_mac_desc = sys_para.add_run(' Instrukcje dla Maca oznaczone ')
    set_font(r_mac_desc, size=10, color=(60, 60, 60))
    r_mac_tag = sys_para.add_run('Na Macu:')
    set_font(r_mac_tag, bold=True, size=10, color=(80, 80, 80))
    r_sep = sys_para.add_run('     ')
    set_font(r_sep, size=10)
    r_win = sys_para.add_run('[Windows]')
    set_font(r_win, bold=True, size=10, color=(0, 84, 166))
    r_win_desc = sys_para.add_run(' Instrukcje dla Windowsa oznaczone ')
    set_font(r_win_desc, size=10, color=(60, 60, 60))
    r_win_tag = sys_para.add_run('Na Windowsie:')
    set_font(r_win_tag, bold=True, size=10, color=(0, 84, 166))

    # ── Powitanie ──
    welcome = doc.add_paragraph()
    welcome.paragraph_format.space_before = Pt(4)
    welcome.paragraph_format.space_after = Pt(8)
    r = welcome.add_run('Hej! Nie stresuj się — to prostsze niż myślisz.')
    set_font(r, bold=True, size=13, color=(31, 73, 125))

    p1 = doc.add_paragraph(
        'Nie musisz być informatykiem ani znać się na programowaniu. '
        'Ten onboarding jest zaprojektowany tak, żeby każdy — naprawdę każdy — '
        'mógł przez niego przejść samodzielnie. '
        'A jeśli coś będzie niejasne, Claude (asystent AI) '
        'będzie przy Tobie na każdym kroku i wytłumaczy wszystko po ludzku.'
    )
    p1.paragraph_format.space_after = Pt(10)
    for r in p1.runs:
        set_font(r, size=10)

    # ── Blok korzyści ──
    benefits_title = doc.add_paragraph()
    benefits_title.paragraph_format.space_before = Pt(2)
    benefits_title.paragraph_format.space_after = Pt(4)
    r = benefits_title.add_run('Co zyskasz po instalacji?')
    set_font(r, bold=True, size=11, color=(27, 94, 32))

    BENEFITS = [
        ('Asystent AI dostępny 24/7',
         'Claude odpowiada na pytania, pisze teksty, tłumaczy dokumenty '
         'i rozwiązuje problemy — o każdej porze dnia i nocy.'),
        ('Oszczędzasz czas na co dzień',
         'Zadania, które zajmowały Ci godziny, teraz trwają minuty. '
         'Raporty, emaile, analizy — Claude robi to za Ciebie.'),
        ('Tworzysz projekty jak profesjonalista',
         'Windsurf daje Ci środowisko pracy, w którym Claude widzi Twoje pliki '
         'i pomaga Ci w całym projekcie — nie tylko w jednej rozmowie.'),
        ('AI pamięta Twoje preferencje',
         'Po konfiguracji Claude zapamiętuje jak lubisz pracować, '
         'w jakim języku, co jest dla Ciebie ważne — i stosuje to automatycznie.'),
        ('Zawsze masz kogoś do pomocy',
         'Nie wiesz jak coś zrobić? Zapytaj Claude. '
         'Nie ocenia, nie się niecierpliwi, tłumaczy tyle razy ile potrzebujesz.'),
    ]

    for title, desc in BENEFITS:
        bp = doc.add_paragraph()
        bp.paragraph_format.left_indent = Cm(0.4)
        bp.paragraph_format.space_before = Pt(3)
        bp.paragraph_format.space_after = Pt(3)

        pPr = bp._p.get_or_add_pPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), 'F1F8F1')
        pPr.append(shd)

        pBdr = OxmlElement('w:pBdr')
        left = OxmlElement('w:left')
        left.set(qn('w:val'), 'single')
        left.set(qn('w:sz'), '12')
        left.set(qn('w:space'), '6')
        left.set(qn('w:color'), '43A047')
        pBdr.append(left)
        pPr.append(pBdr)

        check_run = bp.add_run('  ')
        set_font(check_run, size=10)
        title_run = bp.add_run(f'{title}  ')
        set_font(title_run, bold=True, size=10, color=(27, 94, 32))
        desc_run = bp.add_run(desc)
        set_font(desc_run, size=10, color=(70, 70, 70))

    # ── Szacunek czasu ──
    time_para = doc.add_paragraph()
    time_para.paragraph_format.space_before = Pt(12)
    time_para.paragraph_format.space_after = Pt(4)

    pPr = time_para._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'FFF8E1')
    pPr.append(shd)
    pBdr = OxmlElement('w:pBdr')
    for side in ['top', 'bottom', 'left', 'right']:
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '4')
        el.set(qn('w:space'), '4')
        el.set(qn('w:color'), 'FFA000')
        pBdr.append(el)
    pPr.append(pBdr)

    r1 = time_para.add_run('  Ile to zajmie?  ')
    set_font(r1, bold=True, size=10, color=(230, 81, 0))
    r2 = time_para.add_run(
        'Około 20-30 minut — tyle co filiżanka kawy. '
        'Pierwsze 5 kroków zrobisz sam w ok. 10-15 minut. '
        'Reszta zajmie się Claude interaktywnie.'
    )
    set_font(r2, size=10, color=(80, 60, 0))

    # ── Wymagania przed startem ──
    req_title = doc.add_paragraph()
    req_title.paragraph_format.space_before = Pt(12)
    req_title.paragraph_format.space_after = Pt(4)
    r = req_title.add_run('Czego potrzebujesz przed startem?')
    set_font(r, bold=True, size=11, color=(100, 30, 22))

    REQUIREMENTS = [
        ('Konto Anthropic (Claude)',
         'Bezpłatne konto na claude.ai — bez tego nie zaloguje się Claude. '
         'Jeśli nie masz: wejdź na claude.ai, kliknij "Sign up" i utwórz konto.'),
        ('Konto GitHub',
         'Bezpłatne konto na github.com — potrzebne do tworzenia projektów. '
         'Jeśli nie masz: wejdź na github.com, kliknij "Sign up" i utwórz konto.'),
        ('Mac lub Windows 10/11',
         'Ta instrukcja działa na obu systemach. '
         'Kroki specyficzne dla systemu są wyraźnie oznaczone "Na Macu:" lub "Na Windowsie:".'),
        ('Połączenie z internetem',
         'Potrzebne przez cały czas instalacji i późniejszej pracy z Claude.'),
    ]

    for title, desc in REQUIREMENTS:
        rp = doc.add_paragraph()
        rp.paragraph_format.left_indent = Cm(0.4)
        rp.paragraph_format.space_before = Pt(3)
        rp.paragraph_format.space_after = Pt(3)

        pPr = rp._p.get_or_add_pPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), 'FFF3F3')
        pPr.append(shd)
        pBdr = OxmlElement('w:pBdr')
        left = OxmlElement('w:left')
        left.set(qn('w:val'), 'single')
        left.set(qn('w:sz'), '12')
        left.set(qn('w:space'), '6')
        left.set(qn('w:color'), 'E53935')
        pBdr.append(left)
        pPr.append(pBdr)

        rp.add_run('  ')
        t = rp.add_run(f'{title}  ')
        set_font(t, bold=True, size=10, color=(183, 28, 28))
        d = rp.add_run(desc)
        set_font(d, size=10, color=(70, 70, 70))

    # ── Zachęta ──
    closing = doc.add_paragraph(
        'Masz wszystko? Zacznij od Kroku 1 poniżej. Powodzenia!'
    )
    closing.paragraph_format.space_before = Pt(10)
    closing.paragraph_format.space_after = Pt(4)
    for r in closing.runs:
        set_font(r, size=10, italic=True, color=(100, 100, 100))


def add_prompt_block(doc, text):
    """Dodaje niebieski blok z promptem do skopiowania."""
    para = doc.add_paragraph()
    para.paragraph_format.left_indent = Cm(0.5)
    para.paragraph_format.right_indent = Cm(0.5)
    para.paragraph_format.space_before = Pt(8)
    para.paragraph_format.space_after = Pt(8)
    pPr = para._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'EFF3FB')
    pPr.append(shd)
    pBdr = OxmlElement('w:pBdr')
    for side in ['top', 'bottom', 'left', 'right']:
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '4')
        el.set(qn('w:space'), '4')
        el.set(qn('w:color'), '4472C4')
        pBdr.append(el)
    pPr.append(pBdr)
    run = para.add_run(text)
    set_font(run, name='Courier New', size=8)


def add_whats_next(doc):
    """Dodaje sekcje 'Co dalej?' po zakonczeniu konfiguracji."""
    add_section_heading(doc, 'Co dalej? — po zakończeniu konfiguracji')

    intro = doc.add_paragraph(
        'Gratulacje! Masz skonfigurowane środowisko. '
        'Oto co możesz teraz robić:'
    )
    intro.paragraph_format.space_before = Pt(4)
    intro.paragraph_format.space_after = Pt(6)
    for r in intro.runs:
        set_font(r, size=10)

    NEXT_STEPS = [
        ('Stwórz pierwszy projekt',
         'wpisz /setup-new-project do Claude i on zajmie się resztą'),
        ('Pracuj z Claude',
         'po prostu wpisz pytanie lub zadanie. Claude widzi Twoje pliki i pomaga'),
        ('Gdy za dużo rozmów',
         'wpisz /state-start żeby Claude pamiętał gdzie skończyłeś, potem /clear'),
        ('Wróć po przerwie',
         'wpisz /catchup żeby Claude przypomniał sobie co robiliście'),
    ]

    for title, desc in NEXT_STEPS:
        bp = doc.add_paragraph()
        bp.paragraph_format.left_indent = Cm(0.4)
        bp.paragraph_format.space_before = Pt(3)
        bp.paragraph_format.space_after = Pt(3)

        pPr = bp._p.get_or_add_pPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), 'EFF3FB')
        pPr.append(shd)
        pBdr = OxmlElement('w:pBdr')
        left = OxmlElement('w:left')
        left.set(qn('w:val'), 'single')
        left.set(qn('w:sz'), '12')
        left.set(qn('w:space'), '6')
        left.set(qn('w:color'), '4472C4')
        pBdr.append(left)
        pPr.append(pBdr)

        bp.add_run('  ')
        t = bp.add_run(f'{title}  ')
        set_font(t, bold=True, size=10, color=(31, 73, 125))
        d = bp.add_run(f'— {desc}')
        set_font(d, size=10, color=(70, 70, 70))

    closing = doc.add_paragraph(
        'Wszystkiego najlepszego w pracy z AI — Claude czeka na Twoje pytania!'
    )
    closing.paragraph_format.space_before = Pt(10)
    closing.paragraph_format.space_after = Pt(6)
    for r in closing.runs:
        set_font(r, size=10, italic=True, color=(120, 120, 120))


# ── Treść: kroki ─────────────────────────────────────────────────────────────

def build_steps(tmp_dir):
    """
    Buduje listę kroków — jeden dokument dla macOS i Windows.
    """

    print("\nPrzygotowuję obrazki...")

    # Screenshoty (opcjonalne)
    ss_windsurf = take_screenshot_of_url('https://windsurf.com/download', wait=7)
    if ss_windsurf:
        ss_windsurf = annotate_image(ss_windsurf,
            '-> Kliknij przycisk pobierania dla swojego systemu')
        close_browser_tabs()

    ss_nodejs = take_screenshot_of_url('https://nodejs.org', wait=6)
    if ss_nodejs:
        ss_nodejs = annotate_image(ss_nodejs,
            '-> Kliknij ZIELONY przycisk "Download Node.js (LTS)"')
        close_browser_tabs()

    # Mockupy
    img_windsurf_ide = create_windsurf_ide_mockup()
    img_windsurf_win = create_windsurf_windows_mockup()

    img_npm_mac = create_terminal_mockup([
        'npm install -g @anthropic-ai/claude-code',
        '>>> added 127 packages in 45s',
        '>>> (instalacja zakończona, może chwilę potrwać)',
    ])

    img_npm_win = create_powershell_mockup([
        'npm install -g @anthropic-ai/claude-code',
        '>>> added 127 packages in 45s',
        '>>> (instalacja zakończona, może chwilę potrwać)',
    ])

    img_claude = create_terminal_mockup([
        'claude',
        '>>> Opening browser for login...',
        '>>> (przeglądarka się otworzy — zaloguj się)',
    ])

    steps = [
        {
            'title': 'Zainstaluj Windsurf',
            'description': (
                'Windsurf to program, w którym będziesz pracować razem z asystentem AI. '
                'Musisz go zainstalować jak każdy inny program.'
            ),
            'mac_steps': [
                'Otwórz przeglądarkę (Safari, Chrome — cokolwiek masz).',
                'Wejdź na stronę: windsurf.com i naciśnij Enter.',
                'Kliknij przycisk pobierania dla Maca '
                '(może się nazywać "Download for macOS" lub "Download for Mac").',
                'Poczekaj — plik pobierze się do folderu Pobrane (Downloads). '
                'Zobaczysz go na dole okna przeglądarki lub w Finderze Pobrane.',
                'Kliknij dwukrotnie na pobrany plik (kończy się na .dmg).',
                'Pojawi się okienko — przeciągnij ikonę Windsurf do folderu Applications.',
                'Poczekaj aż się skopiuje i zamknij to okienko.',
                'Otwórz Windsurf: kliknij ikonę rakiety w Docku (Launchpad) '
                'lub naciśnij Cmd+Spacja, wpisz "Windsurf" i kliknij.',
            ],
            'win_steps': [
                'Otwórz przeglądarkę (Edge, Chrome — cokolwiek masz).',
                'Wejdź na stronę: windsurf.com i naciśnij Enter.',
                'Kliknij przycisk pobierania dla Windows '
                '(może się nazywać "Download for Windows" lub podobnie).',
                'Poczekaj — plik .exe lub .msi pobierze się do folderu Pobrane.',
                'Otwórz pobrany plik (kliknij dwukrotnie).',
                'Jeśli Windows zapyta "Czy chcesz zezwolić..." — kliknij Tak.',
                'Instalator się otworzy — klikaj Dalej/Next przez kolejne ekrany.',
                'Po instalacji kliknij Windsurf na Pulpicie lub w Menu Start.',
            ],
            'mac_image': img_windsurf_ide,
            'win_image': img_windsurf_win,
            'mac_image_caption': 'Windsurf na Macu — Terminal otworzysz przez Terminal → New Terminal.',
            'win_image_caption': 'Windsurf na Windowsie — Terminal (niebieski, PowerShell) otworzysz przez Terminal → New Terminal.',
        },
        {
            'title': 'Zainstaluj Node.js',
            'description': (
                'Node.js to silnik, bez którego Claude nie uruchomi się. '
                'Instaluje się jak każdy normalny program — kilka kliknięć.'
            ),
            'mac_steps': [
                'Wejdź na stronę: nodejs.org',
                'Kliknij zielony przycisk "Download Node.js (LTS)" — ten z napisem '
                '"Recommended for most users". NIE klikaj "Current".',
                'Plik .pkg pobierze się — poczekaj aż skończy.',
                'Otwórz pobrany plik (kliknij dwukrotnie).',
                'Klikaj "Kontynuuj" (Continue) przez każdy ekran instalatora.',
                'Na końcu kliknij "Zainstaluj" (Install). '
                'Mac może zapytać o hasło — wpisz swoje hasło do komputera.',
                'Gotowe! Możesz zamknąć instalator.',
            ],
            'win_steps': [
                'Wejdź na stronę: nodejs.org',
                'Kliknij zielony przycisk "Download Node.js (LTS)" — ten z napisem '
                '"Recommended for most users". NIE klikaj "Current".',
                'Plik .msi pobierze się — poczekaj aż skończy.',
                'Otwórz pobrany plik (kliknij dwukrotnie).',
                'Jeśli Windows zapyta "Czy chcesz zezwolić..." — kliknij Tak.',
                'Klikaj Next przez kolejne ekrany instalatora — nic nie zmieniaj.',
                'Na końcu kliknij Install. Może zapytać o hasło/zgodę administratora.',
                'Gotowe! Możesz zamknąć instalator.',
            ],
            'mac_screenshot_desc': 'Strona nodejs.org — zielony przycisk "Download Node.js (LTS)" po lewej',
            'win_screenshot_desc': 'Strona nodejs.org — zielony przycisk "Download Node.js (LTS)" po lewej',
        },
        {
            'title': 'Otwórz terminal w Windsurf i wpisz jedną komendę',
            'description': (
                'Terminal to okienko, w którym wpisujesz polecenia. '
                'W Windsurf jest ukryte na dole ekranu — pokażemy Ci jak je otworzyć.'
            ),
            'sub_steps': [
                'Uruchom Windsurf (jeśli jeszcze nie jest otwarty).',
                'W górnym menu kliknij "Terminal" a potem "New Terminal". '
                'Ewentualnie naciśnij klawisze Ctrl + ` '
                '(tylny apostrof — klawisz obok cyfry 1 na klawiaturze).',
                'Na dole ekranu pojawi się ciemne okienko z kursorem — to terminal.',
                'Kliknij w to okienko żeby je zaznaczyć.',
                'Wpisz dokładnie tę komendę i naciśnij Enter: '
                'npm install -g @anthropic-ai/claude-code',
                'Poczekaj — może trwać 1-3 minuty. Zobaczysz dużo tekstu — to normalne.',
                'Gdy skończy, pojawi się nowa linia z kursorem — to znak że gotowe.',
                'UWAGA dla Windows: zamiast zsh zobaczysz PowerShell (niebieski tekst) — to normalne, '
                'komenda działa tak samo.',
            ],
            'image_path': img_npm_mac,
            'image_caption': 'Mac: ciemny terminal z zielonym tekstem po zainstalowaniu.',
            'screenshot_desc': 'Terminal w Windsurf po wpisaniu komendy npm install — widać dużo tekstu zakończonego nową linią',
        },
        {
            'title': 'Otwórz folder Onboarding w Windsurf',
            'description': (
                'Musisz wskazać Windsurfowi folder z plikami onboardingowymi '
                '— ten sam folder, z którego czytasz ten dokument.'
            ),
            'sub_steps': [
                'W Windsurf kliknij "File" w górnym menu.',
                'Kliknij "Open Folder..." (Otwórz folder).',
                'Pojawi się okienko do wyboru folderu — znajdź i zaznacz folder "Onboarding".',
                'Kliknij przycisk "Open" (lub "Otwórz") na dole okienka.',
                'Po lewej stronie Windsurf pojawi się lista plików z folderu Onboarding '
                '— to znak że zadziałało.',
            ],
            'screenshot_desc': 'Windsurf z otwartym folderem Onboarding — po lewej stronie widać panel z plikami projektu',
        },
        {
            'title': 'Uruchom Claude i zaloguj się',
            'description': (
                'Teraz uruchamiamy samego Claude — asystenta AI. '
                'Przy pierwszym uruchomieniu otworzy się przeglądarka żebyś się zalogował.'
            ),
            'sub_steps': [
                'W ciemnym okienku (terminal) na dole Windsurf kliknij żeby je zaznaczyć.',
                'Wpisz: claude  i naciśnij Enter.',
                'Claude może zapytać o zgodę na uruchomienie — jeśli zobaczysz pytanie, '
                'wpisz Y i Enter.',
                'Automatycznie otworzy się przeglądarka z prośbą o zalogowanie. '
                'Jeśli nie masz konta Anthropic — kliknij "Sign up" i utwórz je teraz (bezpłatne). '
                'Jeśli masz — zaloguj się normalnie.',
                'Po zalogowaniu wróć do Windsurf — zostaw przeglądarkę otwartą.',
                'W terminalu zobaczysz że Claude czeka — pojawi się coś w stylu: "Claude Code >"',
            ],
            'image_path': img_claude,
            'image_caption': 'Tak wygląda uruchomiony Claude w terminalu Windsurf.',
            'screenshot_desc': 'Terminal pokazujący "Claude Code >" — znak że Claude jest uruchomiony i czeka',
        },
        {
            'title': 'Wklej prompt z Części 2 — Claude zajmie się resztą!',
            'description': (
                'To ostatni krok który robisz sam. '
                'Dajesz Claude instrukcje i od tej chwili on prowadzi Cię przez całą konfigurację '
                '— po polsku, krok po kroku, czekając aż każdy krok zrobisz.'
            ),
            'sub_steps': [
                'Przejdź na następną stronę tego dokumentu.',
                'Zaznacz CAŁY tekst w niebieskiej ramce.',
                'Skopiuj go: Cmd+C na Macu  lub  Ctrl+C na Windowsie.',
                'Wróć do Windsurf i kliknij w ciemne okienko terminala.',
                'Wklej: Cmd+V na Macu  lub  Ctrl+V na Windowsie.',
                'Naciśnij Enter.',
                'Claude zacznie pisać do Ciebie i przeprowadzi Cię przez każdy następny krok. '
                'Wystarczy że będziesz odpowiadać "gotowe" gdy skończysz każdy krok.',
            ],
        },
    ]

    return steps


# ── Prompty handoff ────────────────────────────────────────────────────────────

HANDOFF_PROMPT = """\
Przeprowadź mnie przez konfigurację środowiska Claude Code.
Jestem nowym użytkownikiem — właśnie zainstalowałem Windsurf i Claude Code CLI,
jestem zalogowany i pracuję w folderze Onboarding (zawiera podfolder setup/).

Zasady: tłumacz prosto bez żargonu, jedna komenda na raz, czekaj na "gotowe",
sprawdzaj po każdym kroku, napraw błędy zanim przejdziesz dalej.

KROK 0 — Wykryj mój system: uruchom `uname -s` (macOS → Darwin) lub sprawdź
czy jesteś w PowerShell (Windows). Przez całą resztę używaj właściwych komend.

CZĘŚĆ A — Narzędzia

1. Sprawdź `gh --version` i `jq --version`. Jeśli brak:
   macOS: sprawdź Homebrew (brew --version), zainstaluj jeśli brak,
          potem: brew install gh jq
   Windows: winget install GitHub.cli + winget install jqlang.jq
            (potem zamknij i otwórz nowy terminal)

2. Zapytaj czy mam konto github.com (jeśli nie — powiedz żeby założyć).
   Następnie: gh auth login → GitHub.com → HTTPS → przez przeglądarkę
   Sprawdź: gh auth status

CZĘŚĆ B — Konfiguracja Claude

3. Utwórz foldery:
   macOS:   mkdir -p ~/.claude/skills ~/.claude/hooks ~/.claude/memory
   Windows: New-Item -ItemType Directory -Force "$HOME/.claude/skills",
            "$HOME/.claude/hooks","$HOME/.claude/memory"

4. Skopiuj skille z setup/skills/ do ~/.claude/skills/:
   macOS:   cp -r setup/skills/* ~/.claude/skills/
   Windows: Copy-Item -Recurse setup\skills\* "$HOME\.claude\skills\"
   Sprawdź: ls ~/.claude/skills/ → state-start, catchup, setup-new-project

5. Skopiuj security hook:
   macOS:   cp setup/hooks/security-scan.py ~/.claude/hooks/
            chmod +x ~/.claude/hooks/security-scan.py
   Windows: Copy-Item setup\hooks\security-scan.py "$HOME\.claude\hooks\"

6. Skopiuj statusline:
   macOS:   cp setup/statusline-command.sh ~/.claude/
            chmod +x ~/.claude/statusline-command.sh
   Windows: Copy-Item setup\statusline-command.sh "$HOME\.claude\"

7. Wygeneruj ~/.claude/settings.json z absolutnymi ścieżkami (NIE ~):
   macOS (bash heredoc — $HOME rozwinie się automatycznie):
     cat > ~/.claude/settings.json << EOF
     { "model": "sonnet",
       "statusLine": {"type":"command",
         "command":"bash $HOME/.claude/statusline-command.sh"},
       "hooks": {"PreToolUse": [{"matcher":"Write|Edit|Bash",
         "hooks":[{"type":"command",
           "command":"python3 $HOME/.claude/hooks/security-scan.py"}]}]} }
     EOF
   Windows (PowerShell):
     $h = $env:USERPROFILE
     @"{ "model":"sonnet",
       "statusLine":{"type":"command","command":"bash $h/.claude/statusline-command.sh"},
       "hooks":{"PreToolUse":[{"matcher":"Write|Edit|Bash",
         "hooks":[{"type":"command",
           "command":"python3 $h/.claude/hooks/security-scan.py"}]}]} }"@ |
     Set-Content "$HOME\.claude\settings.json"
   Sprawdź: ścieżki muszą być absolutne np. /Users/... lub C:\Users\...

8. Skonfiguruj CLAUDE.md — zapytaj mnie o:
   język pracy z AI / GitHub username / ścieżka do projektów
   Skopiuj setup/global-claude-template.md → ~/.claude/CLAUDE.md
   i uzupełnij wszystkie placeholdery [[...]].

9. Zaktualizuj setup-new-project:
   W ~/.claude/skills/setup-new-project/SKILL.md zamień GITHUB_USERNAME
   na mój username.

CZĘŚĆ C — Weryfikacja końcowa

Sprawdź każdy punkt i podaj wynik jako listę z: OK lub BŁĄD:
1. ls ~/.claude/skills/ → state-start, catchup, setup-new-project
2. ls ~/.claude/hooks/ → security-scan.py
3. ls ~/.claude/ → statusline-command.sh, settings.json, CLAUDE.md
4. Zawartość settings.json → ścieżki absolutne (nie ~)
5. gh auth status → GitHub zalogowany
6. Uruchom /state-start → plik .claude/session-state.md zapisany

Jeśli wszystko OK → powiedz "Środowisko gotowe!" i wyjaśnij w skrócie:
- jak stworzyć pierwszy projekt (/setup-new-project)
- kiedy używać /state-start i /catchup
Jeśli cokolwiek nie OK → napraw zanim zakończysz.\
"""


# ── Generowanie dokumentu ─────────────────────────────────────────────────────

def generate():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_path = os.path.join(project_root, 'docs', 'output', 'onboarding.docx')

    tmp_dir = tempfile.mkdtemp()

    print("Generuje onboarding.docx (macOS + Windows)...")
    steps = build_steps(tmp_dir)

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # ── Tytul ──
    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_para.paragraph_format.space_after = Pt(4)
    r = title_para.add_run('Onboarding — Claude Code w Windsurf')
    set_font(r, bold=True, size=20, color=(31, 73, 125))

    sub_para = doc.add_paragraph()
    sub_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_para.paragraph_format.space_after = Pt(14)
    r = sub_para.add_run('Instrukcja startowa · macOS i Windows')
    set_font(r, size=11, color=(128, 128, 128))

    add_welcome_section(doc)

    # ── Czesc 1: Kroki ──
    add_section_heading(doc, 'Część 1 — Zrób to sam  (6 kroków)')

    for i, step in enumerate(steps, start=1):
        add_step(
            doc,
            number=i,
            title=step['title'],
            description=step.get('description'),
            sub_steps=step.get('sub_steps'),
            mac_steps=step.get('mac_steps'),
            win_steps=step.get('win_steps'),
            image_path=step.get('image_path'),
            image_caption=step.get('image_caption'),
            mac_image=step.get('mac_image'),
            win_image=step.get('win_image'),
            mac_image_caption=step.get('mac_image_caption'),
            win_image_caption=step.get('win_image_caption'),
        )

    # ── Czesc 2: Prompty ──
    doc.add_page_break()
    add_section_heading(doc, 'Część 2 — Tekst do wklejenia do Claude')

    instruction = doc.add_paragraph(
        'Zaznacz CAŁY tekst w niebieskiej ramce poniżej, '
        'skopiuj (Cmd+C na Macu / Ctrl+C na Windowsie) '
        'i wklej do czarnego okienka w Windsurf gdzie działa Claude '
        '(Cmd+V na Macu / Ctrl+V na Windowsie). '
        'Naciśnij Enter. Claude wykryje Twój system i przeprowadzi Cię przez całą resztę.'
    )
    for r in instruction.runs:
        set_font(r, size=10)

    add_prompt_block(doc, HANDOFF_PROMPT)

    note = doc.add_paragraph(
        'Szczegółowy opis każdego kroku konfiguracji: setup/onboarding-prompt.md'
    )
    note.paragraph_format.space_before = Pt(6)
    for r in note.runs:
        set_font(r, size=9, color=(128, 128, 128))

    # ── Czesc 3: Co dalej? ──
    doc.add_page_break()
    add_whats_next(doc)

    # ── Zapis ──
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    print(f'\nZapisano: {output_path}')

    if TAKE_SCREENSHOTS:
        print('\nUwaga: screenshoty zostaly zrobione przy uzyciu aktualnych stron internetowych.')


if __name__ == '__main__':
    generate()
