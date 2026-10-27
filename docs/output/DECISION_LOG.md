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
