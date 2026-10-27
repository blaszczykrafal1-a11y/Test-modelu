# 02 - Unit economics (scripts/02_unit_economics.py)

Wygenerowano: 2026-10-27 14:00

## 0. Dataset Clean Production

| etap | zamowienia |
|---|---|
| surowe wiersze orders.csv | 65,882 |
| - duplikaty ETL (C1) | -604 |
| - zamowienia kont testowych (C2): TEST-QA | -1,781 |
| - zamowienia kont testowych (C2): pozostale zamowienia tych 22 kont | -290 |
| = Clean Production | 63,207 |

Pacjenci produkcyjni z zamowieniem: 40,918. GO produkcyjne: 4,227 (testowe: 0).

## 1. Anomalia: 22 konta TEST-QA

| cecha | wartosc |
|---|---|
| zamowienia (TEST-QA / pozostale) | 1,781 / 290 |
| sesje zalogowane tych kont / w tym z zamowieniem | 2,093 / 2,071 |
| visitor_id / sesje anonimowe tych visitorow | 22 / 0 |
| kanal sesji zamowien | {'direct': 2071} |
| urzadzenie / przegladarka | {('desktop', 'Chrome'): 2071} |
| landing page | {'/konto': 2071} |
| godziny zamowien (PL) | 9:00-17:59 |
| dni tygodnia (0=pon) | {0: 767, 1: 330, 2: 304, 3: 344, 4: 326} |
| tryb / specjalizacja | {'chat': 2071} / {'internista': 2071} |
| czas trwania wizyty [min] | {'1': 2071} |
| statusy TEST-QA | {'completed': 1781} |
| statusy pozostalych | {'refunded': 290} |
| kwoty pozostalych / refund | {89.0: 290} / {89.0: 290} |
| GO kont testowych | 0 |

**Zachowanie w czasie** (miesiac: zamowienia / aktywne konta / koszt lekarza w scenariuszu B):
2024-10: 4/1/100, 2024-11: 7/2/175, 2024-12: 24/6/600, 2025-01: 20/7/500, 2025-02: 38/9/950, 2025-03: 36/9/900, 2025-04: 57/11/1 425, 2025-05: 42/13/1 050, 2025-06: 71/16/1 775, 2025-07: 75/17/1 875, 2025-08: 77/18/1 925, 2025-09: 102/20/2 550, 2025-10: 107/20/2 675, 2025-11: 104/19/2 600, 2025-12: 119/20/2 975, 2026-01: 109/20/2 725, 2026-02: 119/22/2 975, 2026-03: 142/22/3 550, 2026-04: 125/21/3 125, 2026-05: 129/21/3 225, 2026-06: 156/22/3 900, 2026-07: 149/22/3 725, 2026-08: 137/22/3 425, 2026-09: 122/20/3 050
Daty pierwszego zamowienia 22 kont (nowe konta QA dochodza w czasie): 2024-10-21, 2024-11-29, 2024-12-02, 2024-12-06, 2024-12-11, 2024-12-23, 2025-01-14, 2025-02-04, 2025-02-12, 2025-02-24, 2025-04-10, 2025-05-26, 2025-05-28, 2025-06-12, 2025-06-13, 2025-06-25, 2025-07-22, 2025-08-26, 2025-09-17, 2025-09-29, 2026-02-02, 2026-02-13
| scenariusz | przychod netto | koszt lekarza | wynik CM1 |
|---|---|---|---|
| A: blad wykluczenia kont testowych z hurtowni (wizyty nieprawdziwe, lekarz nie rozliczany) | 1 781 | 0 | 1 781 |
| B: realny wyciek - lekarz rozliczany wg reguly README (completed + refunded) | 1 781 | 51 775 | -49 994 |

Za A przemawia: 1-minutowe wizyty, sam chat, godziny 9-17 w dni robocze, jeden desktop/Chrome na konto, brak ocen, 290 zamowien typu zaplac-89-zl-i-zwroc (test sciezki zwrotu). Za B: `started_at` jest wypelnione, czyli system odnotowal rozpoczecie wizyty przez lekarza - jesli rozliczenie z lekarzami bierze `completed/refunded` z tej samej tabeli, wyplata nastapila. Rozstrzygnie to tylko eksport rozliczen z lekarzami.

## 2. Kaskada marzy (Waterfall) - Rok 1 vs Rok 2

| pozycja [PLN] | Rok 1 | Rok 2 | YoY | na zam. R1 | na zam. R2 | % gross R1 | % gross R2 |
|---|---|---|---|---|---|---|---|
| Gross Revenue (cennik konsultacji) | 2 523 464 | 3 903 771 | +54.7% | 102.10 | 101.42 | 100.0% | 100.0% |
| - Rabaty: kody promo | 20 220 | 136 760 | +576.4% | 0.82 | 3.55 | 0.8% | 3.5% |
| - Rabaty: TelemediGO | 128 516 | 258 813 | +101.4% | 5.20 | 6.72 | 5.1% | 6.6% |
| = Billed Revenue | 2 374 728 | 3 508 198 | +47.7% | 96.08 | 91.14 | 94.1% | 89.9% |
| - Zwroty: anulacje (cancelled) | 98 577 | 141 323 | +43.4% | 3.99 | 3.67 | 3.9% | 3.6% |
| - Zwroty po odbytej wizycie (refunded) | 45 884 | 138 532 | +201.9% | 1.86 | 3.60 | 1.8% | 3.5% |
| + Oplaty TelemediGO (89 zl) | 156 551 | 219 652 | +40.3% | 6.33 | 5.71 | 6.2% | 5.6% |
| = Net Revenue | 2 386 817 | 3 447 994 | +44.5% | 96.57 | 89.58 | 94.6% | 88.3% |
| - Koszt lekarza: wizyty completed | 1 154 975 | 1 674 275 | +45.0% | 46.73 | 43.50 | 45.8% | 42.9% |
| - Koszt lekarza: wizyty refunded | 20 725 | 60 550 | +192.2% | 0.84 | 1.57 | 0.8% | 1.6% |
| = CM1 | 1 211 117 | 1 713 169 | +41.5% | 49.00 | 44.51 | 48.0% | 43.9% |
| - Paid media (CPC) | 367 632 | 649 675 | +76.7% | 14.87 | 16.88 | 14.6% | 16.6% |
| - Prowizje afiliacyjne | 10 925 | 10 125 | -7.3% | 0.44 | 0.26 | 0.4% | 0.3% |
| = CM2 | 832 560 | 1 053 369 | +26.5% | 33.69 | 27.37 | 33.0% | 27.0% |

Zamowienia: R1 24,716, R2 38,491 (+55.7%). CM2 / zamowienie: R1 **33.69** vs R2 **27.37** zl.
**Wrazliwosc (koszt lekarza takze za no_show, wbrew README):** CM1 nizsze o 28 875 zl w R1 i 47 500 zl w R2.

### Most CM2: co zjadlo przyrost

| pozycja | zmiana R2 vs R1 wplywu na CM2 [PLN] |
|---|---|
| Gross Revenue (cennik konsultacji) | 1 380 307 |
| - Rabaty: kody promo | -116 540 |
| - Rabaty: TelemediGO | -130 297 |
| - Zwroty: anulacje (cancelled) | -42 746 |
| - Zwroty po odbytej wizycie (refunded) | -92 648 |
| + Oplaty TelemediGO (89 zl) | 63 101 |
| - Koszt lekarza: wizyty completed | -519 300 |
| - Koszt lekarza: wizyty refunded | -39 825 |
| - Paid media (CPC) | -282 043 |
| - Prowizje afiliacyjne | 800 |
| **= zmiana CM2** | **220 809** |


### Kaskada miesiac po miesiacu

| miesiac | zam. | Gross | Rabaty | Billed | Zwroty | GO fee | Net | Lekarz | CM1 | CM1/zam | Marketing | CM2 | CM2/zam | CM2 % Net |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024-10 | 1,351 | 138 525 | 4 621 | 133 904 | 7 960 | 6 853 | 132 797 | 64 650 | 68 147 | 50.44 | 27 810 | 40 337 | 29.86 | 30.4% |
| 2024-11 | 1,636 | 167 242 | 6 056 | 161 186 | 9 977 | 8 633 | 159 842 | 78 900 | 80 942 | 49.48 | 29 962 | 50 979 | 31.16 | 31.9% |
| 2024-12 | 1,932 | 196 498 | 8 270 | 188 228 | 11 314 | 9 790 | 186 704 | 93 575 | 93 130 | 48.20 | 31 955 | 61 174 | 31.66 | 32.8% |
| 2025-01 | 2,218 | 225 036 | 10 431 | 214 605 | 13 262 | 11 392 | 212 735 | 106 400 | 106 335 | 47.94 | 35 781 | 70 554 | 31.81 | 33.2% |
| 2025-02 | 2,173 | 220 935 | 9 679 | 211 256 | 12 960 | 10 057 | 208 353 | 100 750 | 107 603 | 49.52 | 33 760 | 73 844 | 33.98 | 35.4% |
| 2025-03 | 2,435 | 250 115 | 13 348 | 236 767 | 14 172 | 13 884 | 236 479 | 116 225 | 120 254 | 49.39 | 36 574 | 83 679 | 34.37 | 35.4% |
| 2025-04 | 2,341 | 238 539 | 14 314 | 224 225 | 14 447 | 12 905 | 222 682 | 110 575 | 112 107 | 47.89 | 34 414 | 77 693 | 33.19 | 34.9% |
| 2025-05 | 2,262 | 235 018 | 14 902 | 220 116 | 13 508 | 12 371 | 218 980 | 110 075 | 108 905 | 48.15 | 30 086 | 78 819 | 34.84 | 36.0% |
| 2025-06 | 2,052 | 205 896 | 15 068 | 190 828 | 11 461 | 13 973 | 193 340 | 93 175 | 100 165 | 48.81 | 28 483 | 71 682 | 34.93 | 37.1% |
| 2025-07 | 2,104 | 218 368 | 16 280 | 202 088 | 11 317 | 11 926 | 202 697 | 105 800 | 96 897 | 46.05 | 29 740 | 67 157 | 31.92 | 33.1% |
| 2025-08 | 2,041 | 207 605 | 16 836 | 190 769 | 12 073 | 11 837 | 190 534 | 93 825 | 96 709 | 47.38 | 29 169 | 67 540 | 33.09 | 35.4% |
| 2025-09 | 2,171 | 219 687 | 18 931 | 200 756 | 12 011 | 32 930 | 221 675 | 101 750 | 119 925 | 55.24 | 30 823 | 89 102 | 41.04 | 40.2% |
| 2025-10 | 2,432 | 247 428 | 22 582 | 224 846 | 14 742 | 15 664 | 225 769 | 113 775 | 111 994 | 46.05 | 32 510 | 79 484 | 32.68 | 35.2% |
| 2025-11 | 2,713 | 277 661 | 23 647 | 254 014 | 15 992 | 17 266 | 255 287 | 130 400 | 124 887 | 46.03 | 37 625 | 87 262 | 32.16 | 34.2% |
| 2025-12 | 2,960 | 303 274 | 26 780 | 276 494 | 19 948 | 19 313 | 275 859 | 136 750 | 139 109 | 47.00 | 45 505 | 93 604 | 31.62 | 33.9% |
| 2026-01 | 3,566 | 363 850 | 32 032 | 331 818 | 22 436 | 21 538 | 330 920 | 165 850 | 165 070 | 46.29 | 53 269 | 111 801 | 31.35 | 33.8% |
| 2026-02 | 3,449 | 350 747 | 31 747 | 319 000 | 22 785 | 16 821 | 313 036 | 159 300 | 153 736 | 44.57 | 53 669 | 100 067 | 29.01 | 32.0% |
| 2026-03 | 3,964 | 398 972 | 37 865 | 361 107 | 28 769 | 21 805 | 354 143 | 172 725 | 181 418 | 45.77 | 66 838 | 114 580 | 28.91 | 32.4% |
| 2026-04 | 3,570 | 363 786 | 38 955 | 324 831 | 26 013 | 19 046 | 317 864 | 161 675 | 156 189 | 43.75 | 65 047 | 91 142 | 25.53 | 28.7% |
| 2026-05 | 3,475 | 350 011 | 39 669 | 310 342 | 27 309 | 19 224 | 302 258 | 152 625 | 149 632 | 43.06 | 61 328 | 88 305 | 25.41 | 29.2% |
| 2026-06 | 3,181 | 320 637 | 37 729 | 282 908 | 26 330 | 19 313 | 275 892 | 137 250 | 138 642 | 43.58 | 60 306 | 78 336 | 24.63 | 28.4% |
| 2026-07 | 3,070 | 313 792 | 34 611 | 279 181 | 23 990 | 18 601 | 273 792 | 138 850 | 134 942 | 43.96 | 61 159 | 73 784 | 24.03 | 26.9% |
| 2026-08 | 3,011 | 302 427 | 35 119 | 267 308 | 23 350 | 16 287 | 260 245 | 134 000 | 126 245 | 41.93 | 59 680 | 66 565 | 22.11 | 25.6% |
| 2026-09 | 3,100 | 311 186 | 34 837 | 276 349 | 28 192 | 14 774 | 262 931 | 131 625 | 131 306 | 42.36 | 62 867 | 68 439 | 22.08 | 26.0% |


## 3. Kody rabatowe i kampanie L4


### Zamowienia wg kodu (wszystkie zamowienia z kodem)

| kod | zam. | Gross | Rabat | Zwroty | Net | Lekarz | CM1 | CM1/zam | % refunded | % cancelled | lekarz za zwrocone wizyty |
|---|---|---|---|---|---|---|---|---|---|---|---|
| brak | 43,957 | 4 481 791 | 0 | 287 940 | 4 193 851 | 2 072 450 | 2 121 401 | 48.26 | 2.5% | 4.0% | 44 475 |
| GO | 9,738 | 1 008 824 | 387 330 | 35 625 | 585 869 | 470 300 | 115 569 | 11.87 | 1.7% | 4.1% | 7 875 |
| L4SZYBKO20 | 3,511 | 337 667 | 70 220 | 51 251 | 216 196 | 113 700 | 102 496 | 29.19 | 14.4% | 4.3% | 17 150 |
| START10 | 3,386 | 343 490 | 33 860 | 23 187 | 286 443 | 156 525 | 129 918 | 38.37 | 3.2% | 4.5% | 4 125 |
| TIKTOK25 | 1,665 | 159 601 | 41 625 | 20 606 | 97 370 | 53 500 | 43 870 | 26.35 | 13.5% | 3.9% | 6 750 |
| RANKING10 | 595 | 59 305 | 5 950 | 4 003 | 49 352 | 27 050 | 22 302 | 37.48 | 2.5% | 5.0% | 600 |
| WRACAM15 | 355 | 36 557 | 5 325 | 1 704 | 29 528 | 17 000 | 12 528 | 35.29 | 0.6% | 4.2% | 300 |


### Mechanizm: cel wizyty x kod (internista)

| kod | cel wizyty | zam. | % refunded | CM1/zam |
|---|---|---|---|---|
| L4SZYBKO20 | e_recepta | 150 | 2.7% | 41.19 |
| L4SZYBKO20 | konsultacja | 161 | 2.5% | 41.81 |
| L4SZYBKO20 | l4 | 2,903 | 16.2% | 31.54 |
| TIKTOK25 | e_recepta | 67 | 3.0% | 36.30 |
| TIKTOK25 | konsultacja | 87 | 0.0% | 38.68 |
| TIKTOK25 | l4 | 1,375 | 15.7% | 28.00 |
| brak | e_recepta | 11,846 | 1.1% | 61.05 |
| brak | konsultacja | 6,482 | 1.3% | 61.08 |
| brak | l4 | 9,400 | 7.2% | 55.63 |
| brak | skierowanie | 4,076 | 0.9% | 60.93 |
| inne kody / GO | e_recepta | 4,590 | 0.9% | 26.16 |
| inne kody / GO | konsultacja | 1,890 | 1.1% | 30.75 |
| inne kody / GO | l4 | 2,400 | 6.0% | 29.11 |
| inne kody / GO | skierowanie | 1,225 | 1.3% | 29.55 |

Miks `L4SZYBKO20`: internista/l4=2,903, internista/konsultacja=161, internista/e_recepta=150, psychiatra/l4=94, pediatra/konsultacja=48, dermatolog/konsultacja=27
Miks `TIKTOK25`: internista/l4=1,375, internista/konsultacja=87, internista/e_recepta=67, psychiatra/l4=44, pediatra/konsultacja=26, dermatolog/konsultacja=14
Kontrola (L4 u internisty, tylko Rok 2): kod L4: 16.0% refunded (n=4,278), brak kodu: 8.3% refunded (n=5,582), inne: 6.3% refunded (n=1,538)
Kanal / kampania sesji zamowien z kodem: `L4SZYBKO20`: meta_prosp_l4_szybko=2,468, direct=437, seo=242, gs_brand=226; `TIKTOK25`: tt_prosp_l4_15min=1,191, direct=181, gs_brand=116, seo=103

### Pacjenci wg kodu PIERWSZEGO zamowienia (P&L pacjenta)

| kod 1. zamowienia | pacjenci | CAC FT | CAC LT | CM1 1. zam. | CM2 1. zam. (FT) | CM1 180d | CM2 180d (FT) | % powrot 180d | CM2 365d (FT) | masa CM2 FT (caly okres) | masa CM2 LT |
|---|---|---|---|---|---|---|---|---|---|---|---|
| brak | 29,767 | 24.16 | 24.08 | 48.06 | 23.90 | 73.93 | 50.95 | 26.4% | 59.52 | 1 557 311 | 1 559 827 |
| L4SZYBKO20 | 3,511 | 32.35 | 32.83 | 29.19 | -3.15 | 32.64 | 2.82 | 4.9% | - | -2 150 | -3 850 |
| START10 | 3,386 | 24.71 | 24.60 | 38.37 | 13.66 | 63.65 | 40.06 | 24.9% | 51.79 | 139 778 | 140 138 |
| GO | 1,994 | 24.46 | 24.56 | 101.76 | 77.30 | 112.20 | 89.01 | 41.9% | 92.79 | 186 049 | 185 842 |
| TIKTOK25 | 1,665 | 37.73 | 38.10 | 26.35 | -11.38 | 25.82 | -8.05 | 3.9% | - | -16 400 | -17 020 |
| RANKING10 | 595 | 17.21 | 17.79 | 37.48 | 20.28 | 52.23 | 34.84 | 17.4% | 37.18 | 21 339 | 20 992 |

CM1 180d/365d i CM2 180d/365d liczone tylko dla pacjentow z pelnym oknem obserwacji (1. zamowienie <= 2026-04-03 / <= 2025-09-30). CM1 pacjenta zawiera oplaty GO. CAC = koszt puli (kampania x miesiac kohorty) / liczba pacjentow przypisanych do niej.
**Bilans kodow L4 (L4SZYBKO20 + TIKTOK25):** 5,176 zamowien, 5,176 pacjentow. Rabaty 111 845 zl, zwroty po odbytej wizycie 54 905 zl, lekarz za zwrocone wizyty 23 900 zl, CAC (FT) 176 387 zl, CM1 pacjentow w calym oknie 157 838 zl -> **masa CM2 -18 549 zl**.

## 4. Kanaly pozyskania: First-Touch (stitched) vs Last-Touch

Pula kosztow marketingu (CPC + afiliacja): 1 038 357 zl. Nieprzypisane (kampania x miesiac bez nowego pacjenta): FT 0 zl, LT 0 zl. Prowizje afiliacyjne: 842 x 25 zl = 21 050 zl (LT); gdyby liczyc po FT: 1,213 x 25 zl.

### kanal FT (stitched)

| kanal FT (stitched) | pacjenci | CAC FT | CAC LT | CM1 1. zam. | CM2 1. zam. (FT) | CM1 180d | CM2 180d (FT) | % powrot 180d | CM2 365d (FT) | masa CM2 FT (caly okres) | masa CM2 LT |
|---|---|---|---|---|---|---|---|---|---|---|---|
| google_cpc | 15,122 | 42.07 | 41.69 | 49.12 | 7.06 | 73.53 | 32.71 | 27.2% | 39.66 | 527 720 | 533 335 |
| seo | 7,362 | 0.00 | 0.86 | 50.90 | 50.90 | 78.64 | 78.64 | 28.5% | 89.69 | 609 911 | 603 577 |
| meta | 7,311 | 40.86 | 39.54 | 40.04 | -0.82 | 53.49 | 11.15 | 14.1% | 22.74 | 56 797 | 66 425 |
| direct | 6,541 | 0.00 | 0.74 | 51.09 | 51.09 | 78.89 | 78.89 | 29.2% | 88.24 | 543 955 | 539 093 |
| tiktok | 2,159 | 38.20 | 39.16 | 32.00 | -6.19 | 30.80 | -3.61 | 3.1% | - | -10 022 | -12 104 |
| affiliate | 1,213 | 17.35 | 18.22 | 46.73 | 29.38 | 61.00 | 43.43 | 19.3% | 45.57 | 54 806 | 53 754 |
| referral | 1,210 | 0.00 | 0.75 | 51.22 | 51.22 | 80.47 | 80.47 | 30.2% | 90.51 | 102 763 | 101 850 |


### kanal LT

| kanal LT | pacjenci | CAC FT | CAC LT | CM1 1. zam. | CM2 1. zam. (FT) | CM1 180d | CM2 180d (FT) | % powrot 180d | CM2 365d (FT) | masa CM2 FT (caly okres) | masa CM2 LT |
|---|---|---|---|---|---|---|---|---|---|---|---|
| google_cpc | 13,280 | 38.61 | 47.90 | 48.61 | 10.00 | 73.15 | 35.64 | 27.0% | 43.37 | 495 496 | 372 169 |
| direct | 9,344 | 12.52 | 0.00 | 49.60 | 37.08 | 75.76 | 64.76 | 27.6% | 74.79 | 605 247 | 722 240 |
| seo | 7,682 | 8.07 | 0.00 | 49.76 | 41.69 | 77.07 | 70.12 | 27.5% | 81.60 | 547 655 | 609 633 |
| meta | 7,293 | 37.16 | 40.96 | 41.90 | 4.74 | 60.38 | 23.79 | 18.1% | 41.19 | 131 667 | 103 934 |
| tiktok | 1,593 | 38.15 | 51.77 | 32.30 | -5.85 | 31.46 | -2.76 | 3.1% | - | -6 974 | -28 665 |
| referral | 884 | 0.00 | 0.00 | 51.00 | 51.00 | 79.48 | 79.48 | 30.1% | 89.50 | 75 104 | 75 104 |
| affiliate | 842 | 17.61 | 25.00 | 46.11 | 28.49 | 60.41 | 42.59 | 19.7% | 45.20 | 37 735 | 31 515 |


### Kampanie platne i kanaly - FT (stitched), wg puli kosztowej

| kampania / kanal FT | pacjenci | CAC FT | CAC LT | CM1 1. zam. | CM2 1. zam. (FT) | CM1 180d | CM2 180d (FT) | % powrot 180d | CM2 365d (FT) | masa CM2 FT (caly okres) | masa CM2 LT |
|---|---|---|---|---|---|---|---|---|---|---|---|
| seo | 7,362 | 0.00 | 0.86 | 50.90 | 50.90 | 78.64 | 78.64 | 28.5% | 89.69 | 609 911 | 603 577 |
| direct | 6,541 | 0.00 | 0.74 | 51.09 | 51.09 | 78.89 | 78.89 | 29.2% | 88.24 | 543 955 | 539 093 |
| meta_prosp_l4_szybko | 4,946 | 33.02 | 33.89 | 34.84 | 1.82 | 38.21 | 7.79 | 5.5% | - | 22 093 | 17 810 |
| gs_brand | 3,985 | 9.45 | 5.77 | 49.88 | 40.44 | 77.07 | 68.94 | 29.2% | 78.48 | 286 259 | 300 921 |
| gs_generic_lekarz_online | 3,589 | 50.55 | 51.37 | 50.45 | -0.11 | 73.51 | 24.12 | 26.1% | 28.61 | 96 082 | 93 159 |
| gs_generic_erecepta | 3,138 | 56.32 | 57.08 | 56.11 | -0.22 | 90.81 | 36.48 | 34.7% | 50.05 | 117 424 | 115 058 |
| gs_generic_l4 | 2,674 | 52.35 | 53.20 | 55.52 | 3.18 | 70.79 | 17.54 | 18.5% | 20.92 | 53 899 | 51 628 |
| tt_prosp_l4_15min | 2,159 | 38.20 | 39.16 | 32.00 | -6.19 | 30.80 | -3.61 | 3.1% | - | -10 022 | -12 104 |
| meta_prosp_lekarz_online | 2,098 | 56.15 | 56.88 | 51.23 | -4.92 | 69.85 | 14.01 | 22.9% | 20.07 | 31 266 | 29 729 |
| gs_generic_specjalisci | 1,736 | 57.79 | 58.64 | 22.16 | -35.63 | 38.51 | -16.84 | 24.9% | -13.66 | -25 944 | -27 432 |
| affiliate | 1,213 | 17.35 | 18.22 | 46.73 | 29.38 | 61.00 | 43.43 | 19.3% | 45.57 | 54 806 | 53 754 |
| referral | 1,210 | 0.00 | 0.75 | 51.22 | 51.22 | 80.47 | 80.47 | 30.2% | 90.51 | 102 763 | 101 850 |
| meta_rmkt_koszyk | 267 | 65.95 | 8.09 | 48.56 | -17.39 | 75.78 | 21.80 | 29.6% | 45.03 | 3 437 | 18 885 |


### CAC i CM1 1. zamowienia: kanal FT x rok

| kanal FT | pacjenci R1 | pacjenci R2 | CAC R1 | CAC R2 | CM1 1. zam. R1 | CM1 1. zam. R2 | CM2 1. zam. R1 | CM2 1. zam. R2 |
|---|---|---|---|---|---|---|---|---|
| google_cpc | 7,408 | 7,714 | 40.99 | 43.10 | 48.78 | 49.45 | 7.79 | 6.35 |
| meta | 1,144 | 6,167 | 55.93 | 38.07 | 51.95 | 37.84 | -3.98 | -0.23 |
| seo | 3,453 | 3,909 | 0.00 | 0.00 | 50.88 | 50.91 | 50.88 | 50.91 |
| direct | 3,072 | 3,469 | 0.00 | 0.00 | 51.42 | 50.79 | 51.42 | 50.79 |
| tiktok | 0 | 2,159 | 0.00 | 38.20 | 0.00 | 32.00 | 0.00 | -6.19 |
| referral | 550 | 660 | 0.00 | 0.00 | 51.01 | 51.40 | 51.01 | 51.40 |
| affiliate | 604 | 609 | 18.09 | 16.63 | 47.05 | 46.42 | 28.96 | 29.80 |


## 5. Ekonomika TelemediGO

| metryka | Rok 1 | Rok 2 |
|---|---|---|
| czlonkostwa GO sprzedane (w tym osobno) | 1,759 (225) | 2,468 (461) |
| przychod z oplat GO | 156 551 | 219 652 |
| zamowienia z rabatem GO | 3,235 | 6,503 |
| rabaty GO udzielone | 128 516 | 258 813 |
| koszt lekarza wizyt GO | 154 300 | 316 000 |
| CM1 wizyt GO (bez oplat) | 37 153 | 78 416 |
| **program GO: oplaty - rabaty** | 28 035 | -39 161 |


### CM1 na odbyta wizyte wg specjalizacji: cena katalogowa vs z rabatem GO

| specjalizacja | cena | lekarz | CM1/wizyta bez rabatu | CM1/wizyta GO | n GO | CM1/wizyta promo |
|---|---|---|---|---|---|---|
| internista | 89.00 | 25 | 64.00 | 19.50 | 6,385 | 47.20 |
| dermatolog | 109.00 | 100 | 9.00 | -12.80 | 531 | -3.88 |
| ginekolog | 119.00 | 100 | 19.00 | -4.80 | 528 | 6.28 |
| pediatra | 95.00 | 100 | -5.00 | -24.00 | 352 | -18.20 |
| psychiatra | 269.00 | 200 | 69.00 | 15.20 | 480 | 53.80 |
| endokrynolog | 119.00 | 100 | 19.00 | -4.80 | 265 | 5.90 |
| kardiolog | 109.00 | 100 | 9.00 | -12.80 | 130 | -3.84 |
| neurolog | 109.00 | 100 | 9.00 | -12.80 | 90 | -3.38 |
| urolog | 109.00 | 100 | 9.00 | -12.80 | 104 | -2.17 |
| psycholog | 99.00 | 100 | -1.00 | -20.80 | 68 | -13.36 |


### P&L pojedynczego czlonkostwa

**zamkniete (waznosc skonczona)**: 1,759 czlonkostw; srednio 2.79 wizyt GO; nieuzyte (0 wizyt z rabatem): 5.1%; tylko 1 wizyta (ta przy zakupie): 39.9%; rabaty > 89 zl: 39.9%; srednio oplata - rabaty = -21.94 zl; srednio oplata + CM1 wizyt GO = 121.76 zl.
**wszystkie**: 4,227 czlonkostw; srednio 2.30 wizyt GO; nieuzyte (0 wizyt z rabatem): 6.0%; tylko 1 wizyta (ta przy zakupie): 44.5%; rabaty > 89 zl: 31.4%; srednio oplata - rabaty = -2.63 zl; srednio oplata + CM1 wizyt GO = 116.34 zl.

### Czy GO poprawia retencje i wartosc pacjenta? (kohorta Rok 1, 365 dni od 1. zamowienia)

| segment | 1. wizyta | pacjenci | zam./pacjent 365d | % powrot 365d | CM1 365d (z oplata GO) | CM2 365d (FT) |
|---|---|---|---|---|---|---|
| GO przy 1. zam. | internista | 677 | 2.37 | 45.1% | 123.77 | 100.08 |
| GO przy 1. zam. | specjalista | 228 | 2.37 | 44.7% | 97.85 | 71.15 |
| bez GO przy 1. zam. | internista | 11,050 | 1.71 | 27.4% | 93.55 | 71.32 |
| bez GO przy 1. zam. | specjalista | 4,276 | 1.76 | 28.6% | 50.67 | 24.75 |

Uwaga: samoselekcja - GO kupuja pacjenci, ktorzy i tak planuja wracac. Roznica to gorna granica efektu GO.

### Co sie stalo we wrzesniu 2025?

| miesiac | GO osobno | zrodlo sesji zakupu |
|---|---|---|
| 2025-09 | 225 | email=225 |
| 2025-10 | 27 | email=27 |
| 2025-11 | 34 | email=34 |
| 2025-12 | 46 | email=46 |
| 2026-01 | 36 | email=36 |
| 2026-02 | 33 | email=33 |
| 2026-03 | 47 | email=47 |
| 2026-04 | 40 | email=40 |
| 2026-05 | 40 | email=40 |
| 2026-06 | 50 | email=50 |
| 2026-07 | 39 | email=39 |
| 2026-08 | 38 | email=38 |
| 2026-09 | 31 | email=31 |

Sesje z kampanii `crm_go_upsell` per miesiac: 2025-09: 317, 2025-10: 43, 2025-11: 47, 2025-12: 68, 2026-01: 50, 2026-02: 51, 2026-03: 63, 2026-04: 57, 2026-05: 58, 2026-06: 78, 2026-07: 55, 2026-08: 58, 2026-09: 47
Wrzesien 2025, GO osobno: 225; dni z najwieksza sprzedaza: 2025-09-24=19, 2025-09-16=18, 2025-09-20=17, 2025-09-18=16, 2025-09-27=15. Kupujacy z wczesniejszym zamowieniem: 100.0%; z wczesniejszym GO: 0.0% (w tym z nadal aktywnym GO: 0).
Wykorzystanie (do konca danych, waznosc do 2026-09): srednio 2.07 wizyt GO; 0 wizyt: 40.0%; oplaty 20 025 zl vs rabaty 18 612 zl; CM1 tych wizyt 5 764 zl.
