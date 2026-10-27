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
2026-10-27 15:30:00

## Status
zakończona (kroki 1–4 audytu gotowe; czeka na decyzję usera o publikacji GitHub Pages)

## Aktualny cel
telemedi-growth-audit: sprawdzić, czy oficjalne „+52% pacjentów YoY” to zdrowy wzrost, czy iluzja (dane, budżet, rabaty, TelemediGO, koszty lekarzy). User = Growth Manager, Claude = Lead Data & Analytics Engineer. Zasada: nie przytakiwać, weryfikować w kodzie, każdy krok + jawne założenia w `docs/output/DECISION_LOG.md`.

## Co zrobione
- KROK 1 — audyt higieny danych (`01_data_audit.py`): strefy czasowe potwierdzone (orders/GO/users 100% czas PL, sesje/eventy UTC), identity stitching (FT stitched ≠ LT dla 22% pacjentów), 604 duplikaty ETL (2026-06-10…24), 22 konta TEST-QA (2 071 zamówień). „+52%” = nowi płacący pacjenci 1:1, więc to nie artefakt danych.
- KROK 2 — unit economics (`02_unit_economics.py`, `common.py` = dataset Clean Production C1–C3): CM2 +26,5% przy zamówieniach +55,7%; CM2/zam. 33,69 → 27,37 → 22,08 zł (IX 2026). Kody L4: CM1 dodatnie, CM2 ujemne, retencja 4–5%. Pediatra/psycholog z ujemnym CM1 bez rabatu. GO w R2: rabaty > opłaty (−39 tys. zł).
- KROK 3 — kohorty, lejek, change-points, wycena (`03_cohorts_and_funnels.py`): pacjent „umiera” po 120 dniach; „11% R1→R2” to artefakt kalendarzowy; spadek CR −2,18 pp = miks −2,80 pp, jakość +0,62 pp (Simpson); 24 zweryfikowane zdarzenia na osi czasu; przeciążenie internistów (4,2 → 11 min); płatności CRM 74–80% vs 94,6%; 10 inicjatyw = 232,6 tys. zł CM2/rok (201,7 tys. bez a3/c1).
- KROK 4 — dashboard: `04_build_dashboard.py` + `dashboard_template.html` → `index.html` (root) i `docs/output/index.html`, 1,60 MiB, 5 zakładek; `04_smoke_test.py`: 140 interakcji w Edge headless, 0 błędów JS, 0 NaN.
- Refaktor: logika CAC, kohort, lejka i przeżycia w `common.py`; raporty kroków 2 i 3 po refaktorze sprawdzone jako identyczne.
- Wszystko commitowane i pushowane do GitHub (main).

## Co zostało
- Decyzja usera: włączenie GitHub Pages (repo prywatne → wymaga płatnego planu, strona i tak publiczna) albo inny hosting.
- Domknięcie Known Unknowns (zakładka 5 dashboardu): biling lekarzy dla TEST-QA, test cenowy pediatra/psycholog, holdout GO, A/B in-app, logi bramki dla płatności CRM, A/B kodu L4SZYBKO20, krańcowy CAC e-recepty, stawki i grafiki lekarzy.

## Pliki
- `CLAUDE.md` — Project Overview audytu, powiadomienia Windows, reguły Clean Production
- `docs/output/DECISION_LOG.md` — log kroków 1–4, reguły C1–C3, założenia A1–A24
- `docs/output/scripts/common.py` — Dataset Clean Production, strefy, stitching, CAC, kohorty, lejek, przeżycie
- `docs/output/scripts/01_data_audit.py` — audyt higieny (surowe dane)
- `docs/output/scripts/02_unit_economics.py` — kaskada marży, kody, kanały, GO
- `docs/output/scripts/03_cohorts_and_funnels.py` — kohorty, KM, lejek + LMDI, change-points, wycena
- `docs/output/scripts/04_build_dashboard.py` — build dashboardu (agregaty + JSON do szablonu)
- `docs/output/scripts/dashboard_template.html` — HTML/CSS/JS dashboardu (Chart.js 4.4.1 z cdnjs)
- `docs/output/scripts/04_smoke_test.py` — weryfikacja index.html (node --check + Edge headless + zrzuty)
- `docs/output/0{1,2,3}_*_report.md` i `*_metrics.json` — raporty i metryki kroków
- `index.html`, `docs/output/index.html` — dashboard
- `.gitignore` — dodane `__pycache__/`

## Uwagi
- Python 3.14 bez pandas/tzdata — tylko stdlib (decyzja usera: nie instalujemy paczek). DST Warszawy liczony w kodzie.
- Koszt lekarza wg README: tylko completed + refunded (no-show = 0 zł, wariant no-show tylko jako wrażliwość) — user to zaakceptował.
- Konta testowe = 22 user_id z TEST-QA; wycinamy wszystkie ich 2 071 zamówień (nie tylko 1 781).
- Pełny rebuild: `python docs/output/scripts/0{1,2,3}_*.py` → `04_build_dashboard.py` → `04_smoke_test.py` (ok. 3 min).
- Surowe dane `docs/input/dane/*.csv` są w .gitignore — nigdy nie commitować.
- Repo: https://github.com/blaszczykrafal1-a11y/Test-modelu (main, prywatne).
