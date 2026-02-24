# Prompt onboardingowy dla Claude Code

Skopiuj cały poniższy tekst i wklej do terminala w Windsurf gdzie działa Claude.

---

Przeprowadź mnie przez konfigurację środowiska Claude Code. Jestem nowym użytkownikiem — właśnie zainstalowałem Windsurf i Claude Code CLI, jestem zalogowany i pracuję w folderze Onboarding, który zawiera podfolder `setup/` z gotowymi plikami.

**Zasady dla każdego kroku:**
- Wyjaśnij krótko co robimy i dlaczego (prostym językiem, bez technikaliów)
- Podaj jedną komendę na raz
- Poczekaj aż powiem "gotowe" zanim przejdziesz dalej
- Sprawdź że krok się powiódł zanim przejdziesz dalej
- Jeśli coś nie zadziała — pomóż naprawić, nie idź dalej

---

**KROK 0 — Wykryj mój system operacyjny**

Uruchom:
- macOS: `uname -s` (zwróci `Darwin`)
- Windows: jesteś w PowerShell, więc `$env:OS` zwróci `Windows_NT`

Przez całą resztę dopasuj komendy do mojego systemu.

---

**CZĘŚĆ A — Instalacja brakujących narzędzi**

**Krok 1 — GitHub CLI (gh) i jq**

Sprawdź czy są: `gh --version` i `jq --version`

Jeśli brak:
- macOS: najpierw sprawdź Homebrew (`brew --version`), jeśli brak zainstaluj Homebrew. Następnie: `brew install gh jq`
- Windows: `winget install GitHub.cli` i `winget install jqlang.jq` (po instalacji zamknij i otwórz nowy terminal)

**Krok 2 — Logowanie do GitHub**

Najpierw zapytaj mnie czy mam konto na github.com — jeśli nie, powiedz żebym założył (bezpłatne, github.com → Sign up) i poczekaj.

Następnie: `gh auth login`
Wybierz: GitHub.com → HTTPS → zaloguj przez przeglądarkę.
Sprawdź: `gh auth status`

---

**CZĘŚĆ B — Konfiguracja Claude**

**Krok 3 — Foldery konfiguracyjne**

- macOS: `mkdir -p ~/.claude/skills ~/.claude/hooks ~/.claude/memory`
- Windows: `New-Item -ItemType Directory -Force "$HOME/.claude/skills","$HOME/.claude/hooks","$HOME/.claude/memory"`

**Krok 4 — Skille**

Skopiuj foldery z `setup/skills/` do `~/.claude/skills/`:
- macOS: `cp -r setup/skills/* ~/.claude/skills/`
- Windows: `Copy-Item -Recurse setup\skills\* "$HOME\.claude\skills\"`

Sprawdź: `ls ~/.claude/skills/` — powinny być: state-start, catchup, setup-new-project

**Krok 5 — Security hook**

- macOS: `cp setup/hooks/security-scan.py ~/.claude/hooks/ && chmod +x ~/.claude/hooks/security-scan.py`
- Windows: `Copy-Item setup\hooks\security-scan.py "$HOME\.claude\hooks\"`

**Krok 6 — Status line**

- macOS: `cp setup/statusline-command.sh ~/.claude/ && chmod +x ~/.claude/statusline-command.sh`
- Windows: `Copy-Item setup\statusline-command.sh "$HOME\.claude\"`

**Krok 7 — settings.json**

Wygeneruj `~/.claude/settings.json` z absolutnymi ścieżkami (NIE ~).

macOS (bash heredoc — $HOME rozwinie się do pełnej ścieżki):
```bash
cat > ~/.claude/settings.json << EOF
{
  "model": "sonnet",
  "statusLine": {
    "type": "command",
    "command": "bash $HOME/.claude/statusline-command.sh"
  },
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write|Edit|Bash",
      "hooks": [{"type": "command",
        "command": "python3 $HOME/.claude/hooks/security-scan.py"}]
    }]
  }
}
EOF
```

Windows (PowerShell here-string):
```powershell
$h = $env:USERPROFILE
@"
{
  "model": "sonnet",
  "statusLine": {
    "type": "command",
    "command": "bash $h/.claude/statusline-command.sh"
  },
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write|Edit|Bash",
      "hooks": [{"type": "command",
        "command": "python3 $h/.claude/hooks/security-scan.py"}]
    }]
  }
}
"@ | Set-Content "$HOME\.claude\settings.json"
```

Sprawdź wynik:
- macOS: `cat ~/.claude/settings.json`
- Windows: `Get-Content $HOME\.claude\settings.json`

Ścieżki muszą być absolutne, np. `/Users/jan/...` lub `C:\Users\jan\...`

**Krok 8 — Globalny CLAUDE.md**

Zapytaj mnie o:
- preferowany język pracy z AI (np. polski)
- mój GitHub username
- ścieżkę do folderów projektów (np. ~/Projects/)

Następnie skopiuj `setup/global-claude-template.md` do `~/.claude/CLAUDE.md` i zastąp wszystkie placeholdery `[[...]]` podanymi przeze mnie wartościami.

**Krok 9 — Zaktualizuj skill setup-new-project**

W pliku `~/.claude/skills/setup-new-project/SKILL.md` zamień wszystkie wystąpienia `GITHUB_USERNAME` na mój GitHub username.

---

**CZĘŚĆ C — Weryfikacja końcowa**

Sprawdź każdy punkt i podaj wynik jako listę: ✅ OK lub ❌ BŁĄD (z opisem co jest nie tak):

1. `ls ~/.claude/skills/` → state-start, catchup, setup-new-project obecne?
2. `ls ~/.claude/hooks/` → security-scan.py obecny?
3. `ls ~/.claude/` → statusline-command.sh, settings.json, CLAUDE.md obecne?
4. Otwórz settings.json → ścieżki absolutne (nie ~)?
5. `gh auth status` → GitHub zalogowany?
6. Uruchom `/state-start` → pojawił się plik `.claude/session-state.md`?

Jeśli wszystko ✅ → powiedz "Środowisko gotowe do pracy!" i wyjaśnij w 3 zdaniach:
- jak stworzyć pierwszy projekt (`/setup-new-project`)
- kiedy używać `/state-start` i `/catchup`

Jeśli cokolwiek ❌ → napraw zanim zakończysz.
