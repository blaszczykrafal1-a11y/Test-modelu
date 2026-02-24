# Setup Checklist

Szybka lista kontrolna po przejściu przez ONBOARDING.md.

## Prereqs

- [ ] Node.js v18+ (`node --version`)
- [ ] Python 3 (`python3 --version`)
- [ ] Git (`git --version`)
- [ ] GitHub CLI zalogowany (`gh auth status`)
- [ ] jq (`jq --version`)

## Claude Code CLI

- [ ] Zainstalowany (`claude --version`)
- [ ] Zalogowany (`claude` → powinien działać)

## Globalna konfiguracja (~/.claude/)

- [ ] `CLAUDE.md` — wypełniony (brak `[[...]]` placeholderów)
- [ ] `skills/state-start/SKILL.md` — istnieje
- [ ] `skills/catchup/SKILL.md` — istnieje
- [ ] `skills/setup-new-project/SKILL.md` — `GITHUB_USERNAME` zmieniony na Twoje konto
- [ ] `hooks/security-scan.py` — istnieje i wykonywalny (`ls -la`)
- [ ] `statusline-command.sh` — istnieje i wykonywalny

## Konfiguracja Claude Code

- [ ] `claude config list` pokazuje `statusCommand`
- [ ] `claude config list` pokazuje `hooks.pre_tool_use`
- [ ] Status line widoczny w Claude (model + context %)

## Pierwszy projekt

- [ ] Folder zduplikowany z Template
- [ ] `/setup-new-project` uruchomiony pomyślnie
- [ ] Repo widoczne na GitHub
- [ ] `git log` pokazuje initial commit
- [ ] `.git/hooks/pre-commit` istnieje i jest wykonywalny
- [ ] `CLAUDE.md` projektu uzupełniony (sekcja Project Overview)

## Szybki test

Wejdź do projektu i w Claude Code uruchom:

```
/state-start
```

Powinien zapisać stan do `.claude/session-state.md`.

```
/catchup
```

Powinien odczytać i wyświetlić zapisany stan.

---

Jeśli wszystko jest zaznaczone — setup gotowy.
