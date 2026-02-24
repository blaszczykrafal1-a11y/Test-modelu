# CLAUDE.md - Globalne preferencje

<!-- Skopiuj ten plik do ~/.claude/CLAUDE.md i wypełnij wszystkie [[...]] -->

## Preferencje pracy

- Język: [[polski / angielski / inny]]
- Ton: [[casual i bezpośredni / formalny / ...]]
- Autonomia: [[wysoka (nie pytaj o każdy krok) / standardowa]]
- Emojis: [[tak / nie]]
- Propozycje rozwiązań: [[powiedz wprost co byś wybrał i dlaczego / pytaj o preferencje]]

## Środowisko

- OS: [[np. macOS 15.7, Sequoia]], shell: [[zsh / bash]]
- Node.js: [[wersja i sposób zarządzania, np. v24 via nvm]]
- Python: [[ścieżka, np. /usr/bin/python3]]
- Git: [[ścieżka, np. /usr/bin/git]]
- Projekty: [[ścieżka bazowa, np. ~/Projects/]]

## Patterns

### Powiadomienia

Gdy user powie **"daj powiadomienie"** (lub "powiadom mnie", "notify me"):

```bash
osascript -e 'display alert "Claude Code" message "Zadanie zakończone - Claude czeka na Ciebie" giving up after 3' && afplay /System/Library/Sounds/Glass.aiff
```

- Tylko na wyraźne życzenie
- Alert modalny (omija DND), auto-dismiss po 3s

### Session state

Workflow resetu kontekstu:

```
/state-start → /clear → /exit → claude → /catchup
```

- `/state-start` — zapisz postęp do `session-state.md`
- `/clear` — wyczyść historię rozmowy
- `/exit` — zamknij Claude Code
- `claude` — uruchom ponownie (tokeny resetują się do baseline)
- `/catchup` — przywróć kontekst z `session-state.md`

Plik stanu: `.claude/session-state.md` w katalogu projektu.

### Skills

Każdy skill to folder, nie plik:
```
~/.claude/skills/
└── nazwa-skilla/
    └── SKILL.md    # definicja / prompt
```

### Projekty

Aktywne projekty. Aktualizuj gdy powstaje nowy lub zmieniają się powiązania.

| Projekt | Ścieżka | Opis | Powiązania |
|---------|---------|------|-----------|
| [[Nazwa projektu]] | [[~/Projects/NazwaProjektu/]] | [[Opis]] | — |

### Nowe projekty

Każdy nowy projekt = nowe prywatne repo na GitHubie. Workflow:

1. Duplikuj folder Template → zmień nazwę folderu
2. Otwórz w edytorze
3. Wywołaj `/setup-new-project` — skill sam wykrywa nazwę, tworzy repo na GitHubie, instaluje hook, robi initial commit + push
4. Wypełnij sekcje w `CLAUDE.md` (Project Overview, Team, Key Resources)

- GitHub username: [[GITHUB_USERNAME]]
- Projekty w: [[~/Projects/]]
- Repo: prywatne

## Placement Guide

### Gdzie trafia co

| Typ pliku | Gdzie trafia |
|-----------|-------------|
| Dokumenty od usera (PDF, DOCX, spec, notatki) | `docs/input/` |
| Dane osobowe / kontakty (CSV, XLSX) | **NIGDY do git** — ostrzeż usera |
| Pliki wygenerowane przez Claude (raporty, skrypty) | `docs/output/` |
| Dokumentacja API / narzędzi zewnętrznych | `system/instructions/` |
| Przetestowane snippety kodu | `system/reference/snippets.md` |
| Procedury wdrożeniowe / checklisty | `system/reference/deployment-checklist.md` |
| Mapa zależności / architektury | `system/reference/workflow-map.md` |
| Skrypty narzędziowe (git hooks, setup, automacje) | `system/scripts/` |
| Nowy skill specyficzny dla projektu | `.claude/skills/nazwa-skilla/` |
| Nowy skill globalny (multi-projekt) | `~/.claude/skills/nazwa-skilla/` |
| Wiedza przekrojowa (decyzje, anti-patterns) | `~/.claude/memory/temat.md` |

### Co robić gdy user dropuje nowy plik

1. Przeczytaj plik — zrozum co to jest
2. Dopasuj do tabeli powyżej
3. Jeśli niejasne — powiedz: "To wygląda jak [X], wrzucam do `docs/input/`?"
4. Jeśli to dane osobowe — STOP, ostrzeż że plik nie idzie do git

### Konwencje nazewnictwa

- Foldery: `kebab-case`
- Pliki markdown: `kebab-case.md` lub `UPPERCASE.md` (CLAUDE.md, SKILL.md, README.md)
- Skrypty: `kebab-case.sh` / `kebab-case.py`
- Pliki output: opisowa nazwa, np. `raport-outreach-2026-02.md`

## Bezpieczeństwo

### Aktywna ochrona

Dwie warstwy ochrony działają automatycznie:
1. **Claude Code PreToolUse hook** (`~/.claude/hooks/security-scan.py`) — skanuje content przed każdym Write/Edit/Bash
2. **Git pre-commit hook** (`system/scripts/pre-commit.sh`) — blokuje commit z sekretami

### Reguły behawioralne dla Claude

**ZAWSZE sprawdzaj przed zapisem:**
- Czy content zawiera API keys (wzorzec `sk-...`, `AIza...`, `Bearer ...`)
- Czy content zawiera connection stringi z hasłem
- Czy piszesz do pliku `.xlsx`/`.csv`/`.env`

**NIGDY nie rób:**
- Nie commituj plików z `docs/input/` bez wyraźnej zgody usera
- Nie uruchamiaj `git add .` lub `git add -A` bez sprawdzenia co jest staged

**Przed każdym git commit:**
1. Pokaż listę staged files
2. Upewnij się że nie ma `*.xlsx`, `*.csv`, `.env` na liście

## Git — automatyczne commity

Po każdym większym feature commituj bez pytania.

Format: `[kategoria] krótki opis`

Kategorie: `feat` / `fix` / `refactor` / `docs` / `style` / `test` / `chore`
