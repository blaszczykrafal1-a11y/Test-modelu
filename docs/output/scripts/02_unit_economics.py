"""
02_unit_economics.py - KROK 2: marza jednostkowa (P&L zamowienia i pacjenta), Rok 1 vs Rok 2 i miesiac po miesiacu.

Dataset: Clean Production (common.py). Koszt lekarza wg README: completed + refunded; cancelled i no_show = 0
(wariant z kosztem no_show raportowany jako wrazliwosc).

Uruchomienie: python docs/output/scripts/02_unit_economics.py
Wyjscie: docs/output/02_unit_economics_report.md, docs/output/02_unit_economics_metrics.json
"""
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (AFFILIATE_FEE, OUT, PAID_MEDIA, Dataset, Report, doctor_cost, month, pct, year_of, zl,
                    zl2)

sys.stdout.reconfigure(encoding="utf-8")
R = Report()
M = {}
print("Wczytywanie Clean Production...")
ds = Dataset()
orders, patients, sessions = ds.orders, ds.patients, ds.sessions
DATA_END = date(2026, 9, 30)
YEARS = ("Y1", "Y2")

# ===========================================================================
# 0. Clean Production
# ===========================================================================
R.h("0. Dataset Clean Production")
R.table(["etap", "zamowienia"], [
    ["surowe wiersze orders.csv", f"{ds.raw_order_rows:,}"],
    ["- duplikaty ETL (C1)", f"-{ds.etl_duplicates:,}"],
    ["- zamowienia kont testowych (C2): TEST-QA", f"-{sum(1 for o in ds.test_orders if o['code'] == 'TEST-QA'):,}"],
    ["- zamowienia kont testowych (C2): pozostale zamowienia tych 22 kont", f"-{sum(1 for o in ds.test_orders if o['code'] != 'TEST-QA'):,}"],
    ["= Clean Production", f"{len(orders):,}"],
])
R.p(f"Pacjenci produkcyjni z zamowieniem: {len(patients):,}. GO produkcyjne: {len(ds.go):,} (testowe: {len(ds.test_go)}).")
M["clean"] = {"raw": ds.raw_order_rows, "etl_dups": ds.etl_duplicates, "test_orders": len(ds.test_orders),
              "prod_orders": len(orders), "patients": len(patients), "go": len(ds.go)}

# ===========================================================================
# 1. Anomalia: konta testowe
# ===========================================================================
print("1. Konta testowe...")
R.h("1. Anomalia: 22 konta TEST-QA")
to = ds.test_orders
t_sessions = [s for u in ds.test_users for s in ds.user_sessions.get(u, [])]
t_vis = {v for u in ds.test_users for v in ds.user_vis.get(u, ())}
t_anon = [s for v in t_vis for s in ds.vis_sessions[v] if not s["user"]]
order_sids = {o["sid"] for o in to}
R.table(["cecha", "wartosc"], [
    ["zamowienia (TEST-QA / pozostale)", f"{sum(o['code'] == 'TEST-QA' for o in to):,} / {sum(o['code'] != 'TEST-QA' for o in to):,}"],
    ["sesje zalogowane tych kont / w tym z zamowieniem", f"{len(t_sessions):,} / {len(order_sids & {s['sid'] for s in t_sessions}):,}"],
    ["visitor_id / sesje anonimowe tych visitorow", f"{len(t_vis)} / {len(t_anon):,}"],
    ["kanal sesji zamowien", dict(Counter(sessions[o['sid']]['channel'] for o in to))],
    ["urzadzenie / przegladarka", dict(Counter((sessions[o['sid']]['device'], sessions[o['sid']]['browser']) for o in to))],
    ["landing page", dict(Counter(sessions[o['sid']]['landing'] for o in to))],
    ["godziny zamowien (PL)", f"{min(o['t'].hour for o in to)}:00-{max(o['t'].hour for o in to)}:59"],
    ["dni tygodnia (0=pon)", dict(sorted(Counter(o['t'].weekday() for o in to).items()))],
    ["tryb / specjalizacja", f"{dict(Counter(o['mode'] for o in to))} / {dict(Counter(o['spec'] for o in to))}"],
    ["czas trwania wizyty [min]", dict(Counter(o['duration'] for o in to).most_common(3))],
    ["statusy TEST-QA", dict(Counter(o['status'] for o in to if o['code'] == 'TEST-QA'))],
    ["statusy pozostalych", dict(Counter(o['status'] for o in to if o['code'] != 'TEST-QA'))],
    ["kwoty pozostalych / refund", f"{dict(Counter(o['billed'] for o in to if o['code'] != 'TEST-QA'))} / {dict(Counter(o['refund'] for o in to if o['code'] != 'TEST-QA'))}"],
    ["GO kont testowych", len(ds.test_go)],
])
tm = defaultdict(Counter)
for o in to:
    tm[o["month"]]["orders"] += 1
    tm[o["month"]]["doctor"] += o["doctor"]
    tm[o["month"]]["net"] += o["net"]
active = defaultdict(set)
for o in to:
    active[o["month"]].add(o["uid"])
R.p("**Zachowanie w czasie** (miesiac: zamowienia / aktywne konta / koszt lekarza w scenariuszu B):")
R.p(", ".join(f"{m_}: {c['orders']}/{len(active[m_])}/{zl(c['doctor'])}" for m_, c in sorted(tm.items())))
first_seen = sorted(min(o["t"] for o in to if o["uid"] == u).date().isoformat() for u in ds.test_users)
R.p(f"Daty pierwszego zamowienia 22 kont (nowe konta QA dochodza w czasie): {', '.join(first_seen)}")
t_doc = sum(o["doctor"] for o in to)
t_net = sum(o["net"] for o in to)
R.table(["scenariusz", "przychod netto", "koszt lekarza", "wynik CM1"], [
    ["A: blad wykluczenia kont testowych z hurtowni (wizyty nieprawdziwe, lekarz nie rozliczany)", zl(t_net), "0", zl(t_net)],
    ["B: realny wyciek - lekarz rozliczany wg reguly README (completed + refunded)", zl(t_net), zl(t_doc), zl(t_net - t_doc)],
])
R.p("Za A przemawia: 1-minutowe wizyty, sam chat, godziny 9-17 w dni robocze, jeden desktop/Chrome na konto, "
    "brak ocen, 290 zamowien typu zaplac-89-zl-i-zwroc (test sciezki zwrotu). Za B: `started_at` jest wypelnione, "
    "czyli system odnotowal rozpoczecie wizyty przez lekarza - jesli rozliczenie z lekarzami bierze `completed/refunded` "
    "z tej samej tabeli, wyplata nastapila. Rozstrzygnie to tylko eksport rozliczen z lekarzami.")
M["test_accounts"] = {"orders": len(to), "net": round(t_net, 2), "doctor_cost_scenario_B": t_doc,
                      "sessions": len(t_sessions), "visitors": len(t_vis), "by_month": {k: dict(v) for k, v in tm.items()}}

# ===========================================================================
# 2. Pule kosztow marketingu i CAC
# ===========================================================================
print("2. CAC...")
spend_pool = defaultdict(float)  # (key, month) -> PLN
for r in ds.spend:
    spend_pool[(r["camp"], month(r["date"]))] += r["spend"]
# afiliacja: 25 zl za 1. oplacone zamowienie pacjenta, ktorego sesja 1. zamowienia jest z afiliacji (A10)
aff_lt = [p for p in patients.values() if p["lt_channel"] == "affiliate"]
aff_ft = [p for p in patients.values() if p["ft_channel"] == "affiliate"]
for p in aff_lt:
    spend_pool[("affiliate", p["cohort"])] += AFFILIATE_FEE


def allocate(key_field):
    cnt = Counter((p[key_field], p["cohort"]) for p in patients.values())
    unalloc = 0.0
    for k, v in spend_pool.items():
        if cnt.get(k, 0) == 0:
            unalloc += v
    for p in patients.values():
        k = (p[key_field], p["cohort"])
        p["cac_" + key_field[:2]] = spend_pool.get(k, 0.0) / cnt[k]
    return unalloc


unalloc_ft = allocate("ft_key")
unalloc_lt = allocate("lt_key")
total_mkt = sum(spend_pool.values())

# LTV pacjenta
go_by_user = defaultdict(list)
for g in ds.go:
    go_by_user[g["uid"]].append(g)
for p in patients.values():
    f = p["first_t"]
    os_ = p["orders"]
    gs = go_by_user.get(p["uid"], [])
    p["cm1_first"] = os_[0]["cm1"] + sum(g["fee"] for g in gs if g["oid"] == os_[0]["oid"])
    p["cm1_all"] = sum(o["cm1"] for o in os_) + sum(g["fee"] for g in gs)
    for d in (180, 365):
        lim = f + timedelta(days=d)
        p[f"elig_{d}"] = (f.date() + timedelta(days=d)) <= DATA_END
        p[f"cm1_{d}"] = sum(o["cm1"] for o in os_ if o["t"] <= lim) + sum(g["fee"] for g in gs if g["t"] <= lim)
        p[f"orders_{d}"] = sum(1 for o in os_ if o["t"] <= lim)
    p["go_member"] = bool(gs)

# ===========================================================================
# 3. Kaskada marzy
# ===========================================================================
print("3. Kaskada...")
R.h("2. Kaskada marzy (Waterfall) - Rok 1 vs Rok 2")


def waterfall(keyf):
    W = defaultdict(Counter)
    for o in orders:
        k = keyf(o["t"])
        w = W[k]
        w["orders"] += 1
        w["gross"] += o["gross"]
        w["disc_promo"] += o["discount"] if o["disc_type"] == "promo" else 0
        w["disc_go"] += o["discount"] if o["disc_type"] == "go" else 0
        w["ref_cancel"] += o["refund"] if o["status"] == "cancelled" else 0
        w["ref_after"] += o["refund"] if o["status"] == "refunded" else 0
        w["doc_completed"] += o["doctor"] if o["status"] == "completed" else 0
        w["doc_refunded"] += o["doctor"] if o["status"] == "refunded" else 0
        w["noshow_doc_sens"] += doctor_cost(o["spec"]) if o["status"] == "no_show" else 0
    for g in ds.go:
        W[keyf(g["t"])]["go_fees"] += g["fee"]
    for (key, m_), v in spend_pool.items():
        d = date.fromisoformat(m_ + "-01")
        W[keyf(d)]["affiliate" if key == "affiliate" else "paid_media"] += v
    for k, w in W.items():
        w["billed"] = w["gross"] - w["disc_promo"] - w["disc_go"]
        w["net"] = w["billed"] - w["ref_cancel"] - w["ref_after"] + w["go_fees"]
        w["doctor"] = w["doc_completed"] + w["doc_refunded"]
        w["cm1"] = w["net"] - w["doctor"]
        w["cm2"] = w["cm1"] - w["paid_media"] - w["affiliate"]
    return W


WY = waterfall(lambda t: year_of(t))
rows = [
    ("Gross Revenue (cennik konsultacji)", "gross", 1), ("- Rabaty: kody promo", "disc_promo", -1),
    ("- Rabaty: TelemediGO", "disc_go", -1), ("= Billed Revenue", "billed", 1),
    ("- Zwroty: anulacje (cancelled)", "ref_cancel", -1), ("- Zwroty po odbytej wizycie (refunded)", "ref_after", -1),
    ("+ Oplaty TelemediGO (89 zl)", "go_fees", 1), ("= Net Revenue", "net", 1),
    ("- Koszt lekarza: wizyty completed", "doc_completed", -1), ("- Koszt lekarza: wizyty refunded", "doc_refunded", -1),
    ("= CM1", "cm1", 1), ("- Paid media (CPC)", "paid_media", -1), ("- Prowizje afiliacyjne", "affiliate", -1),
    ("= CM2", "cm2", 1),
]
out = []
for label, k, sign in rows:
    y1, y2 = WY["Y1"][k], WY["Y2"][k]
    out.append([label, zl(y1), zl(y2), f"{(y2 / y1 - 1) * 100:+.1f}%" if y1 else "n/a",
                zl2(y1 / WY["Y1"]["orders"]), zl2(y2 / WY["Y2"]["orders"]), pct(y1, WY["Y1"]["gross"]), pct(y2, WY["Y2"]["gross"])])
R.table(["pozycja [PLN]", "Rok 1", "Rok 2", "YoY", "na zam. R1", "na zam. R2", "% gross R1", "% gross R2"], out)
R.p(f"Zamowienia: R1 {WY['Y1']['orders']:,}, R2 {WY['Y2']['orders']:,} ({(WY['Y2']['orders'] / WY['Y1']['orders'] - 1) * 100:+.1f}%). "
    f"CM2 / zamowienie: R1 **{zl2(WY['Y1']['cm2'] / WY['Y1']['orders'])}** vs R2 **{zl2(WY['Y2']['cm2'] / WY['Y2']['orders'])}** zl.")
R.p(f"**Wrazliwosc (koszt lekarza takze za no_show, wbrew README):** CM1 nizsze o {zl(WY['Y1']['noshow_doc_sens'])} zl w R1 "
    f"i {zl(WY['Y2']['noshow_doc_sens'])} zl w R2.")
M["waterfall_year"] = {y: {k: round(v, 2) for k, v in WY[y].items()} for y in YEARS}

# Most CM2 R1 -> R2
R.h("Most CM2: co zjadlo przyrost", 3)
bridge = [(label, sign * (WY["Y2"][k] - WY["Y1"][k])) for label, k, sign in rows if not label.startswith("=")]
R.table(["pozycja", "zmiana R2 vs R1 wplywu na CM2 [PLN]"], [[l_, zl(v)] for l_, v in bridge] +
        [["**= zmiana CM2**", f"**{zl(WY['Y2']['cm2'] - WY['Y1']['cm2'])}**"]])

WM = waterfall(lambda t: month(t))
R.h("Kaskada miesiac po miesiacu", 3)
R.table(["miesiac", "zam.", "Gross", "Rabaty", "Billed", "Zwroty", "GO fee", "Net", "Lekarz", "CM1", "CM1/zam",
         "Marketing", "CM2", "CM2/zam", "CM2 % Net"],
        [[m_, f"{w['orders']:,}", zl(w['gross']), zl(w['disc_promo'] + w['disc_go']), zl(w['billed']),
          zl(w['ref_cancel'] + w['ref_after']), zl(w['go_fees']), zl(w['net']), zl(w['doctor']), zl(w['cm1']),
          zl2(w['cm1'] / w['orders']), zl(w['paid_media'] + w['affiliate']), zl(w['cm2']), zl2(w['cm2'] / w['orders']),
          pct(w['cm2'], w['net'])] for m_, w in sorted(WM.items())])
M["waterfall_month"] = {m_: {k: round(v, 2) for k, v in w.items()} for m_, w in WM.items()}

# ===========================================================================
# 4. Kody rabatowe i mechanizm L4
# ===========================================================================
print("4. Kody...")
R.h("3. Kody rabatowe i kampanie L4")


def code_of(o):
    return o["code"] or ("GO" if o["disc_type"] == "go" else "brak")


agg = defaultdict(Counter)
for o in orders:
    a = agg[code_of(o)]
    a["n"] += 1
    for k in ("gross", "discount", "refund", "net", "doctor", "cm1"):
        a[k] += o[k]
    a[o["status"]] += 1
    a["doc_on_refunded"] += o["doctor"] if o["status"] == "refunded" else 0
R.h("Zamowienia wg kodu (wszystkie zamowienia z kodem)", 3)
R.table(["kod", "zam.", "Gross", "Rabat", "Zwroty", "Net", "Lekarz", "CM1", "CM1/zam", "% refunded", "% cancelled",
         "lekarz za zwrocone wizyty"],
        [[k, f"{a['n']:,}", zl(a['gross']), zl(a['discount']), zl(a['refund']), zl(a['net']), zl(a['doctor']),
          zl(a['cm1']), zl2(a['cm1'] / a['n']), pct(a['refunded'], a['n']), pct(a['cancelled'], a['n']),
          zl(a['doc_on_refunded'])] for k, a in sorted(agg.items(), key=lambda kv: -kv[1]['n'])])
M["codes_orders"] = {k: dict(v) for k, v in agg.items()}

# mechanizm: cel wizyty x kod
R.h("Mechanizm: cel wizyty x kod (internista)", 3)
mech = defaultdict(Counter)
for o in orders:
    if o["spec"] != "internista":
        continue
    c = code_of(o)
    grp = c if c in ("L4SZYBKO20", "TIKTOK25", "brak") else "inne kody / GO"
    k = (grp, o["purpose"])
    mech[k]["n"] += 1
    mech[k]["refunded"] += o["status"] == "refunded"
    mech[k]["cm1"] += o["cm1"]
R.table(["kod", "cel wizyty", "zam.", "% refunded", "CM1/zam"],
        [[g, pu, f"{c['n']:,}", pct(c['refunded'], c['n']), zl2(c['cm1'] / c['n'])]
         for (g, pu), c in sorted(mech.items()) if c["n"] >= 30])
spec_mix = defaultdict(Counter)
for o in orders:
    c = code_of(o)
    if c in ("L4SZYBKO20", "TIKTOK25"):
        spec_mix[c][(o["spec"], o["purpose"])] += 1
for c, cnt in spec_mix.items():
    R.p(f"Miks `{c}`: " + ", ".join(f"{s}/{pu}={v:,}" for (s, pu), v in cnt.most_common(6)))
# czy L4 bez kodu w tym samym czasie tez ma wysoki refund? (kontrola sezonowosci/polityki lekarzy)
ctrl = Counter()
for o in orders:
    if o["purpose"] == "l4" and o["spec"] == "internista" and o["year"] == "Y2":
        g = "kod L4" if o["code"] in ("L4SZYBKO20", "TIKTOK25") else ("brak kodu" if not o["code"] and o["disc_type"] == "none" else "inne")
        ctrl[(g, "n")] += 1
        ctrl[(g, "ref")] += o["status"] == "refunded"
R.p("Kontrola (L4 u internisty, tylko Rok 2): " + ", ".join(
    f"{g}: {pct(ctrl[(g, 'ref')], ctrl[(g, 'n')])} refunded (n={ctrl[(g, 'n')]:,})" for g in ("kod L4", "brak kodu", "inne")))
# kanal sesji zamowien z kodami L4
R.p("Kanal / kampania sesji zamowien z kodem: " + "; ".join(
    f"`{c}`: " + ", ".join(f"{k}={v:,}" for k, v in Counter(ds.cost_key(sessions[o['sid']]) for o in orders if o['code'] == c).most_common(4))
    for c in ("L4SZYBKO20", "TIKTOK25")))

# pacjenci pozyskani kodem
R.h("Pacjenci wg kodu PIERWSZEGO zamowienia (P&L pacjenta)", 3)


def patient_table(groups, label):
    rows_ = []
    res = {}
    for g, ps in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        n = len(ps)
        e180 = [p for p in ps if p["elig_180"]]
        e365 = [p for p in ps if p["elig_365"]]
        cac_ft = sum(p["cac_ft"] for p in ps) / n
        cac_lt = sum(p["cac_lt"] for p in ps) / n
        cm1f = sum(p["cm1_first"] for p in ps) / n
        cm1_180 = sum(p["cm1_180"] for p in e180) / len(e180) if e180 else None
        cm1_365 = sum(p["cm1_365"] for p in e365) / len(e365) if e365 else None
        cm2_180 = sum(p["cm1_180"] - p["cac_ft"] for p in e180) / len(e180) if e180 else None
        cm2_365 = sum(p["cm1_365"] - p["cac_ft"] for p in e365) / len(e365) if e365 else None
        mass = sum(p["cm1_all"] - p["cac_ft"] for p in ps)
        mass_lt = sum(p["cm1_all"] - p["cac_lt"] for p in ps)
        rep = sum(1 for p in e180 if p["orders_180"] > 1)
        f = lambda x: zl2(x) if x is not None else "-"
        rows_.append([g, f"{n:,}", zl2(cac_ft), zl2(cac_lt), zl2(cm1f), zl2(cm1f - cac_ft), f(cm1_180), f(cm2_180),
                      pct(rep, len(e180)) if e180 else "-", f(cm2_365), zl(mass), zl(mass_lt)])
        res[g] = {"n": n, "cac_ft": cac_ft, "cac_lt": cac_lt, "cm1_first": cm1f, "cm2_first_ft": cm1f - cac_ft,
                  "cm1_180": cm1_180, "cm2_180_ft": cm2_180, "cm2_365_ft": cm2_365, "repeat_180": rep / len(e180) if e180 else None,
                  "cm2_mass_ft": mass, "cm2_mass_lt": mass_lt, "n_180": len(e180), "n_365": len(e365)}
    R.table([label, "pacjenci", "CAC FT", "CAC LT", "CM1 1. zam.", "CM2 1. zam. (FT)", "CM1 180d", "CM2 180d (FT)",
             "% powrot 180d", "CM2 365d (FT)", "masa CM2 FT (caly okres)", "masa CM2 LT"], rows_)
    return res


by_code = defaultdict(list)
for p in patients.values():
    by_code[p["first_code"]].append(p)
M["codes_patients"] = patient_table(by_code, "kod 1. zamowienia")
R.p("CM1 180d/365d i CM2 180d/365d liczone tylko dla pacjentow z pelnym oknem obserwacji (1. zamowienie <= 2026-04-03 / <= 2025-09-30). "
    "CM1 pacjenta zawiera oplaty GO. CAC = koszt puli (kampania x miesiac kohorty) / liczba pacjentow przypisanych do niej.")

l4p = [p for p in patients.values() if p["first_code"] in ("L4SZYBKO20", "TIKTOK25")]
l4o = [o for o in orders if o["code"] in ("L4SZYBKO20", "TIKTOK25")]
burn = {
    "rabaty": sum(o["discount"] for o in l4o),
    "zwroty_po_wizycie": sum(o["refund"] for o in l4o if o["status"] == "refunded"),
    "lekarz_za_zwrocone": sum(o["doctor"] for o in l4o if o["status"] == "refunded"),
    "cac_ft": sum(p["cac_ft"] for p in l4p),
    "cm1_all": sum(p["cm1_all"] for p in l4p),
}
burn["cm2_mass_ft"] = burn["cm1_all"] - burn["cac_ft"]
R.p(f"**Bilans kodow L4 (L4SZYBKO20 + TIKTOK25):** {len(l4o):,} zamowien, {len(l4p):,} pacjentow. Rabaty {zl(burn['rabaty'])} zl, "
    f"zwroty po odbytej wizycie {zl(burn['zwroty_po_wizycie'])} zl, lekarz za zwrocone wizyty {zl(burn['lekarz_za_zwrocone'])} zl, "
    f"CAC (FT) {zl(burn['cac_ft'])} zl, CM1 pacjentow w calym oknie {zl(burn['cm1_all'])} zl -> **masa CM2 {zl(burn['cm2_mass_ft'])} zl**.")
M["l4_burn"] = burn

# ===========================================================================
# 5. Kanaly
# ===========================================================================
print("5. Kanaly...")
R.h("4. Kanaly pozyskania: First-Touch (stitched) vs Last-Touch")
R.p(f"Pula kosztow marketingu (CPC + afiliacja): {zl(total_mkt)} zl. Nieprzypisane (kampania x miesiac bez nowego pacjenta): "
    f"FT {zl(unalloc_ft)} zl, LT {zl(unalloc_lt)} zl. Prowizje afiliacyjne: {len(aff_lt):,} x 25 zl = {zl(len(aff_lt) * AFFILIATE_FEE)} zl "
    f"(LT); gdyby liczyc po FT: {len(aff_ft):,} x 25 zl.")
for key, lbl in (("ft_channel", "kanal FT (stitched)"), ("lt_channel", "kanal LT")):
    R.h(lbl, 3)
    gr = defaultdict(list)
    for p in patients.values():
        gr[p[key]].append(p)
    M[f"channels_{key}"] = patient_table(gr, lbl)
R.h("Kampanie platne i kanaly - FT (stitched), wg puli kosztowej", 3)
gr = defaultdict(list)
for p in patients.values():
    gr[p["ft_key"]].append(p)
M["campaigns_ft"] = patient_table(gr, "kampania / kanal FT")

R.h("CAC i CM1 1. zamowienia: kanal FT x rok", 3)
cy = defaultdict(list)
for p in patients.values():
    cy[(p["ft_channel"], p["year"])].append(p)
chans = sorted({k[0] for k in cy}, key=lambda c: -len(cy[(c, 'Y2')]))
R.table(["kanal FT", "pacjenci R1", "pacjenci R2", "CAC R1", "CAC R2", "CM1 1. zam. R1", "CM1 1. zam. R2", "CM2 1. zam. R1", "CM2 1. zam. R2"],
        [[c] + [f"{len(cy[(c, y)]):,}" for y in YEARS] +
         [zl2(sum(p['cac_ft'] for p in cy[(c, y)]) / max(len(cy[(c, y)]), 1)) for y in YEARS] +
         [zl2(sum(p['cm1_first'] for p in cy[(c, y)]) / max(len(cy[(c, y)]), 1)) for y in YEARS] +
         [zl2(sum(p['cm1_first'] - p['cac_ft'] for p in cy[(c, y)]) / max(len(cy[(c, y)]), 1)) for y in YEARS]
         for c in chans])

# ===========================================================================
# 6. TelemediGO
# ===========================================================================
print("6. GO...")
R.h("5. Ekonomika TelemediGO")
go_orders = [o for o in orders if o["disc_type"] == "go"]
gy = defaultdict(Counter)
for g in ds.go:
    gy[year_of(g["t"])]["fees"] += g["fee"]
    gy[year_of(g["t"])]["n"] += 1
    gy[year_of(g["t"])]["standalone"] += not g["oid"]
for o in go_orders:
    a = gy[o["year"]]
    a["orders"] += 1
    a["discount"] += o["discount"]
    a["net"] += o["net"]
    a["doctor"] += o["doctor"]
    a["cm1"] += o["cm1"]
    a["list_cm1"] += o["gross"] - o["refund"] * (o["gross"] / o["billed"] if o["billed"] else 0) - o["doctor"]
R.table(["metryka", "Rok 1", "Rok 2"], [
    ["czlonkostwa GO sprzedane (w tym osobno)", f"{gy['Y1']['n']:,} ({gy['Y1']['standalone']})", f"{gy['Y2']['n']:,} ({gy['Y2']['standalone']})"],
    ["przychod z oplat GO", zl(gy['Y1']['fees']), zl(gy['Y2']['fees'])],
    ["zamowienia z rabatem GO", f"{gy['Y1']['orders']:,}", f"{gy['Y2']['orders']:,}"],
    ["rabaty GO udzielone", zl(gy['Y1']['discount']), zl(gy['Y2']['discount'])],
    ["koszt lekarza wizyt GO", zl(gy['Y1']['doctor']), zl(gy['Y2']['doctor'])],
    ["CM1 wizyt GO (bez oplat)", zl(gy['Y1']['cm1']), zl(gy['Y2']['cm1'])],
    ["**program GO: oplaty - rabaty**", zl(gy['Y1']['fees'] - gy['Y1']['discount']), zl(gy['Y2']['fees'] - gy['Y2']['discount'])],
])
R.h("CM1 na odbyta wizyte wg specjalizacji: cena katalogowa vs z rabatem GO", 3)
sp = defaultdict(Counter)
for o in orders:
    if o["status"] != "completed":
        continue
    k = (o["spec"], "GO" if o["disc_type"] == "go" else ("promo" if o["disc_type"] == "promo" else "brak"))
    sp[k]["n"] += 1
    sp[k]["cm1"] += o["cm1"]
specs = sorted({k[0] for k in sp}, key=lambda s: -sp[(s, 'brak')]['n'])
R.table(["specjalizacja", "cena", "lekarz", "CM1/wizyta bez rabatu", "CM1/wizyta GO", "n GO", "CM1/wizyta promo"],
        [[s, zl2(next(o['gross'] for o in orders if o['spec'] == s)), zl(doctor_cost(s)),
          zl2(sp[(s, 'brak')]['cm1'] / max(sp[(s, 'brak')]['n'], 1)),
          zl2(sp[(s, 'GO')]['cm1'] / sp[(s, 'GO')]['n']) if sp[(s, 'GO')]['n'] else "-", f"{sp[(s, 'GO')]['n']:,}",
          zl2(sp[(s, 'promo')]['cm1'] / sp[(s, 'promo')]['n']) if sp[(s, 'promo')]['n'] else "-"] for s in specs])

# P&L czlonkostwa (zamkniete = waznosc skonczona przed koncem danych)
R.h("P&L pojedynczego czlonkostwa", 3)
user_orders = ds.user_orders
mem = []
for g in ds.go:
    os_ = [o for o in user_orders.get(g["uid"], []) if o["disc_type"] == "go" and g["t"] <= o["t"] and o["t"].date() <= g["valid_until"]]
    mem.append({"g": g, "closed": g["valid_until"] <= DATA_END, "n": len(os_),
                "disc": sum(o["discount"] for o in os_), "cm1": sum(o["cm1"] for o in os_)})
for lbl, ms in (("zamkniete (waznosc skonczona)", [m for m in mem if m["closed"]]), ("wszystkie", mem)):
    n = len(ms)
    R.p(f"**{lbl}**: {n:,} czlonkostw; srednio {sum(m['n'] for m in ms) / n:.2f} wizyt GO; "
        f"nieuzyte (0 wizyt z rabatem): {pct(sum(m['n'] == 0 for m in ms), n)}; tylko 1 wizyta (ta przy zakupie): {pct(sum(m['n'] == 1 for m in ms), n)}; "
        f"rabaty > 89 zl: {pct(sum(m['disc'] > 89 for m in ms), n)}; srednio oplata - rabaty = {zl2(sum(89 - m['disc'] for m in ms) / n)} zl; "
        f"srednio oplata + CM1 wizyt GO = {zl2(sum(89 + m['cm1'] for m in ms) / n)} zl.")
M["go_membership"] = {"closed_n": sum(m["closed"] for m in mem),
                      "closed_avg_fee_minus_disc": sum(89 - m["disc"] for m in mem if m["closed"]) / max(sum(m["closed"] for m in mem), 1)}

# retencja: GO przy 1. zamowieniu vs bez (kohorta R1, okno 365 d)
R.h("Czy GO poprawia retencje i wartosc pacjenta? (kohorta Rok 1, 365 dni od 1. zamowienia)", 3)
go_first = {g["uid"] for g in ds.go if g["oid"] and g["oid"] == patients.get(g["uid"], {}).get("first_oid")}
seg = defaultdict(list)
for p in patients.values():
    if not p["elig_365"]:
        continue
    first_spec = p["orders"][0]["spec"]
    seg[("GO przy 1. zam." if p["uid"] in go_first else "bez GO przy 1. zam.", "internista" if first_spec == "internista" else "specjalista")].append(p)
R.table(["segment", "1. wizyta", "pacjenci", "zam./pacjent 365d", "% powrot 365d", "CM1 365d (z oplata GO)", "CM2 365d (FT)"],
        [[a, b, f"{len(ps):,}", f"{sum(p['orders_365'] for p in ps) / len(ps):.2f}", pct(sum(p['orders_365'] > 1 for p in ps), len(ps)),
          zl2(sum(p['cm1_365'] for p in ps) / len(ps)), zl2(sum(p['cm1_365'] - p['cac_ft'] for p in ps) / len(ps))]
         for (a, b), ps in sorted(seg.items())])
R.p("Uwaga: samoselekcja - GO kupuja pacjenci, ktorzy i tak planuja wracac. Roznica to gorna granica efektu GO.")

# wrzesien 2025
R.h("Co sie stalo we wrzesniu 2025?", 3)
sa = [g for g in ds.go if not g["oid"]]
sa_m = defaultdict(Counter)
for g in sa:
    s = sessions[g["sid"]]
    sa_m[g["t"].strftime("%Y-%m")][ds.cost_key(s)] += 1
R.table(["miesiac", "GO osobno", "zrodlo sesji zakupu"],
        [[m_, sum(c.values()), ", ".join(f"{k}={v}" for k, v in c.most_common(4))] for m_, c in sorted(sa_m.items())])
upsell = Counter(s["t"].strftime("%Y-%m") for s in sessions.values() if s["camp"] == "crm_go_upsell")
R.p("Sesje z kampanii `crm_go_upsell` per miesiac: " + ", ".join(f"{k}: {v}" for k, v in sorted(upsell.items())))
sep = [g for g in sa if g["t"].strftime("%Y-%m") == "2025-09"]
sep_days = Counter(g["t"].date().isoformat() for g in sep)
prior = [g for g in sep if any(o["t"] < g["t"] for o in user_orders.get(g["uid"], []))]
had_go = [g for g in sep if any(x["t"] < g["t"] for x in go_by_user[g["uid"]] if x is not g)]
expiring = [g for g in sep if any(x["t"] < g["t"] and x["valid_until"] >= g["t"].date() for x in go_by_user[g["uid"]] if x is not g)]
R.p(f"Wrzesien 2025, GO osobno: {len(sep)}; dni z najwieksza sprzedaza: " + ", ".join(f"{d}={v}" for d, v in sep_days.most_common(5)) +
    f". Kupujacy z wczesniejszym zamowieniem: {pct(len(prior), len(sep))}; z wczesniejszym GO: {pct(len(had_go), len(sep))} "
    f"(w tym z nadal aktywnym GO: {len(expiring)}).")
used = []
for g in sep:
    os_ = [o for o in user_orders.get(g["uid"], []) if o["disc_type"] == "go" and g["t"] <= o["t"] and o["t"].date() <= g["valid_until"]]
    used.append(os_)
R.p(f"Wykorzystanie (do konca danych, waznosc do 2026-09): srednio {sum(len(u) for u in used) / len(sep):.2f} wizyt GO; "
    f"0 wizyt: {pct(sum(not u for u in used), len(sep))}; oplaty {zl(89 * len(sep))} zl vs rabaty {zl(sum(o['discount'] for u in used for o in u))} zl; "
    f"CM1 tych wizyt {zl(sum(o['cm1'] for u in used for o in u))} zl.")
M["go_sep2025"] = {"standalone": len(sep), "with_prior_order": len(prior), "with_prior_go": len(had_go),
                   "avg_go_visits": sum(len(u) for u in used) / len(sep), "unused": sum(not u for u in used),
                   "fees": 89 * len(sep), "discounts": sum(o["discount"] for u in used for o in u)}

# ---------------------------------------------------------------------------
R.write(os.path.join(OUT, "02_unit_economics_report.md"), "02 - Unit economics (scripts/02_unit_economics.py)")
with open(os.path.join(OUT, "02_unit_economics_metrics.json"), "w", encoding="utf-8") as f:
    json.dump(M, f, ensure_ascii=False, indent=2, default=lambda x: round(x, 2) if isinstance(x, float) else str(x))
print("\n".join(R.lines))
