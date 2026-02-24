# Prompt onboardingowy dla Claude Code

Skopiuj poniższy tekst i wklej do Claude Code w terminalu Windsurf.

---

Przeprowadź mnie przez konfigurację środowiska Claude Code.

Jestem nowym użytkownikiem. Właśnie zainstalowałem Windsurf i Claude Code CLI, jestem zalogowany i pracuję w folderze Onboarding — zawiera podfolder `setup/` z gotowymi plikami do skopiowania.

Przeprowadź mnie kolejno przez każdy krok. Zasady:
- Wyjaśnij krótko co robimy i dlaczego (prostym językiem, bez technikaliów)
- Podaj dokładną komendę do uruchomienia
- Poczekaj aż powiem "gotowe" zanim przejdziesz do kolejnego kroku
- Po każdym kroku sprawdź że się powiódł

Kroki:

**1. Utwórz strukturę folderów globalnych**
   Utwórz `~/.claude/skills/`, `~/.claude/hooks/`, `~/.claude/memory/`

**2. Skopiuj skille**
   Skopiuj całe foldery z `setup/skills/` do `~/.claude/skills/`
   (state-start, catchup, setup-new-project)

**3. Skopiuj security hook**
   Skopiuj `setup/hooks/security-scan.py` do `~/.claude/hooks/`
   Nadaj uprawnienia wykonania: `chmod +x ~/.claude/hooks/security-scan.py`

**4. Skopiuj status line**
   Skopiuj `setup/statusline-command.sh` do `~/.claude/`
   Nadaj uprawnienia wykonania: `chmod +x ~/.claude/statusline-command.sh`

**5. Wygeneruj settings.json**
   Utwórz `~/.claude/settings.json` z DOKŁADNIE taką strukturą.
   Użyj bash heredoc żeby `$HOME` się rozwinął do pełnej ścieżki:

   ```bash
   cat > ~/.claude/settings.json << EOF
   {
     "model": "sonnet",
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

   Po wykonaniu sprawdź: `cat ~/.claude/settings.json`
   Ścieżki muszą być absolutne (np. `/Users/pablo/...`), NIE `~`.

**6. Zaloguj do GitHub CLI**
   Najpierw zapytaj usera czy ma konto na github.com.
   Jeśli nie ma — powiedz żeby je założył (bezpłatne, github.com → Sign up) i poczekaj.
   Następnie wykonaj: `gh auth login`
   Wybierz: GitHub.com → HTTPS → zaloguj przez przeglądarkę.

**7. Skonfiguruj globalny CLAUDE.md**
   Najpierw zapytaj mnie o:
   - preferowany język pracy z AI (np. polski, angielski)
   - mój GitHub username
   - ścieżkę do folderów projektów (np. ~/Projects/)
   - czy chcę wysoki poziom autonomii Claude (nie pytaj o każdy krok)
   Następnie skopiuj `setup/global-claude-template.md` do `~/.claude/CLAUDE.md`
   i zastąp wszystkie placeholdery `[[...]]` podanymi wartościami.

**8. Zaktualizuj skill setup-new-project**
   W pliku `~/.claude/skills/setup-new-project/SKILL.md`
   zamień wszystkie wystąpienia `GITHUB_USERNAME` na mój GitHub username.

**9. Weryfikacja końcowa**
   Sprawdź że wszystkie pliki istnieją:
   - `ls ~/.claude/skills/` — powinny być: state-start, catchup, setup-new-project
   - `ls ~/.claude/hooks/` — powinien być: security-scan.py
   - `cat ~/.claude/settings.json` — sprawdź że ścieżki są absolutne
   Przetestuj: użyj `/state-start` — powinien zapisać stan sesji do pliku.

**Na końcu** powiedz mi:
1. Jak skopiować folder Onboarding jako template dla pierwszego projektu
2. Jak uruchomić `/setup-new-project` żeby stworzyć repo na GitHubie i zainicjować projekt
3. Co warto przeczytać w `CLAUDE.md` projektu przed rozpoczęciem pracy
