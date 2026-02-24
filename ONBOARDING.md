# Claude Code - Instrukcja onboardingu

Instrukcja przeprowadza Cię przez pełny setup Claude Code od zera do działającego środowiska pracy.

**Czas:** ~45-60 minut
**System:** macOS (testowane na macOS 15+, zsh)

---

## Co dostaniesz po setupie

- Claude Code CLI z trwałą pamięcią między sesjami
- System zarządzania kontekstem (save/restore stanu pracy)
- Status line z informacją o zużyciu kontekstu
- Security hook blokujący przypadkowe wyciekanie sekretów i danych
- Template dla każdego nowego projektu
- Workflow dla długich wielosesyjnych zadań

---

## Jak używać tej instrukcji

Odhaczaj `- [ ]` po każdym wykonanym kroku. Po każdej fazie jest sekcja **Weryfikacja** - uruchom ją zanim przejdziesz dalej.

---

## Faza 0 — Wymagania wstępne

Sprawdź, czy masz wszystko zainstalowane:

- [ ] **macOS** z terminalem zsh
- [ ] **Node.js** v18+ (`node --version`)
- [ ] **Python 3** (`python3 --version`)
- [ ] **Git** (`git --version`)
- [ ] **GitHub CLI** (`gh --version`) — [instalacja](https://cli.github.com/)
- [ ] **jq** (`jq --version`) — potrzebny przez status line (`brew install jq`)
- [ ] **Konto GitHub** z uprawnieniami do tworzenia repo
- [ ] **Subskrypcja Claude** (claude.ai/pro) lub dostęp do Claude API

### Weryfikacja Fazy 0

```bash
node --version && python3 --version && git --version && gh --version && jq --version
```

Wszystkie polecenia powinny zwrócić numery wersji bez błędów.

---

## Faza 1 — Instalacja Claude Code CLI

- [ ] Zainstaluj Claude Code:

```bash
npm install -g @anthropic-ai/claude-code
```

- [ ] Uruchom Claude Code i zaloguj się:

```bash
claude
```

Claude poprosi o zalogowanie przez przeglądarkę (OAuth z claude.ai) lub podanie klucza API.

- [ ] Zamknij po udanym logowaniu:

```bash
/exit
```

### Weryfikacja Fazy 1

```bash
claude --version
```

Powinien pokazać numer wersji.

---

## Faza 2 — Konfiguracja globalna

Globalna konfiguracja trafia do `~/.claude/`. Jest współdzielona między wszystkimi projektami.

### 2.1 — Struktura folderów

- [ ] Utwórz strukturę:

```bash
mkdir -p ~/.claude/skills/state-start
mkdir -p ~/.claude/skills/catchup
mkdir -p ~/.claude/skills/setup-new-project
mkdir -p ~/.claude/hooks
mkdir -p ~/.claude/memory
```

### 2.2 — Globalny CLAUDE.md (preferencje)

- [ ] Skopiuj template:

```bash
cp setup/global-claude-template.md ~/.claude/CLAUDE.md
```

- [ ] Otwórz plik i wypełnij placeholdery `[[...]]`:

```bash
open ~/.claude/CLAUDE.md
```

Zmień co najmniej:
- `[[TWOJ_OS]]` — wersja systemu (`sw_vers -productVersion`)
- `[[TWOJE_PROJEKTY]]` — ścieżka do folderów projektów (np. `~/Projects/`)
- `[[GITHUB_USERNAME]]` — Twoja nazwa konta GitHub

> **WAŻNE:** Nie commituj tego pliku do publicznego repo — może zawierać preferencje osobiste.

### 2.3 — Instalacja skillów

Skille to pluginy do Claude Code uruchamiane przez `/nazwa-skilla`.

- [ ] Skopiuj skill `state-start`:

```bash
cp setup/skills/state-start/SKILL.md ~/.claude/skills/state-start/SKILL.md
```

- [ ] Skopiuj skill `catchup`:

```bash
cp setup/skills/catchup/SKILL.md ~/.claude/skills/catchup/SKILL.md
```

- [ ] Skopiuj skill `setup-new-project`:

```bash
cp setup/skills/setup-new-project/SKILL.md ~/.claude/skills/setup-new-project/SKILL.md
```

- [ ] Otwórz skill `setup-new-project` i zmień `GITHUB_USERNAME` na swoje konto GitHub:

```bash
open ~/.claude/skills/setup-new-project/SKILL.md
```

Zmień wszystkie wystąpienia `GITHUB_USERNAME` na Twoją nazwę konta GitHub.

### 2.4 — Security hook

Hook skanuje każdą operację Write/Edit/Bash **zanim** zostanie wykonana. Blokuje przypadkowe zapisanie API keys, haseł i plików z danymi.

- [ ] Skopiuj hook:

```bash
cp setup/hooks/security-scan.py ~/.claude/hooks/security-scan.py
chmod +x ~/.claude/hooks/security-scan.py
```

### 2.5 — Status line

Status line wyświetla model i zużycie kontekstu w terminalu.

- [ ] Skopiuj skrypt:

```bash
cp setup/statusline-command.sh ~/.claude/statusline-command.sh
chmod +x ~/.claude/statusline-command.sh
```

**Format po konfiguracji:**
```
[Claude Sonnet 4.6] Context: 87% remaining | Tokens: 25000/200000
```

Kolor zmienia się gdy kontekst spada poniżej 70% (żółty) i 60% (czerwony).

### 2.6 — Konfiguracja Claude Code (settings.json)

Hook i status line rejestruje się przez `~/.claude/settings.json`. Komenda poniżej tworzy go automatycznie z Twoją ścieżką:

- [ ] Wygeneruj settings.json:

```bash
cat > ~/.claude/settings.json << EOF
{
  "statusLine": {
    "type": "command",
    "command": "bash $HOME/.claude/statusline-command.sh"
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $HOME/.claude/hooks/security-scan.py"
          }
        ]
      }
    ]
  }
}
EOF
```

> `$HOME` zostanie automatycznie zamieniony na Twoją ścieżkę (np. `/Users/jankowalski`).

> **Jak działa hook:** przed każdym Write/Edit/Bash Claude wysyła treść do skryptu. Jeśli znajdzie sekret lub plik z danymi — blokuje operację i pokazuje co znalazł.

### Weryfikacja Fazy 2

- [ ] Sprawdź czy pliki istnieją:

```bash
ls ~/.claude/CLAUDE.md
ls ~/.claude/skills/state-start/SKILL.md
ls ~/.claude/skills/catchup/SKILL.md
ls ~/.claude/skills/setup-new-project/SKILL.md
ls ~/.claude/hooks/security-scan.py
ls ~/.claude/statusline-command.sh
```

- [ ] Sprawdź settings.json:

```bash
cat ~/.claude/settings.json
```

Powinien zawierać sekcje `statusLine` i `hooks`.

---

## Faza 3 — Zaloguj się do GitHub CLI

`setup-new-project` używa `gh` do tworzenia repozytoriów.

- [ ] Zaloguj się:

```bash
gh auth login
```

Wybierz GitHub.com, HTTPS, zaloguj przez przeglądarkę.

- [ ] Sprawdź:

```bash
gh auth status
```

### Weryfikacja Fazy 3

```bash
gh repo list --limit 5
```

Powinien pokazać listę Twoich repozytoriów.

---

## Faza 4 — Pierwszy projekt

Template to gotowa struktura dla każdego nowego projektu.

### 4.1 — Skopiuj Template

Folder Onboarding jest jednocześnie instrukcją i templatem dla nowych projektów. Skopiuj go i usuń pliki onboardingowe, których nie potrzebujesz w nowym projekcie.

- [ ] Zduplikuj folder:

```bash
cp -r /ścieżka/do/Onboarding ~/Projects/MojNoweProjekt
```

> Zamień `/ścieżka/do/Onboarding` na ścieżkę do tego folderu, a `MojNoweProjekt` na nazwę projektu.

- [ ] Usuń pliki onboardingowe z nowego projektu:

```bash
rm ~/Projects/MojNoweProjekt/ONBOARDING.md
rm ~/Projects/MojNoweProjekt/CHECKLIST.md
rm -rf ~/Projects/MojNoweProjekt/setup/
```

> Po tym zostaje czysta struktura Template: `CLAUDE.md`, `docs/`, `system/`, `.claude/`.

- [ ] Otwórz folder w swoim edytorze kodu (np. Cursor, Windsurf, VS Code)

### 4.2 — Uruchom setup

- [ ] W terminalu przejdź do folderu projektu:

```bash
cd ~/Projects/MojNoweProjekt
claude
```

- [ ] W Claude Code uruchom skill:

```
/setup-new-project
```

Skill automatycznie:
1. Wykryje nazwę projektu z nazwy folderu
2. Zamieni `PROJECT_NAME` w CLAUDE.md
3. Zainicjalizuje git i usunie stary remote
4. Utworzy prywatne repo na GitHubie
5. Zainstaluje pre-commit hook (druga warstwa ochrony sekretów)
6. Wykona initial commit i push

### 4.3 — Uzupełnij CLAUDE.md projektu

- [ ] Otwórz `CLAUDE.md` w projekcie
- [ ] Wypełnij sekcję `Project Overview` — co robi ten projekt, jakie narzędzia/API

### Weryfikacja Fazy 4

```bash
git log --oneline
git remote -v
ls -la .git/hooks/pre-commit
```

Powinna być historia commitów, remote wskazujący na GitHub i działający hook.

---

## Faza 5 — Zrozum kluczowe workflow

### 5.1 — Session state (zarządzanie kontekstem)

Claude Code ma ograniczony kontekst (~200k tokenów). Przy długich sesjach tracisz wcześniejszy kontekst. System session state rozwiązuje ten problem.

**Trzy komendy:**

| Komenda | Co robi |
|---------|---------|
| `/state-start` | Zapisuje postęp do `.claude/session-state.md` |
| `/clear` | Czyści okno kontekstu (built-in komenda Claude Code) |
| `/catchup` | Przywraca kontekst z `session-state.md` |

**Workflow resetu:**

```
/state-start → /clear → /exit → claude → /catchup
```

**Kiedy używać `/state-start`:**
- Przed `/clear` (zawsze!)
- Po zakończeniu większego zadania
- Gdy status line pokazuje <70% kontekstu
- Przed przerwą w pracy

### 5.2 — Gdzie trafiają pliki

| Typ pliku | Gdzie |
|-----------|-------|
| Dokumenty, specyfikacje od Ciebie | `docs/input/` |
| Pliki wygenerowane przez Claude | `docs/output/` |
| Dokumentacja API/narzędzi | `system/instructions/` |
| Snippety kodu | `system/reference/snippets.md` |
| Skrypty automatyzacji | `system/scripts/` |
| Nowy skill projektu | `.claude/skills/nazwa/` |
| **Dane osobowe / kontakty (CSV, XLSX)** | **NIGDY do git** |

### 5.3 — Security rules

Dwie warstwy ochrony działają automatycznie:

1. **Pre-tool hook** (`~/.claude/hooks/security-scan.py`) — skanuje przed każdym Write/Edit/Bash
2. **Pre-commit hook** (`.git/hooks/pre-commit`) — blokuje commit z sekretami

**Co jest blokowane:**
- API keys (OpenAI `sk-...`, Google `AIza...`, GitHub `ghp_...`, AWS `AKIA...`)
- Connection stringi z hasłami
- Pliki `.xlsx`, `.csv`, `.env`
- Pliki z nazwami `credential`, `secret`, `password`, `token`

**Jeśli hook blokuje coś błędnie** (false positive):
```bash
git commit --no-verify
```

Użyj tego tylko gdy jesteś pewien że plik nie zawiera wrażliwych danych.

### 5.4 — Git workflow

```bash
# Sprawdź co zmieniłeś
git status
git diff

# Commit (pre-commit hook sprawdzi automatycznie)
git add konkretne-pliki.md
git commit -m "[feat] Opis zmiany"
git push
```

> **WAŻNE:** Nie używaj `git add .` ani `git add -A` bez sprawdzenia co jest w folderze. Możesz przypadkowo dodać wrażliwe pliki.

---

## Faza 6 — Opcjonalnie: Powiadomienia macOS

Jeśli pracujesz w trybie Focus Mode (Nie przeszkadzać) i chcesz wiedzieć gdy Claude skończy długie zadanie:

Powiedz Claude **"daj powiadomienie"** lub **"notify me"** — pojawi się modal alert omijający DND, który auto-zamknie się po 3 sekundach.

> Powiadomienia są wyłącznie manualne (na Twoją prośbę) — nie pojawiają się automatycznie.

---

## Checklist końcowy

Przed uznaniem setupu za gotowy sprawdź:

- [ ] `claude --version` — Claude Code CLI zainstalowany
- [ ] `gh auth status` — GitHub CLI zalogowany
- [ ] `~/.claude/CLAUDE.md` — wypełniony (brak placeholderów `[[...]]`)
- [ ] `~/.claude/skills/state-start/SKILL.md` — istnieje
- [ ] `~/.claude/skills/catchup/SKILL.md` — istnieje
- [ ] `~/.claude/skills/setup-new-project/SKILL.md` — istnieje, `GITHUB_USERNAME` zmieniony
- [ ] `~/.claude/hooks/security-scan.py` — istnieje, wykonywalny
- [ ] `~/.claude/statusline-command.sh` — istnieje, wykonywalny
- [ ] Status line widoczny w Claude Code
- [ ] `/setup-new-project` uruchomiony w testowym projekcie
- [ ] Pre-commit hook zainstalowany w testowym projekcie

---

## Rozwiązywanie problemów

### Status line nie wyświetla się

```bash
# Sprawdź czy jq jest zainstalowane
jq --version

# Jeśli nie:
brew install jq

# Sprawdź konfigurację
claude config list | grep status
```

### Security hook nie działa

```bash
# Sprawdź czy plik jest wykonywalny
ls -la ~/.claude/hooks/security-scan.py

# Jeśli nie:
chmod +x ~/.claude/hooks/security-scan.py

# Sprawdź konfigurację
claude config list | grep hook
```

### `/setup-new-project` nie może utworzyć repo

```bash
# Sprawdź autentykację GitHub
gh auth status

# Zaloguj się ponownie jeśli potrzeba
gh auth login
```

### Skill nie jest rozpoznawany

Skille muszą być w folderze o dokładnej nazwie z `SKILL.md` w środku:
```
~/.claude/skills/nazwa-skilla/SKILL.md
```

Sprawdź:
```bash
ls ~/.claude/skills/
```

---

## Co dalej

Po setup:

1. **Przeczytaj CLAUDE.md** swojego projektu — zawiera konwencje i zasady pracy
2. **Uruchom `/catchup`** na początku każdej sesji (jeśli używałeś `/state-start` wcześniej)
3. **Customizuj `~/.claude/CLAUDE.md`** — dodaj swoje preferencje, aktywne projekty, notacji
4. **Twórz własne skille** w `.claude/skills/` dla powtarzalnych zadań w projekcie

Dokumentacja Claude Code: https://docs.anthropic.com/claude-code
