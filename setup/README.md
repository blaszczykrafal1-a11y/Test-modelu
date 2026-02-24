# setup/

Folder zawiera gotowe pliki do skopiowania podczas onboardingu.

## Zawartość

```
setup/
├── global-claude-template.md      # Template dla ~/.claude/CLAUDE.md
├── statusline-command.sh          # Status line script
├── skills/
│   ├── state-start/SKILL.md       # Skill: zapisuje stan sesji
│   ├── catchup/SKILL.md           # Skill: przywraca stan sesji
│   └── setup-new-project/SKILL.md # Skill: setup nowego projektu
└── hooks/
    └── security-scan.py           # Security hook (Pre-ToolUse)
```

## Jak używać

Patrz `ONBOARDING.md` — każda Faza zawiera dokładne komendy `cp`.

## Co wymaga dostosowania

| Plik | Co zmienić |
|------|-----------|
| `global-claude-template.md` | Wszystkie `[[...]]` placeholdery |
| `skills/setup-new-project/SKILL.md` | `GITHUB_USERNAME` → Twoje konto GitHub |
