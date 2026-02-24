# .claude/skills/

Skille specyficzne dla tego projektu — dostępne tylko w jego kontekście.

## Struktura skilla

```
.claude/skills/
└── nazwa-skilla/
    ├── SKILL.md    # definicja / prompt — główna logika skilla
    └── README.md   # dokumentacja — kiedy używać, parametry, przykłady
```

## Kiedy tworzyć skill projektowy

Kiedy jakaś czynność powtarza się w tym projekcie i ma specyficzny kontekst — np. generowanie raportu w konkretnym formacie, deploy na konkretne środowisko, praca z konkretnym API.

Skille globalne (multi-projekt) trafiają do `~/.claude/skills/`.

## Używanie

```
/nazwa-skilla
```

## Przed stworzeniem skilla

Sprawdź czy nie konfliktujesz z built-in komendami Claude Code:
`/clear`, `/help`, `/exit`, `/config`, `/tasks`
