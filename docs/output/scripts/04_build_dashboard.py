"""
04_build_dashboard.py - KROK 4: interaktywny dashboard (samowystarczalny index.html).

Laczy wyniki krokow 1-3 (metryki JSON + DECISION_LOG) z agregatami liczonymi tu na Clean Production
(kohorty dzienne per segment, kostka lejka, dzienne szeregi osi czasu, kaskada per kanal FT/LT)
i wstawia je jako JSON do szablonu dashboard_template.html.

Uruchomienie: python docs/output/scripts/04_build_dashboard.py
Wyjscie: index.html (root repo) + docs/output/index.html
"""
import html
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (DATA_END, OUT, ROOT, WINDOWS, Dataset, compute_cac, doctor_cost, dt, enrich_patients, km_at,
                    load_events, session_funnel, survival, year_of)

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "dashboard_template.html")
DATA_START = date(2024, 10, 1)
DAYS = [DATA_START + timedelta(days=i) for i in range((DATA_END - DATA_START).days + 1)]
DI = {d: i for i, d in enumerate(DAYS)}
N = len(DAYS)

print("Wczytywanie Clean Production...")
ds = Dataset()
compute_cac(ds)
go_by_user = enrich_patients(ds)
EV = load_events()
prod, _ = session_funnel(ds, EV)
orders, patients, sessions = ds.orders, ds.patients, ds.sessions


def load_metrics(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as f:
        return json.load(f)


M1 = load_metrics("01_data_audit_metrics.json")
M2 = load_metrics("02_unit_economics_metrics.json")
M3 = load_metrics("03_cohorts_and_funnels_metrics.json")


def r(x, n=2):
    return round(x, n) if isinstance(x, float) else x


D = {"generated": date.today().isoformat(), "start": DATA_START.isoformat(), "end": DATA_END.isoformat(),
     "windows": list(WINDOWS)}

# ---------------------------------------------------------------------------
# Zakladka 1: KPI, kaskada, rentownosc
# ---------------------------------------------------------------------------
print("Kaskada i rentownosc...")
wy = M2["waterfall_year"]
yoy = M1["yoy"]
D["kpi"] = {
    "new_patients": [yoy["new_paying_users"]["y1"], yoy["new_paying_users"]["y2"]],
    "orders": [wy["Y1"]["orders"], wy["Y2"]["orders"]],
    "gross": [wy["Y1"]["gross"], wy["Y2"]["gross"]],
    "spend": [wy["Y1"]["paid_media"], wy["Y2"]["paid_media"]],
    "refunds": [wy["Y1"]["ref_cancel"] + wy["Y1"]["ref_after"], wy["Y2"]["ref_cancel"] + wy["Y2"]["ref_after"]],
    "cm1": [wy["Y1"]["cm1"], wy["Y2"]["cm1"]],
    "cm2": [wy["Y1"]["cm2"], wy["Y2"]["cm2"]],
    "cm2_order": [wy["Y1"]["cm2"] / wy["Y1"]["orders"], wy["Y2"]["cm2"] / wy["Y2"]["orders"]],
    "cm2_order_last": M2["waterfall_month"]["2026-09"]["cm2"] / M2["waterfall_month"]["2026-09"]["orders"],
    "cr": [M3["cr_year"]["Y1"], M3["cr_year"]["Y2"]],
}
D["wf_year"] = {y: {k: r(v) for k, v in w.items()} for y, w in wy.items()}
D["wf_month"] = {m: {k: r(v) for k, v in w.items()} for m, w in sorted(M2["waterfall_month"].items())}

# kaskada per kanal pozyskania pacjenta (FT / LT)
WF_KEYS = ("orders", "gross", "disc_promo", "disc_go", "ref_cancel", "ref_after", "go_fees", "doc_completed",
           "doc_refunded", "marketing")


def wf_finish(w):
    w["billed"] = w["gross"] - w["disc_promo"] - w["disc_go"]
    w["net"] = w["billed"] - w["ref_cancel"] - w["ref_after"] + w["go_fees"]
    w["doctor"] = w["doc_completed"] + w["doc_refunded"]
    w["cm1"] = w["net"] - w["doctor"]
    w["cm2"] = w["cm1"] - w["marketing"]
    return {k: r(v) for k, v in w.items()}


wfc = {}
for model in ("ft", "lt"):
    acc = defaultdict(lambda: defaultdict(lambda: dict.fromkeys(WF_KEYS, 0.0)))
    for p in patients.values():
        ch = p[f"{model}_channel"]
        for o in p["orders"]:
            w = acc[ch][o["year"]]
            w["orders"] += 1
            w["gross"] += o["gross"]
            w["disc_promo"] += o["discount"] if o["disc_type"] == "promo" else 0
            w["disc_go"] += o["discount"] if o["disc_type"] == "go" else 0
            w["ref_cancel"] += o["refund"] if o["status"] == "cancelled" else 0
            w["ref_after"] += o["refund"] if o["status"] == "refunded" else 0
            w["doc_completed"] += o["doctor"] if o["status"] == "completed" else 0
            w["doc_refunded"] += o["doctor"] if o["status"] == "refunded" else 0
        for g in go_by_user.get(p["uid"], []):
            acc[ch][year_of(g["t"])]["go_fees"] += g["fee"]
        acc[ch][p["year"]]["marketing"] += p[f"cac_{model}"]
    wfc[model] = {ch: {y: wf_finish(w) for y, w in ys.items()} for ch, ys in acc.items()}
for y in ("Y1", "Y2"):
    tot = sum(wfc["ft"][ch][y]["cm2"] for ch in wfc["ft"] if y in wfc["ft"][ch])
    print(f"  kontrola kaskady {y}: suma kanalow CM2 {tot:,.0f} vs krok 2 {wy[y]['cm2']:,.0f}")
D["wf_channel"] = wfc


def group_stats(key, cac_key):
    gr = defaultdict(list)
    for p in patients.values():
        gr[p[key]].append(p)
    out = []
    for g, ps in sorted(gr.items(), key=lambda kv: -len(kv[1])):
        n = len(ps)
        e180 = [p for p in ps if 180 in p["win"]]
        e365 = [p for p in ps if 365 in p["win"]]
        cm1_first = [p["orders"][0]["cm1"] + sum(x["fee"] for x in go_by_user.get(p["uid"], []) if x["oid"] == p["first_oid"]) for p in ps]
        cm1_all = sum(sum(o["cm1"] for o in p["orders"]) + sum(x["fee"] for x in go_by_user.get(p["uid"], [])) for p in ps)
        cac = sum(p[cac_key] for p in ps)
        out.append({
            "name": g, "n": n, "n_y2": sum(p["year"] == "Y2" for p in ps), "cac": r(cac / n),
            "cm1_first": r(sum(cm1_first) / n), "cm2_first": r((sum(cm1_first) - cac) / n),
            "cm1_180": r(sum(p["win"][180][2] for p in e180) / len(e180)) if e180 else None,
            "cm2_180": r(sum(p["win"][180][2] - p[cac_key] for p in e180) / len(e180)) if e180 else None,
            "ret_180": r(sum(p["win"][180][0] for p in e180) / len(e180), 4) if e180 else None,
            "cm2_365": r(sum(p["win"][365][2] - p[cac_key] for p in e365) / len(e365)) if e365 else None,
            "mass": r(cm1_all - cac, 0), "spend": r(cac, 0),
        })
    return out


D["profit"] = {m: {"channel": group_stats(f"{m}_channel", f"cac_{m}"), "campaign": group_stats(f"{m}_key", f"cac_{m}"),
                   "code": group_stats("first_code", f"cac_{m}")} for m in ("ft", "lt")}
D["codes_orders"] = {k: {kk: r(vv) for kk, vv in v.items()} for k, v in M2["codes_orders"].items()}

sp = defaultdict(lambda: defaultdict(lambda: [0, 0.0]))
price = {}
vol_y2 = Counter()
for o in orders:
    price[o["spec"]] = o["gross"]
    if o["year"] == "Y2":
        vol_y2[o["spec"]] += 1
    if o["status"] == "completed":
        k = "go" if o["disc_type"] == "go" else ("promo" if o["disc_type"] == "promo" else "none")
        sp[o["spec"]][k][0] += 1
        sp[o["spec"]][k][1] += o["cm1"]
D["specs"] = [{"spec": s, "price": price[s], "doctor": doctor_cost(s), "orders_y2": vol_y2[s],
               **{f"cm1_{k}": r(sp[s][k][1] / sp[s][k][0]) if sp[s][k][0] else None for k in ("none", "go", "promo")},
               **{f"n_{k}": sp[s][k][0] for k in ("none", "go", "promo")}}
              for s in sorted(price, key=lambda s: -vol_y2[s])]

# ---------------------------------------------------------------------------
# Zakladka 2: kohorty dzienne, przezycie, os czasu
# ---------------------------------------------------------------------------
print("Kohorty dzienne...")
SEG_DIMS = [("ft_channel", "Kanał first-touch"), ("code_group", "Kod 1. zamówienia"), ("go_path", "TelemediGO"),
            ("first_cat", "Kategoria 1. wizyty")]
segs = {}


def seg(key):
    if key not in segs:
        segs[key] = {"n": [0] * N, "w": {k: [[0] * N for _ in range(4)] for k in WINDOWS}}
    return segs[key]


for p in patients.values():
    i = DI[p["first_t"].date()]
    for key in ["all"] + [f"{dim}|{p[dim]}" for dim, _ in SEG_DIMS]:
        s = seg(key)
        s["n"][i] += 1
        for k, vals in p["win"].items():
            arr = s["w"][k]
            for j in range(4):
                arr[j][i] += vals[j]
for s in segs.values():
    s["w"] = {str(k): [[round(x) for x in a] for a in arrs] for k, arrs in s["w"].items()}
D["cohort_dims"] = [{"key": d, "label": l, "values": sorted({p[d] for p in patients.values()},
                                                           key=lambda v: -sum(1 for p in patients.values() if p[d] == v))}
                    for d, l in SEG_DIMS]
D["cohorts"] = segs

km, gaps = survival(ds)
D["km"] = [r(1 - km_at(km, d), 4) for d in range(0, 541)]
cond = []
for d in (0, 7, 14, 30, 45, 60, 90, 120, 150, 180, 270):
    alive = [g for g in gaps if g > d]
    cond.append({"d": d, "n": len(alive), "p": r(sum(1 for g in alive if g <= 365) / len(alive), 4)})
D["cond_return"] = cond
fin = sorted(g for g in gaps if g <= 365)
D["gap_pct"] = {"p25": r(fin[len(fin) // 4], 1), "p50": r(fin[len(fin) // 2], 1), "p75": r(fin[3 * len(fin) // 4], 1),
                "p90": r(fin[9 * len(fin) // 10], 1)}
D["death_day"] = M3["death_day"]
r1 = [p for p in patients.values() if p["year"] == "Y1"]
D["r1"] = {**M3["r1_explain"], "cohorts": [
    {"m": m, "n": len(ps), "ever": r(sum(1 for p in ps if p["ret_days"]) / len(ps), 4),
     "in_r2": r(sum(1 for p in ps if any(o["year"] == "Y2" for o in p["orders"])) / len(ps), 4),
     "d90": r(sum(1 for p in ps if any(d <= 90 for d in p["ret_days"])) / len(ps), 4)}
    for m in sorted({p["cohort"] for p in r1}) for ps in [[p for p in r1 if p["cohort"] == m]]]}

print("Os czasu...")
TL = {k: [0.0] * N for k in ("sess", "ord_s", "inapp", "orders", "l4", "refunded", "cm1", "cm2", "spend", "new",
                              "delay_sum", "delay_n")}
for s in prod:
    i = DI[s["t"].date()]
    TL["sess"][i] += 1
    TL["ord_s"][i] += s["f"][5]
    TL["inapp"][i] += s["bg"] == "in_app"
delays = defaultdict(list)
for o in orders:
    i = DI[o["t"].date()]
    TL["orders"][i] += 1
    TL["l4"][i] += o["purpose"] == "l4"
    TL["refunded"][i] += o["status"] == "refunded"
    TL["cm1"][i] += o["cm1"]
    TL["cm2"][i] += o["cm1"]
    if o["spec"] == "internista" and o["started"]:
        dl = (dt(o["started"]) - dt(o["scheduled"])).total_seconds() / 60
        delays[i].append(dl)
        TL["delay_sum"][i] += dl
        TL["delay_n"][i] += 1
for g in ds.go:
    TL["cm2"][DI[g["t"].date()]] += g["fee"]
for x in ds.spend:
    TL["cm2"][DI[x["date"]]] -= x["spend"]
    TL["spend"][DI[x["date"]]] += x["spend"]
for p in patients.values():
    TL["new"][DI[p["first_t"].date()]] += 1
    if p["lt_channel"] == "affiliate":
        TL["cm2"][DI[p["first_t"].date()]] -= 25.0


def roll_pct(q, w):
    out = []
    for i in range(N):
        vals = sorted(v for j in range(max(0, i - w + 1), i + 1) for v in delays.get(j, []))
        out.append(r(vals[min(int(q * len(vals)), len(vals) - 1)], 1) if vals else None)
    return out


TL = {k: [r(v, 1) for v in arr] for k, arr in TL.items()}
for w in (1, 7, 28):
    TL[f"p50_{w}"] = roll_pct(0.5, w)
    TL[f"p90_{w}"] = roll_pct(0.9, w)
D["timeline"] = TL

D["events"] = [
    # data, typ, tytul, opis
    ("2024-10-21", "dane", "Pierwsze zamówienie konta TEST-QA", "Start kont QA na produkcji: do 2026-09 22 konta, 2 071 zamówień (1-min czat, 1 zł), rośnie co miesiąc."),
    ("2025-01-18", "marketing", "CPC gs_generic_erecepta +11%", "Pierwszy skok kosztu kliknięcia w kampanii e-recepta: 5,24 → 5,83 zł. Początek inflacji aukcji Google."),
    ("2025-02-28", "marketing", "CPC gs_generic_l4 +14%", "Koszt kliknięcia Google L4: 5,56 → 6,35 zł."),
    ("2025-06-01", "marketing", "CPC gs_generic_erecepta +16%", "Drugi skok: 5,83 → 6,77 zł/klik."),
    ("2025-09-01", "marketing", "Budżet gs_generic_erecepta +25%", "Spend 213 → 267 zł/dzień."),
    ("2025-09-08", "produkt", "Start GO bez konsultacji + e-mail crm_go_upsell", "Nowy landing /telemedigo i wysyłka do bazy: 225 zakupów GO osobno we wrześniu, 100% obecni pacjenci, 40% nigdy nie użyło GO."),
    ("2025-09-29", "produkt", "Koniec wysyłki crm_go_upsell", "Zakupy GO osobno −89% (11,4 → 1,3/dzień)."),
    ("2025-10-01", "marketing", "Retargeting Meta drożeje", "meta_rmkt_koszyk: CPC +12%, od 10-04 spend +40%, od 12-16 kolejne +60%."),
    ("2025-11-03", "marketing", "Start meta_prosp_l4_szybko + kod L4SZYBKO20", "Sesje +50% (420 → 629/dzień), zamówienia +30%, nowi pacjenci +77% od 11-10. Kod 20% od 11-04."),
    ("2025-11-15", "skutek", "Udział in-app browserów rośnie", "10,4% → 17,5% sesji; potem 21,6% (12-05), 26,5% (01-02), 31,9% (02-18), 37,7% (03-24), 42,6% (04-17)."),
    ("2025-11-16", "operacje", "Opóźnienie startu wizyty u internisty rośnie", "Średnio 4,2 → 5,9 min; dalej 7,7 (12-19) i 10,7 min (2026-01-12); p90 z 10 do 32 min. Przeciążenie lekarzy wolumenem L4."),
    ("2025-11-17", "marketing", "gs_brand: spend +69%, CPC +19% (12-01)", "Brand drożeje po starcie Meta L4: halo albo licytowanie marki przez konkurencję."),
    ("2025-11-26", "skutek", "Udział celu L4 w zamówieniach rośnie", "19,5% → 25,7%; od 2026-02-07 34,0%."),
    ("2026-01-11", "marketing", "CPC Meta L4 +20,5%", "Saturacja audytorium po 5 podbiciach budżetu (66 → 574 zł/dzień)."),
    ("2026-01-26", "skutek", "Odsetek zwrotów 2,2% → 4,9%", "Głównie miks (udział kodów L4 6,4% → 13,1%) + realny wzrost zwrotów L4 bez kodu 5,8% → 7,6%; cele nie-L4 bez zmian."),
    ("2026-02-02", "skutek", "CR sesja→zamówienie 15,9% → 13,4%", "Efekt miksu ruchu (Meta/TikTok/in-app), nie awaria lejka. Kolejny krok w dół 2026-03-23 (12,1%)."),
    ("2026-02-05", "skutek", "Zgody marketingowe 63,6% → 53,3%, wiek 37,7 → 33,8", "Miks kanałów, nie zmiana formularza: TikTok 32,8% zgód / 24,8 lat, Meta 44,0% / 30,7, Google 64,4% / 37,6."),
    ("2026-02-09", "marketing", "Start tt_prosp_l4_15min + kod TIKTOK25", "Skalowanie 54 → 405 zł/dzień do 2026-04-06; retencja D+30 tych pacjentów 2,1%."),
    ("2026-02-10", "skutek", "Retencja D+30 kohort dziennych −35%", "10,7% → 6,9%."),
    ("2026-03-10", "marketing", "CPC TikTok L4 +24%", "1,45 → 1,80 zł/klik."),
    ("2026-03-11", "skutek", "Udział mobile 72,8% → 81,8%", ""),
    ("2026-03-21", "marketing", "Przesunięcie budżetu z Google L4 na TikTok", "CPC gs_generic_l4 −15%; spend gs_generic_lekarz_online −16% (04-15), gs_generic_l4 −33% (04-30)."),
    ("2026-06-10", "dane", "Incydent ETL: podwójny load zamówień", "604 zdublowane zamówienia 2026-06-10…24 (36% zamówień z okna). Usunięte w Clean Production."),
    ("2026-07-01", "marketing", "CPC gs_generic_erecepta +11%", "6,77 → 7,51 zł/klik; łącznie +43% w 2 lata."),
]
D["events"] = [{"date": d, "kind": k, "title": t, "desc": x} for d, k, t, x in D["events"]]

# ---------------------------------------------------------------------------
# Zakladka 3: lejek i operacje
# ---------------------------------------------------------------------------
print("Kostka lejka...")
months = sorted({s["t"].strftime("%Y-%m") for s in prod})
devices = ["mobile", "desktop", "tablet"]
browsers = ["Chrome", "Safari", "Samsung Internet", "Firefox", "Edge", "Opera", "Instagram", "Facebook", "TikTok"]
channels = ["google_cpc", "meta", "seo", "direct", "tiktok", "email", "affiliate", "referral", "sms"]
order_by_sid = {o["sid"]: o for o in orders}
cube = defaultdict(lambda: [0] * 8)
for s in prod:
    key = (months.index(s["t"].strftime("%Y-%m")), devices.index(s["device"]), browsers.index(s["browser"]),
           channels.index(s["channel"]))
    c = cube[key]
    c[0] += 1
    for j, v in enumerate(s["f"]):
        c[j + 1] += v
    o = order_by_sid.get(s["sid"])
    c[7] += bool(s["f"][5] and o and o["status"] in ("completed", "refunded"))
D["funnel"] = {"months": months, "devices": devices, "browsers": browsers, "channels": channels,
               "rows": [list(k) + v for k, v in sorted(cube.items())]}
D["decomp"] = {"channel": M3["decomp_channel"], "full": M3["decomp_full"], "cr": M3["cr_year"]}
dm = defaultdict(list)
for o in orders:
    if o["spec"] == "internista" and o["started"]:
        dm[o["month"]].append((dt(o["started"]) - dt(o["scheduled"])).total_seconds() / 60)
D["ops"] = {
    "payment": M3["payment_success_by_source"],
    "delay": [{"m": m, "mean": r(sum(v) / len(v), 1), "p90": r(sorted(v)[int(0.9 * len(v))], 1), "n": len(v)}
              for m, v in sorted(dm.items())],
    "consent": M3["consent_by_channel_y2"],
}

# ---------------------------------------------------------------------------
# Zakladka 4: plan dzialan
# ---------------------------------------------------------------------------
META = {
    "a1 tt_prosp_l4_15min": dict(
        days=1, effort="Decyzja biznesowa (wyłączenie kampanii)", conf="wysoka",
        kpi="CM2 miesięcznie; spend TikTok = 0", guard="Nowi pacjenci z SEO/direct/brand oraz całkowity wolumen L4 (czy część pacjentów wraca innym kanałem)",
        method="Wyłączenie + porównanie z trendem kampanii Google (diff-in-diff, 4–6 tygodni); sezonowość z R1 jako baseline.",
        deps=""),
    "a1 gs_generic_specjalisci": dict(
        days=1, effort="Decyzja biznesowa (wyłączenie kampanii)", conf="wysoka",
        kpi="CM2 specjalistów; spend kampanii = 0", guard="Wolumen wizyt specjalistycznych z SEO/direct",
        method="Pre/post 6 tygodni vs ta sama pora roku w R1; kontrola: kampanie generic bez zmian.",
        deps="Najlepiej razem z b1 (repricing): bez naprawy cen specjalistów kampania nie ma szans na zwrot."),
    "a2 L4SZYBKO20": dict(
        days=3, effort="Konfiguracja kodu + landing (bez developmentu)", conf="średnia",
        kpi="CM2 / pozyskany pacjent kampanii meta_prosp_l4_szybko", guard="CR kampanii i liczba nowych pacjentów L4 (spadek ≤ 25%)",
        method="Test A/B 50/50 na landingu: kod 20% vs brak kodu, 4 tygodnie, losowanie po visitor_id.",
        deps="Nakłada się z d1 (te same zamówienia L4SZYBKO20)."),
    "a3 realokacja": dict(
        days=42, effort="Stopniowe skalowanie budżetu (performance)", conf="niska",
        kpi="Krańcowy CAC i CM2 D+90 gs_generic_erecepta", guard="CPC i impression share (inflacja aukcji, już +43% w 2 lata)",
        method="Podnoszenie budżetu o 25% co 2 tygodnie z pomiarem krańcowego CAC; stop, gdy krańcowe CM1 D+180 < CAC.",
        deps="Wymaga a1 (to jego budżet)."),
    "b1 repricing": dict(
        days=14, effort="Zmiana cennika + komunikacja", conf="wysoka",
        kpi="CM1 / wizyta pediatra i psycholog (cel > 0)", guard="Wolumen wizyt (spadek ≤ 15%) i porzucenia na kroku wyboru terminu",
        method="Test cenowy A/B (cena widoczna przy wyborze usługi) 4 tygodnie albo wdrożenie z monitoringiem elastyczności.",
        deps=""),
    "b2 GO": dict(
        days=14, effort="Zmiana regulaminu GO (nowe członkostwa)", conf="średnia",
        kpi="Rabaty GO u specjalistów; opłaty GO − rabaty", guard="Sprzedaż GO i retencja D+90 członków GO",
        method="Nowe zasady tylko dla nowych członkostw (obecne honorowane); porównanie kohort członkostw przed/po.",
        deps=""),
    "c1 in-app": dict(
        days=28, effort="Development (baner 'otwórz w przeglądarce', płatność one-click)", conf="niska",
        kpi="CR in-app (Meta, mobile)", guard="CR w Chrome/Safari (bez kanibalizacji)",
        method="Test A/B na ruchu in-app, 4 tygodnie; najpierw rozstrzygnąć samoselekcję vs tarcie (Known Unknowns #4).",
        deps=""),
    "c2 CRM platnosc": dict(
        days=21, effort="Diagnoza logów bramki + poprawka deep linków", conf="średnia",
        kpi="% płatność OK w sesjach e-mail/SMS (dziś ok. 74%)", guard="Liczba startów płatności z CRM",
        method="Analiza logów bramki płatniczej per kampania CRM, poprawka, pre/post 4 tygodnie.",
        deps=""),
    "d1 zwroty L4": dict(
        days=28, effort="Ankieta triage przed płatnością + ustalenia z lekarzami", conf="średnia",
        kpi="% refunded L4 z kodem (dziś ok. 17%) i koszt lekarza na zwrotach", guard="CR kampanii L4, liczba zamówień L4",
        method="Test A/B ankiety triage na ścieżce L4, 4 tygodnie.",
        deps="Nakłada się z a2."),
    "d2 TEST-QA": dict(
        days=7, effort="Wyłączenie kont QA z produkcji + uzgodnienie bilingu", conf="zależna od bilingu",
        kpi="Zamówienia kont testowych w produkcji = 0; koszt lekarzy w bilingu", guard="-",
        method="Uzgodnienie 2 071 zamówień z eksportem wypłat dla lekarzy (Known Unknowns #1).",
        deps=""),
}
DESC = {
    "a1 tt_prosp_l4_15min": "Kampania TikTok na szybkie L4: retencja D+180 3,1%, CM2 D+180 −3,61 zł na pacjenta. Nie spłaca się w żadnym oknie.",
    "a1 gs_generic_specjalisci": "Google na specjalistów: CAC ok. 58 zł przy CM1 1. wizyty 22 zł; CM2 D+365 −13,66 zł na pacjenta.",
    "a2 L4SZYBKO20": "Rabat 20% to główna różnica marży względem zamówień bez kodu (20 zł na zamówieniu); kampania zostaje.",
    "a3 realokacja": "Uwolniony budżet z a1 do najlepszej kampanii płatnej (e-recepta: najwyższe CM1 D+180 i retencja 34,7%).",
    "b1 repricing": "Pediatra (95 zł) i psycholog (99 zł) mają ujemne CM1 nawet bez rabatu (koszt lekarza 100 zł). Cena 119 zł jak u ginekologa.",
    "b2 GO": "Rabat GO 20% u specjalistów schodzi poniżej kosztu lekarza (dermatolog −12,80 zł, pediatra −24 zł na wizycie).",
    "c1 in-app": "Przeglądarki w aplikacjach Meta konwertują o połowę gorzej niż Chrome; na TikToku różnicy brak, więc to głównie samoselekcja.",
    "c2 CRM platnosc": "Sukces płatności w sesjach z e-mail/SMS 74–80% vs 94,6% direct przy tej samej populacji zalogowanych pacjentów.",
    "d1 zwroty L4": "Zwroty po odbytej wizycie L4 z kodem 16–17% vs 8–10% bez kodu; triage przed płatnością oszczędza koszt lekarza.",
    "d2 TEST-QA": "22 konta QA na produkcji: 2 071 zamówień, ok. 3,4 tys. zł/mies. kosztu lekarzy, jeśli wizyty są rozliczane.",
}
NAME = {
    "a1 tt_prosp_l4_15min": "Wyłączenie kampanii tt_prosp_l4_15min (TikTok L4)",
    "a1 gs_generic_specjalisci": "Wyłączenie kampanii gs_generic_specjalisci",
    "a2 L4SZYBKO20": "Zdjęcie rabatu 20% z kodu L4SZYBKO20 (kampania Meta L4 zostaje)",
    "a3 realokacja": "Realokacja budżetu z a1 do gs_generic_erecepta",
    "b1 repricing": "Repricing pediatry i psychologa do 119 zł",
    "b2 GO": "TelemediGO: rabat tylko u internisty (0% zamiast 20% u specjalistów)",
    "c1 in-app": "In-app browsery: test „otwórz w przeglądarce” / uproszczenie kroku S2",
    "c2 CRM platnosc": "Naprawa płatności w sesjach z e-mail/SMS",
    "d1 zwroty L4": "Prekwalifikacja (triage) L4 przed płatnością – L4SZYBKO20",
    "d2 TEST-QA": "Usunięcie kont TEST-QA z produkcji i rozliczeń lekarzy",
}
D["sizing"] = [{**s, **META[s["id"]], "desc": DESC[s["id"]], "inicjatywa": NAME[s["id"]]} for s in M3["sizing"]]
D["cm2_run_rate"] = M3["cm2_run_rate"]

# ---------------------------------------------------------------------------
# Zakladka 5: higiena danych, zalozenia
# ---------------------------------------------------------------------------
with open(os.path.join(OUT, "DECISION_LOG.md"), encoding="utf-8") as f:
    log = f.read()


def md_inline(s):
    s = html.escape(s.replace("\\|", "|"))
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)


def md_rows(prefix):
    out = []
    for line in log.splitlines():
        m = re.match(rf"^\| ({prefix}\d+) \| (.+) \|$", line)
        if m:
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", m.group(2))]
            out.append([m.group(1)] + [md_inline(c) for c in cells])
    return out


D["assumptions"] = md_rows("A")
D["cleaning"] = md_rows("C")
D["hygiene"] = {"tz": M1["tz_test"], "night": M1["night_shift"], "identity": M1["identity"],
                "attribution": M1["attribution"], "dups": M1["duplicates"], "dup_window": M1.get("orders_dup_window"),
                "clean": M2["clean"], "test": {k: v for k, v in M2["test_accounts"].items() if k != "by_month"}}
print(f"  zalozenia: {len(D['assumptions'])}, reguly czyszczenia: {len(D['cleaning'])}")

# ---------------------------------------------------------------------------
payload = json.dumps(D, ensure_ascii=False, separators=(",", ":"), default=str).replace("</", "<\\/")
with open(TEMPLATE, encoding="utf-8") as f:
    page = f.read()
page = page.replace("__DATA_JSON__", payload)
for path in (os.path.join(ROOT, "index.html"), os.path.join(OUT, "index.html")):
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
size = os.path.getsize(os.path.join(ROOT, "index.html"))
print(f"Zapisano index.html: {size / 1024 / 1024:.2f} MB (dane {len(payload.encode('utf-8')) / 1024 / 1024:.2f} MB)")
