#!/usr/bin/env python3
"""
Generuje docs/output/onboarding.docx — interaktywny dokument onboardingowy
z klikalnymi checkboxami i obrazkami.

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
        # Bierzemy górne ~60% ekranu (tam jest przeglądarka) i skalujemy.
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
    Tworzy mockup okienka terminala z podanymi liniami tekstu.
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
                # Output (odpowiedź systemu)
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
    Tworzy uproszczony mockup Windsurf pokazujący gdzie jest terminal.
    """
    try:
        font = get_font(12)
        font_sm = get_font(10)
        font_bold = get_font(14)

        height = 300
        editor_split = 175  # gdzie kończy się edytor, a zaczyna terminal

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

        # Podkreślenie "TERMINAL"
        draw.rectangle([(10, editor_split + 20), (72, editor_split + 22)],
                        fill=(80, 180, 255))

        draw.rectangle([(0, editor_split + 22), (width, height)], fill=(28, 28, 28))
        draw.text((10, editor_split + 30), "pablo@Mac Onboarding %",
                  font=get_mono_font(12), fill=(80, 200, 120))
        draw.rectangle([(10, editor_split + 54), (18, editor_split + 68)],
                        fill=(200, 200, 200))

        # ── Strzałka i opis ──
        ax = width - 20
        ay = editor_split + 55
        # strzałka ← wskazująca na terminal
        draw.polygon([(ax - 30, ay), (ax, ay - 14), (ax, ay + 14)],
                      fill=(255, 60, 60))
        draw.rectangle([(ax - 100, ay - 7), (ax - 30, ay + 7)], fill=(255, 60, 60))
        draw.text((ax - 190, ay - 26), "Tu wpisuj", font=font_bold, fill=(255, 60, 60))
        draw.text((ax - 190, ay - 8), "komendy!", font=font, fill=(255, 60, 60))

        # ── Legenda: Menu Terminal → New Terminal ──
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


def add_step(doc, number, title, description, sub_steps=None,
             image_path=None, image_caption=None):
    """
    Dodaje krok z checkboxem, opisem, pod-punktami i opcjonalnym obrazkiem.
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

    # ── Pod-punkty (szczegółowe instrukcje) ──
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

    # ── Obrazek ──
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

    # ── Podpis obrazka ──
    if image_caption:
        cap = doc.add_paragraph(f'  {image_caption}')
        cap.paragraph_format.left_indent = Cm(1.2)
        cap.paragraph_format.space_before = Pt(2)
        cap.paragraph_format.space_after = Pt(6)
        for r in cap.runs:
            set_font(r, size=9, italic=True, color=(100, 100, 100))


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


# ── Treść: kroki ─────────────────────────────────────────────────────────────

def build_steps(tmp_dir):
    """
    Buduje listę kroków. tmp_dir to folder na tymczasowe obrazki.
    Generuje screenshoty i mockupy.
    """

    print("\nPrzygotowuję obrazki...")

    # Krok 1 — Windsurf (screenshot)
    ss_windsurf = take_screenshot_of_url('https://windsurf.com/download', wait=7)
    if ss_windsurf:
        ss_windsurf = annotate_image(ss_windsurf,
            '→ Kliknij przycisk pobierania dla Mac (Download for macOS / Mac)')
        close_browser_tabs()

    # Krok 2 — Node.js (screenshot)
    ss_nodejs = take_screenshot_of_url('https://nodejs.org', wait=6)
    if ss_nodejs:
        ss_nodejs = annotate_image(ss_nodejs,
            '→ Kliknij ZIELONY przycisk "Download Node.js (LTS)" — to ten po lewej stronie')
        close_browser_tabs()

    # Krok 3 — mockup Windsurf IDE (gdzie jest terminal)
    img_windsurf_ide = create_windsurf_ide_mockup()

    # Krok 3 — mockup terminala z komendą
    img_npm = create_terminal_mockup([
        'npm install -g @anthropic-ai/claude-code',
        '>>> added 127 packages in 45s',
        '>>> (instalacja zakończona, może chwilę potrwać)',
    ])

    # Krok 5 — mockup terminala z claude
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
                'Musisz go zainstalować jak każdy inny program na Macu.'
            ),
            'sub_steps': [
                'Otwórz przeglądarkę na Macu (Safari, Chrome — cokolwiek masz).',
                'W pasku adresu u góry wpisz: windsurf.com  i naciśnij Enter.',
                'Na stronie zobaczysz przycisk do pobierania — kliknij go '
                '(może się nazywać "Download for macOS" lub "Download for Mac").',
                'Poczekaj chwilę — plik pobierze się do folderu Pobrane (Downloads). '
                'Zobaczysz go na dole okna przeglądarki lub w Finderze → Pobrane.',
                'Kliknij dwukrotnie na pobrany plik (kończy się na .dmg).',
                'Pojawi się okienko — przeciągnij ikonę Windsurf do folderu Applications.',
                'Poczekaj aż się skopiuje i zamknij to okienko.',
                'Otwórz Windsurf: kliknij ikonę rakiety w Docku (Launchpad) '
                'lub naciśnij Cmd+Spacja, wpisz "Windsurf" i kliknij.',
            ],
            'image_path': ss_windsurf,
            'image_caption': 'Tak wygląda strona Windsurf — kliknij duży przycisk pobierania.',
        },
        {
            'title': 'Zainstaluj Node.js',
            'description': (
                'Node.js to silnik, bez którego Claude nie uruchomi się. '
                'Instaluje się jak każdy normalny program — kilka kliknięć.'
            ),
            'sub_steps': [
                'Otwórz przeglądarkę (albo użyj tej samej co przed chwilą).',
                'Wejdź na stronę: nodejs.org',
                'Zobaczysz dwa przyciski. Kliknij ten zielony — '
                'ma napis "Download Node.js (LTS)" i podpis "Recommended for most users". '
                'NIE klikaj drugiego (Current).',
                'Plik .pkg pobierze się — poczekaj aż skończy.',
                'Otwórz pobrany plik (kliknij dwukrotnie).',
                'Pojawi się instalator. Klikaj "Kontynuuj" (Continue) '
                'przez każdy ekran — nie musisz nic zmieniać.',
                'Na końcu kliknij "Zainstaluj" (Install). '
                'Mac może zapytać o hasło — wpisz swoje hasło do komputera.',
                'Gotowe! Możesz zamknąć instalator.',
            ],
            'image_path': ss_nodejs,
            'image_caption': 'Strona nodejs.org — kliknij zielony przycisk LTS (ten po lewej).',
        },
        {
            'title': 'Otwórz terminal w Windsurf i wpisz jedną komendę',
            'description': (
                'Terminal to czarne okienko, w którym wpisujesz polecenia. '
                'W Windsurf jest ukryte na dole ekranu — pokażemy Ci jak je otworzyć.'
            ),
            'sub_steps': [
                'Uruchom Windsurf (jeśli jeszcze nie jest otwarty).',
                'W górnym menu kliknij "Terminal" a potem "New Terminal". '
                'Ewentualnie naciśnij klawisze Ctrl + ` '
                '(tylni apostrof — klawisz obok cyfry 1 na klawiaturze).',
                'Na dole ekranu pojawi się ciemne okienko z kursorem — to terminal.',
                'Kliknij w to ciemne okienko żeby je zaznaczyć.',
                'Wpisz poniższą komendę i naciśnij Enter. '
                'Poczekaj — może trwać 1-3 minuty (coś się będzie instalować).',
                'Gdy skończy, w terminalu pojawi się nowa linia z kursorem — to znak że gotowe.',
            ],
            'image_path': img_windsurf_ide,
            'image_caption': 'Windsurf — Terminal otworzysz przez menu Terminal → New Terminal.',
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
                'Po lewej stronie Windsurf pojawi się lista plików z folderu Onboarding — to znak że zadziałało.',
            ],
            'image_path': None,
            'image_caption': None,
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
                'Claude może zapytać o zgodę — jeśli zobaczysz pytanie, wpisz Y i Enter.',
                'Automatycznie otworzy się przeglądarka z prośbą o zalogowanie.',
                'Zaloguj się przez swoje konto Anthropic (lub utwórz konto jeśli nie masz).',
                'Wróć do Windsurf — w terminalu zobaczysz że Claude czeka na Twój tekst. '
                'Zobaczysz coś w stylu: "Claude Code > "',
            ],
            'image_path': img_claude,
            'image_caption': 'Tak wygląda uruchomiony Claude w terminalu Windsurf.',
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
                'Zaznacz CAŁY tekst z niebieskiej ramki '
                '(kliknij na początku, potem Shift+kliknij na końcu ramki).',
                'Skopiuj: Cmd+C (lub kliknij prawym przyciskiem → Kopiuj).',
                'Wróć do Windsurf i kliknij w ciemne okienko terminala.',
                'Wklej: Cmd+V (lub kliknij prawym → Wklej).',
                'Naciśnij Enter.',
                'Claude zacznie pisać do Ciebie i przeprowadzi Cię przez każdy następny krok. '
                'Wystarczy że będziesz odpowiadać "gotowe" gdy skończysz każdy krok.',
            ],
            'image_path': None,
            'image_caption': None,
        },
    ]

    return steps


# ── Prompt handoff ────────────────────────────────────────────────────────────

HANDOFF_PROMPT = """\
Przeprowadź mnie przez konfigurację środowiska Claude Code.

Jestem nowym użytkownikiem. Właśnie zainstalowałem Windsurf i Claude Code CLI,
jestem zalogowany. Pracuję w folderze Onboarding — zawiera podfolder setup/
z gotowymi plikami do skopiowania.

Zasady dla każdego kroku:
- Tłumacz prosto, bez żargonu technicznego — jakbyś mówił do osoby która
  nigdy nie programowała
- Podawaj JEDNĄ komendę lub akcję na raz
- Czekaj aż powiem "gotowe" zanim przejdziesz do następnego kroku
- Po każdym kroku sprawdź czy zadziałało
- Jeśli coś się nie uda — pomóż mi to naprawić zanim pójdziemy dalej

CZĘŚĆ A — Instalacja brakujących narzędzi

1. Sprawdź czy mam Homebrew: brew --version
   Jeśli nie ma — zainstaluj. (Homebrew to sklep z narzędziami dla Maca)
2. Zainstaluj gh i jq: brew install gh jq
   (gh = do łączenia z GitHub, jq = pomocnik konfiguracyjny)
3. Zaloguj mnie do GitHub: gh auth login
   Wybierz: GitHub.com → HTTPS → zaloguj przez przeglądarkę

CZĘŚĆ B — Konfiguracja Claude

4. Utwórz foldery: ~/.claude/skills/  ~/.claude/hooks/  ~/.claude/memory/
5. Skopiuj skille z setup/skills/ do ~/.claude/skills/
   (state-start, catchup, setup-new-project)
6. Skopiuj hook bezpieczeństwa: setup/hooks/security-scan.py → ~/.claude/hooks/
   Nadaj uprawnienia: chmod +x
7. Skopiuj status bar: setup/statusline-command.sh → ~/.claude/
   Nadaj uprawnienia: chmod +x
8. Wygeneruj plik konfiguracyjny ~/.claude/settings.json
   z ustawieniami hooka i status baru (użyj $HOME zamiast ~ przy ścieżkach)
9. Zapytaj mnie o:
   - w jakim języku chcę rozmawiać z AI (np. polski)
   - mój GitHub username
   - gdzie trzymam foldery projektów (np. ~/Projects/)
   Potem skopiuj setup/global-claude-template.md → ~/.claude/CLAUDE.md
   i uzupełnij moje dane w miejscach oznaczonych [[...]]
10. W pliku ~/.claude/skills/setup-new-project/SKILL.md
    zamień GITHUB_USERNAME na mój GitHub username
11. Weryfikacja końcowa: sprawdź że wszystkie pliki istnieją,
    pokaż zawartość settings.json, przetestuj komendę /state-start

Na końcu wytłumacz mi jak stworzyć swój pierwszy projekt:
- jak skopiować folder Onboarding jako szablon
- jak uruchomić /setup-new-project żeby stworzyć repo na GitHub

Pełny opis każdego kroku: setup/onboarding-prompt.md\
"""


# ── Generowanie dokumentu ─────────────────────────────────────────────────────

def generate():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_path = os.path.join(project_root, 'docs', 'output', 'onboarding.docx')

    tmp_dir = tempfile.mkdtemp()

    print("Generuję onboarding.docx...")
    steps = build_steps(tmp_dir)

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # ── Tytuł ──
    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_para.paragraph_format.space_after = Pt(4)
    r = title_para.add_run('Onboarding — Claude Code w Windsurf')
    set_font(r, bold=True, size=20, color=(31, 73, 125))

    sub_para = doc.add_paragraph()
    sub_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_para.paragraph_format.space_after = Pt(14)
    r = sub_para.add_run('Instrukcja startowa · macOS')
    set_font(r, size=11, color=(128, 128, 128))

    intro = doc.add_paragraph(
        'Masz przed sobą 6 prostych kroków. Nie musisz wiedzieć nic o programowaniu — '
        'wystarczy klikać i wpisywać dokładnie to co widzisz. '
        'Po 6. kroku Claude (asystent AI) przejmuje i prowadzi Cię przez resztę po polsku.'
    )
    intro.paragraph_format.space_after = Pt(6)
    for r in intro.runs:
        set_font(r, size=10)

    # ── Część 1: Kroki ──
    add_section_heading(doc, 'Część 1 — Zrób to sam  (6 kroków)')

    for i, step in enumerate(steps, start=1):
        add_step(
            doc,
            number=i,
            title=step['title'],
            description=step['description'],
            sub_steps=step.get('sub_steps'),
            image_path=step.get('image_path'),
            image_caption=step.get('image_caption'),
        )

    # ── Część 2: Prompt ──
    doc.add_page_break()
    add_section_heading(doc, 'Część 2 — Tekst do wklejenia do Claude')

    instruction = doc.add_paragraph(
        'Zaznacz cały tekst w niebieskiej ramce poniżej, skopiuj (Cmd+C) '
        'i wklej do czarnego okienka w Windsurf gdzie działa Claude (Cmd+V). '
        'Naciśnij Enter. Claude zacznie rozmawiać z Tobą i przeprowadzi Cię przez całą resztę.'
    )
    for r in instruction.runs:
        set_font(r, size=10)

    doc.add_paragraph()
    add_prompt_block(doc, HANDOFF_PROMPT)

    note = doc.add_paragraph(
        'Szczegółowy opis każdego kroku konfiguracji: setup/onboarding-prompt.md'
    )
    note.paragraph_format.space_before = Pt(6)
    for r in note.runs:
        set_font(r, size=9, color=(128, 128, 128))

    # ── Zapis ──
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    print(f'\nZapisano: {output_path}')

    # Informacja o screenshotach
    if TAKE_SCREENSHOTS:
        print('\nUwaga: screenshoty zostały zrobione przy użyciu aktualnych stron internetowych.')
        print('Jeśli strony wyglądają inaczej niż w dokumencie — to normalne, strony się aktualizują.')


if __name__ == '__main__':
    generate()
