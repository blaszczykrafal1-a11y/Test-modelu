# 03 - Kohorty, lejek, zdarzenia, wycena (scripts/03_cohorts_and_funnels.py)

Wygenerowano: 2026-10-27 15:04

## 1. Kohorty i krzywe retencji / LTV

Kohorta = dzien 1. oplaconego zamowienia (czas PL). Retencja D+k = co najmniej jedno kolejne zamowienie w ciagu k dni. Wartosci skumulowane na pacjenta, wliczajac 1. zamowienie i oplaty GO; CM2 = CM1 - CAC (FT stitched). Kazde okno liczone tylko dla kohort z pelnym oknem obserwacji.
| okno | pacjenci w oknie | retencja | Net Revenue / pacjent | CM1 / pacjent | CM2 / pacjent |
|---|---|---|---|---|---|
| D+7 | 40,407 | 1.6% | 93.19 | 47.97 | 22.65 |
| D+14 | 39,904 | 4.6% | 96.36 | 49.50 | 24.24 |
| D+30 | 38,877 | 9.2% | 101.83 | 52.28 | 27.18 |
| D+60 | 37,054 | 16.5% | 111.88 | 57.42 | 32.65 |
| D+90 | 35,155 | 20.9% | 120.84 | 62.00 | 37.57 |
| D+180 | 28,822 | 25.7% | 141.98 | 72.24 | 48.86 |
| D+365 | 16,231 | 28.7% | 167.66 | 83.57 | 60.25 |


### Kanal first-touch (stitched)

| ft_channel | pacjenci | ret D+30 | ret D+90 | ret D+180 | ret D+365 | CM2 D+30 | CM2 D+180 | CM2 D+365 |
|---|---|---|---|---|---|---|---|---|
| google_cpc | 15,122 | 10.7% | 23.6% | 27.2% | 28.6% | 12.84 | 32.71 | 39.66 |
| seo | 7,362 | 11.1% | 23.9% | 28.5% | 29.2% | 56.78 | 78.64 | 89.69 |
| meta | 7,311 | 4.4% | 10.4% | 14.1% | 26.5% | 1.62 | 11.15 | 22.74 |
| direct | 6,541 | 10.9% | 24.8% | 29.2% | 30.7% | 57.01 | 78.89 | 88.24 |
| tiktok | 2,159 | 2.1% | 3.1% | 3.1% | - | -5.59 | -3.61 | - |
| affiliate | 1,213 | 6.9% | 16.7% | 19.3% | 19.4% | 32.71 | 43.43 | 45.57 |
| referral | 1,210 | 12.7% | 26.3% | 30.2% | 30.4% | 57.66 | 80.47 | 90.51 |


### Kod 1. zamowienia

| code_group | pacjenci | ret D+30 | ret D+90 | ret D+180 | ret D+365 | CM2 D+30 | CM2 D+180 | CM2 D+365 |
|---|---|---|---|---|---|---|---|---|
| brak kodu | 29,767 | 10.0% | 22.2% | 26.4% | 28.1% | 29.75 | 50.95 | 59.52 |
| kod L4 | 5,176 | 2.1% | 4.0% | 4.8% | - | -4.59 | 1.30 | - |
| inne kody | 3,981 | 9.2% | 20.3% | 23.7% | 25.1% | 19.94 | 39.24 | 49.36 |
| rabat GO | 1,994 | 14.9% | 35.5% | 41.9% | 45.0% | 78.98 | 89.01 | 92.79 |


### Sciezka TelemediGO

| go_path | pacjenci | ret D+30 | ret D+90 | ret D+180 | ret D+365 | CM2 D+30 | CM2 D+180 | CM2 D+365 |
|---|---|---|---|---|---|---|---|---|
| bez GO | 36,776 | 7.1% | 15.6% | 19.2% | 21.4% | 22.49 | 36.21 | 42.75 |
| GO kupione pozniej | 2,148 | 38.6% | 87.0% | 97.8% | 99.9% | 56.98 | 183.47 | 236.04 |
| GO przy 1. zam. | 1,994 | 14.9% | 35.5% | 41.9% | 45.0% | 78.98 | 89.01 | 92.79 |


### Kategoria 1. wizyty

| first_cat | pacjenci | ret D+30 | ret D+90 | ret D+180 | ret D+365 | CM2 D+30 | CM2 D+180 | CM2 D+365 |
|---|---|---|---|---|---|---|---|---|
| internista: l4 | 13,196 | 5.2% | 10.4% | 13.8% | 18.0% | 22.68 | 37.81 | 50.59 |
| specjalista | 9,928 | 11.2% | 23.2% | 27.8% | 29.4% | -2.02 | 18.04 | 27.10 |
| internista: e_recepta | 8,839 | 10.5% | 32.0% | 36.8% | 38.4% | 43.27 | 76.54 | 89.76 |
| internista: konsultacja | 5,840 | 11.9% | 22.0% | 26.9% | 28.9% | 49.91 | 68.18 | 75.66 |
| internista: skierowanie | 3,115 | 11.0% | 20.1% | 23.2% | 25.0% | 50.46 | 66.57 | 75.46 |


### Kohorty miesieczne (agregacja kohort dziennych)

| kohorta | pacjenci | D+7 | D+30 | D+90 | D+180 | D+365 | CM2 D+30 | CM2 D+180 | CM2 D+365 | % z kodem L4 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2024-10 | 1,285 | 1.5% | 10.3% | 22.9% | 25.9% | 26.6% | 34.23 | 52.52 | 60.20 | 0.0% |
| 2024-11 | 1,400 | 1.6% | 11.3% | 24.3% | 28.1% | 29.2% | 34.08 | 52.53 | 61.83 | 0.0% |
| 2024-12 | 1,501 | 2.2% | 12.7% | 26.6% | 29.6% | 30.4% | 33.85 | 55.95 | 65.35 | 0.0% |
| 2025-01 | 1,628 | 2.3% | 12.1% | 27.3% | 31.1% | 32.0% | 33.58 | 55.95 | 66.11 | 0.0% |
| 2025-02 | 1,560 | 2.1% | 10.1% | 23.6% | 26.9% | 27.7% | 33.69 | 51.13 | 59.10 | 0.0% |
| 2025-03 | 1,601 | 2.2% | 12.2% | 24.7% | 27.6% | 28.5% | 33.82 | 53.82 | 62.77 | 0.0% |
| 2025-04 | 1,430 | 1.9% | 11.5% | 23.1% | 26.8% | 27.8% | 31.14 | 50.64 | 56.38 | 0.0% |
| 2025-05 | 1,266 | 2.4% | 11.7% | 25.5% | 29.6% | 30.7% | 32.81 | 59.09 | 68.44 | 0.0% |
| 2025-06 | 1,123 | 1.5% | 10.3% | 23.9% | 27.6% | 27.9% | 31.55 | 50.66 | 57.04 | 0.0% |
| 2025-07 | 1,116 | 1.5% | 9.1% | 22.4% | 25.4% | 26.1% | 27.37 | 45.37 | 49.94 | 0.0% |
| 2025-08 | 1,074 | 1.9% | 9.9% | 21.9% | 25.7% | 26.6% | 29.25 | 46.43 | 52.69 | 0.0% |
| 2025-09 | 1,247 | 1.7% | 10.1% | 24.6% | 28.2% | 29.3% | 30.68 | 52.09 | 57.66 | 0.0% |
| 2025-10 | 1,383 | 2.0% | 11.1% | 24.2% | 28.3% | - | 34.03 | 53.82 | - | 0.0% |
| 2025-11 | 1,692 | 1.8% | 9.8% | 20.6% | 25.0% | - | 31.03 | 47.64 | - | 5.0% |
| 2025-12 | 1,889 | 0.7% | 9.0% | 19.4% | 21.9% | - | 28.70 | 42.83 | - | 10.7% |
| 2026-01 | 2,423 | 1.8% | 9.2% | 20.6% | 24.1% | - | 30.37 | 47.74 | - | 13.1% |
| 2026-02 | 2,303 | 1.7% | 8.8% | 19.8% | 22.3% | - | 26.85 | 41.97 | - | 18.6% |
| 2026-03 | 2,682 | 1.3% | 7.3% | 16.4% | 19.1% | - | 25.09 | 37.77 | - | 21.4% |
| 2026-04 | 2,256 | 1.3% | 6.2% | 14.3% | 18.3% | - | 18.85 | 32.03 | - | 26.6% |
| 2026-05 | 2,199 | 0.9% | 6.2% | 14.2% | - | - | 18.16 | - | - | 29.3% |
| 2026-06 | 1,974 | 1.0% | 5.9% | 15.0% | - | - | 15.81 | - | - | 30.2% |
| 2026-07 | 1,958 | 1.5% | 7.9% | 9.8% | - | - | 17.27 | - | - | 28.6% |
| 2026-08 | 1,887 | 1.1% | 7.7% | - | - | - | 14.44 | - | - | 30.0% |
| 2026-09 | 2,041 | 1.3% | - | - | - | - | - | - | - | 29.5% |


### Krzywa przezycia: czas do 2. zamowienia (Kaplan-Meier) i kiedy pacjent 'umiera'

| dzien | D+1 | D+7 | D+14 | D+30 | D+60 | D+90 | D+120 | D+180 | D+270 | D+365 | D+540 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| % pacjentow z 2. zamowieniem (KM) | 0.0% | 1.6% | 4.6% | 9.2% | 16.3% | 20.5% | 22.5% | 23.8% | 24.4% | 24.6% | 24.7% |

Przyrost udzialu powracajacych w przedzialach: do D+1: +0.0 pp, do D+7: +1.6 pp, do D+14: +3.0 pp, do D+30: +4.6 pp, do D+60: +7.1 pp, do D+90: +4.2 pp, do D+120: +1.9 pp, do D+180: +1.3 pp, do D+270: +0.6 pp, do D+365: +0.2 pp, do D+540: +0.1 pp
| dni bez zamowienia | zamowienia w probie | P(kolejne zamowienie w 365 dni od ostatniego) |
|---|---|---|
| 0 | 24,716 | 41.3% |
| 7 | 24,081 | 39.8% |
| 14 | 22,914 | 36.7% |
| 30 | 20,913 | 30.7% |
| 60 | 17,842 | 18.7% |
| 90 | 15,997 | 9.4% |
| 120 | 15,236 | 4.8% |
| 180 | 14,794 | 2.0% |
| 270 | 14,572 | 0.5% |

Odstepy miedzy kolejnymi zamowieniami (gdy nastepuje w 365 dni, n=10,218): p25 23.0 d, mediana 38.9 d, p75 70.1 d, p90 105.3 d. Pacjent 'umiera' (P powrotu < 5%) po **120 dniach** bez zamowienia.

### Dlaczego tylko 11% pacjentow z R1 kupilo w R2?

| kohorta R1 | pacjenci | kiedykolwiek wrocil | kupil w R2 | wrocil w 90 dni |
|---|---|---|---|---|
| 2024-10 | 1,285 | 26.9% | 4.6% | 22.9% |
| 2024-11 | 1,400 | 29.3% | 5.4% | 24.3% |
| 2024-12 | 1,501 | 30.4% | 6.9% | 26.6% |
| 2025-01 | 1,628 | 32.1% | 7.9% | 27.3% |
| 2025-02 | 1,560 | 27.8% | 6.5% | 23.6% |
| 2025-03 | 1,601 | 28.6% | 9.0% | 24.7% |
| 2025-04 | 1,430 | 27.8% | 8.7% | 23.1% |
| 2025-05 | 1,266 | 31.0% | 15.7% | 25.5% |
| 2025-06 | 1,123 | 27.9% | 12.4% | 23.9% |
| 2025-07 | 1,116 | 26.1% | 13.7% | 22.4% |
| 2025-08 | 1,074 | 26.6% | 18.7% | 21.9% |
| 2025-09 | 1,247 | 29.3% | 26.7% | 24.6% |

R1: 16,231 pacjentow; kiedykolwiek wrocilo 28.8%; kupilo w R2 10.8%; wrocilo, ale tylko w R1 17.9%.

## 2. Lejek konwersji (sesja -> zamowienie)

Kroki: S1 `service_selected` / sesja; S2 `slot_selected` / S1; S3 konto (`account_completed` albo zalogowany na wejsciu) / S2; S4 `payment_started` / S3; S5 `payment_succeeded` / S4. CR = sesje z zamowieniem konsultacji / sesje. Sesje kont testowych wykluczone.
Kontrola spojnosci: platnosc bez wyboru uslugi (GO osobno): 686
| rok | sesje | CR sesja->zam. | S1 usluga | S2 termin | S3 konto | S4 start platn. | S5 platn. OK |
|---|---|---|---|---|---|---|---|
| Y1 | 162,336 | 15.2% | 36.8% | 70.7% | 73.8% | 86.7% | 91.5% |
| Y2 | 295,128 | 13.0% | 33.7% | 69.3% | 71.0% | 86.3% | 91.1% |


### Urzadzenie x rok

| urzadzenie / rok | sesje | CR sesja->zam. | S1 usluga | S2 termin | S3 konto | S4 start platn. | S5 platn. OK |
|---|---|---|---|---|---|---|---|
| desktop / Y1 | 41,370 | 16.5% | 38.9% | 71.7% | 73.6% | 87.7% | 91.7% |
| desktop / Y2 | 53,328 | 17.4% | 39.5% | 72.4% | 75.9% | 87.5% | 91.7% |
| mobile / Y1 | 116,328 | 14.7% | 36.0% | 70.3% | 73.8% | 86.4% | 91.5% |
| mobile / Y2 | 234,296 | 12.0% | 32.4% | 68.4% | 69.6% | 85.9% | 90.9% |
| tablet / Y1 | 4,638 | 16.1% | 37.8% | 70.3% | 76.6% | 86.7% | 91.3% |
| tablet / Y2 | 7,504 | 13.2% | 34.3% | 69.3% | 70.3% | 86.9% | 90.8% |


### Grupa przegladarek x rok

| przegladarki / rok | sesje | CR sesja->zam. | S1 usluga | S2 termin | S3 konto | S4 start platn. | S5 platn. OK |
|---|---|---|---|---|---|---|---|
| chrome/safari / Y1 | 115,411 | 16.4% | 38.7% | 71.6% | 74.3% | 86.8% | 91.6% |
| chrome/safari / Y2 | 154,267 | 16.3% | 38.5% | 72.0% | 73.3% | 87.3% | 91.7% |
| in_app / Y1 | 16,684 | 4.9% | 19.6% | 56.9% | 60.6% | 81.3% | 88.3% |
| in_app / Y2 | 100,938 | 6.6% | 24.7% | 60.8% | 61.2% | 81.7% | 88.3% |
| inne / Y1 | 30,241 | 16.5% | 38.7% | 71.1% | 74.8% | 87.3% | 91.9% |
| inne / Y2 | 39,923 | 16.8% | 38.3% | 72.4% | 75.7% | 87.5% | 91.6% |


### Przegladarka (caly okres)

| przegladarka | sesje | CR sesja->zam. | S1 usluga | S2 termin | S3 konto | S4 start platn. | S5 platn. OK |
|---|---|---|---|---|---|---|---|
| Chrome | 183,003 | 16.6% | 38.5% | 72.0% | 75.1% | 87.3% | 91.7% |
| Edge | 15,961 | 16.8% | 38.9% | 72.1% | 74.8% | 87.7% | 91.6% |
| Facebook | 36,017 | 6.5% | 24.1% | 60.1% | 61.3% | 82.1% | 89.0% |
| Firefox | 17,974 | 17.2% | 39.2% | 71.7% | 76.1% | 87.5% | 92.1% |
| Instagram | 49,918 | 6.6% | 24.3% | 60.7% | 61.8% | 81.7% | 88.8% |
| Opera | 5,326 | 16.2% | 38.3% | 71.9% | 73.8% | 87.0% | 91.6% |
| Safari | 86,675 | 15.6% | 38.8% | 71.5% | 70.7% | 86.8% | 91.7% |
| Samsung Internet | 30,903 | 16.4% | 37.9% | 71.7% | 75.4% | 87.2% | 91.7% |
| TikTok | 31,687 | 5.9% | 23.2% | 60.2% | 59.7% | 81.1% | 86.6% |


### Kanal x rok

| kanal / rok | sesje | CR sesja->zam. | S1 usluga | S2 termin | S3 konto | S4 start platn. | S5 platn. OK |
|---|---|---|---|---|---|---|---|
| affiliate / Y1 | 4,741 | 9.2% | 31.7% | 61.0% | 64.7% | 82.6% | 89.4% |
| affiliate / Y2 | 5,275 | 7.7% | 31.1% | 57.8% | 59.0% | 83.4% | 86.9% |
| direct / Y1 | 24,113 | 31.8% | 57.1% | 82.0% | 79.1% | 91.0% | 94.3% |
| direct / Y2 | 35,039 | 32.2% | 57.0% | 83.5% | 78.2% | 91.3% | 94.8% |
| email / Y1 | 4,927 | 18.5% | 43.7% | 70.9% | 100.0% | 74.8% | 79.7% |
| email / Y2 | 9,018 | 16.5% | 42.9% | 70.0% | 100.0% | 72.4% | 75.7% |
| google_cpc / Y1 | 58,037 | 13.7% | 37.4% | 66.8% | 70.0% | 85.9% | 91.4% |
| google_cpc / Y2 | 65,830 | 14.9% | 38.6% | 69.4% | 69.3% | 87.1% | 91.9% |
| meta / Y1 | 25,652 | 7.4% | 23.3% | 65.4% | 64.3% | 84.9% | 89.0% |
| meta / Y2 | 89,776 | 6.7% | 24.9% | 60.4% | 61.2% | 82.3% | 88.9% |
| referral / Y1 | 2,063 | 19.2% | 50.2% | 69.1% | 72.7% | 81.5% | 93.4% |
| referral / Y2 | 2,678 | 18.2% | 47.9% | 68.6% | 68.7% | 88.1% | 91.6% |
| seo / Y1 | 41,335 | 12.5% | 31.0% | 69.1% | 72.4% | 87.4% | 92.1% |
| seo / Y2 | 51,307 | 13.6% | 32.4% | 71.3% | 71.2% | 88.8% | 92.8% |
| sms / Y1 | 1,468 | 18.8% | 48.4% | 68.6% | 100.0% | 73.7% | 76.9% |
| sms / Y2 | 2,735 | 17.0% | 46.5% | 68.2% | 100.0% | 69.8% | 76.6% |
| tiktok / Y2 | 33,470 | 4.8% | 21.2% | 54.6% | 58.4% | 81.4% | 86.4% |


### Meta + TikTok, mobile: in-app vs Chrome/Safari (kontrola miksu kanalu i urzadzenia)

| kanal / OS / przegladarki | sesje | CR sesja->zam. | S1 usluga | S2 termin | S3 konto | S4 start platn. | S5 platn. OK |
|---|---|---|---|---|---|---|---|
| meta / Android / chrome/safari | 14,359 | 9.6% | 27.6% | 68.3% | 67.4% | 84.7% | 89.2% |
| meta / Android / in_app | 48,375 | 5.1% | 22.1% | 55.3% | 59.5% | 80.4% | 87.6% |
| meta / Android / inne | 5,126 | 9.7% | 27.4% | 68.4% | 65.7% | 87.5% | 90.2% |
| meta / iOS / chrome/safari | 10,935 | 8.5% | 28.7% | 67.9% | 59.6% | 83.0% | 88.4% |
| meta / iOS / in_app | 27,462 | 5.4% | 22.4% | 56.6% | 58.1% | 81.9% | 89.3% |
| meta / iOS / inne | 341 | 7.9% | 24.9% | 70.6% | 63.3% | 76.3% | 93.1% |
| tiktok / Android / chrome/safari | 1,815 | 4.9% | 20.9% | 57.1% | 57.6% | 82.4% | 86.4% |
| tiktok / Android / in_app | 17,643 | 4.7% | 20.9% | 54.6% | 58.6% | 80.7% | 87.4% |
| tiktok / Android / inne | 607 | 5.9% | 20.8% | 56.3% | 59.2% | 92.9% | 92.3% |
| tiktok / iOS / chrome/safari | 1,385 | 3.0% | 19.7% | 52.4% | 42.0% | 80.0% | 87.5% |
| tiktok / iOS / in_app | 9,894 | 5.0% | 21.8% | 55.0% | 60.0% | 81.6% | 84.5% |


### Kroki lejka miesiac po miesiacu (in-app vs Chrome/Safari)

| miesiac | in-app sesje | in-app S3 konto | in-app S5 platn. | in-app CR | chr/saf sesje | chr/saf S3 konto | chr/saf S5 platn. | chr/saf CR |
|---|---|---|---|---|---|---|---|---|
| 2024-10 | 1,328 | 57.6% | 84.5% | 4.5% | 8,027 | 68.5% | 90.2% | 12.6% |
| 2024-11 | 1,287 | 55.6% | 82.0% | 3.9% | 9,088 | 70.2% | 90.6% | 14.2% |
| 2024-12 | 1,422 | 58.0% | 87.7% | 4.5% | 10,150 | 69.9% | 91.6% | 14.6% |
| 2025-01 | 1,527 | 55.9% | 89.6% | 3.9% | 11,276 | 71.7% | 90.4% | 15.1% |
| 2025-02 | 1,345 | 56.6% | 88.6% | 4.6% | 10,580 | 74.0% | 91.3% | 15.8% |
| 2025-03 | 1,616 | 61.1% | 88.2% | 4.1% | 11,224 | 73.4% | 91.5% | 16.6% |
| 2025-04 | 1,388 | 65.8% | 90.2% | 5.3% | 10,541 | 75.2% | 92.3% | 17.1% |
| 2025-05 | 1,377 | 63.3% | 86.7% | 5.2% | 9,529 | 76.5% | 92.8% | 18.1% |
| 2025-06 | 1,397 | 70.2% | 94.7% | 6.4% | 8,645 | 77.8% | 90.7% | 18.4% |
| 2025-07 | 1,353 | 57.8% | 87.8% | 5.3% | 8,477 | 78.6% | 92.0% | 18.8% |
| 2025-08 | 1,327 | 58.7% | 87.3% | 4.7% | 8,555 | 77.4% | 92.1% | 18.0% |
| 2025-09 | 1,317 | 64.2% | 89.7% | 5.9% | 9,319 | 77.4% | 92.5% | 17.6% |
| 2025-10 | 1,409 | 64.4% | 86.5% | 5.5% | 10,488 | 75.5% | 91.9% | 17.7% |
| 2025-11 | 2,704 | 58.8% | 92.0% | 6.4% | 11,598 | 75.6% | 92.0% | 17.3% |
| 2025-12 | 4,298 | 61.8% | 89.6% | 6.8% | 12,693 | 75.3% | 90.9% | 16.5% |
| 2026-01 | 6,102 | 60.9% | 90.6% | 6.8% | 14,712 | 75.1% | 91.8% | 16.9% |
| 2026-02 | 7,702 | 61.1% | 87.7% | 7.0% | 14,261 | 75.3% | 92.1% | 16.6% |
| 2026-03 | 10,526 | 61.9% | 89.0% | 7.1% | 15,658 | 72.5% | 91.9% | 16.3% |
| 2026-04 | 11,716 | 60.4% | 88.6% | 6.5% | 14,387 | 70.3% | 91.3% | 15.3% |
| 2026-05 | 11,595 | 61.8% | 87.9% | 6.7% | 12,797 | 73.3% | 91.6% | 16.6% |
| 2026-06 | 11,243 | 60.9% | 87.2% | 6.3% | 12,207 | 71.8% | 91.6% | 15.9% |
| 2026-07 | 11,049 | 61.2% | 87.9% | 6.7% | 11,664 | 72.0% | 90.4% | 15.4% |
| 2026-08 | 11,139 | 60.9% | 87.8% | 6.3% | 11,629 | 72.3% | 93.1% | 15.8% |
| 2026-09 | 11,455 | 61.2% | 87.9% | 6.7% | 12,173 | 70.1% | 92.1% | 15.0% |


### Dekompozycja zmiany CR R1 -> R2: miks vs jakosc lejka

**Segmenty: kanal:** zmiana CR -2.18 pp = miks -2.35 pp + jakosc w segmentach +0.17 pp. Jakosc wg krokow: S1 +0.31 pp, S2 +0.07 pp, S3 -0.25 pp, S4 +0.02 pp, S5 +0.01 pp, S6 +0.00 pp
**Segmenty: kanal x urzadzenie x przegladarki:** zmiana CR -2.18 pp = miks -2.80 pp + jakosc w segmentach +0.62 pp. Jakosc wg krokow: S1 +0.44 pp, S2 +0.18 pp, S3 -0.11 pp, S4 +0.08 pp, S5 +0.03 pp, S6 +0.00 pp
Czytanie: 'miks' = efekt przesuniecia ruchu do segmentow o innej konwersji przy stalych stawkach R1; 'jakosc' = zmiana konwersji wewnatrz tych samych segmentow, rozlozona na kroki lejka metoda LMDI (sumuje sie dokladnie).

## 3. Detekcja ukrytych zdarzen na osi czasu


### Punkty zmiany (binary segmentation, test t na dziennych wartosciach)

Parametry: min. segment 7 dni, |t| >= 7.0, zmiana wzgledna >= 10%. Delta/dzien = (po - przed) x sredni dzienny mianownik po zmianie (np. dodatkowe zamowienia/dzien).
| data | szereg | przed | po | zmiana | |t| | dni przed/po | delta / dzien |
|---|---|---|---|---|---|---|---|
| 2024-10-08 | udzial kanalu direct | 0.1098 | 0.1492 | +35.9% | 9.2 | 7/466 | +19.0 sesji |
| 2024-10-11 | udzial kanalu sms | 0 | 0.0004891 | +inf% | 2.2 | 10/20 | +0.2 sesji |
| 2024-10-14 | udzial zalogowanych na wejsciu | 0.0003691 | 0.008124 | +2100.7% | 9.1 | 13/31 | +3.1 sesji |
| 2024-10-15 | udzial kanalu email | 0.0008693 | 0.005202 | +498.5% | 7.8 | 14/28 | +1.7 sesji |
| 2024-10-18 | nowi pacjenci | 38.41 | 50.23 | +30.8% | 7.2 | 17/189 | +11.8 pacjentow |
| 2024-10-21 | sesje | 347.1 | 482.5 | +39.0% | 11.5 | 20/192 | +135.3 sesji |
| 2024-10-28 | rejestracje | 51.07 | 64.31 | +25.9% | 7.6 | 27/178 | +13.2 rejestracji |
| 2024-10-31 | udzial kanalu sms | 0.0004891 | 0.00403 | +724.0% | 9.8 | 20/104 | +1.7 sesji |
| 2024-11-04 | spend gs_brand | 26.87 | 40.16 | +49.5% | 9.5 | 34/378 | +13.3 PLN |
| 2024-11-04 | zamowienia | 42.74 | 56.79 | +32.9% | 7.4 | 34/28 | +14.1 zamowien |
| 2024-11-12 | udzial kanalu email | 0.005202 | 0.009538 | +83.3% | 4.9 | 28/40 | +2.0 sesji |
| 2024-11-14 | udzial zalogowanych na wejsciu | 0.008124 | 0.01686 | +107.5% | 7.2 | 31/26 | +3.9 sesji |
| 2024-12-02 | zamowienia | 56.79 | 72.12 | +27.0% | 10.6 | 28/336 | +15.3 zamowien |
| 2024-12-10 | udzial zalogowanych na wejsciu | 0.01686 | 0.03047 | +80.8% | 9.5 | 26/67 | +6.7 sesji |
| 2024-12-20 | CR sesja->zamowienie | 0.1256 | 0.1593 | +26.9% | 15.4 | 80/409 | +17.0 zamowien |
| 2024-12-22 | udzial kanalu email | 0.009538 | 0.01683 | +76.4% | 6.2 | 40/48 | +3.6 sesji |
| 2025-01-12 | S3 konto/termin [desktop] | 0.6742 | 0.7597 | +12.7% | 9.8 | 103/627 | +3.3 sesji przechodzacych krok |
| 2025-01-14 | GO zakupy | 3.105 | 4.62 | +48.8% | 6.7 | 105/234 | +1.5 GO |
| 2025-01-18 | CPC gs_generic_erecepta | 5.235 | 5.829 | +11.3% | 10.9 | 109/134 | +23.2 PLN/klik |
| 2025-02-08 | udzial kanalu email | 0.01683 | 0.02548 | +51.4% | 6.8 | 48/41 | +4.5 sesji |
| 2025-02-12 | udzial kanalu sms | 0.00403 | 0.007739 | +92.0% | 5.5 | 104/31 | +2.0 sesji |
| 2025-02-15 | udzial zalogowanych na wejsciu | 0.03047 | 0.04662 | +53.0% | 7.5 | 67/55 | +8.3 sesji |
| 2025-02-28 | CPC gs_generic_l4 | 5.556 | 6.351 | +14.3% | 18.9 | 150/386 | +26.3 PLN/klik |
| 2025-03-15 | udzial kanalu sms | 0.007739 | 0.01364 | +76.2% | 8.1 | 31/239 | +2.6 sesji |
| 2025-03-21 | udzial kanalu email | 0.02548 | 0.031 | +21.6% | 3.4 | 41/29 | +2.8 sesji |
| 2025-03-27 | udzial rabatu GO | 0.08418 | 0.1712 | +103.4% | 25.9 | 177/553 | +8.2 zamowien |
| 2025-03-30 | rabat sr. | 4.287 | 7.124 | +66.2% | 13.9 | 180/145 | +201.3 PLN |
| 2025-04-11 | udzial zalogowanych na wejsciu | 0.04662 | 0.07781 | +66.9% | 13.6 | 55/215 | +13.5 sesji |
| 2025-04-19 | udzial kanalu email | 0.031 | 0.04514 | +45.6% | 8.5 | 29/258 | +6.7 sesji |
| 2025-04-24 | rejestracje | 64.31 | 50.59 | -21.3% | 11.5 | 178/200 | -13.7 rejestracji |
| 2025-04-25 | nowi pacjenci | 50.23 | 39.75 | -20.9% | 10.9 | 189/199 | -10.5 pacjentow |
| 2025-05-01 | sesje | 482.5 | 419.9 | -13.0% | 8.4 | 192/186 | -62.6 sesji |
| 2025-05-28 | udzial kanalu seo | 0.2647 | 0.2342 | -11.5% | 12.9 | 239/202 | -14.1 sesji |
| 2025-06-01 | CPC gs_generic_erecepta | 5.829 | 6.766 | +16.1% | 20.5 | 134/395 | +35.2 PLN/klik |
| 2025-08-22 | rabat sr. | 7.124 | 9.091 | +27.6% | 9.5 | 145/219 | +193.2 PLN |
| 2025-09-01 | spend gs_generic_erecepta | 212.7 | 267 | +25.5% | 11.0 | 335/395 | +54.3 PLN |
| 2025-09-05 | GO zakupy | 4.62 | 7.212 | +56.1% | 11.4 | 234/391 | +2.6 GO |
| 2025-09-15 | GO osobno | 9.286 | 11.36 | +22.3% | 1.4 | 7/14 | +2.1 GO |
| 2025-09-29 | GO osobno | 11.36 | 1.259 | -88.9% | 7.7 | 14/367 | -10.1 GO |
| 2025-10-01 | CPC meta_rmkt_koszyk | 1.368 | 1.536 | +12.3% | 20.8 | 351/343 | +3.5 PLN/klik |
| 2025-10-04 | spend meta_rmkt_koszyk | 15.76 | 22.05 | +39.9% | 7.5 | 368/73 | +6.3 PLN |
| 2025-11-03 | sesje | 419.9 | 628.6 | +49.7% | 14.0 | 186/63 | +208.7 sesji |
| 2025-11-03 | zamowienia | 72.12 | 94.03 | +30.4% | 11.3 | 336/62 | +21.9 zamowien |
| 2025-11-09 | udzial kanalu sms | 0.01364 | 0.009149 | -32.9% | 10.3 | 239/326 | -3.8 sesji |
| 2025-11-10 | nowi pacjenci | 39.75 | 70.34 | +76.9% | 29.4 | 199/325 | +30.6 pacjentow |
| 2025-11-10 | rejestracje | 50.59 | 90.63 | +79.1% | 32.0 | 200/325 | +40.0 rejestracji |
| 2025-11-12 | udzial zalogowanych na wejsciu | 0.07781 | 0.04857 | -37.6% | 19.8 | 215/323 | -24.9 sesji |
| 2025-11-14 | spend meta_prosp_l4_szybko | 66.31 | 151.2 | +128.1% | 9.3 | 11/17 | +84.9 PLN |
| 2025-11-14 | udzial kanalu google_cpc | 0.3539 | 0.2964 | -16.2% | 14.3 | 409/35 | -37.3 sesji |
| 2025-11-14 | udzial kanalu meta | 0.1602 | 0.2363 | +47.5% | 13.8 | 409/14 | +46.9 sesji |
| 2025-11-15 | udzial in_app w sesjach | 0.1044 | 0.175 | +67.7% | 18.4 | 410/20 | +44.4 sesji |
| 2025-11-16 | opoznienie startu [min] [internista] | 4.179 | 5.942 | +42.2% | 8.6 | 411/33 | +116.3 min |
| 2025-11-17 | spend gs_brand | 40.16 | 67.78 | +68.8% | 29.7 | 378/318 | +27.6 PLN |
| 2025-11-26 | udzial celu L4 | 0.195 | 0.2574 | +32.0% | 11.3 | 421/73 | +6.6 zamowien |
| 2025-11-27 | udzial kanalu affiliate | 0.0288 | 0.02153 | -25.2% | 8.0 | 422/83 | -5.5 sesji |
| 2025-11-28 | udzial kanalu meta | 0.2363 | 0.2659 | +12.5% | 4.1 | 14/15 | +19.3 sesji |
| 2025-12-01 | CPC gs_brand | 1.018 | 1.216 | +19.4% | 28.0 | 426/304 | +11.2 PLN/klik |
| 2025-12-01 | spend meta_prosp_l4_szybko | 151.2 | 225.1 | +48.8% | 6.4 | 17/16 | +73.8 PLN |
| 2025-12-05 | udzial in_app w sesjach | 0.175 | 0.2162 | +23.5% | 7.0 | 20/28 | +26.6 sesji |
| 2025-12-10 | udzial promo | 0.08138 | 0.1497 | +84.0% | 14.5 | 435/49 | +7.1 zamowien |
| 2025-12-13 | udzial kanalu meta | 0.2659 | 0.32 | +20.3% | 10.5 | 15/292 | +47.2 sesji |
| 2025-12-16 | spend meta_rmkt_koszyk | 22.05 | 35.29 | +60.1% | 13.8 | 73/289 | +13.2 PLN |
| 2025-12-16 | udzial kanalu seo | 0.2342 | 0.21 | -10.3% | 8.1 | 202/61 | -18.7 sesji |
| 2025-12-17 | spend meta_prosp_l4_szybko | 225.1 | 279.6 | +24.2% | 2.6 | 16/19 | +54.5 PLN |
| 2025-12-19 | opoznienie startu [min] [internista] | 5.942 | 7.661 | +28.9% | 5.1 | 33/24 | +115.4 min |
| 2025-12-19 | udzial kanalu google_cpc | 0.2964 | 0.2642 | -10.9% | 6.9 | 35/43 | -23.9 sesji |
| 2026-01-02 | udzial in_app w sesjach | 0.2162 | 0.2646 | +22.4% | 7.7 | 28/47 | +40.7 sesji |
| 2026-01-02 | udzial kanalu email | 0.04514 | 0.02971 | -34.2% | 14.4 | 258/272 | -13.7 sesji |
| 2026-01-04 | zamowienia | 94.03 | 120 | +27.6% | 11.8 | 62/147 | +25.9 zamowien |
| 2026-01-05 | sesje | 628.6 | 892.9 | +42.0% | 16.8 | 63/269 | +264.3 sesji |
| 2026-01-05 | spend meta_prosp_l4_szybko | 279.6 | 453.1 | +62.1% | 7.6 | 19/28 | +173.5 PLN |
| 2026-01-11 | CPC meta_prosp_l4_szybko | 1.774 | 2.138 | +20.5% | 16.9 | 69/263 | +96.0 PLN/klik |
| 2026-01-12 | opoznienie startu [min] [internista] | 7.661 | 10.69 | +39.5% | 9.9 | 24/262 | +239.8 min |
| 2026-01-17 | udzial kanalu direct | 0.1492 | 0.1206 | -19.2% | 17.9 | 466/120 | -26.7 sesji |
| 2026-01-26 | % refunded | 0.02168 | 0.04851 | +123.8% | 16.5 | 482/248 | +3.0 zamowien |
| 2026-01-27 | % refunded L4 internista | 0.0588 | 0.1207 | +105.2% | 13.2 | 479/247 | +2.2 zamowien |
| 2026-01-28 | udzial promo | 0.1497 | 0.1971 | +31.7% | 7.3 | 49/54 | +5.9 zamowien |
| 2026-01-29 | CM2 D+30 / pacjent (kohorta dzienna) | 31.91 | 26.15 | -18.0% | 7.8 | 485/55 | -486.0 PLN |
| 2026-01-31 | udzial kanalu google_cpc | 0.2642 | 0.2326 | -12.0% | 8.1 | 43/39 | -29.0 sesji |
| 2026-02-02 | CR sesja->zamowienie | 0.1593 | 0.134 | -15.9% | 14.3 | 409/49 | -23.7 zamowien |
| 2026-02-02 | spend meta_prosp_l4_szybko | 453.1 | 574.4 | +26.8% | 9.0 | 28/241 | +121.3 PLN |
| 2026-02-05 | % zgody marketingowej | 0.6357 | 0.5331 | -16.1% | 21.8 | 492/238 | -9.5 rejestracji |
| 2026-02-05 | wiek sr. rejestrujacych | 37.74 | 33.8 | -10.4% | 35.6 | 492/238 | -363.6 lat |
| 2026-02-07 | udzial celu L4 | 0.2574 | 0.34 | +32.1% | 14.0 | 73/236 | +9.1 zamowien |
| 2026-02-09 | udzial kanalu tiktok | 0 | 0.03368 | +inf% | 14.1 | 496/11 | +31.7 sesji |
| 2026-02-10 | retencja D+30 kohort dziennych | 0.1067 | 0.06945 | -34.9% | 11.9 | 497/203 | -2.7 pacjentow powracajacych |
| 2026-02-15 | udzial kanalu seo | 0.21 | 0.1803 | -14.2% | 7.8 | 61/37 | -28.5 sesji |
| 2026-02-17 | spend tt_prosp_l4_15min | 54.28 | 104.6 | +92.7% | 7.2 | 8/12 | +50.3 PLN |
| 2026-02-18 | udzial in_app w sesjach | 0.2646 | 0.3189 | +20.5% | 10.1 | 47/14 | +51.1 sesji |
| 2026-02-18 | udzial kanalu affiliate | 0.02153 | 0.01497 | -30.5% | 7.7 | 83/225 | -5.9 sesji |
| 2026-02-20 | udzial kanalu tiktok | 0.03368 | 0.06197 | +84.0% | 10.3 | 11/8 | +26.5 sesji |
| 2026-02-24 | udzial specjalistow | 0.2794 | 0.2364 | -15.4% | 11.5 | 511/219 | -4.7 zamowien |
| 2026-02-28 | udzial kanalu tiktok | 0.06197 | 0.0803 | +29.6% | 6.1 | 8/11 | +17.3 sesji |
| 2026-03-01 | spend tt_prosp_l4_15min | 104.6 | 159.8 | +52.8% | 5.5 | 12/8 | +55.2 PLN |
| 2026-03-01 | udzial kanalu referral | 0.0123 | 0.00773 | -37.2% | 14.6 | 516/214 | -4.1 sesji |
| 2026-03-04 | udzial in_app w sesjach | 0.3189 | 0.3407 | +6.9% | 4.3 | 14/20 | +20.9 sesji |
| 2026-03-09 | spend tt_prosp_l4_15min | 159.8 | 210.9 | +32.0% | 5.6 | 8/8 | +51.1 PLN |
| 2026-03-10 | CPC tt_prosp_l4_15min | 1.446 | 1.796 | +24.2% | 15.7 | 29/205 | +75.2 PLN/klik |
| 2026-03-11 | udzial kanalu google_cpc | 0.2326 | 0.1901 | -18.3% | 14.3 | 39/204 | -38.1 sesji |
| 2026-03-11 | udzial kanalu tiktok | 0.0803 | 0.1139 | +41.8% | 7.3 | 11/22 | +33.1 sesji |
| 2026-03-11 | udzial mobile w sesjach | 0.7276 | 0.8176 | +12.4% | 51.8 | 526/204 | +80.8 sesji |
| 2026-03-17 | spend tt_prosp_l4_15min | 210.9 | 282.3 | +33.8% | 6.2 | 8/20 | +71.3 PLN |
| 2026-03-21 | CPC gs_generic_l4 | 6.351 | 5.404 | -14.9% | 23.3 | 386/194 | -26.6 PLN/klik |
| 2026-03-23 | CR sesja->zamowienie | 0.134 | 0.1205 | -10.1% | 8.1 | 49/192 | -12.0 zamowien |
| 2026-03-23 | udzial promo | 0.1971 | 0.238 | +20.7% | 7.2 | 54/192 | +4.4 zamowien |
| 2026-03-24 | udzial in_app w sesjach | 0.3407 | 0.3774 | +10.8% | 6.4 | 20/24 | +36.5 sesji |
| 2026-03-24 | udzial kanalu seo | 0.1803 | 0.1632 | -9.5% | 4.7 | 37/37 | -17.1 sesji |
| 2026-03-25 | CM2 D+30 / pacjent (kohorta dzienna) | 26.15 | 17.23 | -34.1% | 10.4 | 55/160 | -607.1 PLN |
| 2026-03-29 | rabat sr. | 9.091 | 11.41 | +25.5% | 14.2 | 219/186 | +246.9 PLN |
| 2026-03-31 | S1 usluga/sesja | 0.3657 | 0.3234 | -11.6% | 25.1 | 546/184 | -37.5 sesji z wyborem uslugi |
| 2026-04-02 | udzial kanalu tiktok | 0.1139 | 0.1422 | +24.8% | 4.5 | 22/8 | +28.0 sesji |
| 2026-04-06 | spend tt_prosp_l4_15min | 282.3 | 405.4 | +43.6% | 10.4 | 20/178 | +123.2 PLN |
| 2026-04-10 | udzial kanalu tiktok | 0.1422 | 0.1846 | +29.8% | 8.1 | 8/174 | +37.3 sesji |
| 2026-04-15 | spend gs_generic_lekarz_online | 258.3 | 216.1 | -16.4% | 8.1 | 561/169 | -42.2 PLN |
| 2026-04-17 | udzial in_app w sesjach | 0.3774 | 0.4259 | +12.9% | 10.5 | 24/167 | +42.6 sesji |
| 2026-04-30 | spend gs_generic_l4 | 205.9 | 138.7 | -32.7% | 15.6 | 576/154 | -67.3 PLN |
| 2026-04-30 | udzial kanalu seo | 0.1632 | 0.1399 | -14.3% | 8.9 | 37/154 | -20.2 sesji |
| 2026-05-17 | udzial kanalu direct | 0.1206 | 0.1039 | -13.8% | 10.6 | 120/137 | -14.4 sesji |
| 2026-05-31 | zamowienia | 120 | 101.4 | -15.5% | 11.8 | 147/123 | -18.6 zamowien |
| 2026-07-01 | CPC gs_generic_erecepta | 6.766 | 7.507 | +11.0% | 11.9 | 395/92 | +26.2 PLN/klik |
| 2026-09-09 | CPC meta_rmkt_koszyk | 1.536 | 1.694 | +10.3% | 7.6 | 343/22 | +3.6 PLN/klik |


### Impulsy: krotkie anomalie 1-6 dni (robust z vs mediana +/-14 dni)

| od | do | szereg | wartosc | mediana okna | z | wplyw (suma) |
|---|---|---|---|---|---|---|
| 2024-10-04 | 2024-10-04 | koszt lekarza / zamowienie | 67.36 | 49.49 | +8.6 | +643.4 PLN |
| 2024-10-06 | 2024-10-06 | udzial platnosci blik | 0.3077 | 0.5429 | -7.9 | -6.1 zamowien |
| 2024-11-07 | 2024-11-07 | opoznienie startu [min] [psychiatra] | 16.97 | 2.883 | +8.7 | +70.4 min |
| 2024-12-22 | 2024-12-22 | opoznienie startu [min] [ginekolog] | 18.12 | 4.142 | +6.7 | +69.9 min |
| 2025-05-16 | 2025-05-16 | udzial trybu video | 0.03279 | 0.1481 | -6.9 | -7.0 zamowien |
| 2025-07-19 | 2025-07-19 | % refunded | 0.04167 | 0.01449 | +9.6 | +1.3 zamowien |
| 2025-10-02 | 2025-10-02 | S4 start platn./konto [in_app] | 0.5 | 0.8333 | -6.7 | -2.0 sesji przechodzacych krok |
| 2025-11-01 | 2025-11-01 | udzial kanalu email | 0.0935 | 0.03825 | +6.3 | +13.6 sesji |
| 2025-11-01 | 2025-11-01 | udzial zalogowanych na wejsciu | 0.1463 | 0.06166 | +6.1 | +20.8 sesji |
| 2026-02-10 | 2026-02-10 | opoznienie startu [min] [psychiatra] | 17.44 | 3.595 | +7.4 | +83.1 min |
| 2026-02-26 | 2026-02-26 | opoznienie startu [min] [pediatra] | 11.29 | 2.573 | +6.7 | +43.6 min |
| 2026-03-20 | 2026-03-20 | opoznienie startu [min] [psychiatra] | 13.68 | 3.461 | +6.3 | +51.1 min |


### Weryfikacja: zdarzenie czy trend / efekt miksu?

Binary segmentation zamienia plynny trend na 'skok'. Ponizsze kontrole rozstrzygaja, ktore punkty zmiany to zdarzenia.
**Udzial rabatu GO (CP 2025-03-27) i rabat sredni (CP 2025-08-22):** aktywni czlonkowie GO 2024-12-01: 179, 2025-03-01: 531, 2025-03-27: 663, 2025-06-01: 966, 2025-09-01: 1,394, 2026-03-01: 2,263, 2026-09-01: 2,684. Stawki rabatu bez zmian (50% / 20%) -> narastanie bazy, nie zmiana zasad.
| okres | % refunded L4 z kodem | % refunded L4 bez kodu | % refunded cele nie-L4 | udzial zamowien z kodem L4 |
|---|---|---|---|---|
| 2025-11-01..2026-01-25 | 14.7% | 5.8% | 1.3% | 6.4% |
| 2026-01-26..2026-03-31 | 15.7% | 7.6% | 1.3% | 13.1% |

**Zgoda marketingowa i wiek (CP 2026-02-05):** w R2 wg kanalu rejestracji (n / % zgody / sr. wiek): google_cpc: 9,044 / 64.4% / 37.6, meta: 7,589 / 44.0% / 30.7, direct: 6,367 / 61.6% / 36.8, seo: 5,375 / 60.6% / 37.4, tiktok: 2,246 / 32.8% / 24.8, referral: 601 / 72.9% / 37.6, affiliate: 558 / 48.6% / 36.2. Wewnatrz kanalow stabilnie -> spadek to miks (Meta/TikTok: mlodsi, mniej zgod), nie zmiana formularza.
**Rejestracje/nowi pacjenci -21% (CP 2025-04-24), udzial SEO (CP 2025-05-28):** sesje SEO / mies. 2024-10: 2,948, 2024-11: 3,356, 2024-12: 3,897, 2025-01: 4,464, 2025-02: 4,006, 2025-03: 4,102, 2025-04: 3,882, 2025-05: 3,284, 2025-06: 2,789, 2025-07: 2,723, 2025-08: 2,799, 2025-09: 3,085, 2025-10: 3,687, 2025-11: 4,209, 2025-12: 4,486, 2026-01: 5,219, 2026-02: 4,989, 2026-03: 5,255, 2026-04: 4,860, 2026-05: 3,961, 2026-06: 3,767, 2026-07: 3,530, 2026-08: 3,544, 2026-09: 3,800 -> sezon infekcyjny (szczyt I-III, dolek VI-VIII w obu latach).
| zrodlo | starty platnosci (konsultacja) | % platnosc OK |
|---|---|---|
| crm_reactivation | 2,021 | 75.7% |
| crm_sms_przypomnienie | 965 | 76.7% |
| crm_recepta_przypomnienie | 1,082 | 79.9% |
| tiktok | 1,843 | 86.4% |
| affiliate | 955 | 88.2% |
| meta | 8,941 | 88.9% |
| google_cpc | 19,374 | 91.6% |
| referral | 957 | 92.4% |
| seo | 13,104 | 92.5% |
| direct | 20,007 | 94.6% |

**Opoznienie startu wizyty u internisty (CP 2025-11-16, 2025-12-19, 2026-01-12)** - srednia / p90 [min]: 2024-10: 3.8/10, 2024-11: 4.2/10, 2024-12: 4.1/10, 2025-01: 4.4/11, 2025-02: 4.1/10, 2025-03: 4.5/10, 2025-04: 4.3/10, 2025-05: 4.3/10, 2025-06: 4.0/10, 2025-07: 4.2/10, 2025-08: 4.1/10, 2025-09: 4.3/10, 2025-10: 3.9/10, 2025-11: 4.9/12, 2025-12: 6.9/18, 2026-01: 8.7/24, 2026-02: 10.9/32, 2026-03: 10.5/30, 2026-04: 11.1/32, 2026-05: 10.4/29, 2026-06: 10.9/30, 2026-07: 10.7/30, 2026-08: 11.5/34, 2026-09: 11.3/32. No-show internisty w tym czasie stabilny (ok. 2-3%).

### Zdarzenia dyskretne (pierwsze/ostatnie wystapienia, pauzy)

Ceny katalogowe per specjalizacja: dermatolog: [109.0], endokrynolog: [119.0], ginekolog: [119.0], internista: [89.0], kardiolog: [109.0], neurolog: [109.0], pediatra: [95.0], psychiatra: [269.0], psycholog: [99.0], urolog: [109.0]
| data | zdarzenie | szczegoly |
|---|---|---|
| 2024-10-01 | pierwsze uzycie kodu `START10` | 3,386 uzyc do 2026-09-30 |
| 2024-10-01 | start kampanii platnej `gs_brand` | 730 dni ze spendem, sredni spend 52 zl/dzien |
| 2024-10-01 | start kampanii platnej `gs_generic_erecepta` | 730 dni ze spendem, sredni spend 242 zl/dzien |
| 2024-10-01 | start kampanii platnej `gs_generic_l4` | 730 dni ze spendem, sredni spend 192 zl/dzien |
| 2024-10-01 | start kampanii platnej `gs_generic_lekarz_online` | 730 dni ze spendem, sredni spend 249 zl/dzien |
| 2024-10-01 | start kampanii platnej `gs_generic_specjalisci` | 730 dni ze spendem, sredni spend 137 zl/dzien |
| 2024-10-01 | start kampanii platnej `meta_prosp_lekarz_online` | 730 dni ze spendem, sredni spend 161 zl/dzien |
| 2024-10-01 | start kampanii platnej `meta_rmkt_koszyk` | 730 dni ze spendem, sredni spend 24 zl/dzien |
| 2024-10-02 | pierwsze uzycie kodu `RANKING10` | 595 uzyc do 2026-09-29 |
| 2024-10-06 | pierwsze uzycie kodu `WRACAM15` | 355 uzyc do 2026-09-27 |
| 2025-09-08 | nowa wartosc: landing page = `/telemedigo` |  |
| 2025-09-08 | nowa wartosc: utm_campaign w sesjach = `crm_go_upsell` |  |
| 2025-09-08 | pierwszy zakup GO osobno (bez konsultacji) |  |
| 2025-11-03 | nowa wartosc: utm_campaign w sesjach = `meta_prosp_l4_szybko` |  |
| 2025-11-03 | start kampanii platnej `meta_prosp_l4_szybko` | 332 dni ze spendem, sredni spend 492 zl/dzien |
| 2025-11-04 | pierwsze uzycie kodu `L4SZYBKO20` | 3,511 uzyc do 2026-09-30 |
| 2026-02-09 | nowa wartosc: przegladarka = `TikTok` |  |
| 2026-02-09 | nowa wartosc: utm_campaign w sesjach = `tt_prosp_l4_15min` |  |
| 2026-02-09 | start kampanii platnej `tt_prosp_l4_15min` | 234 dni ze spendem, sredni spend 352 zl/dzien |
| 2026-02-10 | pierwsze uzycie kodu `TIKTOK25` | 1,665 uzyc do 2026-09-30 |


## 4. Wycena dzwigni wzrostowych (run-rate: 2026-04..09 x 2 = rocznie)

| inicjatywa | dCM2 / rok (central) | zakres | dCM2 / mies. | zalozenia |
|---|---|---|---|---|
| Wylaczenie `tt_prosp_l4_15min` | 30 340 | 30 340 .. 65 453 | 2 528 | spend 147 383 zl/rok; traci 3,800 pacjentow/rok x CM1 D+180 30.80 zl; high: 30% pacjentow wraca bezkosztowo |
| Wylaczenie `gs_generic_specjalisci` | 22 378 | 22 378 .. 31 807 | 1 865 | spend 53 806 zl/rok; traci 816 pacjentow/rok x CM1 D+180 38.51 zl; high: 30% pacjentow wraca bezkosztowo |
| Zdjecie rabatu 20% z kodu `L4SZYBKO20` (kampania Meta L4 zostaje) | 28 843 | -26 635 .. 62 129 | 2 404 | rabat 84 320 zl/rok; utrata konwersji 25% (10-50%) x 4,216 pacjentow/rok x CM1 D+180 32.64 zl |
| Realokacja uwolnionego budzetu (a1) do `gs_generic_erecepta` | 20 383 | -53 474 .. 94 241 | 1 699 | budzet 201 189 zl/rok; CM1 D+180 90.81 / CAC R2 61.84 = 1.47 zl na 1 zl; krancowa efektywnosc 75% (50-100%) |
| Repricing pediatry i psychologa do 119 zl | 33 146 | 30 039 .. 36 254 | 2 762 | pediatra: 1,472 zam./rok, CM1 dzis -14 292 zl/rok; psycholog: 274 zam./rok, CM1 dzis -1 245 zl/rok; spadek wolumenu 15% (0-30%), utracony wolumen mial ujemne CM1 |
| TelemediGO: rabat tylko u internisty (0% zamiast 20% u specjalistow) | 27 771 | -4 403 .. 49 220 | 2 314 | rabaty GO u specjalistow 49 220 zl/rok; spadek sprzedazy GO 10% (0-25%) z 214 490 zl/rok oplat |
| Test 'otworz w przegladarce' / uproszczenie kroku `S2 termin / usluga` w in-app (Meta/TikTok, mobile) | 10 546 | 0 .. 21 092 | 879 | in-app 55.9% vs Chrome/Safari 63.4% na tym kroku; 27,138 sesji/rok dochodzi do kroku; domkniecie 25% luki (0-50%) = 214 zam./rok x CM1 D+180 pacjenta in-app 49.26 zl. Niska pewnosc: na TikToku in-app = Chrome, luka na Meta to w duzej mierze samoselekcja |
| Naprawa platnosci w sesjach z e-mail/SMS (powracajacy pacjenci) | 9 440 | 4 720 .. 18 881 | 787 | sukces platnosci CRM 74.3% vs direct 95.2% (ta sama populacja zalogowanych); 2,732 startow platnosci/rok; domkniecie 50% luki (25-100%) x CM1/zam. z CRM 33.15 zl |
| Prekwalifikacja L4 przed platnoscia (ankieta / triage) - `L4SZYBKO20` | 8 860 | 4 430 .. 52 950 | 738 | zwroty L4 z kodem 17.3% -> 10.1% (poziom bez kodu); 261 unikniętych wizyt/rok x koszt lekarza 33.95 zl; high: zero zwrotow L4 we wszystkich zamowieniach |
| Wyczyszczenie TEST-QA (konta QA poza produkcja / bez rozliczenia lekarzy) | 40 900 | 0 .. 40 900 | 3 408 | low = scenariusz A (blad hurtowni, lekarz nieplacony); central/high = scenariusz B (wyplaty lekarzom) |

Suma central: **232 607 zl/rok** vs CM2 run-rate 933 142 zl/rok (+24.9%). Naklada sie glownie a2 i d1 (te same zamowienia L4SZYBKO20; przy -25% wolumenu d1 maleje o ok. 1/4); a3 zalezy od a1.
