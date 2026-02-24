#!/usr/bin/env python3
"""
Generuje docs/output/onboarding.docx — interaktywny dokument onboardingowy
z klikalnymi checkboxami (legacy form fields) dla Microsoft Word.

Uruchomienie:
    python3 system/scripts/generate-onboarding-docx.py

Wymagania:
    pip3 install python-docx
"""

import subprocess
import sys
import os

# Zainstaluj python-docx jeśli brakuje
try:
    from docx import Document
except ImportError:
    print("Instaluję python-docx...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
    from docx import Document

from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH


# ── Helpers ──────────────────────────────────────────────────────────────────

def add_formcheckbox(paragraph):
    """Dodaje klikalny checkbox (legacy FORMCHECKBOX) do akapitu."""
    run = paragraph.add_run()

    fldChar_begin = OxmlElement('w:fldChar')
    fldChar_begin.set(qn('w:fldCharType'), 'begin')

    ffData = OxmlElement('w:ffData')

    name_el = OxmlElement('w:name')
    name_el.set(qn('w:val'), '')
    ffData.append(name_el)

    enabled_el = OxmlElement('w:enabled')
    ffData.append(enabled_el)

    calcOnExit_el = OxmlElement('w:calcOnExit')
    calcOnExit_el.set(qn('w:val'), '0')
    ffData.append(calcOnExit_el)

    checkBox_el = OxmlElement('w:checkBox')
    sizeAuto_el = OxmlElement('w:sizeAuto')
    checkBox_el.append(sizeAuto_el)
    default_el = OxmlElement('w:default')
    default_el.set(qn('w:val'), '0')
    checkBox_el.append(default_el)
    checked_el = OxmlElement('w:checked')
    checked_el.set(qn('w:val'), '0')
    checkBox_el.append(checked_el)
    ffData.append(checkBox_el)

    fldChar_begin.append(ffData)
    run._r.append(fldChar_begin)

    run2 = paragraph.add_run()
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = ' FORMCHECKBOX '
    run2._r.append(instrText)

    run3 = paragraph.add_run()
    fldChar_sep = OxmlElement('w:fldChar')
    fldChar_sep.set(qn('w:fldCharType'), 'separate')
    run3._r.append(fldChar_sep)

    run4 = paragraph.add_run()
    fldChar_end = OxmlElement('w:fldChar')
    fldChar_end.set(qn('w:fldCharType'), 'end')
    run4._r.append(fldChar_end)


def set_font(run, name='Calibri', size=11, bold=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_step(doc, number, title, description, commands=None):
    """
    Dodaje krok z checkboxem.
    commands: lista stringów (komendy do wyświetlenia w bloku kodu)
    """
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(10)
    para.paragraph_format.space_after = Pt(2)
    para.paragraph_format.left_indent = Cm(0)

    # Checkbox
    add_formcheckbox(para)

    # Spacja po checkboxie
    space_run = para.add_run('  ')
    space_run.font.size = Pt(11)

    # Numer + tytuł
    title_run = para.add_run(f'Krok {number} — {title}')
    set_font(title_run, bold=True, size=12)

    # Opis
    if description:
        desc_para = doc.add_paragraph(description)
        desc_para.paragraph_format.left_indent = Cm(1.2)
        desc_para.paragraph_format.space_before = Pt(2)
        desc_para.paragraph_format.space_after = Pt(2)
        for run in desc_para.runs:
            set_font(run, size=10, color=(80, 80, 80))

    # Blok kodu
    if commands:
        for cmd in commands:
            code_para = doc.add_paragraph()
            code_para.paragraph_format.left_indent = Cm(1.2)
            code_para.paragraph_format.space_before = Pt(1)
            code_para.paragraph_format.space_after = Pt(1)

            # Szare tło przez shading XML
            pPr = code_para._p.get_or_add_pPr()
            shd = OxmlElement('w:shd')
            shd.set(qn('w:val'), 'clear')
            shd.set(qn('w:color'), 'auto')
            shd.set(qn('w:fill'), 'F0F0F0')
            pPr.append(shd)

            code_run = code_para.add_run(cmd)
            set_font(code_run, name='Courier New', size=9)


def add_section_heading(doc, text):
    """Dodaje nagłówek sekcji."""
    doc.add_paragraph()
    heading = doc.add_paragraph()
    heading.paragraph_format.space_before = Pt(16)
    heading.paragraph_format.space_after = Pt(6)
    run = heading.add_run(text)
    set_font(run, bold=True, size=14, color=(31, 73, 125))

    # Linia pod nagłówkiem (border bottom)
    pPr = heading._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '1F497D')
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_prompt_block(doc, prompt_text):
    """Dodaje blok z promptem do skopiowania."""
    para = doc.add_paragraph()
    para.paragraph_format.left_indent = Cm(0.5)
    para.paragraph_format.right_indent = Cm(0.5)
    para.paragraph_format.space_before = Pt(6)
    para.paragraph_format.space_after = Pt(6)

    pPr = para._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'EFF3FB')
    pPr.append(shd)

    # Ramka
    pBdr = OxmlElement('w:pBdr')
    for side in ['top', 'bottom', 'left', 'right']:
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '4')
        el.set(qn('w:space'), '4')
        el.set(qn('w:color'), '4472C4')
        pBdr.append(el)
    pPr.append(pBdr)

    run = para.add_run(prompt_text)
    set_font(run, name='Courier New', size=8)


# ── Treść dokumentu ──────────────────────────────────────────────────────────

STEPS = [
    {
        'title': 'Pobierz i zainstaluj Windsurf',
        'description': (
            'Windsurf to program, w którym będziesz pracować z asystentem AI. '
            'Wejdź na poniższą stronę, pobierz plik instalacyjny i zainstaluj '
            'go tak jak każdy inny program na Macu (kliknij, przeciągnij do Applications).'
        ),
        'commands': ['windsurf.com/download'],
    },
    {
        'title': 'Pobierz i zainstaluj Node.js',
        'description': (
            'Node.js to silnik, którego Claude potrzebuje żeby w ogóle ruszyć. '
            'Wejdź na stronę poniżej, kliknij zielony przycisk "LTS" i zainstaluj '
            'pobrany plik tak jak poprzednio.'
        ),
        'commands': ['nodejs.org  →  kliknij zielony przycisk LTS'],
    },
    {
        'title': 'Otwórz Windsurf i wpisz jedną komendę',
        'description': (
            'Uruchom Windsurf. Na dole ekranu zobaczysz czarne okienko — to "terminal", '
            'miejsce gdzie wpisujesz polecenia. Kliknij w to okienko, wpisz poniższe '
            'i naciśnij Enter. Poczekaj aż skończy (może chwilę potrwać).'
        ),
        'commands': ['npm install -g @anthropic-ai/claude-code'],
    },
    {
        'title': 'Otwórz folder Onboarding w Windsurf',
        'description': (
            'W Windsurf kliknij u góry: File → Open Folder, '
            'a potem wskaż folder Onboarding — ten, który właśnie masz.'
        ),
        'commands': None,
    },
    {
        'title': 'Uruchom Claude i zaloguj się',
        'description': (
            'W czarnym okienku (terminal) wpisz claude i naciśnij Enter. '
            'Otworzy się przeglądarka — zaloguj się przez swoje konto Anthropic. '
            'Wróć do Windsurf. Claude czeka na Ciebie w terminalu.'
        ),
        'commands': ['claude'],
    },
    {
        'title': 'Wklej prompt z Części 2 — i gotowe!',
        'description': (
            'To ostatni krok który robisz sam. Skopiuj cały tekst z niebieskiej ramki '
            'na następnej stronie, wklej go do terminala w Windsurf (Ctrl+V lub kliknij prawym → Paste) '
            'i naciśnij Enter. Od tej chwili Claude przejmuje stery i przeprowadza Cię '
            'przez całą resztę krok po kroku.'
        ),
        'commands': None,
    },
]

# Treść prompta — Claude ogarnie resztę instalacji i całą konfigurację
HANDOFF_PROMPT = """\
Przeprowadź mnie przez konfigurację środowiska Claude Code.

Jestem nowym użytkownikiem. Właśnie zainstalowałem Windsurf i Claude Code CLI,
jestem zalogowany. Pracuję w folderze Onboarding — zawiera podfolder setup/
z gotowymi plikami do skopiowania.

Zasady dla każdego kroku:
- Tłumacz prosto, bez żargonu technicznego — jakbyś mówił do osoby która
  nigdy nie programowała
- Podawaj JEDNĄ komendę na raz
- Czekaj aż powiem "gotowe" zanim przejdziesz do następnego kroku
- Po każdym kroku sprawdź czy zadziałało

CZĘŚĆ A — Instalacja brakujących narzędzi

1. Sprawdź czy mam Homebrew (brew --version). Jeśli nie — zainstaluj.
   (Homebrew to sklep z narzędziami dla Maca, będzie potrzebny za chwilę)
2. Zainstaluj gh i jq: brew install gh jq
   (gh = logowanie do GitHub, jq = pomocnik do plików konfiguracyjnych)
3. Zaloguj mnie do GitHub: gh auth login
   Wybierz: GitHub.com → HTTPS → zaloguj przez przeglądarkę

CZĘŚĆ B — Konfiguracja Claude

4. Utwórz foldery: ~/.claude/skills/  ~/.claude/hooks/  ~/.claude/memory/
5. Skopiuj skille z setup/skills/ do ~/.claude/skills/
   (state-start, catchup, setup-new-project)
6. Skopiuj security hook: setup/hooks/security-scan.py → ~/.claude/hooks/ + chmod +x
7. Skopiuj status line: setup/statusline-command.sh → ~/.claude/ + chmod +x
8. Wygeneruj ~/.claude/settings.json z konfiguracją hooka i status line
   (użyj $HOME zamiast ~ przy ścieżkach — to ważne)
9. Zapytaj mnie o:
   - język pracy z AI (np. polski / angielski)
   - mój GitHub username
   - gdzie trzymam projekty (np. ~/Projects/)
   Skopiuj setup/global-claude-template.md → ~/.claude/CLAUDE.md
   i zastąp wszystkie znaczniki [[...]] moimi danymi
10. W ~/.claude/skills/setup-new-project/SKILL.md zamień GITHUB_USERNAME
    na mój GitHub username
11. Weryfikacja: pokaż listę plików, wyświetl settings.json, przetestuj /state-start

Na końcu powiedz mi jak stworzyć swój pierwszy projekt korzystając z tego folderu
jako szablonu i jak uruchomić /setup-new-project.

Pełny opis każdego kroku znajdziesz w: setup/onboarding-prompt.md\
"""


# ── Generowanie dokumentu ────────────────────────────────────────────────────

def generate():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_path = os.path.join(project_root, 'docs', 'output', 'onboarding.docx')

    doc = Document()

    # Marginesy
    section = doc.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # Tytuł
    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_para.paragraph_format.space_after = Pt(4)
    title_run = title_para.add_run('Onboarding — Claude Code w Windsurf')
    set_font(title_run, bold=True, size=20, color=(31, 73, 125))

    # Podtytuł
    sub_para = doc.add_paragraph()
    sub_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_para.paragraph_format.space_after = Pt(16)
    sub_run = sub_para.add_run('Instrukcja startowa · macOS')
    set_font(sub_run, size=11, color=(128, 128, 128))

    # Intro
    intro = doc.add_paragraph(
        'Masz przed sobą 6 kroków. Pierwsze 5 robisz sam — to proste rzeczy: '
        'pobranie programów i wpisanie jednej komendy. W kroku 6 wklejasz gotowy tekst '
        'do Claude i od tej chwili asystent AI przeprowadza Cię przez wszystko sam.'
    )
    intro.paragraph_format.space_after = Pt(4)
    for run in intro.runs:
        set_font(run, size=10)

    # ── Część 1: Instalacja ──
    add_section_heading(doc, 'Część 1 — Zrób to sam  (6 prostych kroków)')

    for i, step in enumerate(STEPS, start=1):
        add_step(
            doc,
            number=i,
            title=step['title'],
            description=step['description'],
            commands=step.get('commands'),
        )

    # ── Część 2: Prompt dla Claude ──
    doc.add_page_break()

    add_section_heading(doc, 'Część 2 — Tekst do wklejenia do Claude')

    instruction = doc.add_paragraph(
        'Zaznacz cały tekst w niebieskiej ramce poniżej (kliknij i Ctrl+A lub zaznacz myszką), '
        'skopiuj (Ctrl+C), a potem wklej do czarnego okienka w Windsurf gdzie działa Claude '
        '(Ctrl+V lub kliknij prawym → Paste). Naciśnij Enter. '
        'Claude zacznie rozmawiać z Tobą i przeprowadzi Cię przez całą resztę konfiguracji — '
        'krok po kroku, po polsku.'
    )
    for run in instruction.runs:
        set_font(run, size=10)

    doc.add_paragraph()
    add_prompt_block(doc, HANDOFF_PROMPT)

    note = doc.add_paragraph(
        'Szczegółowy opis każdego kroku konfiguracji: setup/onboarding-prompt.md'
    )
    note.paragraph_format.space_before = Pt(6)
    for run in note.runs:
        set_font(run, size=9, color=(128, 128, 128))

    # Zapis
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    print(f'Zapisano: {output_path}')


if __name__ == '__main__':
    generate()
