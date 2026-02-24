# Session State

<!-- Ten plik przechowuje stan sesji pracy z Claude Code.
     Używaj go gdy musisz wyczyścić kontekst i wrócić do pracy później.

     Komendy:
       /state-start  — zapisz aktualny postęp do tego pliku (przed /clear)
       /clear        — wyczyść kontekst (built-in komenda Claude Code)
       /catchup      — przywróć kontekst z tego pliku (po /clear lub nowej sesji)

     Workflow: /state-start → /clear → /exit → claude → /catchup
-->

## Ostatnia aktualizacja
2026-02-24 18:30:00

## Status
zakończona

## Aktualny cel
Stworzenie kompletnego, przyjaznego dokumentu onboardingowego dla nowej osoby dołączającej do środowiska Claude Code — jeden plik .docx dla macOS i Windows z prostym językiem, obrazkami, wstępem z korzyściami i sekcją "Co dalej?".

## Co zrobione
- Uproszczenie kroków dla użytkownika: z 9 do 6 ręcznych kroków (nvm, Homebrew, gh, jq przeniesione do Claude)
- Przepisanie języka na prosty — "dla 5-latka": "ciemne okienko" zamiast "terminal", etc.
- Dodanie mockupów wizualnych (Windsurf IDE, terminal, PowerShell) przez Pillow
- Wyłączenie automatycznych screenshotów (TAKE_SCREENSHOTS=False) po proteście użytkownika
- Dodanie wstępu z korzyściami (zielone bloki), wymaganiami (czerwone bloki), szacunkiem czasu
- Stworzenie wersji Windows: generate-onboarding-windows-docx.py + onboarding-windows.docx
- Analiza luk w dokumencie i onboardingu AI — znalezione i naprawione:
  - Brak "Co potrzebujesz przed startem" (konta Anthropic + GitHub) → dodano
  - Komenda npm niewidoczna w tekście Kroku 3 → dodano jawnie
  - Brak instrukcji tworzenia konta Anthropic w Kroku 5 → dodano
  - KRYTYCZNE: brak formatu settings.json w onboarding-prompt.md → dodano z heredoc
  - Brak sprawdzenia konta GitHub przed gh auth login → dodano
- Połączenie macOS + Windows w jeden onboarding.docx:
  - Kroki 1-2: sekcje "Na Macu:" (szary pasek) i "Na Windowsie:" (niebieski pasek)
  - Kroki 3-6: wspólne z notami gdzie się różni
  - Dwa bloki promptów (Mac + Windows) na jednej stronie
  - Nowa sekcja "Co dalej?" z 4 akcjami post-onboarding
  - Ramka "Który masz system?" we wstępie
- Poprawka WIN_HANDOFF_PROMPT: polskie znaki + settings.json czytelny wieloliniowo
- Usunięcie generate-onboarding-windows-docx.py i onboarding-windows.docx (zastąpione)
- Wszystkie zmiany commitowane i pushowane do GitHub

## Co zostało
- Weryfikacja onboarding.docx przez użytkownika (czy wygląda OK na Windowsie/Macu)
- Ewentualne drobne korekty treści po przejrzeniu

## Pliki
- `system/scripts/generate-onboarding-docx.py` — główny skrypt generujący .docx (przepisany, łączy macOS+Win)
- `docs/output/onboarding.docx` — końcowy dokument Word (~74KB, macOS+Windows)
- `setup/onboarding-prompt.md` — prompt handoff dla Claude (poprawiony, 9 kroków, format settings.json)
- `system/scripts/generate-onboarding-windows-docx.py` — USUNIĘTY (zastąpiony)
- `docs/output/onboarding-windows.docx` — USUNIĘTY (zastąpiony)

## Uwagi
- .docx używa legacy FORMCHECKBOX — klikalny w Word bez trybu Developer
- settings.json: absolutna ścieżka przez $HOME (bash heredoc) lub $env:USERPROFILE (PowerShell)
- TAKE_SCREENSHOTS=False — nie otwiera przeglądarki przy generowaniu
- Mockupy tworzone przez Pillow (auto-instalowany): terminal macOS (zielony), PowerShell (niebieski)
- WIN_HANDOFF_PROMPT używa PowerShell New-Item i Get-Content zamiast mkdir/cat
- Repo: https://github.com/PablosekRepo/template (main branch)
