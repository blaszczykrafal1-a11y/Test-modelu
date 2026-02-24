# Skill: state-start

Zapisuje aktualny postęp sesji do pliku `session-state.md`.

## Wywołanie

```
/state-start
```

## Co robi

1. Analizuje historię rozmowy
2. Aktualizuje `.claude/session-state.md`:
   - aktualny cel sesji
   - lista wykonanych zadań
   - lista pozostałych zadań
   - zmodyfikowane pliki
   - decyzje i notatki
3. Zapisuje timestamp

## Kiedy używać

- Przed `/clear` — zawsze, żeby nie stracić kontekstu
- Po zakończeniu większego zadania
- Przed przerwą
- Gdy kontekst spada poniżej 40%
- Na koniec dnia pracy

## Workflow

```
# Standardowy reset kontekstu
/state-start   ← zapisz postęp
/clear         ← wyczyść kontekst
/exit          ← zamknij Claude Code
claude         ← uruchom ponownie
/catchup       ← przywróć kontekst
```

## Output

```
📝 Session State Updated

Status: w toku
Goal: [opis celu]
Tasks completed: 5
Tasks remaining: 3
Files modified: 8

Saved to: .claude/session-state.md
```

## Plik stanu

Lokalizacja: `.claude/session-state.md` w katalogu projektu.

Pola:
- `Ostatnia aktualizacja` — timestamp
- `Status` — w toku / zakończona / wstrzymana / planowanie
- `Aktualny cel` — co robimy w tej sesji
- `Co zrobione` — lista bulletów
- `Co zostało` — lista bulletów
- `Pliki` — zmodyfikowane/stworzone pliki
- `Uwagi` — decyzje, blokery, ważny kontekst
