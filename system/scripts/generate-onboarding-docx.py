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
        'description': 'Windsurf to edytor kodu (IDE). Pobierz instalator, uruchom i zainstaluj.',
        'commands': ['https://windsurf.com/download'],
    },
    {
        'title': 'Zainstaluj nvm i Node.js',
        'description': 'nvm to menedżer wersji Node.js. Uruchom w terminalu systemowym (nie w Windsurf). Po instalacji ZAMKNIJ terminal i otwórz ponownie.',
        'commands': [
            'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash',
            '# Po ponownym otwarciu terminala:',
            'nvm install --lts',
            'node --version    # powinien pokazać v22.x.x lub wyżej',
        ],
    },
    {
        'title': 'Zainstaluj Homebrew',
        'description': 'Homebrew to menedżer pakietów dla macOS. Potrzebny do instalacji gh i jq.',
        'commands': [
            '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        ],
    },
    {
        'title': 'Zainstaluj gh i jq',
        'description': 'gh = GitHub CLI (tworzenie repozytoriów). jq = narzędzie do JSON (status line Claude).',
        'commands': ['brew install gh jq'],
    },
    {
        'title': 'Zainstaluj Claude Code CLI',
        'description': 'Claude Code to asystent AI działający w terminalu. Instalacja przez npm.',
        'commands': ['npm install -g @anthropic-ai/claude-code'],
    },
    {
        'title': 'Otwórz folder Onboarding w Windsurf',
        'description': 'W Windsurf: File → Open Folder → wybierz folder Onboarding (ten który właśnie czytasz).',
        'commands': None,
    },
    {
        'title': 'Uruchom Claude Code i zaloguj się',
        'description': 'Otwórz terminal w Windsurf: Ctrl+` (backtick). Uruchom claude — otworzy przeglądarkę do logowania przez konto Anthropic.',
        'commands': ['claude'],
    },
    {
        'title': 'Zaloguj się do GitHub CLI',
        'description': 'Potrzebne do tworzenia repozytoriów przez /setup-new-project. Wybierz: GitHub.com → HTTPS → zaloguj przez przeglądarkę.',
        'commands': ['gh auth login'],
    },
    {
        'title': 'Wklej prompt do Claude — resztą zajmie się AI',
        'description': 'Skopiuj prompt z Części 2 poniżej i wklej go do terminala Windsurf gdzie działa Claude. Claude przeprowadzi Cię przez całą konfigurację.',
        'commands': None,
    },
]

# Treść prompta (skrócona wersja do dokumentu)
HANDOFF_PROMPT = """\
Przeprowadź mnie przez konfigurację środowiska Claude Code.

Jestem nowym użytkownikiem. Właśnie zainstalowałem Windsurf i Claude Code CLI,
jestem zalogowany i pracuję w folderze Onboarding który zawiera setup/ z plikami
do skopiowania.

Przeprowadź mnie kolejno przez każdy krok. Na każdym kroku:
- wyjaśnij krótko co robimy i dlaczego
- podaj dokładną komendę
- poczekaj aż powiem "gotowe" zanim przejdziesz dalej
- sprawdź że krok się powiódł

Kroki:
1. Utwórz strukturę ~/.claude/skills/, ~/.claude/hooks/, ~/.claude/memory/
2. Skopiuj foldery setup/skills/ do ~/.claude/skills/ (state-start, catchup, setup-new-project)
3. Skopiuj setup/hooks/security-scan.py do ~/.claude/hooks/ i chmod +x
4. Skopiuj setup/statusline-command.sh do ~/.claude/ i chmod +x
5. Wygeneruj ~/.claude/settings.json z konfiguracją hooka i status line (użyj $HOME)
6. Zapytaj mnie o: język pracy z AI, GitHub username, ścieżkę do projektów.
   Skopiuj setup/global-claude-template.md do ~/.claude/CLAUDE.md i wypełnij wartości.
7. W ~/.claude/skills/setup-new-project/SKILL.md zamień GITHUB_USERNAME na mój username.
8. Zweryfikuj setup: sprawdź pliki, cat ~/.claude/settings.json, test /state-start.

Na końcu powiedz jak skopiować folder Onboarding jako template dla pierwszego projektu
i uruchomić /setup-new-project.

Pełny prompt z opisem kroków: setup/onboarding-prompt.md\
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
        'Ten dokument przeprowadza przez instalację środowiska pracy z Claude Code. '
        'Część 1 to kroki ręczne — wykonaj je samodzielnie. Po dotarciu do Kroku 9 '
        'przekazujesz sterowanie Claude, który przeprowadzi Cię przez resztę konfiguracji.'
    )
    intro.paragraph_format.space_after = Pt(4)
    for run in intro.runs:
        set_font(run, size=10)

    # ── Część 1: Instalacja ──
    add_section_heading(doc, 'Część 1 — Instalacja  (wykonaj ręcznie)')

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

    add_section_heading(doc, 'Część 2 — Prompt dla Claude')

    instruction = doc.add_paragraph(
        'Skopiuj poniższy prompt i wklej do terminala Windsurf gdzie działa Claude Code '
        '(Ctrl+V lub kliknij prawym → Paste). Od tego momentu Claude przeprowadza Cię '
        'przez całą konfigurację interaktywnie.'
    )
    for run in instruction.runs:
        set_font(run, size=10)

    doc.add_paragraph()
    add_prompt_block(doc, HANDOFF_PROMPT)

    note = doc.add_paragraph(
        'Pełna wersja prompta z opisem każdego kroku: setup/onboarding-prompt.md'
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
