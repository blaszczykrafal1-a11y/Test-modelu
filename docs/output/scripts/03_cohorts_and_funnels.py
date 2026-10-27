"""
03_cohorts_and_funnels.py - KROK 3: kohorty dzienne + krzywe LTV/retencji, lejek konwersji,
detekcja ukrytych zdarzen (change-points), wycena dzwigni wzrostowych.

Dataset: Clean Production (common.py). Tylko stdlib.

Uruchomienie: python docs/output/scripts/03_cohorts_and_funnels.py
Wyjscie: docs/output/03_cohorts_and_funnels_report.md, docs/output/03_cohorts_and_funnels_metrics.json
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (OUT, Dataset, Report, compute_cac, dt, load_events, pct, year_of, zl, zl2)

sys.stdout.reconfigure(encoding="utf-8")
R = Report()
M = {}
print("Wczytywanie Clean Production + eventy...")
ds = Dataset()
compute_cac(ds)
EV = load_events()
orders, patients, sessions = ds.orders, ds.patients, ds.sessions

DATA_START, DATA_END = date(2024, 10, 1), date(2026, 9, 30)
END_DT = datetime(2026, 10, 1)
DAYS = [DATA_START + timedelta(days=i) for i in range((DATA_END - DATA_START).days + 1)]
WINDOWS = (7, 14, 30, 60, 90, 180, 365)
RR_FROM = date(2026, 4, 1)  # run-rate: ostatnie 6 miesiecy x 2 (A20)
IN_APP = {"Instagram", "Facebook", "TikTok"}
L4_CODES = {"L4SZYBKO20", "TIKTOK25"}
STEP_NAMES = ["S1 wybor uslugi / sesja", "S2 termin / usluga", "S3 konto / termin", "S4 start platnosci / konto",
              "S5 platnosc OK / start platnosci", "S6 zamowienie / platnosc OK"]


def bgroup(b):
    return "in_app" if b in IN_APP else ("chrome/safari" if b in ("Chrome", "Safari") else "inne")


def f2(x):
    return zl2(x) if x is not None else "-"


# ===========================================================================
# 1. KOHORTY
# ===========================================================================
print("1. Kohorty...")
go_by_user = defaultdict(list)
for g in ds.go:
    go_by_user[g["uid"]].append(g)


def code_group(c):
    if c in L4_CODES:
        return "kod L4"
    return {"brak": "brak kodu", "GO": "rabat GO"}.get(c, "inne kody")


for p in patients.values():
    f, os_ = p["first_t"], p["orders"]
    gs = go_by_user.get(p["uid"], [])
    first = os_[0]
    p["code_group"] = code_group(p["first_code"])
    p["go_path"] = ("GO przy 1. zam." if any(g["oid"] == first["oid"] for g in gs)
                    else ("GO kupione pozniej" if gs else "bez GO"))
    p["first_cat"] = "specjalista" if first["spec"] != "internista" else f"internista: {first['purpose']}"
    p["ret_days"] = [(o["t"] - f).total_seconds() / 86400 for o in os_[1:]]
    p["win"] = {}
    for k in WINDOWS:
        if f.date() + timedelta(days=k) > DATA_END:
            continue
        lim = f + timedelta(days=k)
        fees = sum(g["fee"] for g in gs if g["t"] <= lim)
        net = sum(o["net"] for o in os_ if o["t"] <= lim) + fees
        cm1 = sum(o["cm1"] for o in os_ if o["t"] <= lim) + fees
        ret = any(d <= k for d in p["ret_days"])
        p["win"][k] = (ret, net, cm1, cm1 - p["cac_ft"])

R.h("1. Kohorty i krzywe retencji / LTV")
R.p("Kohorta = dzien 1. oplaconego zamowienia (czas PL). Retencja D+k = co najmniej jedno kolejne zamowienie w ciagu k dni. "
    "Wartosci skumulowane na pacjenta, wliczajac 1. zamowienie i oplaty GO; CM2 = CM1 - CAC (FT stitched). "
    "Kazde okno liczone tylko dla kohort z pelnym oknem obserwacji.")
rows, curve = [], {}
for k in WINDOWS:
    el = [p for p in patients.values() if k in p["win"]]
    n = len(el)
    r_ = sum(p["win"][k][0] for p in el)
    curve[k] = {"n": n, "ret": r_ / n, "net": sum(p["win"][k][1] for p in el) / n,
                "cm1": sum(p["win"][k][2] for p in el) / n, "cm2": sum(p["win"][k][3] for p in el) / n}
    rows.append([f"D+{k}", f"{n:,}", pct(r_, n), zl2(curve[k]["net"]), zl2(curve[k]["cm1"]), zl2(curve[k]["cm2"])])
R.table(["okno", "pacjenci w oknie", "retencja", "Net Revenue / pacjent", "CM1 / pacjent", "CM2 / pacjent"], rows)
M["curve"] = curve


def curve_by(dim, title, ks=(30, 90, 180, 365)):
    gr = defaultdict(list)
    for p in patients.values():
        gr[p[dim]].append(p)
    rows_, res = [], {}
    for g, ps in sorted(gr.items(), key=lambda kv: -len(kv[1])):
        row, rr = [g, f"{len(ps):,}"], {"n": len(ps)}
        for k in ks:
            el = [p for p in ps if k in p["win"]]
            v = sum(p["win"][k][0] for p in el) / len(el) if el else None
            row.append(f"{100 * v:.1f}%" if v is not None else "-")
            rr[f"ret_{k}"] = v
        for k in (30, 180, 365):
            el = [p for p in ps if k in p["win"]]
            v = sum(p["win"][k][3] for p in el) / len(el) if el else None
            row.append(f2(v))
            rr[f"cm2_{k}"] = v
        rows_.append(row)
        res[g] = rr
    R.h(title, 3)
    R.table([dim, "pacjenci"] + [f"ret D+{k}" for k in ks] + ["CM2 D+30", "CM2 D+180", "CM2 D+365"], rows_)
    return res


M["by_channel"] = curve_by("ft_channel", "Kanal first-touch (stitched)")
M["by_code"] = curve_by("code_group", "Kod 1. zamowienia")
M["by_go"] = curve_by("go_path", "Sciezka TelemediGO")
M["by_cat"] = curve_by("first_cat", "Kategoria 1. wizyty")

# macierz kohort miesiecznych
R.h("Kohorty miesieczne (agregacja kohort dziennych)", 3)
cm = defaultdict(list)
for p in patients.values():
    cm[p["cohort"]].append(p)
rows = []
for m_, ps in sorted(cm.items()):
    row = [m_, f"{len(ps):,}"]
    for k in (7, 30, 90, 180, 365):
        el = [p for p in ps if k in p["win"]]
        row.append(pct(sum(p["win"][k][0] for p in el), len(el)) if el else "-")
    for k in (30, 180, 365):
        el = [p for p in ps if k in p["win"]]
        row.append(f2(sum(p["win"][k][3] for p in el) / len(el)) if el else "-")
    row.append(pct(sum(p["code_group"] == "kod L4" for p in ps), len(ps)))
    rows.append(row)
R.table(["kohorta", "pacjenci", "D+7", "D+30", "D+90", "D+180", "D+365", "CM2 D+30", "CM2 D+180", "CM2 D+365", "% z kodem L4"], rows)

wk = defaultdict(list)
for p in patients.values():
    y, w, _ = p["first_t"].isocalendar()
    wk[f"{y}-W{w:02d}"].append(p)
M["weekly_d30"] = {w: {"n": len(ps), "ret30": (sum(p["win"][30][0] for p in ps if 30 in p["win"]) /
                                                max(sum(30 in p["win"] for p in ps), 1))} for w, ps in sorted(wk.items())}

# --- krzywa przezycia ---------------------------------------------------------
R.h("Krzywa przezycia: czas do 2. zamowienia (Kaplan-Meier) i kiedy pacjent 'umiera'", 3)
obs = []
for p in patients.values():
    if p["ret_days"]:
        obs.append((p["ret_days"][0], 1))
    else:
        obs.append(((END_DT - p["first_t"]).total_seconds() / 86400, 0))
obs.sort()
S, at_risk, i, km = 1.0, len(obs), 0, []
while i < len(obs):
    t = obs[i][0]
    d = c = 0
    while i < len(obs) and obs[i][0] == t:
        d += obs[i][1]
        c += 1
        i += 1
    if d:
        S *= 1 - d / at_risk
    km.append((t, S))
    at_risk -= c


def km_at(day):
    s = 1.0
    for t, v in km:
        if t > day:
            break
        s = v
    return s


checkpoints = (1, 7, 14, 30, 60, 90, 120, 180, 270, 365, 540)
R.table(["dzien"] + [f"D+{d}" for d in checkpoints],
        [["% pacjentow z 2. zamowieniem (KM)"] + [f"{100 * (1 - km_at(d)):.1f}%" for d in checkpoints]])
km_vals = {d: 1 - km_at(d) for d in checkpoints}
inc = [(checkpoints[j], km_vals[checkpoints[j]] - (km_vals[checkpoints[j - 1]] if j else 0)) for j in range(len(checkpoints))]
R.p("Przyrost udzialu powracajacych w przedzialach: " + ", ".join(
    f"do D+{d}: +{100 * v:.1f} pp" for d, v in inc))
M["km"] = km_vals

# warunkowe prawdopodobienstwo powrotu po d dniach bezczynnosci
gaps = []
for p in patients.values():
    os_ = p["orders"]
    for j, o in enumerate(os_):
        if o["t"] + timedelta(days=365) > END_DT:
            continue
        nxt = (os_[j + 1]["t"] - o["t"]).total_seconds() / 86400 if j + 1 < len(os_) else math.inf
        gaps.append(nxt)
rows, death = [], None
for d in (0, 7, 14, 30, 60, 90, 120, 180, 270):
    alive = [g for g in gaps if g > d]
    ret = sum(1 for g in alive if g <= 365)
    v = ret / len(alive) if alive else 0
    if death is None and v < 0.05:
        death = d
    rows.append([f"{d}", f"{len(alive):,}", f"{100 * v:.1f}%"])
R.table(["dni bez zamowienia", "zamowienia w probie", "P(kolejne zamowienie w 365 dni od ostatniego)"], rows)
fin = sorted(g for g in gaps if g <= 365)
R.p(f"Odstepy miedzy kolejnymi zamowieniami (gdy nastepuje w 365 dni, n={len(fin):,}): p25 {fin[len(fin) // 4]:.1f} d, "
    f"mediana {fin[len(fin) // 2]:.1f} d, p75 {fin[3 * len(fin) // 4]:.1f} d, p90 {fin[9 * len(fin) // 10]:.1f} d. "
    f"Pacjent 'umiera' (P powrotu < 5%) po **{death} dniach** bez zamowienia.")
M["death_day"] = death
M["gap_pct"] = {"p25": fin[len(fin) // 4], "p50": fin[len(fin) // 2], "p75": fin[3 * len(fin) // 4], "p90": fin[9 * len(fin) // 10]}

# --- dlaczego 11% ---------------------------------------------------------------
R.h("Dlaczego tylko 11% pacjentow z R1 kupilo w R2?", 3)
r1 = [p for p in patients.values() if p["year"] == "Y1"]
any_ret = sum(1 for p in r1 if p["ret_days"])
in_r2 = sum(1 for p in r1 if any(o["year"] == "Y2" for o in p["orders"]))
ret_in_r1_only = sum(1 for p in r1 if p["ret_days"] and not any(o["year"] == "Y2" for o in p["orders"]))
rows = []
for m_ in sorted({p["cohort"] for p in r1}):
    ps = [p for p in r1 if p["cohort"] == m_]
    rows.append([m_, f"{len(ps):,}", pct(sum(1 for p in ps if p["ret_days"]), len(ps)),
                 pct(sum(1 for p in ps if any(o["year"] == "Y2" for o in p["orders"])), len(ps)),
                 pct(sum(1 for p in ps if any(d <= 90 for d in p["ret_days"])), len(ps))])
R.table(["kohorta R1", "pacjenci", "kiedykolwiek wrocil", "kupil w R2", "wrocil w 90 dni"], rows)
R.p(f"R1: {len(r1):,} pacjentow; kiedykolwiek wrocilo {pct(any_ret, len(r1))}; kupilo w R2 {pct(in_r2, len(r1))}; "
    f"wrocilo, ale tylko w R1 {pct(ret_in_r1_only, len(r1))}.")
M["r1_explain"] = {"n": len(r1), "any_return": any_ret, "bought_in_r2": in_r2, "returned_only_r1": ret_in_r1_only}

# ===========================================================================
# 2. LEJEK
# ===========================================================================
print("2. Lejek...")
order_sids = {o["sid"]: o for o in orders}
prod_sessions = [s for s in sessions.values() if not ds.is_test_session(s)]
inconsist = Counter()
for s in prod_sessions:
    ev = EV.get(s["sid"], {})
    logged_entry = bool(s["user"]) and "account_completed" not in ev
    s1 = "service_selected" in ev
    s2 = s1 and "slot_selected" in ev
    s3 = s2 and ("account_completed" in ev or logged_entry)
    s4 = s3 and "payment_started" in ev
    s5 = s4 and "payment_succeeded" in ev
    od = s["sid"] in order_sids
    s["f"] = (s1, s2, s3, s4, s5, od and s5)
    s["logged_entry"] = logged_entry
    s["bg"] = bgroup(s["browser"])
    s["year"] = year_of(s["t"])
    if od and not s5:
        inconsist["zamowienie bez pelnej sciezki S1-S5"] += 1
    if s5 and not od:
        inconsist["S5 bez zamowienia (np. GO z usluga)"] += 1
    if "payment_started" in ev and not s1:
        inconsist["platnosc bez wyboru uslugi (GO osobno)"] += 1


def fun_agg(key_fn, filt=lambda s: True):
    agg = defaultdict(lambda: [0] * 7)
    for s in prod_sessions:
        if not filt(s):
            continue
        a = agg[key_fn(s)]
        a[0] += 1
        for j, v in enumerate(s["f"]):
            a[j + 1] += v
    return agg


def rates(a):
    out = []
    for j in range(6):
        out.append(a[j + 1] / a[j] if a[j] else 0.0)
    return out  # S1/n, S2/S1, S3/S2, S4/S3, S5/S4, ord/S5


def fun_table(agg, label, min_n=500):
    rows_ = []
    for k, a in sorted(agg.items(), key=lambda kv: (str(kv[0]))):
        if a[0] < min_n:
            continue
        r = rates(a)
        rows_.append([k if isinstance(k, str) else " / ".join(k), f"{a[0]:,}", pct(a[6], a[0])] + [f"{100 * x:.1f}%" for x in r[:5]])
    R.table([label, "sesje", "CR sesja->zam.", "S1 usluga", "S2 termin", "S3 konto", "S4 start platn.", "S5 platn. OK"], rows_)


R.h("2. Lejek konwersji (sesja -> zamowienie)")
R.p("Kroki: S1 `service_selected` / sesja; S2 `slot_selected` / S1; S3 konto (`account_completed` albo zalogowany na wejsciu) / S2; "
    "S4 `payment_started` / S3; S5 `payment_succeeded` / S4. CR = sesje z zamowieniem konsultacji / sesje. Sesje kont testowych wykluczone.")
R.p("Kontrola spojnosci: " + ", ".join(f"{k}: {v:,}" for k, v in inconsist.items()))
fy = fun_agg(lambda s: s["year"])
fun_table(fy, "rok", 0)
cr = {y: fy[y][6] / fy[y][0] for y in fy}
M["cr_year"] = cr
R.h("Urzadzenie x rok", 3)
fun_table(fun_agg(lambda s: (s["device"], s["year"])), "urzadzenie / rok")
R.h("Grupa przegladarek x rok", 3)
fun_table(fun_agg(lambda s: (s["bg"], s["year"])), "przegladarki / rok")
R.h("Przegladarka (caly okres)", 3)
fun_table(fun_agg(lambda s: s["browser"]), "przegladarka")
R.h("Kanal x rok", 3)
fun_table(fun_agg(lambda s: (s["channel"], s["year"])), "kanal / rok")
R.h("Meta + TikTok, mobile: in-app vs Chrome/Safari (kontrola miksu kanalu i urzadzenia)", 3)
ctrl = fun_agg(lambda s: (s["channel"], s["os"], s["bg"]),
               lambda s: s["channel"] in ("meta", "tiktok") and s["device"] == "mobile")
fun_table(ctrl, "kanal / OS / przegladarki", 300)

# --- czas: miesiac x krok ---------------------------------------------------
R.h("Kroki lejka miesiac po miesiacu (in-app vs Chrome/Safari)", 3)
fm = fun_agg(lambda s: (s["t"].strftime("%Y-%m"), s["bg"]))
rows = []
for m_ in sorted({k[0] for k in fm}):
    row = [m_]
    for g in ("in_app", "chrome/safari"):
        a = fm.get((m_, g))
        if not a or a[0] == 0:
            row += ["-"] * 4
            continue
        r = rates(a)
        row += [f"{a[0]:,}", f"{100 * r[2]:.1f}%", f"{100 * r[4]:.1f}%", pct(a[6], a[0])]
    rows.append(row)
R.table(["miesiac", "in-app sesje", "in-app S3 konto", "in-app S5 platn.", "in-app CR",
         "chr/saf sesje", "chr/saf S3 konto", "chr/saf S5 platn.", "chr/saf CR"], rows)

# --- dekompozycja spadku CR ---------------------------------------------------
R.h("Dekompozycja zmiany CR R1 -> R2: miks vs jakosc lejka", 3)


def decompose(key_fn, label):
    agg = fun_agg(lambda s: (key_fn(s), s["year"]))
    segs = {k[0] for k in agg}
    n1 = sum(agg[(s_, "Y1")][0] for s_ in segs if (s_, "Y1") in agg)
    n2 = sum(agg[(s_, "Y2")][0] for s_ in segs if (s_, "Y2") in agg)
    mix = rate_eff = 0.0
    step = [0.0] * 6
    for s_ in segs:
        a1, a2 = agg.get((s_, "Y1"), [0] * 7), agg.get((s_, "Y2"), [0] * 7)
        w1, w2 = a1[0] / n1, a2[0] / n2
        c2 = a2[6] / a2[0] if a2[0] else 0.0
        c1 = a1[6] / a1[0] if a1[0] else c2
        mix += (w2 - w1) * c1
        d = w2 * (c2 - c1)
        rate_eff += d
        r1_, r2_ = rates(a1), rates(a2)
        if a1[0] and a2[0] and all(x > 0 for x in r1_ + r2_) and c1 != c2:
            L = (c2 - c1) / (math.log(c2) - math.log(c1))
            for j in range(6):
                step[j] += w2 * L * math.log(r2_[j] / r1_[j])
        else:
            step[5] += d  # segmenty bez porownywalnego R1 trafiaja do reszty
    tot = cr["Y2"] - cr["Y1"]
    R.p(f"**{label}:** zmiana CR {100 * tot:+.2f} pp = miks {100 * mix:+.2f} pp + jakosc w segmentach {100 * rate_eff:+.2f} pp. "
        "Jakosc wg krokow: " + ", ".join(f"{STEP_NAMES[j].split(' ')[0]} {100 * step[j]:+.2f} pp" for j in range(6)))
    return {"total": tot, "mix": mix, "rate": rate_eff, "steps": step}


M["decomp_channel"] = decompose(lambda s: s["channel"], "Segmenty: kanal")
M["decomp_full"] = decompose(lambda s: (s["channel"], s["device"], s["bg"]), "Segmenty: kanal x urzadzenie x przegladarki")
R.p("Czytanie: 'miks' = efekt przesuniecia ruchu do segmentow o innej konwersji przy stalych stawkach R1; "
    "'jakosc' = zmiana konwersji wewnatrz tych samych segmentow, rozlozona na kroki lejka metoda LMDI (sumuje sie dokladnie).")

# ===========================================================================
# 3. DETEKCJA ZDARZEN
# ===========================================================================
print("3. Change-points...")
R.h("3. Detekcja ukrytych zdarzen na osi czasu")
SER = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))
LEVEL = set()
UNIT = {}


def rate(name, d, hit, den=1.0, unit="zamowien"):
    c = SER[name][d]
    c[0] += hit
    c[1] += den
    UNIT.setdefault(name, unit)


def level(name, d, v, unit="szt."):
    c = SER[name][d]
    c[0] += v
    c[1] = 1
    LEVEL.add(name)
    UNIT.setdefault(name, unit)


STEP_SHORT = ["S2 termin/usluga", "S3 konto/termin", "S4 start platn./konto", "S5 platn. OK/start"]
for s in prod_sessions:
    d = s["t"].date()
    f = s["f"]
    level("sesje", d, 1, "sesji")
    rate("CR sesja->zamowienie", d, f[5], unit="zamowien")
    rate("S1 usluga/sesja", d, f[0], unit="sesji z wyborem uslugi")
    for grp in ("all", s["bg"], s["device"]):
        suf = "" if grp == "all" else f" [{grp}]"
        for j in range(4):
            if f[j]:
                rate(STEP_SHORT[j] + suf, d, f[j + 1], unit="sesji przechodzacych krok")
    rate("udzial in_app w sesjach", d, s["bg"] == "in_app", unit="sesji")
    rate("udzial mobile w sesjach", d, s["device"] == "mobile", unit="sesji")
    rate("udzial zalogowanych na wejsciu", d, s["logged_entry"], unit="sesji")
    for ch in ("meta", "tiktok", "google_cpc", "seo", "direct", "email", "sms", "affiliate", "referral"):
        rate(f"udzial kanalu {ch}", d, s["channel"] == ch, unit="sesji")

for o in orders:
    d = o["t"].date()
    level("zamowienia", d, 1, "zamowien")
    rate("cena katalogowa sr.", d, o["gross"], unit="PLN")
    rate("kwota zaplacona sr.", d, o["billed"], unit="PLN")
    rate("rabat sr.", d, o["discount"], unit="PLN")
    rate("CM1 / zamowienie", d, o["cm1"], unit="PLN")
    rate("koszt lekarza / zamowienie", d, o["doctor"], unit="PLN")
    rate("udzial promo", d, o["disc_type"] == "promo")
    rate("udzial rabatu GO", d, o["disc_type"] == "go")
    for st in ("refunded", "cancelled", "no_show"):
        rate(f"% {st}", d, o["status"] == st)
    if o["purpose"] == "l4" and o["spec"] == "internista":
        rate("% refunded L4 internista", d, o["status"] == "refunded")
    rate("udzial celu L4", d, o["purpose"] == "l4")
    rate("udzial specjalistow", d, o["spec"] != "internista")
    for pm in ("blik", "card", "transfer"):
        rate(f"udzial platnosci {pm}", d, o["payment"] == pm)
    for md in ("phone", "chat", "video"):
        rate(f"udzial trybu {md}", d, o["mode"] == md)
    rate("udzial ocenionych", d, bool(o["rating"]))
    if o["rating"]:
        rate("ocena sr.", d, int(o["rating"]), unit="ocen")
    sch = dt(o["scheduled"])
    rate("czas do terminu [h]", d, (sch - o["t"]).total_seconds() / 3600, unit="h")
    sgrp = o["spec"] if o["spec"] in ("internista", "psychiatra", "pediatra", "ginekolog", "dermatolog") else "inni specjalisci"
    rate(f"cena katalogowa [{sgrp}]", d, o["gross"], unit="PLN")
    if o["started"]:
        rate(f"czas wizyty [min] [{sgrp}]", d, float(o["duration"]), unit="min")
        rate(f"opoznienie startu [min] [{sgrp}]", d, (dt(o["started"]) - sch).total_seconds() / 60, unit="min")

paid_sess = Counter()
for s in prod_sessions:
    if s["med"] in ("cpc", "paid_social"):
        paid_sess[(s["camp"], s["t"].date())] += 1
for r in ds.spend:
    d, c = r["date"], r["camp"]
    level(f"spend {c}", d, r["spend"], "PLN")
    if r["clicks"]:
        rate(f"CPC {c}", d, r["spend"], r["clicks"], unit="PLN/klik")
        rate(f"sesje na klik {c}", d, paid_sess[(c, d)], r["clicks"], unit="sesji")
for u in ds.users.values():
    d = dt(u["registered_at"]).date()
    level("rejestracje", d, 1, "rejestracji")
    rate("% zgody marketingowej", d, u["marketing_consent"] == "1", unit="rejestracji")
    rate("udzial kobiet", d, u["gender"] == "K", unit="rejestracji")
    rate("wiek sr. rejestrujacych", d, d.year - int(u["birth_year"]), unit="lat")
for g in ds.go:
    level("GO zakupy", g["t"].date(), 1, "GO")
    if not g["oid"]:
        level("GO osobno", g["t"].date(), 1, "GO")
for p in patients.values():
    d = p["first_t"].date()
    level("nowi pacjenci", d, 1, "pacjentow")
    if 30 in p["win"]:
        rate("retencja D+30 kohort dziennych", d, p["win"][30][0], unit="pacjentow powracajacych")
        rate("CM2 D+30 / pacjent (kohorta dzienna)", d, p["win"][30][3], unit="PLN")


def series_points(name):
    ser = SER[name]
    if name in LEVEL:
        days = [d for d in DAYS if min(ser) <= d <= max(ser)] if ser else []
        return [(d, ser[d][0] if d in ser else 0.0, 1.0) for d in days]
    return [(d, ser[d][0] / ser[d][1], ser[d][1]) for d in DAYS if d in ser and ser[d][1] >= 5]


def tstat(xs):
    n = len(xs)
    m = sum(xs) / n
    v = sum((x - m) ** 2 for x in xs) / (n - 1) if n > 1 else 0.0
    return m, v, n


MIN_SEG, T_MIN, REL_MIN = 7, 7.0, 0.10


def segment(pts, lo, hi, out, depth=0):
    xs = [p[1] for p in pts[lo:hi]]
    n = len(xs)
    if n < 2 * MIN_SEG or depth > 6:
        return
    pre = [0.0]
    pre2 = [0.0]
    for x in xs:
        pre.append(pre[-1] + x)
        pre2.append(pre2[-1] + x * x)
    best = None
    for k in range(MIN_SEG, n - MIN_SEG + 1):
        n1, n2 = k, n - k
        m1, m2 = pre[k] / n1, (pre[n] - pre[k]) / n2
        v1 = max((pre2[k] - n1 * m1 * m1) / (n1 - 1), 1e-12)
        v2 = max((pre2[n] - pre2[k] - n2 * m2 * m2) / (n2 - 1), 1e-12)
        t = (m2 - m1) / math.sqrt(v1 / n1 + v2 / n2)
        if best is None or abs(t) > abs(best[0]):
            best = (t, k)
    t, k = best
    m1 = sum(xs[:k]) / k
    m2 = sum(xs[k:]) / (n - k)
    rel = abs(m2 - m1) / max(abs(m1), 1e-9)
    if abs(t) >= T_MIN and rel >= REL_MIN:
        out.append(lo + k)
        segment(pts, lo, lo + k, out, depth + 1)
        segment(pts, lo + k, hi, out, depth + 1)


cps = []
for name in sorted(SER):
    pts = series_points(name)
    if len(pts) < 4 * MIN_SEG:
        continue
    br = []
    segment(pts, 0, len(pts), br)
    br = sorted(br)
    bounds = [0] + br + [len(pts)]
    for j, b in enumerate(br):
        left = pts[bounds[j]:b]
        right = pts[b:bounds[j + 2]]
        m1, v1, n1 = tstat([p[1] for p in left])
        m2, v2, n2 = tstat([p[1] for p in right])
        t = (m2 - m1) / math.sqrt(max(v1, 1e-12) / n1 + max(v2, 1e-12) / n2)
        den_day = sum(p[2] for p in right) / len(right)
        cps.append({"date": pts[b][0].isoformat(), "series": name, "before": m1, "after": m2,
                    "rel": (m2 - m1) / m1 if m1 else float("inf"), "t": t, "days_before": n1, "days_after": n2,
                    "delta_per_day": (m2 - m1) * den_day, "unit": UNIT.get(name, "")})

R.h("Punkty zmiany (binary segmentation, test t na dziennych wartosciach)", 3)
R.p(f"Parametry: min. segment {MIN_SEG} dni, |t| >= {T_MIN}, zmiana wzgledna >= {100 * REL_MIN:.0f}%. "
    "Delta/dzien = (po - przed) x sredni dzienny mianownik po zmianie (np. dodatkowe zamowienia/dzien).")
cps.sort(key=lambda c: (c["date"], c["series"]))
R.table(["data", "szereg", "przed", "po", "zmiana", "|t|", "dni przed/po", "delta / dzien"],
        [[c["date"], c["series"], f"{c['before']:.4g}", f"{c['after']:.4g}", f"{100 * c['rel']:+.1f}%", f"{abs(c['t']):.1f}",
          f"{c['days_before']}/{c['days_after']}", f"{c['delta_per_day']:+.1f} {c['unit']}"] for c in cps])
M["change_points"] = cps

# --- impulsy (krotkie awarie / akcje) -----------------------------------------------
R.h("Impulsy: krotkie anomalie 1-6 dni (robust z vs mediana +/-14 dni)", 3)
pulses = []
for name in sorted(SER):
    pts = series_points(name)
    if len(pts) < 60:
        continue
    vals = [p[1] for p in pts]
    flags = []
    for i_, (d, x, den) in enumerate(pts):
        win = vals[max(0, i_ - 14):i_] + vals[i_ + 1:i_ + 15]
        sw = sorted(win)
        med = sw[len(sw) // 2]
        mad = sorted(abs(w - med) for w in win)[len(win) // 2] * 1.4826
        if mad <= 0:
            continue
        z = (x - med) / mad
        if abs(z) >= 6 and abs(x - med) >= 0.3 * max(abs(med), 1e-9):
            flags.append((i_, d, x, med, z, den))
    # grupowanie dni z rzedu
    grp = []
    for fl in flags:
        if grp and fl[0] == grp[-1][-1][0] + 1:
            grp[-1].append(fl)
        else:
            grp.append([fl])
    for g in grp:
        if len(g) > 6:
            continue
        impact = sum((x - med) * den for _, _, x, med, _, den in g)
        pulses.append({"from": g[0][1].isoformat(), "to": g[-1][1].isoformat(), "series": name,
                       "value": sum(x for _, _, x, _, _, _ in g) / len(g), "median": sum(m for _, _, _, m, _, _ in g) / len(g),
                       "z": max((z for *_, z, _ in g), key=abs), "impact": impact, "unit": UNIT.get(name, "")})
pulses.sort(key=lambda p_: (p_["from"], p_["series"]))
R.table(["od", "do", "szereg", "wartosc", "mediana okna", "z", "wplyw (suma)"],
        [[p_["from"], p_["to"], p_["series"], f"{p_['value']:.4g}", f"{p_['median']:.4g}", f"{p_['z']:+.1f}",
          f"{p_['impact']:+.1f} {p_['unit']}"] for p_ in pulses])
M["pulses"] = pulses

# --- weryfikacja kluczowych punktow zmiany ----------------------------------------
R.h("Weryfikacja: zdarzenie czy trend / efekt miksu?", 3)
R.p("Binary segmentation zamienia plynny trend na 'skok'. Ponizsze kontrole rozstrzygaja, ktore punkty zmiany to zdarzenia.")


def share(xs, pred):
    return pct(sum(1 for x in xs if pred(x)), len(xs))


def between(o, a, b):
    return a <= o["t"].date() < b


# GO: aktywna baza czlonkow rosnie liniowo -> udzial rabatu GO to trend, nie zdarzenie
act = {d: sum(1 for g in ds.go if g["t"].date() <= d <= g["valid_until"]) for d in
       (date(2024, 12, 1), date(2025, 3, 1), date(2025, 3, 27), date(2025, 6, 1), date(2025, 9, 1), date(2026, 3, 1), date(2026, 9, 1))}
R.p("**Udzial rabatu GO (CP 2025-03-27) i rabat sredni (CP 2025-08-22):** aktywni czlonkowie GO " +
    ", ".join(f"{d}: {v:,}" for d, v in act.items()) + ". Stawki rabatu bez zmian (50% / 20%) -> narastanie bazy, nie zmiana zasad.")
# zwroty L4 przed/po 2026-01-26
cut = date(2026, 1, 26)
rows = []
for lbl, (a, b) in (("2025-11-01..2026-01-25", (date(2025, 11, 1), cut)), ("2026-01-26..2026-03-31", (cut, date(2026, 4, 1)))):
    l4 = [o for o in orders if between(o, a, b) and o["purpose"] == "l4" and o["spec"] == "internista"]
    kod = [o for o in l4 if o["code"] in L4_CODES]
    brak = [o for o in l4 if not o["code"] and o["disc_type"] == "none"]
    other = [o for o in orders if between(o, a, b) and o["purpose"] != "l4"]
    rows.append([lbl, share(kod, lambda o: o["status"] == "refunded"), share(brak, lambda o: o["status"] == "refunded"),
                 share(other, lambda o: o["status"] == "refunded"), share([o for o in orders if between(o, a, b)], lambda o: o["code"] in L4_CODES)])
R.table(["okres", "% refunded L4 z kodem", "% refunded L4 bez kodu", "% refunded cele nie-L4", "udzial zamowien z kodem L4"], rows)
# zgoda marketingowa i wiek: miks kanalow
reg_ch = {}
for s in sessions.values():
    if s["user"] and "account_completed" in EV.get(s["sid"], {}):
        if s["user"] not in reg_ch or s["utc"] < reg_ch[s["user"]][0]:
            reg_ch[s["user"]] = (s["utc"], s["channel"])
rc = defaultdict(lambda: [0, 0, 0])
for u in ds.users.values():
    if u["user_id"] in reg_ch and dt(u["registered_at"]).date() >= date(2025, 10, 1):
        c = rc[reg_ch[u["user_id"]][1]]
        c[0] += 1
        c[1] += u["marketing_consent"] == "1"
        c[2] += dt(u["registered_at"]).year - int(u["birth_year"])
R.p("**Zgoda marketingowa i wiek (CP 2026-02-05):** w R2 wg kanalu rejestracji (n / % zgody / sr. wiek): " +
    ", ".join(f"{k}: {v[0]:,} / {pct(v[1], v[0])} / {v[2] / v[0]:.1f}" for k, v in sorted(rc.items(), key=lambda kv: -kv[1][0])) +
    ". Wewnatrz kanalow stabilnie -> spadek to miks (Meta/TikTok: mlodsi, mniej zgod), nie zmiana formularza.")
M["consent_by_channel_y2"] = {k: {"n": v[0], "consent": v[1] / v[0], "age": v[2] / v[0]} for k, v in rc.items()}
# sezonowosc SEO
sm = Counter(s["t"].strftime("%Y-%m") for s in prod_sessions if s["channel"] == "seo")
R.p("**Rejestracje/nowi pacjenci -21% (CP 2025-04-24), udzial SEO (CP 2025-05-28):** sesje SEO / mies. " +
    ", ".join(f"{k}: {v:,}" for k, v in sorted(sm.items())) + " -> sezon infekcyjny (szczyt I-III, dolek VI-VIII w obu latach).")
# platnosci w CRM
crm = defaultdict(lambda: [0, 0])
for s in prod_sessions:
    ev = EV.get(s["sid"], {})
    if "payment_started" in ev and "service_selected" in ev:
        k = s["camp"] if s["channel"] in ("email", "sms") else s["channel"]
        crm[k][0] += 1
        crm[k][1] += "payment_succeeded" in ev
R.table(["zrodlo", "starty platnosci (konsultacja)", "% platnosc OK"],
        [[k, f"{v[0]:,}", pct(v[1], v[0])] for k, v in sorted(crm.items(), key=lambda kv: kv[1][1] / max(kv[1][0], 1))])
M["payment_success_by_source"] = {k: v[1] / v[0] for k, v in crm.items() if v[0]}
# obciazenie lekarzy
wm = defaultdict(list)
for o in orders:
    if o["spec"] == "internista" and o["started"]:
        wm[o["month"]].append((dt(o["started"]) - dt(o["scheduled"])).total_seconds() / 60)
R.p("**Opoznienie startu wizyty u internisty (CP 2025-11-16, 2025-12-19, 2026-01-12)** - srednia / p90 [min]: " +
    ", ".join(f"{m_}: {sum(v) / len(v):.1f}/{sorted(v)[int(0.9 * len(v))]:.0f}" for m_, v in sorted(wm.items())) +
    ". No-show internisty w tym czasie stabilny (ok. 2-3%).")
M["internist_delay"] = {m_: sum(v) / len(v) for m_, v in wm.items()}

# --- zdarzenia dyskretne ---------------------------------------------------------
R.h("Zdarzenia dyskretne (pierwsze/ostatnie wystapienia, pauzy)", 3)
disc = []
by_camp = defaultdict(dict)
for r in ds.spend:
    by_camp[r["camp"]][r["date"]] = r["spend"]
for c, dd in by_camp.items():
    first, last = min(dd), max(dd)
    gaps_ = [d for d in DAYS if first <= d <= last and dd.get(d, 0) <= 0]
    disc.append((first.isoformat(), f"start kampanii platnej `{c}`", f"{len(dd)} dni ze spendem, sredni spend {zl(sum(dd.values()) / len(dd))} zl/dzien"))
    if last < DATA_END:
        disc.append((last.isoformat(), f"koniec kampanii `{c}`", ""))
    if gaps_:
        disc.append((gaps_[0].isoformat(), f"pauza kampanii `{c}`", f"{len(gaps_)} dni bez spendu do {gaps_[-1].isoformat()}"))
first_use = {}
for o in orders:
    if o["code"]:
        first_use.setdefault(o["code"], [o["t"].date(), o["t"].date(), 0])
        fu = first_use[o["code"]]
        fu[1] = o["t"].date()
        fu[2] += 1
for c, (a, b, n) in first_use.items():
    disc.append((a.isoformat(), f"pierwsze uzycie kodu `{c}`", f"{n:,} uzyc do {b.isoformat()}"))


def first_seen(items, label, skip_days=14):
    fs_ = {}
    for d, v in items:
        if v and (v not in fs_ or d < fs_[v]):
            fs_[v] = d
    for v, d in fs_.items():
        if d > DATA_START + timedelta(days=skip_days):
            disc.append((d.isoformat(), f"nowa wartosc: {label} = `{v}`", ""))


first_seen(((s["t"].date(), s["camp"]) for s in prod_sessions), "utm_campaign w sesjach")
first_seen(((s["t"].date(), s["landing"]) for s in prod_sessions), "landing page")
first_seen(((s["t"].date(), s["browser"]) for s in prod_sessions), "przegladarka")
first_seen(((o["t"].date(), o["payment"]) for o in orders), "metoda platnosci")
first_seen(((o["t"].date(), o["mode"]) for o in orders), "tryb konsultacji")
first_seen(((o["t"].date(), o["purpose"]) for o in orders), "cel wizyty")
first_seen(((o["t"].date(), o["spec"]) for o in orders), "specjalizacja")
price_hist = defaultdict(dict)
for o in orders:
    price_hist[o["spec"]].setdefault(o["gross"], o["t"].date())
for sp, h in price_hist.items():
    if len(h) > 1:
        for pr, d in sorted(h.items(), key=lambda kv: kv[1])[1:]:
            disc.append((d.isoformat(), f"zmiana ceny katalogowej `{sp}`", f"nowa cena {pr}"))
R.p("Ceny katalogowe per specjalizacja: " + ", ".join(f"{sp}: {sorted(h)}" for sp, h in sorted(price_hist.items())))
go_sa = [g["t"].date() for g in ds.go if not g["oid"]]
if go_sa:
    disc.append((min(go_sa).isoformat(), "pierwszy zakup GO osobno (bez konsultacji)", ""))
disc.sort()
R.table(["data", "zdarzenie", "szczegoly"], [list(x) for x in disc])
M["discrete_events"] = disc

# ===========================================================================
# 4. WYCENA DZWIGNI
# ===========================================================================
print("4. Sizing...")
R.h("4. Wycena dzwigni wzrostowych (run-rate: 2026-04..09 x 2 = rocznie)")


def in_rr(d):
    return d >= RR_FROM


def ltv180(ps):
    el = [p for p in ps if 180 in p["win"]]
    return sum(p["win"][180][2] for p in el) / len(el) if el else 0.0


sizing = []
# (a1) ciecie kampanii
freed = 0.0
for camp in ("tt_prosp_l4_15min", "gs_generic_specjalisci"):
    spend_rr = 2 * sum(r["spend"] for r in ds.spend if r["camp"] == camp and in_rr(r["date"]))
    ps_all = [p for p in patients.values() if p["ft_key"] == camp]
    n_rr = 2 * sum(1 for p in ps_all if in_rr(p["first_t"].date()))
    l180 = ltv180(ps_all)
    lost = n_rr * l180
    freed += spend_rr
    sizing.append({"id": f"a1 {camp}", "inicjatywa": f"Wylaczenie `{camp}`",
                   "central": spend_rr - lost, "low": spend_rr - lost, "high": spend_rr - 0.7 * lost,
                   "zalozenia": f"spend {zl(spend_rr)} zl/rok; traci {n_rr:,.0f} pacjentow/rok x CM1 D+180 {zl2(l180)} zl; high: 30% pacjentow wraca bezkosztowo"})
# (a2) L4SZYBKO20 bez rabatu
code_o = [o for o in orders if o["code"] == "L4SZYBKO20" and in_rr(o["t"].date())]
disc_rr = 2 * sum(o["discount"] for o in code_o)
code_p = [p for p in patients.values() if p["first_code"] == "L4SZYBKO20"]
n_code_rr = 2 * sum(1 for p in code_p if in_rr(p["first_t"].date()))
l180_code = ltv180(code_p)


def a2(loss):
    return (1 - loss) * disc_rr - loss * n_code_rr * l180_code


sizing.append({"id": "a2 L4SZYBKO20", "inicjatywa": "Zdjecie rabatu 20% z kodu `L4SZYBKO20` (kampania Meta L4 zostaje)",
               "central": a2(0.25), "low": a2(0.5), "high": a2(0.1),
               "zalozenia": f"rabat {zl(disc_rr)} zl/rok; utrata konwersji 25% (10-50%) x {n_code_rr:,.0f} pacjentow/rok x CM1 D+180 {zl2(l180_code)} zl"})
# (a3) realokacja do gs_generic_erecepta
er = [p for p in patients.values() if p["ft_key"] == "gs_generic_erecepta" and p["year"] == "Y2"]
er_cac = sum(p["cac_ft"] for p in er) / len(er)
er_l180 = ltv180([p for p in patients.values() if p["ft_key"] == "gs_generic_erecepta"])
roi = er_l180 / er_cac


def a3(eff):
    return freed * (eff * roi - 1)


sizing.append({"id": "a3 realokacja", "inicjatywa": "Realokacja uwolnionego budzetu (a1) do `gs_generic_erecepta`",
               "central": a3(0.75), "low": a3(0.5), "high": a3(1.0),
               "zalozenia": f"budzet {zl(freed)} zl/rok; CM1 D+180 {zl2(er_l180)} / CAC R2 {zl2(er_cac)} = {roi:.2f} zl na 1 zl; krancowa efektywnosc 75% (50-100%)"})
# (b1) repricing pediatra / psycholog
NEW_PRICE = 119.0
b1_rows = []
b1 = {0.0: 0.0, 0.15: 0.0, 0.3: 0.0}
for sp in ("pediatra", "psycholog"):
    os_ = [o for o in orders if o["spec"] == sp and in_rr(o["t"].date())]
    n_rr = 2 * len(os_)
    uplift = 2 * sum((NEW_PRICE - o["gross"]) * (o["billed"] / o["gross"]) for o in os_ if o["status"] in ("completed", "no_show"))
    cm1_now = 2 * sum(o["cm1"] for o in os_)
    for loss in b1:
        b1[loss] += (1 - loss) * uplift - loss * cm1_now
    b1_rows.append(f"{sp}: {n_rr:,} zam./rok, CM1 dzis {zl(cm1_now)} zl/rok")
sizing.append({"id": "b1 repricing", "inicjatywa": f"Repricing pediatry i psychologa do {NEW_PRICE:.0f} zl",
               "central": b1[0.15], "low": b1[0.3], "high": b1[0.0],
               "zalozenia": "; ".join(b1_rows) + "; spadek wolumenu 15% (0-30%), utracony wolumen mial ujemne CM1"})
# (b2) GO bez rabatu na specjalistow
go_spec = [o for o in orders if o["disc_type"] == "go" and o["spec"] != "internista" and in_rr(o["t"].date())]
go_spec_disc = 2 * sum(o["discount"] for o in go_spec if o["status"] in ("completed", "no_show"))
go_fees_rr = 2 * sum(g["fee"] for g in ds.go if in_rr(g["t"].date()))


def b2(churn):
    return go_spec_disc - churn * go_fees_rr


sizing.append({"id": "b2 GO", "inicjatywa": "TelemediGO: rabat tylko u internisty (0% zamiast 20% u specjalistow)",
               "central": b2(0.1), "low": b2(0.25), "high": b2(0.0),
               "zalozenia": f"rabaty GO u specjalistow {zl(go_spec_disc)} zl/rok; spadek sprzedazy GO 10% (0-25%) z {zl(go_fees_rr)} zl/rok oplat"})
# (c1) lejek in-app
win_s = [s for s in prod_sessions if in_rr(s["t"].date()) and s["channel"] in ("meta", "tiktok") and s["device"] == "mobile"]
ia = [0] * 7
na = [0] * 7
for s in win_s:
    tgt = ia if s["bg"] == "in_app" else (na if s["bg"] == "chrome/safari" else None)
    if tgt is None:
        continue
    tgt[0] += 1
    for j, v in enumerate(s["f"]):
        tgt[j + 1] += v
ri, rn = rates(ia), rates(na)
gaps_step = [(rn[j] - ri[j], j) for j in range(1, 5)]
gap, kstar = max(gaps_step)
downstream = 1.0
for j in range(kstar + 1, 6):
    downstream *= ri[j]
reach = ia[kstar]  # sesje in-app, ktore doszly do kroku kstar (mianownik r[kstar])
extra_orders_rr = 2 * reach * gap * downstream
ia_first = [p for p in patients.values() if sessions[p["orders"][0]["sid"]]["bg"] == "in_app"]
val = ltv180(ia_first)


def c1(close):
    return extra_orders_rr * close * val


sizing.append({"id": "c1 in-app", "inicjatywa": f"Test 'otworz w przegladarce' / uproszczenie kroku `{STEP_NAMES[kstar]}` w in-app (Meta/TikTok, mobile)",
               "central": c1(0.25), "low": 0.0, "high": c1(0.5),
               "zalozenia": f"in-app {100 * ri[kstar]:.1f}% vs Chrome/Safari {100 * rn[kstar]:.1f}% na tym kroku; {reach * 2:,} sesji/rok dochodzi do kroku; "
                            f"domkniecie 25% luki (0-50%) = {extra_orders_rr * 0.25:,.0f} zam./rok x CM1 D+180 pacjenta in-app {zl2(val)} zl. "
                            "Niska pewnosc: na TikToku in-app = Chrome, luka na Meta to w duzej mierze samoselekcja"})
M["inapp_gap"] = {"step": STEP_NAMES[kstar], "in_app": ri, "native": rn, "extra_orders_full_gap": extra_orders_rr}
# (c2) platnosci w sesjach CRM (e-mail / SMS)
crm_s = [s for s in prod_sessions if in_rr(s["t"].date()) and s["channel"] in ("email", "sms") and s["f"][3]]
crm_ok = sum(s["f"][4] for s in crm_s) / len(crm_s)
dir_s = [s for s in prod_sessions if in_rr(s["t"].date()) and s["channel"] == "direct" and s["f"][3]]
dir_ok = sum(s["f"][4] for s in dir_s) / len(dir_s)
crm_cm1 = [order_sids[s["sid"]]["cm1"] for s in prod_sessions if s["channel"] in ("email", "sms") and s["sid"] in order_sids]
crm_val = sum(crm_cm1) / len(crm_cm1)


def c2(target):
    return 2 * len(crm_s) * max(target - crm_ok, 0) * crm_val


sizing.append({"id": "c2 CRM platnosc", "inicjatywa": "Naprawa platnosci w sesjach z e-mail/SMS (powracajacy pacjenci)",
               "central": c2((crm_ok + dir_ok) / 2), "low": c2(crm_ok + 0.25 * (dir_ok - crm_ok)), "high": c2(dir_ok),
               "zalozenia": f"sukces platnosci CRM {100 * crm_ok:.1f}% vs direct {100 * dir_ok:.1f}% (ta sama populacja zalogowanych); "
                            f"{2 * len(crm_s):,} startow platnosci/rok; domkniecie 50% luki (25-100%) x CM1/zam. z CRM {zl2(crm_val)} zl"})
# (d1) zwroty L4
# tylko L4SZYBKO20: TIKTOK25 znika razem z kampania TikTok (a1), bez podwojnego liczenia
l4o = [o for o in orders if o["code"] == "L4SZYBKO20" and o["purpose"] == "l4" and in_rr(o["t"].date())]
base = [o for o in orders if not o["code"] and o["disc_type"] == "none" and o["purpose"] == "l4" and o["spec"] == "internista" and in_rr(o["t"].date())]
ref_now = sum(o["status"] == "refunded" for o in l4o) / len(l4o)
ref_base = sum(o["status"] == "refunded" for o in base) / len(base)
avg_doc = sum(o["doctor"] for o in l4o if o["status"] == "refunded") / max(sum(o["status"] == "refunded" for o in l4o), 1)
avoided = 2 * len(l4o) * (ref_now - ref_base)
all_l4_ref = [o for o in orders if o["purpose"] == "l4" and o["status"] == "refunded" and in_rr(o["t"].date())]
sizing.append({"id": "d1 zwroty L4", "inicjatywa": "Prekwalifikacja L4 przed platnoscia (ankieta / triage) - `L4SZYBKO20`",
               "central": avoided * avg_doc, "low": 0.5 * avoided * avg_doc, "high": 2 * sum(o["doctor"] for o in all_l4_ref),
               "zalozenia": f"zwroty L4 z kodem {100 * ref_now:.1f}% -> {100 * ref_base:.1f}% (poziom bez kodu); {avoided:,.0f} unikniętych wizyt/rok x koszt lekarza {zl2(avg_doc)} zl; "
                            "high: zero zwrotow L4 we wszystkich zamowieniach"})
# (d2) TEST-QA
tq_rr = 2 * sum(o["doctor"] for o in ds.test_orders if in_rr(o["t"].date()))
sizing.append({"id": "d2 TEST-QA", "inicjatywa": "Wyczyszczenie TEST-QA (konta QA poza produkcja / bez rozliczenia lekarzy)",
               "central": tq_rr, "low": 0.0, "high": tq_rr,
               "zalozenia": "low = scenariusz A (blad hurtowni, lekarz nieplacony); central/high = scenariusz B (wyplaty lekarzom)"})

R.table(["inicjatywa", "dCM2 / rok (central)", "zakres", "dCM2 / mies.", "zalozenia"],
        [[s_["inicjatywa"], zl(s_["central"]), f"{zl(s_['low'])} .. {zl(s_['high'])}", zl(s_["central"] / 12), s_["zalozenia"]] for s_ in sizing])
tot_c = sum(s_["central"] for s_ in sizing)
cm2_rr = 0.0
for o in orders:
    if in_rr(o["t"].date()):
        cm2_rr += o["cm1"]
cm2_rr += sum(g["fee"] for g in ds.go if in_rr(g["t"].date()))
cm2_rr -= sum(r["spend"] for r in ds.spend if in_rr(r["date"]))
cm2_rr -= 25 * sum(1 for p in patients.values() if p["lt_channel"] == "affiliate" and in_rr(p["first_t"].date()))
R.p(f"Suma central: **{zl(tot_c)} zl/rok** vs CM2 run-rate {zl(2 * cm2_rr)} zl/rok (+{100 * tot_c / (2 * cm2_rr):.1f}%). "
    "Naklada sie glownie a2 i d1 (te same zamowienia L4SZYBKO20; przy -25% wolumenu d1 maleje o ok. 1/4); a3 zalezy od a1.")
M["sizing"] = sizing
M["cm2_run_rate"] = 2 * cm2_rr

# ---------------------------------------------------------------------------
R.write(os.path.join(OUT, "03_cohorts_and_funnels_report.md"), "03 - Kohorty, lejek, zdarzenia, wycena (scripts/03_cohorts_and_funnels.py)")
with open(os.path.join(OUT, "03_cohorts_and_funnels_metrics.json"), "w", encoding="utf-8") as fh:
    json.dump(M, fh, ensure_ascii=False, indent=1, default=str)
print("OK")
