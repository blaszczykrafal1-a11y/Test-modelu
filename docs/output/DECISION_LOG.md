# DECISION LOG - telemedi-growth-audit

Log kroków, decyzji i jawnych założeń (Explicit Assumptions). Każda liczba ma źródło w skrypcie w `docs/output/scripts/`.
Format wpisu: kontekst → co sprawdziliśmy → wynik (twarde liczby) → decyzja / założenie → co dalej.

---

## KROK 1 - Setup i audyt higieny danych (2026-10-27)

**Skrypt:** `docs/output/scripts/01_data_audit.py` (stdlib, ~30 s)
**Pełny raport:** `docs/output/01_data_audit_report.md` · **metryki JSON:** `docs/output/01_data_audit_metrics.json`

### 1.1 Wolumeny i schemat

| tabela | wiersze | uwagi |
|---|---|---|
| sessions (8 plików) | 459,557 | 0 duplikatów `session_id`; `user_id` pusty w 77.19% (sesje niezalogowane) |
| events (5 plików) | 494,605 | 0 duplikatów; 5 znanych nazw zdarzeń; 162,033 sesji z ≥1 eventem |
| orders | 65,882 | **65,278 unikalnych `order_id`** (604 duplikaty) |
| users | 52,422 | 0 duplikatów |
| go_memberships | 4,227 | 686 (16.23%) bez `order_id` = GO kupione osobno |
| marketing_spend | 5,676 | 9 kampanii; 730 dni |

- Nulle tylko tam, gdzie wynikają z definicji: `started_at`/`duration_min` 6.35% (= cancelled + no_show), `promo_code` 82.61%, `rating` 71.40%, UTM 13.33% (direct).
- Integralność referencyjna czysta: 0 zamówień bez sesji / z nieistniejącą sesją / z innym `user_id` niż sesja / bez `payment_succeeded`; 0 eventów bez sesji; 0 `payment_succeeded` bez zamówienia lub GO; 0 naruszeń reguł biznesowych (kwoty vs rabat, refund vs status, GO bez aktywnego członkostwa, ważność GO = 12 mies.).
- Pliki partycjonowane są cięte o północy czasu polskiego (22:00/23:00 UTC), nie nakładają się.

### 1.2 Strefy czasowe - hipoteza usera: sesje/eventy w UTC, transakcje i spend w czasie PL

**Test:** różnica `orders.created_at` − `payment_succeeded.event_at_utc` w tej samej sesji vs oczekiwany offset Warszawy.

| tabela | dopasowanie do offsetu PL | rozkład |
|---|---|---|
| orders.created_at | **65,278 / 65,278 (100%)** | +120 min w CEST: 37,317; +60 min w CET: 27,961 |
| go_memberships.purchased_at | **4,227 / 4,227 (100%)** | |
| users.registered_at vs 1. `account_completed` | **52,422 / 52,422 (100%)** | |
| marketing_spend.date | **nierozstrzygalne z danych** | korelacja klików z sesjami płatnymi: dzień UTC 0.9952 vs dzień PL 0.9955; MAE 9.17 vs 9.12 |

**Werdykt: hipoteza POTWIERDZONA** dla orders/GO/users (DST obsłużony poprawnie, brak „stałego +1h”). Dla `marketing_spend` dane nie odróżniają UTC od PL (nocny ruch jest zbyt mały) → przyjmujemy README (dzień PL).

**Skala przesunięć po konwersji do Europe/Warsaw:**

| miara | n | % |
|---|---|---|
| Sesje lokalnie 22:00-02:00 | 40,640 | 8.84% |
| Sesje zmieniające dzień (UTC→PL) | 9,497 | 2.07% |
| Sesje zmieniające miesiąc | 299 | 0.07% |
| Zamówienia lokalnie 22:00-02:00 | 6,121 | 9.38% |
| Zamówienia: dzień PL ≠ dzień UTC | 1,594 | 2.44% |
| Zamówienia: naiwny join po dacie (sesja UTC vs zamówienie PL) - niezgodny dzień | 1,687 | 2.58% |
| Pacjenci: zmiana **dnia** kohorty 1. zamówienia | 1,302 | 3.18% |
| Pacjenci: zmiana **miesiąca** kohorty 1. zamówienia | 43 | 0.11% |

**Wniosek:** strefa czasowa psuje analizy dzienne (≈2.5% rekordów w złym dniu, np. dzienne CR i CAC), ale jest **pomijalna dla kohort miesięcznych i YoY** (0.1%). To nie jest źródło „+52%”.

### 1.3 Identity stitching (visitor_id ↔ user_id)

| miara | wartość |
|---|---|
| visitor_id ogółem | 365,078 |
| visitor_id kiedykolwiek zalogowane | 57,495 (15.75%) |
| pacjenci z 1 / 2 / 3 / 4 / 5+ visitor_id | 48,587 (92.68%) / 2,961 / 605 / 193 / 76 |
| visitor_id współdzielony przez >1 pacjenta | 0 |
| pacjenci z anonimową sesją PRZED 1. logowaniem | 14,096 (26.89%) |
| mediana dni od 1. anonimowego dotyku do 1. logowania | 1.2 |
| sesje anonimowe ogółem / mapowalne do znanego pacjenta | 354,726 / 15,608 (4.40%) |

**Zniekształcenie „nowych”:**
- Płacący pacjenci (user_id): **40,940**; płacące visitor_id: **45,495** → licznik na cookie zawyża kupujących o **+11.13%**.
- **4,555 z 24,338 (18.7%)** powtórnych zamówień przyszło z visitor_id, które analityka bez stitchingu widzi jako nowe → retencja zaniżona, „nowi” zawyżeni.

**Atrybucja pozyskania (40,940 nowych płacących pacjentów):**

| kanał | Last-Touch (sesja 1. zamówienia) | First-Touch tylko zalogowane | First-Touch ze stitchingiem |
|---|---|---|---|
| google_cpc | 32.44% | 33.31% | **36.94%** |
| direct | 22.88% | 21.83% | **16.03%** |
| seo | 18.76% | 18.49% | 17.98% |
| meta | 17.81% | 17.73% | 17.86% |
| tiktok | 3.89% | 4.08% | **5.27%** |
| referral | 2.16% | 2.33% | 2.96% |
| affiliate | 2.06% | 2.23% | 2.96% |

- FT(stitched) ≠ LT dla **9,044 (22.09%)** pacjentów; stitching zmienia FT dla **7,461 (18.22%)**.
- Główny przepływ: google_cpc→direct (1,741), google_cpc→seo (947), seo→direct (848), meta→direct (780).
- **Wniosek:** bez wstecznego stitchingu kanał `direct` jest przeszacowany o ~7 pp, a płatne kanały (Google CPC, TikTok) i afiliacja niedoszacowane. Paradoksalnie oznacza to, że **paid pozyskuje więcej, niż pokazuje Last-Touch** - CAC liczony na LT będzie zawyżony. Musimy to uwzględnić, zanim oskarżymy budżet o przepalanie.

### 1.4 Brudne dane i anomalie

1. **Duplikaty zamówień (incydent ETL):** 604 identyczne wiersze, wszystkie w oknie **2026-06-10 … 2026-06-24** (15 dni, ~40/dzień), tj. **35.97%** zamówień z tego okna zdublowane. Żadnych duplikatów poza oknem.
2. **Konta testowe na produkcji (`TEST-QA`):** **1,781** zamówień od **22** kont, wszystkie po **1.00 zł**, 100% `completed`, 100% internista. Te konta mają łącznie 2,071 zamówień (~94 na konto). Koszt lekarza 25 zł × 1,781 ≈ **42.7 tys. zł straty** przy ~1.8 tys. zł przychodu. Udział rośnie w czasie (4 zamówienia w 2024-10, 132 w 2026-06).
3. **Kody pozyskaniowe z wysokim zwrotem:**

| kod | od | rabat | % jako 1. zamówienie | % refunded | % cancelled |
|---|---|---|---|---|---|
| L4SZYBKO20 | 2025-11-04 | 22% | 100% | **14.38%** | 4.33% |
| TIKTOK25 | 2026-02-10 | 28% | 100% | **13.51%** | 3.90% |
| START10 | 2024-10-01 | 11% | 100% | 3.16% | 4.55% |
| RANKING10 | 2024-10-02 | 11% | 100% | 2.52% | 5.04% |
| WRACAM15 | 2024-10-06 | 17% | 0% (retencyjny) | 0.56% | 4.23% |
| bez kodu | - | - | - | 2.88% | 3.99% |

   Nowe kody L4 startują razem z nowymi kampaniami `meta_prosp_l4_szybko` (332 dni w spend → od ~2025-11) i `tt_prosp_l4_15min` (234 dni → od ~2026-02). `refunded` = wizyta odbyta, lekarz opłacony, pacjent dostaje zwrot → **czysta strata**.
4. **GO kupowane osobno** pojawia się dopiero w **2025-09 (225 sztuk w jednym miesiącu)**, potem 27–50/mies. Wygląda na start produktu lub akcję promocyjną; do zbadania w kroku GO.
5. **Skoki dzienne:** brak dużych skoków w górę na wolumenach podstawowych (sesje, zamówienia). Istotne spadki to święta (1.11, 25–26.12, 3.05): naturalne. Max sesji na visitor_id = 149, więc brak oczywistego bot-trafficu.

### 1.5 Kontekst YoY (rok 1 = 2024-10…2025-09, rok 2 = 2025-10…2026-09, czas PL)

| metryka | rok 1 | rok 2 | YoY |
|---|---|---|---|
| sesje | 162,909 | 296,648 | +82.1% |
| distinct visitor_id | 128,954 | 239,346 | +85.6% |
| rejestracje | 20,640 | 31,782 | +54.0% |
| zamówienia surowe | 25,269 | 40,613 | +60.7% |
| zamówienia po deduplikacji | 25,269 | 40,009 | +58.3% |
| zamówienia bez duplikatów i kont testowych | 24,716 | 38,491 | **+55.7%** |
| zamówienia refunded + cancelled (bez testów) | 1,522 | 3,168 | **+108.1%** |
| płacący pacjenci | 16,251 | 26,470 | +62.9% |
| **nowi płacący pacjenci** | 16,251 | 24,689 | **+51.9%** |
| nowi płacący bez kont testowych | 16,231 | 24,687 | +52.1% |
| pacjenci z roku 1 kupujący w roku 2 | - | 1,781 | **11.0% bazy roku 1** |
| przychód netto (paid − refund) | 2,230,744 | 3,229,645 | **+44.8%** |
| zakupy GO | 1,759 | 2,468 | +40.3% |
| spend CPC | 367,632 | 649,675 | **+76.7%** |

### 1.6 Werdykt kroku 1 i kontr-hipotezy

- **„+52% pacjentów” odtwarza się 1:1 jako nowi płacący pacjenci (+51.9%).** Higiena danych (duplikaty, testy, strefy czasowe) przesuwa ten wynik o <1 pp. **Kontr-hipoteza do hipotezy usera:** wzrost NIE jest artefaktem błędów w danych. Jeśli jest iluzją, to ekonomiczną, nie techniczną.
- Sygnały ostrzegawcze (do kroków 2+):
  - spend +76.7% vs nowi płacący +52.1% → blended CAC (spend CPC / nowy płacący) **22.62 → 26.32 zł (+16%)**;
  - przychód netto +44.8% < zamówienia +55.7% → spada wartość zamówienia (rabaty, miks);
  - zwroty i anulacje +108% przy +56% zamówień, skoncentrowane w nowych kodach L4;
  - CR sesja→zamówienie spada z 15.5% do 13.5% (ruch rośnie szybciej niż zakupy);
  - tylko 11% płacących z roku 1 kupiło w roku 2 → wzrost jest prawie w całości akwizycyjny.
- Uwaga metodologiczna: rok 1 to z definicji 100% nowych pacjentów (dane startują od zera), więc porównania „nowi vs powracający” rok do roku są asymetryczne. Retencję trzeba liczyć kohortowo (M+n), nie YoY.

### 1.7 Jawne założenia (Explicit Assumptions)

| # | założenie | uzasadnienie / ryzyko |
|---|---|---|
| A1 | Wszystkie analizy liczymy w czasie **Europe/Warsaw** (sesje i eventy konwertujemy z UTC). | Biznes (transakcje, spend) jest w PL; potwierdzone w 1.2. |
| A2 | Offset Warszawy liczymy regułą DST UE w kodzie (brak `tzdata`); niejednoznaczną godzinę przy zmianie czasu jesienią traktujemy jako CEST. | Wpływ: pojedyncze rekordy 1 h w roku. |
| A3 | Deduplikacja `orders` po `order_id`, zostawiamy pierwsze wystąpienie. | Duplikaty są identyczne w 100% kolumn. |
| A4 | **Konta testowe = 22 `user_id`, które kiedykolwiek użyły `TEST-QA`.** Wykluczamy WSZYSTKIE ich zamówienia (2,071, nie tylko 1,781), ale koszt lekarza za nie raportujemy osobno jako stratę operacyjną. | 1.00 zł, ~94 zamówień/konto: to nie są pacjenci. Ryzyko: wyciek kodu do realnych pacjentów; przeczy temu brak jakiegokolwiek innego wzorca. |
| A5 | **Nowy pacjent = `user_id` przy pierwszym opłaconym zamówieniu** (nie rejestracja, nie visitor_id). | Metryka zgodna z dashboardem (+52%). |
| A6 | Kanały: google cpc → `google_cpc`; meta / tiktok paid_social → `meta` / `tiktok`; google+bing organic → `seo`; puste UTM → `direct`; pozostałe wg `utm_medium`. | 10 kombinacji UTM, brak śmieci w danych. |
| A7 | **Atrybucja domyślna = First-Touch ze stitchingiem** (najwcześniejsza sesja dowolnego visitor_id kiedykolwiek powiązanego z pacjentem, do sesji 1. zamówienia). LT raportujemy obok. | Stitching zmienia kanał dla 18% pacjentów. Ograniczenie: nie widzimy visitorów nigdy niezalogowanych (cross-device bez logowania). |
| A8 | Rok 1 = 2024-10-01…2025-09-30, rok 2 = 2025-10-01…2026-09-30. | 12 vs 12 pełnych miesięcy. |
| A9 | `marketing_spend.date` = dzień PL (README). | Dane nie rozstrzygają (1.2). |

### 1.8 Następne kroki (propozycja)

1. **Unit economics per zamówienie i kohorta:** przychód − zwroty − koszt lekarza (25/100/200 zł za completed+refunded) − rabat − afiliacja 25 zł; osobno dla kodów L4 i TEST-QA.
2. **CAC per kanał** na atrybucji FT-stitched vs LT; payback.
3. **Retencja kohortowa** (M+1…M+12) z wykluczeniem kont testowych, przed i po starcie kampanii L4.
4. **TelemediGO:** kanibalizacja (rabat 50% u internisty vs 89 zł opłaty), skok osobnych zakupów w 2025-09.

---

## KROK 2 - Unit economics: P&L zamówienia i pacjenta (2026-10-27)

**Skrypty:** `docs/output/scripts/common.py` (dataset Clean Production, wspólny dla kroków 2+), `docs/output/scripts/02_unit_economics.py`
**Raport:** `docs/output/02_unit_economics_report.md` · **metryki:** `docs/output/02_unit_economics_metrics.json`

### 2.0 Twarde reguły czyszczenia - dataset „Clean Production” (obowiązują od kroku 2)

| # | reguła | efekt |
|---|---|---|
| C1 | Deduplikacja `orders` po `order_id` (okno ETL 2026-06-10…24). | −604 wiersze |
| C2 | **Wykluczamy wszystkie zamówienia 22 kont, które kiedykolwiek użyły `TEST-QA`**: 1,781 TEST-QA + 290 pozostałych. Raportujemy je osobno jako anomalię. | −2,071 → **63,207 zamówień, 40,918 pacjentów** |
| C3 | Wszystkie daty w Europe/Warsaw; atrybucja po identity stitchingu (visitor_id → user_id wstecz). | - |

**Odstępstwo od briefu (C2):** brief mówił o wycięciu 1,781 zamówień TEST-QA. Te same 22 konta mają jeszcze 290 zamówień: wszystkie po 89 zł, bez rabatu, 100% `refunded` (zwrot 89 zł), czyli test ścieżki płatność → zwrot. To nie są pacjenci, więc wycinamy 2,071 (zgodnie z A4 z kroku 1).

**Odstępstwo od briefu (koszt lekarza):** brief zakładał koszt lekarza także dla no-show. README mówi wprost: „Za `cancelled` i `no_show` kosztu lekarza nie ma”. Liczymy według README; wariant z no-show raportujemy jako wrażliwość: CM1 niższe o 28,875 zł (R1) i 47,500 zł (R2). Wniosków to nie zmienia.

### 2.1 Anomalia: konta TEST-QA

- Profil skryptu QA: 100% wejście bezpośrednie na `/konto`, desktop/Chrome, 1 visitor_id na konto, chat, wizyta 1 min, internista, godziny 9-17 w dni robocze (37% w poniedziałki), brak ocen. Konta mają 2,093 sesji zalogowanych i 0 anonimowych.
- Rośnie w czasie: 4 zamówienia / 1 konto w 2024-10 → 156 / 22 konta w 2026-06. Nowe konta QA dochodzą co 1-3 miesiące (ostatnie: 2026-02).
- **Scenariusz A (błąd wykluczenia z hurtowni, lekarz nieopłacony):** wpływ tylko na raportowanie (+2,071 zamówień, +22 „pacjentów”), CM1 +1,781 zł.
- **Scenariusz B (realny wyciek):** koszt lekarza 51,775 zł (2,071 × 25 zł, bo `refunded` też jest płatne) → CM1 **−49,994 zł**, obecnie ok. 3-4 tys. zł/mies. i rośnie.
- Dane nie rozstrzygają: `started_at` jest wypełnione (za B), ale wizyta 1-min na czacie to raczej automat (za A). **Do potwierdzenia eksportem rozliczeń z lekarzami.**

### 2.2 Kaskada marży R1 vs R2 (Clean Production)

| pozycja [PLN] | Rok 1 | Rok 2 | YoY | /zam. R1 | /zam. R2 |
|---|---|---|---|---|---|
| Gross Revenue | 2,523,464 | 3,903,771 | +54.7% | 102.10 | 101.42 |
| − Rabaty promo | 20,220 | 136,760 | **+576%** | 0.82 | 3.55 |
| − Rabaty GO | 128,516 | 258,813 | +101% | 5.20 | 6.72 |
| = Billed | 2,374,728 | 3,508,198 | +47.7% | 96.08 | 91.14 |
| − Zwroty cancelled | 98,577 | 141,323 | +43% | 3.99 | 3.67 |
| − Zwroty po wizycie (refunded) | 45,884 | 138,532 | **+202%** | 1.86 | 3.60 |
| + Opłaty GO | 156,551 | 219,652 | +40% | 6.33 | 5.71 |
| = Net Revenue | 2,386,817 | 3,447,994 | +44.5% | 96.57 | 89.58 |
| − Lekarz (completed + refunded) | 1,175,700 | 1,734,825 | +47.6% | 47.57 | 45.07 |
| = **CM1** | 1,211,117 | 1,713,169 | **+41.5%** | 49.00 | 44.51 |
| − Paid media | 367,632 | 649,675 | +76.7% | 14.87 | 16.88 |
| − Afiliacja | 10,925 | 10,125 | −7% | 0.44 | 0.26 |
| = **CM2** | 832,560 | 1,053,369 | **+26.5%** | **33.69** | **27.37** |

- Zamówienia +55.7%, CM2 tylko +26.5%. **CM2 na zamówienie spada o 19%** (33.69 → 27.37 zł), CM2 % gross z 33.0% do 27.0%.
- Miesięcznie: CM2/zamówienie ok. 31-35 zł przez cały R1 → spadek od 2026-02 → **22.08 zł we wrześniu 2026** (−35% vs R1). Erozja przyspiesza, nie wyhamowuje.
- Most CM2 (+220,809 zł): przyrost gross +1.38 mln zjadają: paid media −282k, rabaty −247k (promo −117k, GO −130k), zwroty −135k (w tym po wizycie −93k), koszt lekarza proporcjonalnie do wolumenu.

### 2.3 Kody rabatowe i L4 - weryfikacja hipotezy usera

**Hipoteza usera:** kampanie „szybkie L4” przyciągają pacjentów, którym lekarz odmawia L4 → zwrot po odbytej wizycie → **ujemne CM1**.

| kod | zam. | CM1/zam. | % refunded | pacjenci (1. zam.) | CAC FT | CM2 1. zam. | CM2 180d | % powrót 180d |
|---|---|---|---|---|---|---|---|---|
| brak kodu | 43,957 | 48.26 | 2.5% | 29,767 | 24.16 | 23.90 | 50.95 | 26.4% |
| **L4SZYBKO20** | 3,511 | **29.19** | **14.4%** | 3,511 | 32.35 | **−3.15** | 2.82 | **4.9%** |
| **TIKTOK25** | 1,665 | **26.35** | **13.5%** | 1,665 | 37.73 | **−11.38** | **−8.05** | **3.9%** |
| START10 | 3,386 | 38.37 | 3.2% | 3,386 | 24.71 | 13.66 | 40.06 | 24.9% |
| RANKING10 | 595 | 37.48 | 2.5% | 595 | 17.21 | 20.28 | 34.84 | 17.4% |
| GO (rabat GO) | 9,738 | 11.87 | 1.7% | 1,994 | 24.46 | 77.30* | 89.01* | 41.9% |

\* CM1 pacjenta zawiera opłatę GO 89 zł.

**Werdykt: mechanizm POTWIERDZONY, ale wniosek o ujemnym CM1 OBALONY.**
- Mechanizm: L4 u internisty w R2 ma 16.0% zwrotów z kodem L4 vs 8.3% bez kodu (n = 4,278 vs 5,582). Na celach innych niż L4 te same kody mają 0-3% zwrotów, więc problemem jest konkretnie odmowa zwolnienia.
- CM1 na zamówienie z L4SZYBKO20 jest **dodatnie: +29.19 zł**. Pojedyncze zwrócone zamówienie to −33.96 zł, ale stanowi tylko 14% zamówień; odbyte dają +40.82 zł. Różnica vs brak kodu (−19 zł/zam.) to głównie **rabat (20.00 zł/zam.)**, a dopiero potem zwroty (14.60 vs 6.84 zł/zam.).
- **Prawdziwy problem to CM2 i retencja:** CAC 32-38 zł vs 24 zł, powrót w 180 dni 4-5% vs 26%. Pacjent z kodu L4 przychodzi po jedno zwolnienie i nie wraca.
- **Ile przepaliliśmy na kodach L4 (5,176 pacjentów):** rabaty 111,845 zł + zwroty po wizycie 54,905 zł + lekarz za zwrócone wizyty 23,900 zł = **190,650 zł wycieku**. CAC 176,387 zł zjada całe CM1 tych pacjentów (157,838 zł) → **masa CM2 −18,549 zł**. Netto ta akwizycja nie zarobiła złotówki.
- 70% zamówień z L4SZYBKO20 przychodzi z `meta_prosp_l4_szybko`, 72% TIKTOK25 z `tt_prosp_l4_15min`.

### 2.4 Kanały: First-Touch (stitched) vs Last-Touch

| kanał FT | pacjenci | CAC | CM2 1. zam. | CM2 180d | CM2 365d (kohorta R1) | % powrót 180d | masa CM2 FT | masa CM2 LT |
|---|---|---|---|---|---|---|---|---|
| seo | 7,362 | 0 | 50.90 | 78.64 | 89.69 | 28.5% | 609,911 | 603,577 |
| direct | 6,541 | 0 | 51.09 | 78.89 | 88.24 | 29.2% | 543,955 | 539,093 |
| google_cpc | 15,122 | 42.07 | 7.06 | 32.71 | 39.66 | 27.2% | 527,720 | 533,335 |
| referral | 1,210 | 0 | 51.22 | 80.47 | 90.51 | 30.2% | 102,763 | 101,850 |
| meta | 7,311 | 40.86 | −0.82 | 11.15 | 22.74 | 14.1% | 56,797 | 66,425 |
| affiliate | 1,213 | 17.35 | 29.38 | 43.43 | 45.57 | 19.3% | 54,806 | 53,754 |
| **tiktok** | 2,159 | 38.20 | **−6.19** | **−3.61** | - (tylko R2) | **3.1%** | **−10,022** | −12,104 |

Kampanie (FT), które **nie spłacają się nigdy w obserwowanym oknie**:
- `gs_generic_specjalisci`: CAC 57.79, CM1 1. zamówienia tylko 22.16 (specjaliści mają strukturalnie niskie CM1, patrz 2.5) → CM2 365d **−13.66 zł/pacjenta**, masa −25,944 zł.
- `tt_prosp_l4_15min`: CM2 180d −3.61, powrót 3.1%, masa −10,022 zł.
- `meta_prosp_l4_szybko`: CM2 180d **+7.79**, ledwo nad kreską (powrót 5.5%).

Spłacają się po kolejnych wizytach (pod wodą lub ~0 na 1. zamówieniu, dodatnie w 180-365 dni): `gs_generic_lekarz_online` (−0.11 → +28.61), `gs_generic_erecepta` (−0.22 → +50.05), `meta_prosp_lekarz_online` (−4.92 → +20.07).

**Meta zmieniła charakter:** pacjenci FT z Meta 1,144 (R1) → 6,167 (R2), CM1 1. zamówienia 51.95 → 37.84 zł. Wzrost Meta to prawie w całości kampania L4.

**FT vs LT:** LT przenosi masę CM2 do kanałów bezkosztowych (direct +117k, seo +62k) i zaniża google_cpc (−123k) oraz meta (−28k vs FT). Na LT płatne kanały wyglądają gorzej, niż są. Wniosek o tiktok/L4 nie zależy od modelu atrybucji.

### 2.5 TelemediGO

| | Rok 1 | Rok 2 |
|---|---|---|
| członkostwa (w tym kupione osobno) | 1,759 (225) | 2,468 (461) |
| opłaty GO | 156,551 | 219,652 |
| rabaty GO udzielone | 128,516 | 258,813 |
| **opłaty − rabaty** | **+28,035** | **−39,161** |
| CM1 wizyt GO (bez opłat) | 37,153 | 78,416 |

- **Sam program już nie pokrywa rabatów:** w R2 rabaty przekraczają opłaty o 39 tys. zł. Zamknięte członkostwa (1,759): średnio 2.79 wizyty GO, opłata − rabaty = **−21.94 zł/członkostwo**, 39.9% członkostw dało rabaty > 89 zł.
- Z kosztem lekarza członkostwo nadal jest dodatnie na CM1: opłata + CM1 wizyt GO = **+121.76 zł/członkostwo**, bo internista z rabatem 50% to 44.50 − 25 = +19.50 zł.
- **Specjaliści na GO są pod wodą:** CM1/wizyta z rabatem GO: dermatolog/kardiolog/neurolog/urolog −12.80, pediatra −24.00, psycholog −20.80, ginekolog/endokrynolog −4.80. **Pediatra (−5.00) i psycholog (−1.00) są pod wodą nawet bez żadnego rabatu.** To problem cennika, niezależny od GO.
- Retencja (kohorta R1, 365 dni, 1. wizyta u internisty): GO przy 1. zamówieniu → 2.37 zam./pacjenta, 45.1% powrotu, CM1 123.77 zł; bez GO → 1.71, 27.4%, 93.55 zł. **Uwaga: samoselekcja.** To górna granica efektu GO, nie dowód przyczynowy.
- **Wrzesień 2025:** 225 osobnych zakupów GO, **100% z sesji e-mail `crm_go_upsell`** (start kampanii: 317 sesji vs ok. 50/mies. później), 100% kupujących to istniejący pacjenci, 0% miało wcześniej GO. To jednorazowy blast CRM do bazy, nie organiczny popyt. Efekt: 40% nigdy nie użyło GO; opłaty 20,025 zł vs rabaty 18,612 zł; CM1 wizyt +5,764 zł. Lekko na plus, ale **zawyżyło CM1 R1 we wrześniu 2025 (55.24 zł/zam. vs ~48 normalnie)**, czyli upiększyło bazę porównania YoY.

### 2.6 Jawne założenia kroku 2

| # | założenie | uzasadnienie / ryzyko |
|---|---|---|
| A10 | Koszt lekarza: 25 zł internista, 200 zł psychiatra, 100 zł pozostali; tylko `completed` + `refunded`. | README. No-show jako wrażliwość. |
| A11 | Opłaty GO (89 zł) to przychód w miesiącu zakupu, bez zwrotów; w P&L pacjenta wliczone do jego CM1. | Brak danych o zwrotach GO. |
| A12 | Prowizja afiliacyjna 25 zł naliczana, gdy sesja 1. opłaconego zamówienia pacjenta ma `utm_medium = affiliate` (842 pacjentów = 21,050 zł). | README nie mówi, jaki model atrybucji stosuje partner; po FT byłoby 1,213 × 25 zł. |
| A13 | **Cały koszt CPC i afiliacji obciąża pozyskanie nowych pacjentów.** CAC = koszt puli (kampania × miesiąc kohorty) / nowi pacjenci przypisani do tej puli (FT lub LT). 0 zł nieprzypisane. | Konserwatywne dla CAC: brand i retargeting częściowo obsługują powracających, więc CAC brandu/rmkt jest zawyżony, a reszty lekko zaniżony. |
| A14 | Organic, direct, referral, e-mail, SMS = 0 zł kosztu pozyskania. | README: koszt pomijalny / brak w danych. Brak kosztów SEO/CRM, więc ich CM2 jest zawyżone. |
| A15 | LTV porównujemy w równych oknach: 180 dni (1. zamówienie ≤ 2026-04-03) i 365 dni (kohorta R1). „Masa CM2” = cały obserwowany okres (różne okna, tylko jako suma). | Kampanie L4/TikTok startują w R2, więc nie mają okna 365 dni. |
| A16 | Rabat = `list_price − amount_paid`; Net Revenue = Billed − `refund_amount` + opłaty GO. | Spójne z danymi (0 naruszeń w kroku 1). |

### 2.7 Wnioski kroku 2 → co dalej

1. **Wzrost jest realny w przychodzie, ale jakość jednostki spada:** CM2/zamówienie −19% YoY i −35% we wrześniu 2026 vs średnia R1. Masa CM2 rośnie (+26.5%), ale wolniej niż wolumen, a trend miesięczny jest spadkowy.
2. **Najgorsze źródło to nie zwroty, tylko kampanie L4 i TikTok:** dodatnie CM1, ujemne lub zerowe CM2 i retencja 3-5%. To kupowanie jednorazowych transakcji.
3. **Strukturalna dziura cenowa u specjalistów** (pediatra, psycholog < 0 nawet bez rabatu; GO i promo pogłębiają) i kampania `gs_generic_specjalisci`, która nigdy się nie spłaca.
4. **GO w R2 przestało pokrywać własne rabaty** (−39k), ale broni się na CM1 i prawdopodobnie retencją. Do sprawdzenia kauzalnie.
5. Kolejny krok (proponowany): **retencja kohortowa M+1…M+12** per kanał/kod/GO i test „czy pacjenci L4 kiedykolwiek wracają po innej usłudze”; potem rekomendacje budżetowe (realokacja L4/TikTok → gs_generic_erecepta / brand / SEO).
