# CLAUDE.md - PROJECT_NAME

## Project Overview

<!-- Opisz projekt: cel, kontekst, dla kogo, jakie narzędzia -->

## Team

<!-- Kto pracuje: role, uprawnienia, kontakty -->

## Project Structure

```
PROJECT_NAME/
├── CLAUDE.md
├── .claude/
│   ├── session-state.md
│   └── skills/              # Project-specific skills
├── docs/
│   ├── input/               # Pliki kontekstowe od usera (nie commituj danych klientów)
│   └── output/              # Pliki wygenerowane przez Claude
└── system/
    ├── instructions/        # Dokumentacja narzędzi/API
    ├── reference/           # Wiedza projektowa: snippety, checklisty, mapy
    └── scripts/             # Skrypty narzędziowe
```

## Key Resources

<!-- Linki, ID, endpointy, credentials (tylko nazwy — nie wklejaj wartości) -->

## Docs Folder

### `docs/input/`
Pliki wrzucone przez usera jako kontekst — specyfikacje, dane, screenshoty, opisy wymagań.
Przeczytaj **przed** rozpoczęciem zadania gdy pliki są obecne.

### `docs/output/`
Pliki wygenerowane przez Claude — gotowe do użycia. Po zakończeniu zadania które produkuje plik — zapisz tutaj i poinformuj usera o nazwie.

### `system/reference/`
- `snippets.md` — przetestowane fragmenty kodu, copy-paste ready
- `deployment-checklist.md` — checklist wdrożenia u klienta / na nowym środowisku
- `workflow-map.md` — mapa zależności między procesami i shared resources

## User Notifications

Gdy user powie **"daj powiadomienie"** (lub "powiadom mnie"):

```bash
osascript -e 'display alert "Claude Code" message "Zadanie zakończone - Claude czeka na Ciebie" giving up after 3' && afplay /System/Library/Sounds/Glass.aiff
```

Tylko na wyraźne życzenie — user pracuje w Focus mode.

## Session State

Workflow resetu kontekstu:
```
/state-start → /clear → /exit → claude → /catchup
```

Plik: `.claude/session-state.md`

## Git Backup

**Po każdym większym feature — commituj automatycznie bez pytania.**

Format: `[kategoria] krótki opis`

Kategorie: `feat` / `fix` / `refactor` / `docs` / `style` / `test` / `chore`

**Przed commitem:**
1. Pokaż staged files
2. Upewnij się że nie ma `*.xlsx`, `*.csv`, `.env` na liście

**Remote:** <!-- dodaj URL repo po /setup-new-project -->

## Notes

<!-- Decyzje techniczne, konwencje, ograniczenia, anti-patterns -->
