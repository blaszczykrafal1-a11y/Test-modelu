# Skill: setup-new-project

Jednorazowy setup nowego projektu — tworzy repo na GitHubie, instaluje hook, robi initial commit.

## Wywołanie

```
/setup-new-project
```

## Wymagania wstępne

Przed uruchomieniem:
- [ ] Zduplikuj `~/CascadeProjects/Template/` i zmień nazwę folderu
- [ ] Otwórz nowy folder w Windsurf
- [ ] Upewnij się że `gh auth status` zwraca zalogowanego użytkownika

## Co robi (kolejność automatyczna)

1. Wykrywa nazwę projektu z nazwy folderu (`basename $PWD`)
2. Aktualizuje `CLAUDE.md` — zamienia wszystkie `PROJECT_NAME` na rzeczywistą nazwę
3. Inicjalizuje git (`git init`) lub czyści remote po duplikowaniu
4. Tworzy prywatne repo na GitHubie (`gh repo create blaszczykrafal1-a11y/NazwaProjektu --private`)
5. Instaluje pre-commit hook (`system/scripts/pre-commit.sh` → `.git/hooks/pre-commit`)
6. Robi initial commit i push do `main`
7. Inicjalizuje plik memory (`~/.claude/projects/[hash]/memory/MEMORY.md`)

## Workflow

```bash
# 1. Duplikuj Template
cp -r ~/CascadeProjects/Template/ ~/CascadeProjects/NazwaProjektu/

# 2. Otwórz w Windsurf, uruchom Claude Code

# 3. Uruchom skill
/setup-new-project

# 4. Uzupełnij CLAUDE.md — sekcja Project Overview
```

## Po uruchomieniu

Sprawdź:
```bash
ls -la .git/hooks/pre-commit   # musi być wykonywalny, nie .sample
gh repo view                   # powinien pokazać nowe repo
git log --oneline              # initial commit
```

## Skille globalne vs projektowe

- Ten skill uruchamiasz tylko raz na nowy projekt
- Skille specyficzne dla projektu tworzysz potem w `.claude/skills/` projektu
- Skille wieloprojektowe trafiają do `~/.claude/skills/`
