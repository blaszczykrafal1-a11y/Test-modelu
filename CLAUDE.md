# CLAUDE.md - Onboarding

## Project Overview

Folder onboardingowy dla nowych osób dołączających do środowiska Claude Code.
Zawiera kompletną instrukcję setup krok po kroku (`ONBOARDING.md`), gotowe pliki
do skopiowania (`setup/`) oraz checklistę weryfikacyjną (`CHECKLIST.md`).

Nie wymaga n8n. Pokrywa: Claude Code CLI, globalna konfiguracja (`~/.claude/`),
skille (state-start, catchup, setup-new-project), security hook, status line,
Template projektowy.

## Project Structure

```
PROJECT_NAME/
├── CLAUDE.md                          # Ten plik - instrukcje dla Claude
├── .claude/
│   ├── session-state.md               # Stan sesji (aktualizuj przed /clear)
│   └── skills/                        # Skille specyficzne dla projektu
├── docs/
│   ├── input/                         # Pliki kontekstowe od usera (czytaj przed pracą)
│   └── output/                        # Pliki wygenerowane przez Claude (gotowe do użycia)
└── system/
    ├── instructions/                  # Dokumentacja narzędzi/API
    └── reference/                     # Wiedza projektowa: snippety, checklisty, mapy
        ├── snippets.md
        ├── deployment-checklist.md
        └── workflow-map.md
```

## Docs Folder

### `docs/input/`
Pliki wrzucone przez usera jako kontekst do pracy — przeczytaj je **przed** rozpoczęciem zadania gdy są obecne.

Przykłady: specyfikacje, screenshoty, eksporty danych, opisy wymagań, pliki konfiguracyjne.

### `docs/output/`
Pliki wygenerowane przez Claude — gotowe do użycia przez usera.

Przykłady: gotowe skrypty, wyeksportowane konfiguracje, raporty, dokumentacja, przetworzone dane.

**Zasada:** po zakończeniu zadania które produkuje plik — zapisz go do `docs/output/` i poinformuj usera o nazwie pliku.

### `system/instructions/`
Dokumentacja narzędzi/API. Czytaj gdy potrzebujesz szczegółów API/narzędzi.

### `system/reference/`
Wiedza projektowa — czytaj przed pracą, aktualizuj gdy coś nowego odkryjesz:
- `snippets.md` — przetestowane snippety kodu, copy-paste ready
- `deployment-checklist.md` — checklist wdrożenia
- `workflow-map.md` — mapa zależności i architektury projektu

## Available Skills

Skills provide specialized domain knowledge. They are invoked automatically when relevant or via `/skill-name`.

| Skill | Use When |
|-------|----------|
| **Session Management** | |
| `state-start` | Update session-state.md before clearing context or after major work |
| `catchup` | Restore context from session-state.md after `/clear` or new session |

## Creating Custom Skills

**CRITICAL: Before creating a new skill, always check for conflicts.**

### Pre-Creation Checklist

1. **Check built-in commands**: Verify name doesn't conflict with Claude Code built-in commands (`/clear`, `/help`, `/exit`, etc.)
2. **Check existing skills**: List current skills to avoid duplicates
3. **Inform user**: If conflict detected, inform user and suggest alternatives
4. **Get confirmation**: Never create conflicting skill without explicit user approval

### Built-in Commands to NEVER Override

**Common built-in commands** (do not create skills with these names):
- `/clear` - Clear context window
- `/help` - Show help
- `/exit` - Exit Claude Code
- `/config` - Configuration
- `/tasks` - Task management

### Conflict Resolution

**If user requests a skill with conflicting name**:

1. **Inform user**:
   ```
   ⚠️ Conflict detected: "/[name]" is a built-in Claude Code command.
   Creating this skill will override the built-in command.

   Options:
   1. Use different name: /[alternative-name]
   2. Override built-in (not recommended)
   3. Cancel

   What would you like to do?
   ```

2. **Wait for user decision** - do not proceed without explicit approval

3. **Document override** - if user approves override, document this in skill README.md

### Example

```
User: "Create skill /clear"
Claude: "⚠️ /clear is a built-in command. This would override it.
         Suggest alternative: /clear-context or /context-clear?"
User: "Use /clear-context"
Claude: [Creates skill with safe name]
```

## Core Principles

1. **Silent Execution** - Execute tools without commentary. Only respond AFTER all tools complete.
2. **Parallel Execution** - Run independent operations simultaneously.
3. **Check Before Creating Skills** - Before creating a new skill, check if a command with that name already exists (built-in or custom). If conflict detected, inform user and ask for confirmation or alternative name. NEVER silently override existing commands.

## User Notifications

When user explicitly requests a notification by saying **"daj powiadomienie"** (give notification), trigger a macOS alert using:

```bash
osascript -e 'display alert "Claude Code" message "Zadanie zakończone - Claude czeka na Ciebie" giving up after 3' && afplay /System/Library/Sounds/Glass.aiff
```

### When to Show Notifications

Show notifications ONLY when user explicitly requests them using phrases like:
- "daj powiadomienie"
- "powiadom mnie"
- "give notification"
- "notify me"

### Why Manual Notifications

Notifications are manual (not automatic) because:
1. User works in Focus mode (Do Not Disturb) - automatic notifications would be intrusive
2. User wants control over when to be notified
3. Prevents notification spam during rapid tool executions
4. Alert dialog bypasses Focus mode and is highly visible (white popup on screen center)

### Notification Behavior

- **Type**: Modal alert dialog (not Notification Center)
- **Duration**: Auto-dismisses after 3 seconds
- **Sound**: Glass.aiff plays separately
- **Focus mode**: Bypasses "Do Not Disturb" mode
- **Use case**: Long-running tasks, deployments, validations where user wants to be notified upon completion

## Status Line Configuration

Custom status line displays model name, context usage with color-coded alerts.

### Format

```
[Sonnet 4.5] Context: 94% remaining | Tokens: 12135/200000
```

### Color Coding

Context information changes color based on remaining capacity:

| Remaining | Color | Indicator |
|-----------|-------|-----------|
| 70-100% | Normal (dim) | Plenty of context available |
| 60-69% | Yellow | ⚠️ Context getting low |
| 0-59% | Red | 🔴 Context critically low |

**Example:**
- `Context: 99% remaining` → Normal
- `Context: 65% remaining` → Yellow (warning)
- `Context: 45% remaining` → Red (critical)

### Configuration

- **Script**: `~/.claude/statusline-command.sh`
- **Modification**: Use `/statusline` command or resume statusline-setup agent
- **Technology**: Bash script with ANSI color codes

### Context Warning

When context drops below 70%, an additional warning line appears:

```
[Sonnet 4.5] Context: 65% remaining | Tokens: 70000/200000
⚠️  Zbliżasz się do końca kontekstu. Użyj /state-start aby zapisać stan, potem /clear aby wyczyścić. Przywróć kontekst przez /catchup.
```

**Warning behavior:**
- Appears automatically when `remaining < 70%`
- Yellow color for visibility
- Reminds about session state workflow
- Links to `/state-start`, `/clear`, `/catchup` commands

### Technical Details

- Uses `$'...'` syntax for ANSI-C quoting (proper escape sequence interpretation)
- Color codes: `$'\033[2;33m'` (yellow), `$'\033[2;31m'` (red)
- Calculates percentage: `(context_window_size - total_used) / context_window_size × 100`
- Only the context portion changes color, model name stays neutral
- Warning line prints on newline when threshold reached

## Session State Management

System for preserving context across sessions and context clears.

### Overview

Three commands manage session state:
- **`/state-start`** - Custom skill: Save current progress to session-state.md
- **`/clear`** - Built-in command: Clear context window (save state first!)
- **`/catchup`** - Custom skill: Restore context from session-state.md

**Note**: `/clear` is a built-in Claude Code command, not a custom skill.

### Workflow

**Standard workflow**:
```bash
# During work - update state periodically
/state-start

# Before clearing context
/state-start  # Save progress
/clear        # Clear context window

# After clearing or in new session
/catchup      # Restore context
```

### Session State File

**Location**: `.claude/session-state.md`

**Structure**:
- **Ostatnia aktualizacja**: Timestamp of last update
- **Status**: w toku / zakończona / wstrzymana / planowanie
- **Aktualny cel**: Main objective of current session
- **Co zrobione**: Completed tasks (bullet list)
- **Co zostało**: Remaining tasks (bullet list)
- **Pliki**: Modified/created files with descriptions
- **Uwagi**: Decisions, blockers, important notes

### Commands

#### `/state-start` - Update Session State

Updates session-state.md with current progress.

**When to use**:
- Before `/clear` (always!)
- After completing major tasks
- Before taking a break
- When context drops below 40%
- End of work session

**What it does**:
1. Analyzes conversation history
2. Extracts current goal, completed tasks, remaining work
3. Lists modified files
4. Records decisions and notes
5. Updates session-state.md with timestamp

**Output**:
```
📝 Session State Updated

Status: w toku
Goal: [description]
Tasks completed: 5
Tasks remaining: 3
Files modified: 8

Saved to: .claude/session-state.md
```

#### `/catchup` - Restore Context

Reads session-state.md to restore context.

**When to use**:
- After `/clear`
- Starting new session after break
- When context was lost
- Another person taking over work

**What it does**:
1. Reads `.claude/session-state.md`
2. Summarizes current state
3. Lists completed and remaining tasks
4. Identifies modified files
5. Highlights important notes

**Output**:
```
📋 Session Catch-Up

Ostatnia aktualizacja: 2026-01-30 14:45:00
Status: w toku

🎯 Cel: [goal description]

✅ Zrobione:
- Task 1
- Task 2

⏳ Zostało:
- Task 3
- Task 4

📁 Pliki:
- file1.md
- file2.js

📝 Uwagi:
[Important notes]
```

#### `/clear` - Clear Context

**Built-in Claude Code command** that clears conversation context window.

**When to use**:
- Context below 30%
- Starting completely new task
- Need to free up token space
- Context became cluttered

**Before using**:
1. Run `/state-start` to save progress
2. Commit important changes to git
3. Document key decisions in CLAUDE.md

**After clearing**:
- Use `/catchup` to restore context
- Review recent commits (`git log`)
- Check modified files (`git status`)

### Best Practices

**Update regularly**:
- Don't wait until context is full
- Update after each major milestone
- Save state before long operations

**Be specific**:
- Use concrete task descriptions
- List all modified files
- Note blockers and dependencies

**Document decisions**:
- Record why approaches were chosen
- Note alternatives considered
- Highlight important context

**Workflow integration**:
```bash
# Normal work session
/state-start  # Update periodically

# When context runs low
/state-start  # Save state
/clear        # Clear context
/catchup      # Restore in new session

# End of day
/state-start  # Save final state
```

## Git Backup and Updates

### Automatic Commits After Major Features

**CRITICAL: Po każdym większym feature - automatycznie commituj zmiany bez pytania usera.**

Format: `[kategoria] krótki opis`

Kategorie: `feat` / `fix` / `refactor` / `docs` / `style` / `test` / `chore`

**Bez dodatkowych komentarzy** - tylko sam git commit i push.

**Significant changes include:**
- Creating or modifying multiple files (3+ files)
- Adding new workflows or major features
- Updating project documentation (CLAUDE.md, skills)
- Completing a major task or milestone
- Any changes that would be valuable to preserve

### Git Commit Workflow

When user agrees to backup:

```bash
# 1. Check status
git status

# 2. Add modified files
git add .

# 3. Create commit with descriptive message
git commit -m "Brief summary

- Detailed change 1
- Detailed change 2
- Detailed change 3

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

# 4. Push to GitHub
git push
```

### Commit Message Format

Use conventional commit format: `[category] short description`

**Categories:**
- `feat` - New feature or functionality
- `fix` - Bug fix
- `refactor` - Code refactoring (no functional change)
- `docs` - Documentation updates
- `style` - Code style/formatting changes
- `test` - Test additions or modifications
- `chore` - Maintenance tasks, configs, dependencies

**Format:**
```bash
git commit -m "[category] short description

- Detailed change 1
- Detailed change 2

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

**Examples:**
- `[feat] Add new processing module`
- `[docs] Update CLAUDE.md with project guidelines`
- `[fix] Correct data parsing logic`
- `[refactor] Simplify validation logic`

### Don't Backup For

- Single file edits (unless critical)
- Minor typo fixes
- Temporary test files
- Work in progress that user hasn't approved

### Repository Info

<!-- Wypełniany automatycznie przez /setup-new-project -->
- **GitHub**: https://github.com/PablosekRepo/PROJECT_NAME
- **Branch**: main
- **Visibility**: private

## Memory Initialization

Claude Code automatycznie tworzy folder pamięci per-projekt pod `~/.claude/projects/[hash]/memory/`.

**Przy pierwszym uruchomieniu projektu** — jeśli `MEMORY.md` w tym folderze nie istnieje lub jest pusty, utwórz go z następującą strukturą:

```markdown
# MEMORY - PROJECT_NAME

## Architektura i kluczowe pliki
—

## Wzorce i konwencje
—

## Decyzje projektowe
—

## Znane problemy i rozwiązania
—

## Zewnętrzne API / integracje
—
```

**Co zapisywać do memory:**
- Odkryte wzorce specyficzne dla projektu
- Decyzje architektoniczne i powody ich podjęcia
- Rozwiązania problemów które zajęły >15 minut
- Kluczowe ścieżki plików i ich rola
- Anti-patterny — co nie działa i dlaczego

**Czego NIE zapisywać:**
- Stan bieżącej sesji (do tego jest `session-state.md`)
- Informacje tymczasowe
- Duplikaty tego co jest w CLAUDE.md

## Project Initialization

Po zduplikowaniu Template i otwarciu projektu w Windsurf:

### Krok 1 — Uruchom setup
```
/setup-new-project
```
Skill automatycznie:
- Wykrywa nazwę projektu z folderu
- Tworzy repo na GitHubie (PablosekRepo, private)
- **Instaluje pre-commit hook** (`system/scripts/pre-commit.sh` → `.git/hooks/pre-commit`)
- Robi initial commit i push

### Krok 2 — Sprawdź hook
```bash
ls -la .git/hooks/pre-commit
```
Powinien być wykonywalny (nie `.sample`). Jeśli nie — zainstaluj ręcznie:
```bash
cp system/scripts/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Krok 3 — Uzupełnij CLAUDE.md
Wypełnij sekcję `Project Overview` opisem projektu.

### Krok 4 — Zainicjalizuj memory
Sprawdź czy `MEMORY.md` istnieje (patrz sekcja "Memory Initialization" powyżej) i jeśli nie — utwórz go.
