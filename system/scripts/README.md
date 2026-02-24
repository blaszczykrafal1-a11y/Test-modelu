# system/scripts/

Skrypty narzędziowe projektu — git hooks, setup, automacje środowiskowe.

## Pliki

| Plik | Co robi |
|------|---------|
| `pre-commit.sh` | Git pre-commit hook — blokuje commit z sekretami lub plikami danych klientów. |

## Instalacja hooków w nowym środowisku

```bash
cp system/scripts/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Konwencja

Nazwy plików: `kebab-case.sh` / `kebab-case.py`

Każdy skrypt powinien mieć komentarz na górze z opisem co robi i jak go uruchomić.
