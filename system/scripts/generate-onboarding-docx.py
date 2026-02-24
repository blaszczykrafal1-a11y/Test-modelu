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


def _add_os_subheading(doc, label, border_color_hex):
    """Pomocniczy — dodaje nagłówek OS (Na Macu: / Na Windowsie:) z lewym bordem."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.5)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)

    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), '8')
    left.set(qn('w:space'), '6')
    left.set(qn('w:color'), border_color_hex)
    pBdr.append(left)
    pPr.append(pBdr)

    r = p.add_run(label)
    set_font(r, bold=True, size=10)
    return p


def add_step(doc, number, title, description, sub_steps=None,
             mac_steps=None, win_steps=None,
             image_path=None, image_caption=None,
             mac_image=None, win_image=None,
             mac_image_caption=None, win_image_caption=None):
    """
    Dodaje krok z checkboxem, opisem, pod-punktami i opcjonalnym obrazkiem.

    sub_steps  — wspólne pod-punkty (renderowane jako jedna lista)
    mac_steps  — pod-punkty specyficzne dla macOS
    win_steps  — pod-punkty specyficzne dla Windows

    Gdy mac_steps lub win_steps są podane, renderowane są dwa bloki
    z nagłówkami "Na Macu:" (border #999999) i "Na Windowsie:" (border #0078D4).

    image_path / image_caption  — wspólny obrazek (fallback)
    mac_image / win_image       — osobne obrazki per OS
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
        # ── Blok macOS ──
        if mac_steps:
            _add_os_subheading(doc, 'Na Macu:', '999999')
            for i, step_text in enumerate(mac_steps, start=1):
                sp = doc.add_paragraph()
                sp.paragraph_format.left_indent = Cm(2.2)
                sp.paragraph_format.first_line_indent = Cm(-0.4)
                sp.paragraph_format.space_before = Pt(1)
                sp.paragraph_format.space_after = Pt(2)
                num_run = sp.add_run(f'{i}.  ')
                set_font(num_run, bold=True, size=10, color=(80, 80, 80))
                text_run = sp.add_run(step_text)
                set_font(text_run, size=10)

        # Obrazek macOS
        _insert_image(doc, mac_image or image_path, mac_image_caption or image_caption)

        # ── Blok Windows ──
        if win_steps:
            _add_os_subheading(doc, 'Na Windowsie:', '0078D4')
            for i, step_text in enumerate(win_steps, start=1):
                sp = doc.add_paragraph()
                sp.paragraph_format.left_indent = Cm(2.2)
                sp.paragraph_format.first_line_indent = Cm(-0.4)
                sp.paragraph_format.space_before = Pt(1)
                sp.paragraph_format.space_after = Pt(2)
                num_run = sp.add_run(f'{i}.  ')
                set_font(num_run, bold=True, size=10, color=(0, 84, 166))
                text_run = sp.add_run(step_text)
                set_font(text_run, size=10)

        # Obrazek Windows
        _insert_image(doc, win_image, win_image_caption)

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

        # ── Obrazek wspólny ──
        _insert_image(doc, image_path, image_caption)


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

    r_label = sys_para.add_run('  Ktory masz system?   ')
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
    r = welcome.add_run('Hej! Nie stresuj sie — to prostsze niz myslisz.')
    set_font(r, bold=True, size=13, color=(31, 73, 125))

    p1 = doc.add_paragraph(
        'Nie musisz byc informatykiem ani znac sie na programowaniu. '
        'Ten onboarding jest zaprojektowany tak, zeby kazdy — naprawde kazdy — '
        'mogl przez niego przejsc samodzielnie. '
        'A jesli cos bedzie niejasne, Claude (asystent AI) '
        'bedzie przy Tobie na kazdym kroku i wytlumaczy wszystko po ludzku.'
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
        ('Asystent AI dostepny 24/7',
         'Claude odpowiada na pytania, pisze teksty, tlumaczy dokumenty '
         'i rozwiazuje problemy — o kazdej porze dnia i nocy.'),
        ('Oszczedzasz czas na co dzien',
         'Zadania, ktore zajmowaly Ci godziny, teraz trwaja minuty. '
         'Raporty, emaile, analizy — Claude robi to za Ciebie.'),
        ('Tworzysz projekty jak profesjonalista',
         'Windsurf daje Ci srodowisko pracy, w ktorym Claude widzi Twoje pliki '
         'i pomaga Ci w calym projekcie — nie tylko w jednej rozmowie.'),
        ('AI pamieta Twoje preferencje',
         'Po konfiguracji Claude zapamietuje jak lubisz pracowac, '
         'w jakim jezyku, co jest dla Ciebie wazne — i stosuje to automatycznie.'),
        ('Zawsze masz kogos do pomocy',
         'Nie wiesz jak cos zrobic? Zapytaj Claude. '
         'Nie ocenia, nie sie niecierpliwi, tlumaczy tyle razy ile potrzebujesz.'),
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
        'Okolo 20-30 minut — tyle co filizanka kawy. '
        'Pierwsze 5 krokow zrobisz sam w ok. 10-15 minut. '
        'Reszta zajmie sie Claude interaktywnie.'
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
         'Bezplatne konto na claude.ai — bez tego nie zaloguje sie Claude. '
         'Jesli nie masz: wejdz na claude.ai, kliknij "Sign up" i utworz konto.'),
        ('Konto GitHub',
         'Bezplatne konto na github.com — potrzebne do tworzenia projektow. '
         'Jesli nie masz: wejdz na github.com, kliknij "Sign up" i utworz konto.'),
        ('Mac lub Windows 10/11',
         'Ta instrukcja dziala na obu systemach. '
         'Kroki specyficzne dla systemu sa wyraznie oznaczone "Na Macu:" lub "Na Windowsie:".'),
        ('Polaczenie z internetem',
         'Potrzebne przez caly czas instalacji i pozniejszej pracy z Claude.'),
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
        'Masz wszystko? Zacznij od Kroku 1 ponizej. Powodzenia!'
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
    add_section_heading(doc, 'Co dalej? — po zakonczeniu konfiguracji')

    intro = doc.add_paragraph(
        'Gratulacje! Masz skonfigurowane srodowisko. '
        'Oto co mozesz teraz robic:'
    )
    intro.paragraph_format.space_before = Pt(4)
    intro.paragraph_format.space_after = Pt(6)
    for r in intro.runs:
        set_font(r, size=10)

    NEXT_STEPS = [
        ('Stworz pierwszy projekt',
         'wpisz /setup-new-project do Claude i on zajmie sie reszta'),
        ('Pracuj z Claude',
         'po prostu wpisz pytanie lub zadanie. Claude widzi Twoje pliki i pomaga'),
        ('Gdy za duzo rozmow',
         'wpisz /state-start zeby Claude pamietat gdzie skonczyles, potem /clear'),
        ('Wron po przerwie',
         'wpisz /catchup zeby Claude przypominal sobie co robiliście'),
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
        '>>> (instalacja zakonczona, moze chwile potrwac)',
    ])

    img_npm_win = create_powershell_mockup([
        'npm install -g @anthropic-ai/claude-code',
        '>>> added 127 packages in 45s',
        '>>> (instalacja zakonczona, moze chwile potrwac)',
    ])

    img_claude = create_terminal_mockup([
        'claude',
        '>>> Opening browser for login...',
        '>>> (przegladarka sie otworzy — zaloguj sie)',
    ])

    steps = [
        {
            'title': 'Zainstaluj Windsurf',
            'description': (
                'Windsurf to program, w ktorym bedziesz pracowac razem z asystentem AI. '
                'Musisz go zainstalowac jak kazdy inny program.'
            ),
            'mac_steps': [
                'Otworz przegladarke (Safari, Chrome — cokolwiek masz).',
                'Wejdz na strone: windsurf.com i nacisnij Enter.',
                'Kliknij przycisk pobierania dla Maca '
                '(moze sie nazywac "Download for macOS" lub "Download for Mac").',
                'Poczekaj — plik pobierze sie do folderu Pobrane (Downloads). '
                'Zobaczysz go na dole okna przegladarki lub w Finderze Pobrane.',
                'Kliknij dwukrotnie na pobrany plik (konczy sie na .dmg).',
                'Pojawi sie okienko — przeciagnij ikone Windsurf do folderu Applications.',
                'Poczekaj az sie skopiuje i zamknij to okienko.',
                'Otworz Windsurf: kliknij ikone rakiety w Docku (Launchpad) '
                'lub nacisnij Cmd+Spacja, wpisz "Windsurf" i kliknij.',
            ],
            'win_steps': [
                'Otworz przegladarke (Edge, Chrome — cokolwiek masz).',
                'Wejdz na strone: windsurf.com i nacisnij Enter.',
                'Kliknij przycisk pobierania dla Windows '
                '(moze sie nazywac "Download for Windows" lub podobnie).',
                'Poczekaj — plik .exe lub .msi pobierze sie do folderu Pobrane.',
                'Otworz pobrany plik (kliknij dwukrotnie).',
                'Jesli Windows zapyta "Czy chcesz zezwolic..." — kliknij Tak.',
                'Instalator sie otworzy — klikaj Dalej/Next przez kolejne ekrany.',
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
                'Node.js to silnik, bez ktorego Claude nie uruchomi sie. '
                'Instaluje sie jak kazdy normalny program — kilka klikniec.'
            ),
            'mac_steps': [
                'Wejdz na strone: nodejs.org',
                'Kliknij zielony przycisk "Download Node.js (LTS)" — ten z napisem '
                '"Recommended for most users". NIE klikaj "Current".',
                'Plik .pkg pobierze sie — poczekaj az skonczy.',
                'Otworz pobrany plik (kliknij dwukrotnie).',
                'Klikaj "Kontynuuj" (Continue) przez kazdy ekran instalatora.',
                'Na koncu kliknij "Zainstaluj" (Install). '
                'Mac moze zapytac o haslo — wpisz swoje haslo do komputera.',
                'Gotowe! Mozesz zamknac instalator.',
            ],
            'win_steps': [
                'Wejdz na strone: nodejs.org',
                'Kliknij zielony przycisk "Download Node.js (LTS)" — ten z napisem '
                '"Recommended for most users". NIE klikaj "Current".',
                'Plik .msi pobierze sie — poczekaj az skonczy.',
                'Otworz pobrany plik (kliknij dwukrotnie).',
                'Jesli Windows zapyta "Czy chcesz zezwolic..." — kliknij Tak.',
                'Klikaj Next przez kolejne ekrany instalatora — nic nie zmieniaj.',
                'Na koncu kliknij Install. Moze zapytac o haslo/zgode administratora.',
                'Gotowe! Mozesz zamknac instalator.',
            ],
            'image_path': ss_nodejs,
            'image_caption': 'Strona nodejs.org — kliknij zielony przycisk LTS (ten po lewej).',
        },
        {
            'title': 'Otworz terminal w Windsurf i wpisz jedna komende',
            'description': (
                'Terminal to okienko, w ktorym wpisujesz polecenia. '
                'W Windsurf jest ukryte na dole ekranu — pokarzemy Ci jak je otworzyc.'
            ),
            'sub_steps': [
                'Uruchom Windsurf (jesli jeszcze nie jest otwarty).',
                'W gornym menu kliknij "Terminal" a potem "New Terminal". '
                'Ewentualnie nacisnij klawisze Ctrl + ` '
                '(tylni apostrof — klawisz obok cyfry 1 na klawiaturze).',
                'Na dole ekranu pojawi sie ciemne okienko z kursorem — to terminal.',
                'Kliknij w to okienko zeby je zaznaczyc.',
                'Wpisz dokladnie te komende i nacisnij Enter: '
                'npm install -g @anthropic-ai/claude-code',
                'Poczekaj — moze trwac 1-3 minuty. Zobaczysz duzo tekstu — to normalne.',
                'Gdy skonczy, pojawi sie nowa linia z kursorem — to znak ze gotowe.',
                'UWAGA dla Windows: zamiast zsh zobaczysz PowerShell (niebieski tekst) — to normalne, '
                'komenda dziala tak samo.',
            ],
            'mac_image': img_windsurf_ide,
            'win_image': img_windsurf_win,
            'mac_image_caption': 'Mac: ciemny terminal z zielonym tekstem.',
            'win_image_caption': 'Windows: niebieski PowerShell — to rowniez terminal, dziala tak samo.',
        },
        {
            'title': 'Otworz folder Onboarding w Windsurf',
            'description': (
                'Musisz wskazac Windsurfowi folder z plikami onboardingowymi '
                '— ten sam folder, z ktorego czytasz ten dokument.'
            ),
            'sub_steps': [
                'W Windsurf kliknij "File" w gornym menu.',
                'Kliknij "Open Folder..." (Otworz folder).',
                'Pojawi sie okienko do wyboru folderu — znajdz i zaznacz folder "Onboarding".',
                'Kliknij przycisk "Open" (lub "Otworz") na dole okienka.',
                'Po lewej stronie Windsurf pojawi sie lista plikow z folderu Onboarding '
                '— to znak ze zadzialalo.',
            ],
        },
        {
            'title': 'Uruchom Claude i zaloguj sie',
            'description': (
                'Teraz uruchamiamy samego Claude — asystenta AI. '
                'Przy pierwszym uruchomieniu otworzy sie przegladarka zebys sie zalogowal.'
            ),
            'sub_steps': [
                'W ciemnym okienku (terminal) na dole Windsurf kliknij zeby je zaznaczyc.',
                'Wpisz: claude  i nacisnij Enter.',
                'Claude moze zapytac o zgode na uruchomienie — jesli zobaczysz pytanie, '
                'wpisz Y i Enter.',
                'Automatycznie otworzy sie przegladarka z prosba o zalogowanie. '
                'Jesli nie masz konta Anthropic — kliknij "Sign up" i utworz je teraz (bezplatne). '
                'Jesli masz — zaloguj sie normalnie.',
                'Po zalogowaniu wron do Windsurf — zostaw przegladarke otwarta.',
                'W terminalu zobaczysz ze Claude czeka — pojawi sie cos w stylu: "Claude Code >"',
            ],
            'image_path': img_claude,
            'image_caption': 'Tak wyglada uruchomiony Claude w terminalu Windsurf.',
        },
        {
            'title': 'Wklej prompt z Czesci 2 — Claude zajmie sie reszta!',
            'description': (
                'To ostatni krok ktory robisz sam. '
                'Dajesz Claude instrukcje i od tej chwili on prowadzi Cie przez cala konfiguracje '
                '— po polsku, krok po kroku, czekajac az kazdy krok zrobisz.'
            ),
            'sub_steps': [
                'Przejdz na nastepna strone tego dokumentu.',
                'Znajdz swoj system — "Jesli masz Maca" lub "Jesli masz Windowsa" — '
                'i zaznacz CALY tekst w niebieskiej ramce dla swojego systemu.',
                '(Mac) Skopiuj: Cmd+C  |  (Windows) Skopiuj: Ctrl+C',
                'Wron do Windsurf i kliknij w ciemne okienko terminala.',
                '(Mac) Wklej: Cmd+V  |  (Windows) Wklej: Ctrl+V',
                'Nacisnij Enter.',
                'Claude zacznie pisac do Ciebie i przeprowadzi Cie przez kazdy nastepny krok. '
                'Wystarczy ze bedziesz odpowiadac "gotowe" gdy skonczysz kazdy krok.',
            ],
        },
    ]

    return steps


# ── Prompty handoff ────────────────────────────────────────────────────────────

HANDOFF_PROMPT = """\
Przeprowadz mnie przez konfiguracje srodowiska Claude Code.

Jestem nowym uzytkownikiem. Wlasnie zainstalowalem Windsurf i Claude Code CLI,
jestem zalogowany. Pracuje w folderze Onboarding — zawiera podfolder setup/
z gotowymi plikami do skopiowania.

Zasady dla kazdego kroku:
- Tlumacz prosto, bez zargonu technicznego — jakbys mowil do osoby ktora
  nigdy nie programowala
- Podawaj JEDNA komende lub akcje na raz
- Czekaj az powiem "gotowe" zanim przejdziesz do nastepnego kroku
- Po kazdym kroku sprawdz czy zadzialalo
- Jesli cos sie nie uda — pomoz mi to naprawic zanim pojdziemy dalej

CZESC A — Instalacja brakujacych narzedzi

1. Sprawdz czy mam Homebrew: brew --version
   Jesli nie ma — zainstaluj. (Homebrew to sklep z narzediami dla Maca)
2. Zainstaluj gh i jq: brew install gh jq
   (gh = do laczenia z GitHub, jq = pomocnik konfiguracyjny)
3. Zaloguj mnie do GitHub: gh auth login
   Wybierz: GitHub.com -> HTTPS -> zaloguj przez przegladarke

CZESC B — Konfiguracja Claude

4. Utworz foldery: ~/.claude/skills/  ~/.claude/hooks/  ~/.claude/memory/
5. Skopiuj skille z setup/skills/ do ~/.claude/skills/
   (state-start, catchup, setup-new-project)
6. Skopiuj hook bezpieczenstwa: setup/hooks/security-scan.py -> ~/.claude/hooks/
   Nadaj uprawnienia: chmod +x
7. Skopiuj status bar: setup/statusline-command.sh -> ~/.claude/
   Nadaj uprawnienia: chmod +x
8. Wygeneruj plik konfiguracyjny ~/.claude/settings.json
   z ustawieniami hooka i status baru (uzyj $HOME zamiast ~ przy sciezkach)
9. Zapytaj mnie o:
   - w jakim jezyku chce rozmawiac z AI (np. polski)
   - moj GitHub username
   - gdzie trzymam foldery projektow (np. ~/Projects/)
   Potem skopiuj setup/global-claude-template.md -> ~/.claude/CLAUDE.md
   i uzupelnij moje dane w miejscach oznaczonych [[...]]
10. W pliku ~/.claude/skills/setup-new-project/SKILL.md
    zamien GITHUB_USERNAME na moj GitHub username
11. Weryfikacja koncowa: sprawdz ze wszystkie pliki istnieja,
    pokaz zawartosc settings.json, przetestuj komende /state-start

Na koncu wytlumacz mi jak stworzyc swoj pierwszy projekt:
- jak skopiowac folder Onboarding jako szablon
- jak uruchomic /setup-new-project zeby stworzyc repo na GitHub

Pelny opis kazdego kroku: setup/onboarding-prompt.md\
"""

WIN_HANDOFF_PROMPT = (
    "Przeprowadź mnie przez konfigurację środowiska Claude Code.\n"
    "\n"
    "Jestem nowym użytkownikiem na WINDOWS 10/11. Właśnie zainstalowałem Windsurf\n"
    "i Claude Code CLI, jestem zalogowany. Pracuję w folderze Onboarding — zawiera\n"
    "podfolder setup/ z gotowymi plikami do skopiowania.\n"
    "\n"
    "Zasady dla każdego kroku:\n"
    "- Tłumacz prosto, bez żargonu — jakbyś mówił do osoby która nigdy nie programowała\n"
    "- Używaj komend dla Windows (PowerShell), NIE dla macOS\n"
    "- Jedna komenda na raz, czekaj na 'gotowe', sprawdzaj po każdym kroku\n"
    "\n"
    "CZĘŚĆ A — Instalacja narzędzi (jeśli brakuje):\n"
    "\n"
    "1. Sprawdź: winget --version\n"
    "   Jeśli brak — powiedz żeby zainstalować 'App Installer' z Microsoft Store.\n"
    "2. Zainstaluj narzędzia:\n"
    "   winget install GitHub.cli\n"
    "   winget install jqlang.jq\n"
    "3. Zamknij i otwórz nowy terminal w Windsurf (żeby narzędzia były widoczne).\n"
    "4. Zapytaj czy user ma konto github.com. Jeśli nie — powiedz żeby założył (bezpłatne).\n"
    "   Potem: gh auth login  (GitHub.com -> HTTPS -> zaloguj przez przeglądarkę)\n"
    "\n"
    "CZĘŚĆ B — Konfiguracja Claude:\n"
    "\n"
    "5. Utwórz foldery konfiguracyjne:\n"
    "   New-Item -ItemType Directory -Force $HOME/.claude/skills\n"
    "   New-Item -ItemType Directory -Force $HOME/.claude/hooks\n"
    "   New-Item -ItemType Directory -Force $HOME/.claude/memory\n"
    "6. Skopiuj skille z setup/skills/ do $HOME/.claude/skills/\n"
    "   (state-start, catchup, setup-new-project)\n"
    "7. Skopiuj hook: setup/hooks/security-scan.py -> $HOME/.claude/hooks/\n"
    "8. Skopiuj status bar: setup/statusline-command.sh -> $HOME/.claude/\n"
    "9. Wygeneruj $HOME/.claude/settings.json z DOKŁADNIE taką strukturą:\n"
    "   (użyj $env:USERPROFILE żeby ścieżki były absolutne)\n"
    "\n"
    '   $home = $env:USERPROFILE\n'
    '   $json = @"\n'
    '   {\n'
    '     "model": "sonnet",\n'
    '     "statusLine": {\n'
    '       "type": "command",\n'
    '       "command": "bash $home/.claude/statusline-command.sh"\n'
    '     },\n'
    '     "hooks": {\n'
    '       "PreToolUse": [{\n'
    '         "matcher": "Write|Edit|Bash",\n'
    '         "hooks": [{ "type": "command",\n'
    '           "command": "python3 $home/.claude/hooks/security-scan.py" }]\n'
    '       }]\n'
    '     }\n'
    '   }\n'
    '   "@\n'
    '   $json | Set-Content $HOME/.claude/settings.json\n'
    "\n"
    "   Sprawdź: Get-Content $HOME/.claude/settings.json\n"
    "   Ścieżki muszą zawierać pełną ścieżkę (C:\\Users\\...), nie ~.\n"
    "\n"
    "10. Zapytaj o: język AI, GitHub username, ścieżka projektów.\n"
    "    Skopiuj setup/global-claude-template.md -> $HOME/.claude/CLAUDE.md\n"
    "    i wypełnij miejsca oznaczone [[...]] moimi danymi.\n"
    "11. W $HOME/.claude/skills/setup-new-project/SKILL.md\n"
    "    zamień GITHUB_USERNAME na mój GitHub username.\n"
    "12. Weryfikacja końcowa:\n"
    "    Get-ChildItem $HOME/.claude/skills/\n"
    "    Get-Content $HOME/.claude/settings.json\n"
    "    Przetestuj /state-start — powinien zapisać stan sesji.\n"
    "\n"
    "Na końcu powiedz jak stworzyć pierwszy projekt (/setup-new-project)\n"
    "i wytłumacz kiedy używać /state-start i /catchup.\n"
    "\n"
    "Pełny opis kroków: setup/onboarding-prompt.md"
)


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
    add_section_heading(doc, 'Czesc 1 — Zrob to sam  (6 krokow)')

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
    add_section_heading(doc, 'Czesc 2 — Tekst do wklejenia do Claude')

    instruction = doc.add_paragraph(
        'Znajdz swoj system ponizej. Zaznacz CALY tekst w niebieskiej ramce, '
        'skopiuj (Cmd+C na Macu / Ctrl+C na Windowsie) '
        'i wklej do czarnego okienka w Windsurf gdzie dziala Claude '
        '(Cmd+V na Macu / Ctrl+V na Windowsie). '
        'Nacisnij Enter. Claude zacznie rozmawiac z Toba i przeprowadzi Cie przez cala reszte.'
    )
    for r in instruction.runs:
        set_font(r, size=10)

    # Naglowek macOS
    mac_heading = doc.add_paragraph()
    mac_heading.paragraph_format.space_before = Pt(10)
    mac_heading.paragraph_format.space_after = Pt(4)
    r = mac_heading.add_run('Jesli masz Maca — skopiuj to:')
    set_font(r, bold=True, size=11, color=(60, 60, 60))

    add_prompt_block(doc, HANDOFF_PROMPT)

    # Naglowek Windows
    win_heading = doc.add_paragraph()
    win_heading.paragraph_format.space_before = Pt(12)
    win_heading.paragraph_format.space_after = Pt(4)
    r = win_heading.add_run('Jesli masz Windowsa — skopiuj to:')
    set_font(r, bold=True, size=11, color=(0, 84, 166))

    add_prompt_block(doc, WIN_HANDOFF_PROMPT)

    note = doc.add_paragraph(
        'Szczegolowy opis kazdego kroku konfiguracji: setup/onboarding-prompt.md'
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
