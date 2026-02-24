# Prompt onboardingowy dla Claude Code

Skopiuj poniższy tekst i wklej do Claude Code w terminalu Windsurf.

---

Przeprowadź mnie przez konfigurację środowiska Claude Code.

Jestem nowym użytkownikiem. Właśnie zainstalowałem Windsurf i Claude Code CLI, jestem zalogowany i pracuję w folderze Onboarding — zawiera podfolder `setup/` z gotowymi plikami do skopiowania.

Przeprowadź mnie kolejno przez każdy krok. Zasady:
- Wyjaśnij krótko co robimy i dlaczego
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
   Nadaj uprawnienia wykonania: `chmod +x`

**4. Skopiuj status line**
   Skopiuj `setup/statusline-command.sh` do `~/.claude/`
   Nadaj uprawnienia wykonania: `chmod +x`

**5. Wygeneruj settings.json**
   Utwórz `~/.claude/settings.json` z konfiguracją hooka i status line.
   Użyj `$HOME` zamiast hardcoded ścieżki (bash shell command).

**6. Skonfiguruj globalny CLAUDE.md**
   Najpierw zapytaj mnie o:
   - preferowany język pracy z AI (np. polski, angielski)
   - mój GitHub username
   - ścieżkę do folderów projektów (np. ~/Projects/)
   - czy chcę wysoki poziom autonomii Claude (nie pytaj o każdy krok)
   Następnie skopiuj `setup/global-claude-template.md` do `~/.claude/CLAUDE.md`
   i zastąp wszystkie placeholdery `[[...]]` podanymi wartościami.

**7. Zaktualizuj skill setup-new-project**
   W pliku `~/.claude/skills/setup-new-project/SKILL.md`
   zamień wszystkie wystąpienia `GITHUB_USERNAME` na mój GitHub username.

**8. Weryfikacja**
   Sprawdź że wszystkie pliki istnieją i `cat ~/.claude/settings.json` wygląda poprawnie.
   Uruchom test: spróbuj użyć `/state-start` — powinien zapisać stan sesji.

**Na końcu** powiedz mi:
1. Jak skopiować folder Onboarding jako template dla pierwszego projektu
2. Jak uruchomić `/setup-new-project` żeby stworzyć repo na GitHubie i zainicjować projekt
3. Co warto przeczytać w `CLAUDE.md` projektu przed rozpoczęciem pracy
