# Setup New Project

Skill do uruchomienia po zduplikowaniu folderu Template i otwarciu projektu w edytorze.

## Przed użyciem

Zmień `GITHUB_USERNAME` w tym pliku na swoje konto GitHub.

## Co robi

Wykonaj poniższe kroki **w tej kolejności**, bez pytania o każdy krok:

### 1. Wykryj nazwę projektu

```bash
basename "$PWD"
```

To jest `PROJECT_NAME`. Użyj tej nazwy wszędzie poniżej.

### 2. Zaktualizuj CLAUDE.md

Zamień wszystkie wystąpienia `PROJECT_NAME` na rzeczywistą nazwę projektu w pliku `CLAUDE.md`.

### 3. Git setup

Sprawdź czy `.git` istnieje:

```bash
ls -la .git 2>/dev/null
```

**Jeśli `.git` istnieje** (skopiowany z Template):
```bash
git remote remove origin
```

**Jeśli `.git` nie istnieje:**
```bash
git init
git branch -M main
```

### 4. Sprawdź czy repo już istnieje na GitHub

```bash
gh repo view GITHUB_USERNAME/PROJECT_NAME 2>&1
```

**Jeśli nie istnieje** — utwórz:
```bash
gh repo create GITHUB_USERNAME/PROJECT_NAME --private
git remote add origin https://github.com/GITHUB_USERNAME/PROJECT_NAME.git
```

**Jeśli istnieje** — tylko dodaj remote:
```bash
git remote add origin https://github.com/GITHUB_USERNAME/PROJECT_NAME.git
```

### 5. Zainstaluj pre-commit hook

```bash
cp system/scripts/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### 6. Initial commit i push

```bash
git add CLAUDE.md .gitignore system/scripts/pre-commit.sh system/reference/snippets.md .claude/session-state.md
git commit -m "[init] PROJECT_NAME setup

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git push -u origin main
```

### 7. Potwierdź

Po zakończeniu wyświetl:
```
Projekt skonfigurowany: PROJECT_NAME
GitHub: https://github.com/GITHUB_USERNAME/PROJECT_NAME
Pre-commit hook: zainstalowany
```

I zapytaj usera: **"Co robimy w tym projekcie?"**

## Uwagi

- Nie pytaj o potwierdzenie każdego kroku — wykonuj sekwencyjnie
- Jeśli któryś krok się nie powiedzie, zatrzymaj się i zgłoś błąd
- `PROJECT_NAME` nie może zawierać spacji — jeśli folder ma spacje, zamień na myślniki
