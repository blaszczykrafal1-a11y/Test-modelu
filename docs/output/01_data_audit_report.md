# 01 - Audyt higieny danych (wygenerowane przez scripts/01_data_audit.py)

Wygenerowano: 2026-10-27 13:49

## 1. Schemat, wolumeny, nulle, zakresy dat


### `sessions (8 plikow)` - 459,557 wierszy, 11 kolumn

| kolumna | nulle | % null | distinct | zakres / wartosci |
|---|---|---|---|---|
| session_id | 0 | 0.00% | 459,557 |  |
| visitor_id | 0 | 0.00% | 365,078 |  |
| user_id | 354,726 | 77.19% | 52,422 |  |
| started_at_utc | 0 | 0.00% | 457,193 | 2024-09-30 22:01:31 .. 2026-09-30 21:26:12 |
| utm_source | 61,245 | 13.33% | 8 | google=212565, meta=115428, tiktok=33470, newsletter=13945, rankinglekarzy=10016, polecenie=4741, sms=4203, bing=3944 |
| utm_medium | 61,245 | 13.33% | 7 | paid_social=148898, cpc=123867, organic=92642, email=13945, affiliate=10016, referral=4741, sms=4203 |
| utm_campaign | 163,903 | 35.67% | 14 |  |
| device | 0 | 0.00% | 3 | mobile=350624, desktop=96791, tablet=12142 |
| os | 0 | 0.00% | 5 | Android=229080, iOS=133686, Windows=75106, macOS=19705, Linux=1980 |
| browser | 0 | 0.00% | 9 | Chrome=185096, Safari=86675, Instagram=49918, Facebook=36017, TikTok=31687, Samsung Internet=30903, Firefox=17974, Edge=15961, Opera=5326 |
| landing_page | 0 | 0.00% | 21 |  |


### `events (5 plikow)` - 494,605 wierszy, 3 kolumn

| kolumna | nulle | % null | distinct | zakres / wartosci |
|---|---|---|---|---|
| session_id | 0 | 0.00% | 162,033 |  |
| event_name | 0 | 0.00% | 5 | service_selected=161325, slot_selected=113233, account_completed=82077, payment_started=72006, payment_succeeded=65964 |
| event_at_utc | 0 | 0.00% | 492,142 | 2024-09-30 22:14:45 .. 2026-09-30 21:34:11 |


### `orders` - 65,882 wierszy, 18 kolumn

| kolumna | nulle | % null | distinct | zakres / wartosci |
|---|---|---|---|---|
| order_id | 0 | 0.00% | 65,278 |  |
| user_id | 0 | 0.00% | 40,940 |  |
| session_id | 0 | 0.00% | 65,278 |  |
| created_at | 0 | 0.00% | 65,246 | 2024-10-01 05:24:16 .. 2026-09-30 23:34:11 |
| specialization | 0 | 0.00% | 10 | internista=49192, ginekolog=3116, dermatolog=3100, psychiatra=2947, pediatra=2788, endokrynolog=1614, kardiolog=1001, neurolog=824, urolog=783, psycholog=517 |
| visit_purpose | 0 | 0.00% | 4 | konsultacja=21927, e_recepta=21265, l4=17094, skierowanie=5596 |
| consultation_mode | 0 | 0.00% | 3 | phone=39404, chat=16763, video=9715 |
| scheduled_at | 0 | 0.00% | 53,610 | 2024-10-01 06:35:00 .. 2026-10-02 23:00:00 |
| started_at | 4,185 | 6.35% | 61,043 | 2024-10-01 06:36:48 .. 2026-10-02 23:06:31 |
| duration_min | 4,185 | 6.35% | 35 |  |
| list_price | 0 | 0.00% | 6 | 89.00=49192, 109.00=5708, 119.00=4730, 269.00=2947, 95.00=2788, 99.00=517 |
| discount_type | 0 | 0.00% | 3 | none=44590, promo=11459, go=9833 |
| promo_code | 54,423 | 82.61% | 6 | L4SZYBKO20=3575, START10=3412, TEST-QA=1810, TIKTOK25=1706, RANKING10=598, WRACAM15=358 |
| amount_paid | 0 | 0.00% | 28 |  |
| payment_method | 0 | 0.00% | 3 | blik=37359, card=20692, transfer=7831 |
| status | 0 | 0.00% | 4 | completed=59254, cancelled=2590, refunded=2443, no_show=1595 |
| refund_amount | 0 | 0.00% | 27 |  |
| rating | 47,043 | 71.40% | 5 | 5=9525, 4=6579, 3=2093, 2=507, 1=135 |


### `users` - 52,422 wierszy, 7 kolumn

| kolumna | nulle | % null | distinct | zakres / wartosci |
|---|---|---|---|---|
| user_id | 0 | 0.00% | 52,422 |  |
| registered_at | 0 | 0.00% | 52,387 | 2024-10-01 00:18:07 .. 2026-09-30 23:32:58 |
| birth_year | 0 | 0.00% | 67 |  |
| gender | 0 | 0.00% | 2 | K=30411, M=22011 |
| region | 0 | 0.00% | 16 |  |
| city_size | 0 | 0.00% | 4 | miasto_pow_200k=14688, wies=14617, miasto_do_50k=12505, miasto_50_200k=10612 |
| marketing_consent | 0 | 0.00% | 2 | 1=31010, 0=21412 |


### `go_memberships` - 4,227 wierszy, 7 kolumn

| kolumna | nulle | % null | distinct | zakres / wartosci |
|---|---|---|---|---|
| membership_id | 0 | 0.00% | 4,227 |  |
| user_id | 0 | 0.00% | 4,142 |  |
| purchased_at | 0 | 0.00% | 4,226 | 2024-10-01 05:24:16 .. 2026-09-30 20:48:08 |
| valid_until | 0 | 0.00% | 720 | 2025-10-01 .. 2027-09-30 |
| amount_paid | 0 | 0.00% | 1 | 89.00=4227 |
| order_id | 686 | 16.23% | 3,541 |  |
| session_id | 0 | 0.00% | 4,227 |  |


### `marketing_spend` - 5,676 wierszy, 7 kolumn

| kolumna | nulle | % null | distinct | zakres / wartosci |
|---|---|---|---|---|
| date | 0 | 0.00% | 730 | 2024-10-01 .. 2026-09-30 |
| utm_source | 0 | 0.00% | 3 | google=3650, meta=1792, tiktok=234 |
| utm_medium | 0 | 0.00% | 2 | cpc=3650, paid_social=2026 |
| utm_campaign | 0 | 0.00% | 9 | gs_brand=730, gs_generic_lekarz_online=730, gs_generic_erecepta=730, gs_generic_l4=730, gs_generic_specjalisci=730, meta_prosp_lekarz_online=730, meta_rmkt_koszyk=730, meta_prosp_l4_szybko=332, tt_prosp_l4_15min=234 |
| impressions | 0 | 0.00% | 2,405 |  |
| clicks | 0 | 0.00% | 292 |  |
| spend_pln | 0 | 0.00% | 5,238 |  |


### Pliki partycjonowane - zakresy

| plik | wiersze | min UTC | max UTC |
|---|---|---|---|
| sessions_2024q4.csv | 38,490 | 2024-09-30 22:01:31 | 2024-12-31 22:55:51 |
| sessions_2025q1.csv | 46,524 | 2024-12-31 23:08:01 | 2025-03-31 21:51:31 |
| sessions_2025q2.csv | 40,384 | 2025-03-31 22:03:33 | 2025-06-30 21:41:50 |
| sessions_2025q3.csv | 37,511 | 2025-06-30 22:13:06 | 2025-09-30 21:57:58 |
| sessions_2025q4.csv | 52,797 | 2025-09-30 22:00:58 | 2025-12-31 22:55:13 |
| sessions_2026q1.csv | 80,728 | 2025-12-31 23:00:22 | 2026-03-31 21:59:28 |
| sessions_2026q2.csv | 84,383 | 2026-03-31 22:00:19 | 2026-06-30 21:59:15 |
| sessions_2026q3.csv | 78,740 | 2026-06-30 22:01:41 | 2026-09-30 21:26:12 |
| events_2024h2.csv | 39,510 | 2024-09-30 22:14:45 | 2024-12-31 22:56:28 |
| events_2025h1.csv | 101,513 | 2024-12-31 23:09:16 | 2025-06-30 21:43:09 |
| events_2025h2.csv | 109,052 | 2025-06-30 22:14:41 | 2025-12-31 22:55:28 |
| events_2026h1.csv | 168,991 | 2025-12-31 23:29:14 | 2026-06-30 21:54:02 |
| events_2026h2.csv | 75,539 | 2026-06-30 22:01:56 | 2026-09-30 21:34:11 |

Granice plikow wypadaja o 22:00/23:00 UTC = polnoc czasu polskiego: eksport ciety po dniu PL, mimo ze kolumny sa w UTC (to potwierdza, ze `*_utc` jest naprawde UTC).

## 2. Duplikaty ID

| klucz | wiersze | unikalne klucze | klucze zduplikowane | nadmiarowe wiersze | w tym identyczne wiersze | w tym konfliktowe |
|---|---|---|---|---|---|---|
| sessions.session_id | 459,557 | 459,557 | 0 | 0 | 0 | 0 |
| events (session_id, event_name, event_at_utc) | 494,605 | 494,605 | 0 | 0 | 0 | 0 |
| events (session_id, event_name) | 494,605 | 494,605 | 0 | 0 | 0 | 0 |
| orders.order_id | 65,882 | 65,278 | 604 | 604 | 604 | 0 |
| orders (user_id, created_at) | 65,882 | 65,278 | 604 | 604 | 604 | 0 |
| orders.session_id | 65,882 | 65,278 | 604 | 604 | 604 | 0 |
| users.user_id | 52,422 | 52,422 | 0 | 0 | 0 | 0 |
| go_memberships.membership_id | 4,227 | 4,227 | 0 | 0 | 0 | 0 |
| marketing_spend (date, source, medium, campaign) | 5,676 | 5,676 | 0 | 0 | 0 | 0 |

Zduplikowane session_id wystepujace w >1 pliku (nakladanie eksportow): **0** z 0.
Kolumny rozniace sie w zduplikowanych order_id: brak (pelne duplikaty)
Duplikaty order_id per miesiac: 2026-06: 604

## 3. Strefy czasowe - weryfikacja hipotezy UTC vs Europe/Warsaw


### orders.created_at: porownanie z `payment_succeeded` (UTC) w tej samej sesji

| wynik | n | % |
|---|---|---|
| = offset PL (CET/CEST) | 65,278 | 100.00% |

Przetestowano 65,278; bez eventu payment_succeeded: 0; z >1 payment_succeeded: 0 (pominiete). Najczestsze pary (sezon, roznica min): ('CEST', 120): 37,317, ('CET', 60): 27,961

### go_memberships.purchased_at: porownanie z `payment_succeeded` (UTC) w tej samej sesji

| wynik | n | % |
|---|---|---|
| = offset PL (CET/CEST) | 4,227 | 100.00% |

Przetestowano 4,227; bez eventu payment_succeeded: 0; z >1 payment_succeeded: 0 (pominiete). Najczestsze pary (sezon, roznica min): ('CEST', 120): 2,536, ('CET', 60): 1,691

### users.registered_at vs pierwszy `account_completed` uzytkownika (UTC)

| wynik | n | % |
|---|---|---|
| = offset PL | 52,422 | 100.00% |

Uwaga: pacjent zalogowany na wejsciu nie ma account_completed, a account_completed moze byc logowaniem - stad czesc 'rejestracja wczesniej'.

### marketing_spend.date: clicks vs liczba sesji platnych (dzien x kampania)

| agregacja sesji | korelacja | MAE (klik/dzien/kampania) | sesje / klik |
|---|---|---|---|
| dzien UTC | 0.9952 | 9.17 | 0.841 |
| dzien Europe/Warsaw | 0.9955 | 9.12 | 0.841 |

Dni x kampanie z klikami > 0, ale bez zadnej sesji platnej (dzien PL): 0 z 5,676.

### Przesuniecia dnia/miesiaca kohortowego po konwersji do Europe/Warsaw

| miara | n | % bazy |
|---|---|---|
| Sesje: lokalnie 22:00-02:00 (PL) | 40,640 | 8.84% |
| Sesje: zmiana dnia UTC -> PL | 9,497 | 2.07% |
| Sesje: zmiana miesiaca UTC -> PL | 299 | 0.07% |
| Zamowienia: lokalnie 22:00-02:00 (PL) | 6,121 | 9.38% |
| Zamowienia: dzien PL != dzien UTC | 1,594 | 2.44% |
| Zamowienia: miesiac PL != miesiac UTC | 51 | 0.08% |
| Zamowienia: naiwny join (dzien sesji UTC != dzien zamowienia PL) | 1,687 | 2.58% |
| Pacjenci: dzien kohorty 1. zamowienia zmienia sie UTC vs PL | 1,302 | 3.18% |
| Pacjenci: MIESIAC kohorty 1. zamowienia zmienia sie UTC vs PL | 43 | 0.11% |


## 4. Identity stitching (visitor_id <-> user_id)

| visitor_id na pacjenta | pacjenci | % |
|---|---|---|
| 1 | 48,587 | 92.68% |
| 2 | 2,961 | 5.65% |
| 3 | 605 | 1.15% |
| 4 | 193 | 0.37% |
| 5+ | 76 | 0.14% |

Visitor_id ogolem: 365,078; z kiedykolwiek zalogowanym user_id: 57,495 (15.75%); visitor_id wspoldzielony przez >1 pacjenta: 0.
| miara | wartosc |
|---|---|
| Pacjenci z sesjami (user_id w sesjach) | 52,422 |
| Pacjenci z anonimowymi sesjami PRZED 1. sesja zalogowana | 14,096 (26.89%) |
| Liczba takich anonimowych sesji (do wstecznego zmapowania) | 14,096 |
| Mediana dni od 1. anonimowego dotyku do 1. logowania | 1.2 |
| Sesje anonimowe ogolem | 354,726 |
| ...z visitor_id, ktory kiedykolwiek byl zalogowany (mapowalne wstecz/wprzod) | 15,608 (4.40%) |


### Jak brak stitchingu zawyza 'nowych' pacjentow

Pacjenci z zamowieniem (user_id): **40,940**; distinct visitor_id, ktore zaplacily: **45,495** -> licznik na cookie zawyza 'kupujacych' o 11.13%.
Zamowienia powracajacych pacjentow (2.+ zamowienie) zlozone z NOWEGO visitor_id (widocznego jako nowy klient w analityce bez stitchingu): **4,555** z 24,338 powtornych zamowien.

### Atrybucja pozyskania: First-Touch (z/bez stitchingu) vs Last-Touch

| kanal | Last-Touch (sesja 1. zamowienia) | First-Touch tylko sesje zalogowane | First-Touch ze stitchingiem visitor_id |
|---|---|---|---|
| google_cpc | 13,280 (32.44%) | 13,637 (33.31%) | 15,122 (36.94%) |
| direct | 9,366 (22.88%) | 8,938 (21.83%) | 6,563 (16.03%) |
| seo | 7,682 (18.76%) | 7,569 (18.49%) | 7,362 (17.98%) |
| meta | 7,293 (17.81%) | 7,258 (17.73%) | 7,311 (17.86%) |
| tiktok | 1,593 (3.89%) | 1,671 (4.08%) | 2,159 (5.27%) |
| referral | 884 (2.16%) | 954 (2.33%) | 1,210 (2.96%) |
| affiliate | 842 (2.06%) | 913 (2.23%) | 1,213 (2.96%) |

Nowi pacjenci z atrybucja: 40,940. Kanal FT(stitched) != LT: **9,044 (22.09%)**. FT(stitched) != FT(tylko zalogowane): **7,461 (18.22%)**.
Najczestsze przejscia FT(stitched) -> LT (gdy rozne): google_cpc->direct: 1,741, google_cpc->seo: 947, seo->direct: 848, meta->direct: 780, google_cpc->meta: 718, seo->google_cpc: 493, meta->google_cpc: 421, meta->seo: 404, direct->seo: 395, seo->meta: 373, direct->google_cpc: 363, direct->meta: 298, tiktok->direct: 225, affiliate->direct: 142, tiktok->google_cpc: 135, referral->direct: 123, tiktok->seo: 122, affiliate->seo: 87, tiktok->meta: 84, affiliate->google_cpc: 81, referral->seo: 79, referral->google_cpc: 71, affiliate->meta: 61, referral->meta: 53

## 5. Brudne dane i anomalie

| kontrola | n | % bazy |
|---|---|---|
| Zamowienia bez session_id | 0 | 0.00% |
| Zamowienia z session_id nieistniejacym w sessions | 0 | 0.00% |
| Zamowienia: user_id sesji != user_id zamowienia | 0 | 0.00% |
| Zamowienia: sesja bez eventu payment_succeeded | 0 | 0.00% |
| Zamowienia: user_id nieistniejacy w users | 0 | 0.00% |
| Zamowienia: created_at przed registered_at | 0 | 0.00% |
| Zamowienia: created_at (->UTC) przed startem sesji | 0 | 0.00% |
| Eventy bez sesji (orphan) | 0 | 0.00% |
| Eventy wczesniej niz start sesji | 0 | 0.00% |
| Sesje bez zadnego eventu (bounce wg README) | 297,524 | 64.74% |
| Sesje z payment_succeeded bez zamowienia i bez GO | 0 | 0.00% |


### Spojnosc biznesowa zamowien

| kontrola | n | % zamowien |
|---|---|---|
| brak | 0 | 0% |

GO: waznosc != 12 mies.: 0; nakladajace sie czlonkostwa tego samego pacjenta: 0; order_id GO nieistniejacy w orders: 0; kwoty: {'89.00': 4227}.

### Kody promocyjne per miesiac (top 3)

| miesiac | zamowienia promo | top kody |
|---|---|---|
| 2024-10 | 135 | START10=110, RANKING10=20, TEST-QA=4 |
| 2024-11 | 159 | START10=120, RANKING10=29, TEST-QA=7 |
| 2024-12 | 199 | START10=147, TEST-QA=23, RANKING10=20 |
| 2025-01 | 230 | START10=159, RANKING10=38, TEST-QA=17 |
| 2025-02 | 207 | START10=135, TEST-QA=32, RANKING10=27 |
| 2025-03 | 240 | START10=159, RANKING10=38, TEST-QA=29 |
| 2025-04 | 216 | START10=125, TEST-QA=45, RANKING10=30 |
| 2025-05 | 203 | START10=132, TEST-QA=37, WRACAM15=18 |
| 2025-06 | 194 | START10=97, TEST-QA=66, RANKING10=19 |
| 2025-07 | 196 | START10=101, TEST-QA=65, RANKING10=18 |
| 2025-08 | 207 | START10=98, TEST-QA=66, RANKING10=22 |
| 2025-09 | 240 | START10=117, TEST-QA=87, RANKING10=23 |
| 2025-10 | 269 | START10=135, TEST-QA=94, WRACAM15=20 |
| 2025-11 | 374 | START10=167, L4SZYBKO20=84, TEST-QA=82 |
| 2025-12 | 508 | L4SZYBKO20=203, START10=163, TEST-QA=104 |
| 2026-01 | 653 | L4SZYBKO20=318, START10=189, TEST-QA=97 |
| 2026-02 | 777 | L4SZYBKO20=382, START10=191, TEST-QA=105 |
| 2026-03 | 955 | L4SZYBKO20=416, START10=199, TIKTOK25=159 |
| 2026-04 | 915 | L4SZYBKO20=358, TIKTOK25=241, START10=162 |
| 2026-05 | 956 | L4SZYBKO20=391, TIKTOK25=253, START10=165 |
| 2026-06 | 884 | L4SZYBKO20=355, TIKTOK25=241, TEST-QA=132 |
| 2026-07 | 843 | L4SZYBKO20=333, TIKTOK25=227, TEST-QA=128 |
| 2026-08 | 828 | L4SZYBKO20=321, TIKTOK25=246, START10=116 |
| 2026-09 | 905 | L4SZYBKO20=350, TIKTOK25=252, START10=160 |


### Konta testowe (TEST-QA) i jakosc kodow promocyjnych

Zamowienia z kodem TEST-QA: **1,781** od **22** kont; kwoty zaplacone: {'1.00': 1781}; statusy: {'completed': 1781}; specjalizacje: {'internista': 1781}. Wszystkie zamowienia tych kont: 2,071 (srednio 94 na konto). Koszt lekarza (25 zl x completed) przy przychodzie 1 zl/wizyte: ~42,744 zl straty.
| kod | zamowienia | pierwsze uzycie | dominujacy rabat | % jako 1. zamowienie pacjenta | % refunded | % cancelled | % no_show |
|---|---|---|---|---|---|---|---|
| L4SZYBKO20 | 3,511 | 2025-11-04 | 22% | 100.00% | 14.38% | 4.33% | 2.56% |
| RANKING10 | 595 | 2024-10-02 | 11% | 100.00% | 2.52% | 5.04% | 2.52% |
| START10 | 3,386 | 2024-10-01 | 11% | 100.00% | 3.16% | 4.55% | 2.75% |
| TEST-QA | 1,781 | 2024-10-21 | 99% | 1.01% | 0.00% | 0.00% | 0.00% |
| TIKTOK25 | 1,665 | 2026-02-10 | 28% | 100.00% | 13.51% | 3.90% | 2.22% |
| WRACAM15 | 355 | 2024-10-06 | 17% | 0.00% | 0.56% | 4.23% | 3.38% |
| (bez kodu) | 53,985 |  |  |  | 2.88% | 3.99% | 2.47% |

Okno duplikatow zamowien: 2026-06-10 .. 2026-06-24 (15 dni), 604 zdublowanych z 1,679 unikalnych zamowien w oknie (35.97%) - wyglada na podwojny load ETL.
GO kupione osobno (bez zamowienia) per miesiac: 2025-09: 225, 2025-10: 27, 2025-11: 34, 2025-12: 46, 2026-01: 36, 2026-02: 33, 2026-03: 47, 2026-04: 40, 2026-05: 40, 2026-06: 50, 2026-07: 39, 2026-08: 38, 2026-09: 31

### Podejrzane skoki dziennych wolumenow (dzien PL, vs mediana +/-14 dni)

| metryka | dzien | wartosc | mediana okna | x mediany |
|---|---|---|---|---|
| orders_promo | 2025-05-08 | 15 | 5 | 3.00 |
| orders_promo | 2025-01-05 | 18 | 6 | 3.00 |
| orders_promo | 2025-07-22 | 17 | 6 | 2.83 |
| orders_promo | 2025-11-03 | 27 | 10 | 2.70 |
| orders_promo | 2025-03-31 | 21 | 8 | 2.62 |
| orders_promo | 2024-12-11 | 15 | 6 | 2.50 |
| go_purchases | 2026-01-26 | 17 | 7 | 2.43 |
| orders_cancel_refund | 2025-08-26 | 12 | 5 | 2.40 |
| orders_cancel_refund | 2025-03-06 | 12 | 5 | 2.40 |
| go_purchases | 2026-09-01 | 12 | 5 | 2.40 |
| orders_promo | 2025-09-16 | 14 | 6 | 2.33 |
| orders_promo | 2025-09-02 | 14 | 6 | 2.33 |
| orders_promo | 2025-06-09 | 14 | 6 | 2.33 |
| orders_promo | 2025-04-28 | 14 | 6 | 2.33 |
| orders_promo | 2025-01-06 | 14 | 6 | 2.33 |
| orders_promo | 2025-03-13 | 16 | 7 | 2.29 |
| go_purchases | 2025-09-16 | 25 | 11 | 2.27 |
| orders_cancel_refund | 2025-02-05 | 11 | 5 | 2.20 |
| go_purchases | 2025-07-02 | 11 | 5 | 2.20 |
| orders_promo | 2025-05-12 | 13 | 6 | 2.17 |
| orders_promo | 2024-12-23 | 13 | 6 | 2.17 |
| orders_cancel_refund | 2025-11-12 | 13 | 6 | 2.17 |
| go_purchases | 2026-03-30 | 15 | 7 | 2.14 |
| orders_promo | 2025-09-25 | 17 | 8 | 2.12 |
| orders_promo | 2025-10-27 | 19 | 9 | 2.11 |
| go_purchases | 2025-09-18 | 23 | 11 | 2.09 |
| orders_promo | 2025-09-08 | 16 | 8 | 2.00 |
| orders_promo | 2025-09-03 | 14 | 7 | 2.00 |
| orders_promo | 2025-08-18 | 14 | 7 | 2.00 |
| orders_promo | 2025-08-14 | 14 | 7 | 2.00 |
| new_visitors | 2025-11-01 | 116 | 362 | 0.32 |
| spend_pln | 2025-11-01 | 362 | 1,115 | 0.32 |
| spend_pln | 2024-12-25 | 403 | 1,090 | 0.37 |
| spend_pln | 2024-11-01 | 367 | 946 | 0.39 |
| new_visitors | 2025-05-03 | 122 | 308 | 0.40 |
| new_visitors | 2025-12-26 | 203 | 510 | 0.40 |
| registrations | 2025-12-25 | 34 | 85 | 0.40 |
| registrations | 2024-11-01 | 24 | 59 | 0.41 |
| spend_pln | 2025-12-26 | 666 | 1,598 | 0.42 |
| spend_pln | 2025-05-03 | 419 | 994 | 0.42 |

Lacznie flag: 334 (w gore: 92, istotne spadki przy medianie >= 20: 35). Per metryka: orders_cancel_refund=114, orders_promo=102, go_purchases=86, spend_pln=12, new_visitors=11, registrations=4, sessions=3, payment_succeeded=1, orders=1. Spadki przy medianie < 20 to glownie szum malych licznikow.

### Wolumeny miesieczne (PL)

| miesiac | sessions | new_visitors | payment_succeeded | orders | orders_promo | orders_cancel_refund | registrations | go_purchases | spend_pln |
|---|---|---|---|---|---|---|---|---|---|
| 2024-10 | 11,499 | 8,835 | 1,355 | 1,355 | 135 | 82 | 1,625 | 77 | 27,160 |
| 2024-11 | 12,699 | 9,427 | 1,643 | 1,643 | 159 | 95 | 1,789 | 97 | 28,962 |
| 2024-12 | 14,292 | 10,453 | 1,956 | 1,956 | 199 | 125 | 1,893 | 110 | 31,130 |
| 2025-01 | 15,832 | 11,372 | 2,238 | 2,238 | 230 | 142 | 2,074 | 128 | 34,406 |
| 2025-02 | 14,733 | 10,430 | 2,211 | 2,211 | 207 | 135 | 1,959 | 113 | 32,760 |
| 2025-03 | 15,959 | 10,950 | 2,471 | 2,471 | 240 | 152 | 2,065 | 156 | 35,399 |
| 2025-04 | 14,761 | 9,972 | 2,398 | 2,398 | 216 | 168 | 1,809 | 145 | 33,289 |
| 2025-05 | 13,393 | 8,717 | 2,304 | 2,304 | 203 | 148 | 1,603 | 139 | 29,361 |
| 2025-06 | 12,230 | 7,839 | 2,123 | 2,123 | 194 | 131 | 1,427 | 157 | 27,733 |
| 2025-07 | 12,162 | 7,762 | 2,179 | 2,179 | 196 | 134 | 1,457 | 134 | 29,040 |
| 2025-08 | 12,138 | 7,800 | 2,118 | 2,118 | 207 | 143 | 1,363 | 133 | 28,419 |
| 2025-09 | 13,211 | 8,404 | 2,498 | 2,273 | 240 | 142 | 1,576 | 370 | 29,973 |
| 2025-10 | 14,784 | 9,622 | 2,566 | 2,539 | 269 | 177 | 1,757 | 176 | 31,860 |
| 2025-11 | 17,459 | 11,820 | 2,851 | 2,817 | 374 | 201 | 2,180 | 194 | 36,825 |
| 2025-12 | 20,554 | 14,177 | 3,125 | 3,079 | 508 | 229 | 2,444 | 217 | 44,405 |
| 2026-01 | 24,717 | 17,353 | 3,711 | 3,675 | 653 | 262 | 3,019 | 242 | 52,194 |
| 2026-02 | 25,604 | 18,012 | 3,601 | 3,568 | 777 | 270 | 2,975 | 189 | 52,694 |
| 2026-03 | 30,407 | 21,786 | 4,153 | 4,106 | 955 | 337 | 3,401 | 245 | 65,738 |
| 2026-04 | 29,896 | 21,565 | 3,735 | 3,695 | 915 | 327 | 2,913 | 214 | 64,197 |
| 2026-05 | 27,765 | 19,604 | 3,644 | 3,604 | 956 | 328 | 2,831 | 216 | 60,478 |
| 2026-06 | 26,722 | 19,141 | 3,387 | 3,337 | 884 | 314 | 2,561 | 217 | 59,731 |
| 2026-07 | 25,930 | 18,477 | 3,258 | 3,219 | 843 | 290 | 2,558 | 209 | 60,659 |
| 2026-08 | 25,914 | 18,639 | 3,186 | 3,148 | 828 | 304 | 2,496 | 183 | 58,805 |
| 2026-09 | 26,896 | 19,522 | 3,253 | 3,222 | 905 | 344 | 2,647 | 166 | 62,092 |

Top visitor_id wg liczby sesji: vaae49a0f=149, vc1f9fa84=147, v6e75a6ad=143, vf597bfe9=143, v60317435=124

## 6. Kontekst YoY (rok 1: 2024-10..2025-09, rok 2: 2025-10..2026-09; czas PL)

| metryka | rok 1 | rok 2 | YoY |
|---|---|---|---|
| sessions | 162,909 | 296,648 | +82.1% |
| distinct_visitors | 128,954 | 239,346 | +85.6% |
| registrations | 20,640 | 31,782 | +54.0% |
| orders_raw | 25,269 | 40,613 | +60.7% |
| orders_dedup | 25,269 | 40,009 | +58.3% |
| orders_dedup_no_test | 24,716 | 38,491 | +55.7% |
| orders_not_cancelled | 24,239 | 38,467 | +58.7% |
| orders_completed | 23,081 | 35,637 | +54.4% |
| orders_refunded_or_cancelled_no_test | 1,522 | 3,168 | +108.1% |
| paying_users | 16,251 | 26,470 | +62.9% |
| new_paying_users | 16,251 | 24,689 | +51.9% |
| new_paying_users_no_test | 16,231 | 24,687 | +52.1% |
| returning_users_from_y1 | 0 | 1,781 | n/a |
| revenue_net_pln | 2,230,744 | 3,229,645 | +44.8% |
| go_purchases | 1,759 | 2,468 | +40.3% |
| spend_pln | 367,632 | 649,675 | +76.7% |

