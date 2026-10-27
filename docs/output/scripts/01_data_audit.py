"""
01_data_audit.py - KROK 1: audyt higieny danych (telemedi-growth-audit).

Tylko biblioteka standardowa Pythona (brak pandas / tzdata w srodowisku).
Strefa Europe/Warsaw liczona regula UE: CEST od ostatniej niedzieli marca 01:00 UTC
do ostatniej niedzieli pazdziernika 01:00 UTC, poza tym CET (UTC+1).

Uruchomienie (z katalogu projektu):
    python docs/output/scripts/01_data_audit.py

Wyjscie:
    docs/output/01_data_audit_report.md   - pelny raport z liczbami
    docs/output/01_data_audit_metrics.json - kluczowe metryki (do kolejnych krokow)
"""
import csv
import glob
import json
import math
import os
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA = os.path.join(ROOT, "docs", "input", "dane")
OUT_MD = os.path.join(ROOT, "docs", "output", "01_data_audit_report.md")
OUT_JSON = os.path.join(ROOT, "docs", "output", "01_data_audit_metrics.json")

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Raport
# ---------------------------------------------------------------------------
REPORT = []
METRICS = {}


def h(title, level=2):
    REPORT.append(f"\n{'#' * level} {title}\n")


def p(text=""):
    REPORT.append(text)


def table(headers, rows):
    REPORT.append("| " + " | ".join(str(x) for x in headers) + " |")
    REPORT.append("|" + "---|" * len(headers))
    for r in rows:
        REPORT.append("| " + " | ".join(str(x) for x in r) + " |")
    REPORT.append("")


def pct(a, b):
    return f"{(100.0 * a / b):.2f}%" if b else "n/a"


# ---------------------------------------------------------------------------
# Strefa czasowa Europe/Warsaw (bez tzdata)
# ---------------------------------------------------------------------------
_DST = {}


def _last_sunday(y, m):
    d = date(y, m + 1, 1) - timedelta(days=1)
    while d.weekday() != 6:
        d -= timedelta(days=1)
    return d


def waw_offset_h(utc):
    """Offset Europe/Warsaw (h) dla momentu w UTC."""
    y = utc.year
    if y not in _DST:
        s, e = _last_sunday(y, 3), _last_sunday(y, 10)
        _DST[y] = (datetime(y, s.month, s.day, 1), datetime(y, e.month, e.day, 1))
    s, e = _DST[y]
    return 2 if s <= utc < e else 1


def utc_to_waw(utc):
    return utc + timedelta(hours=waw_offset_h(utc))


def waw_to_utc(local):
    # niejednoznaczna godzina przy zmianie czasu jesienia -> przyjmujemy CEST
    u = local - timedelta(hours=2)
    return u if waw_offset_h(u) == 2 else local - timedelta(hours=1)


def dt(s):
    return datetime.fromisoformat(s) if s else None


def month(d):
    return d.strftime("%Y-%m")


# ---------------------------------------------------------------------------
# Wczytanie
# ---------------------------------------------------------------------------
def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        header = next(r)
        return header, list(r)


def read_parts(pattern):
    header, rows, files = None, [], []
    for path in sorted(glob.glob(os.path.join(DATA, pattern))):
        hd, rs = read(path)
        if header is None:
            header = hd
        elif hd != header:
            raise SystemExit(f"Niespojny naglowek w {path}: {hd}")
        name = os.path.basename(path)
        files.append((name, rs))
        rows.extend(rs)
    return header, rows, files


print("Wczytywanie danych...")
SES_H, SES, SES_FILES = read_parts("sessions_*.csv")
EV_H, EV, EV_FILES = read_parts("events_*.csv")
ORD_H, ORD = read(os.path.join(DATA, "orders.csv"))
USR_H, USR = read(os.path.join(DATA, "users.csv"))
GO_H, GO = read(os.path.join(DATA, "go_memberships.csv"))
MKT_H, MKT = read(os.path.join(DATA, "marketing_spend.csv"))

TABLES = {
    "sessions (8 plikow)": (SES_H, SES),
    "events (5 plikow)": (EV_H, EV),
    "orders": (ORD_H, ORD),
    "users": (USR_H, USR),
    "go_memberships": (GO_H, GO),
    "marketing_spend": (MKT_H, MKT),
}
S = {c: i for i, c in enumerate(SES_H)}
E = {c: i for i, c in enumerate(EV_H)}
O = {c: i for i, c in enumerate(ORD_H)}
U = {c: i for i, c in enumerate(USR_H)}
G = {c: i for i, c in enumerate(GO_H)}
M = {c: i for i, c in enumerate(MKT_H)}

DATE_COLS = {"started_at_utc", "event_at_utc", "created_at", "scheduled_at", "started_at",
             "registered_at", "purchased_at", "valid_until", "date"}

# ===========================================================================
# 1. SCHEMAT, WOLUMENY, NULLE, ZAKRESY DAT
# ===========================================================================
print("1. Schemat i profilowanie...")
h("1. Schemat, wolumeny, nulle, zakresy dat")
for tname, (hd, rows) in TABLES.items():
    h(f"`{tname}` - {len(rows):,} wierszy, {len(hd)} kolumn", 3)
    out = []
    for i, c in enumerate(hd):
        vals = [r[i] for r in rows]
        nulls = sum(1 for v in vals if v == "")
        nonnull = [v for v in vals if v != ""]
        distinct = len(set(nonnull))
        rng = ""
        if c in DATE_COLS and nonnull:
            rng = f"{min(nonnull)} .. {max(nonnull)}"
        elif distinct <= 12:
            rng = ", ".join(f"{k}={v}" for k, v in Counter(nonnull).most_common())
        out.append([c, f"{nulls:,}", pct(nulls, len(rows)), f"{distinct:,}", rng])
    table(["kolumna", "nulle", "% null", "distinct", "zakres / wartosci"], out)
    METRICS.setdefault("rows", {})[tname] = len(rows)

h("Pliki partycjonowane - zakresy", 3)
out = []
for name, rs in SES_FILES:
    ts = [r[S["started_at_utc"]] for r in rs]
    out.append([name, f"{len(rs):,}", min(ts), max(ts)])
for name, rs in EV_FILES:
    ts = [r[E["event_at_utc"]] for r in rs]
    out.append([name, f"{len(rs):,}", min(ts), max(ts)])
table(["plik", "wiersze", "min UTC", "max UTC"], out)
p("Granice plikow wypadaja o 22:00/23:00 UTC = polnoc czasu polskiego: eksport ciety po dniu PL, "
  "mimo ze kolumny sa w UTC (to potwierdza, ze `*_utc` jest naprawde UTC).")

# ===========================================================================
# 2. DUPLIKATY
# ===========================================================================
print("2. Duplikaty...")
h("2. Duplikaty ID")
dup_rows = []


def dup_check(label, rows, key_fn):
    by_key = defaultdict(list)
    for r in rows:
        by_key[key_fn(r)].append(r)
    dups = {k: v for k, v in by_key.items() if len(v) > 1}
    extra = sum(len(v) - 1 for v in dups.values())
    exact = sum(1 for v in dups.values() if all(x == v[0] for x in v))
    dup_rows.append([label, f"{len(rows):,}", f"{len(by_key):,}", f"{len(dups):,}", f"{extra:,}",
                     f"{exact:,}", f"{len(dups) - exact:,}"])
    METRICS.setdefault("duplicates", {})[label] = {"keys_dup": len(dups), "extra_rows": extra,
                                                   "exact_dup_keys": exact}
    return by_key, dups


ses_by_id, ses_dups = dup_check("sessions.session_id", SES, lambda r: r[S["session_id"]])
_, ev_dups = dup_check("events (session_id, event_name, event_at_utc)", EV, lambda r: tuple(r))
_, ev_name_dups = dup_check("events (session_id, event_name)", EV,
                            lambda r: (r[E["session_id"]], r[E["event_name"]]))
ord_by_id, ord_dups = dup_check("orders.order_id", ORD, lambda r: r[O["order_id"]])
_, ord_nat_dups = dup_check("orders (user_id, created_at)", ORD,
                            lambda r: (r[O["user_id"]], r[O["created_at"]]))
_, ord_ses_dups = dup_check("orders.session_id", ORD, lambda r: r[O["session_id"]])
usr_by_id, usr_dups = dup_check("users.user_id", USR, lambda r: r[U["user_id"]])
go_by_id, go_dups = dup_check("go_memberships.membership_id", GO, lambda r: r[G["membership_id"]])
_, mkt_dups = dup_check("marketing_spend (date, source, medium, campaign)", MKT,
                        lambda r: (r[M["date"]], r[M["utm_source"]], r[M["utm_medium"]], r[M["utm_campaign"]]))
table(["klucz", "wiersze", "unikalne klucze", "klucze zduplikowane", "nadmiarowe wiersze",
       "w tym identyczne wiersze", "w tym konfliktowe"], dup_rows)

# kropka nad i: czy duplikaty sesji siedza na granicach plikow
ses_file_of = defaultdict(list)
for name, rs in SES_FILES:
    for r in rs:
        ses_file_of[r[S["session_id"]]].append(name)
cross_file = sum(1 for k in ses_dups if len(set(ses_file_of[k])) > 1)
p(f"Zduplikowane session_id wystepujace w >1 pliku (nakladanie eksportow): **{cross_file:,}** "
  f"z {len(ses_dups):,}.")

if ord_dups:
    # czym roznia sie konfliktowe duplikaty zamowien
    diff_cols = Counter()
    for v in ord_dups.values():
        for i, c in enumerate(ORD_H):
            if len({x[i] for x in v}) > 1:
                diff_cols[c] += 1
    p("Kolumny rozniace sie w zduplikowanych order_id: " +
      (", ".join(f"`{k}`={v}" for k, v in diff_cols.most_common()) or "brak (pelne duplikaty)"))
if ord_dups:
    dmonths = Counter(month(dt(v[0][O["created_at"]])) for v in ord_dups.values())
    p("Duplikaty order_id per miesiac: " + ", ".join(f"{k}: {v}" for k, v in sorted(dmonths.items())))
if ses_dups:
    smonths = Counter(v[0][S["started_at_utc"]][:7] for v in ses_dups.values())
    p("Duplikaty session_id per miesiac (UTC): " + ", ".join(f"{k}: {v}" for k, v in sorted(smonths.items())))
if ev_dups:
    emonths = Counter(k[2][:7] for k in ev_dups)
    p("Identyczne duplikaty eventow per miesiac: " + ", ".join(f"{k}: {v}" for k, v in sorted(emonths.items())))

# ---------------------------------------------------------------------------
# Struktury deduplikowane (pierwsze wystapienie) do dalszych krokow
# ---------------------------------------------------------------------------
sessions = {}
for r in SES:
    sid = r[S["session_id"]]
    if sid not in sessions:
        sessions[sid] = r + [dt(r[S["started_at_utc"]])]
ST = len(SES_H)  # indeks sparsowanego started_at

events_by_sid = defaultdict(list)
seen_ev = set()
for r in EV:
    t = tuple(r)
    if t in seen_ev:
        continue
    seen_ev.add(t)
    events_by_sid[r[E["session_id"]]].append((r[E["event_name"]], dt(r[E["event_at_utc"]])))

orders = {}
for r in ORD:
    oid = r[O["order_id"]]
    if oid not in orders:
        orders[oid] = r
users = {}
for r in USR:
    users.setdefault(r[U["user_id"]], r)
gos = {}
for r in GO:
    gos.setdefault(r[G["membership_id"]], r)


def channel(src, med):
    if not src and not med:
        return "direct"
    if med == "cpc":
        return "google_cpc"
    if med == "paid_social":
        return src  # meta / tiktok
    if med == "organic":
        return "seo"
    return med  # email, sms, affiliate, referral


def ses_channel(sid):
    r = sessions[sid]
    return channel(r[S["utm_source"]], r[S["utm_medium"]])


# ===========================================================================
# 3. STREFY CZASOWE
# ===========================================================================
print("3. Strefy czasowe...")
h("3. Strefy czasowe - weryfikacja hipotezy UTC vs Europe/Warsaw")


def single_payment(sid):
    ps = [t for n, t in events_by_sid.get(sid, []) if n == "payment_succeeded"]
    return ps[0] if len(ps) == 1 else None, len(ps)


def offset_test(label, rows, sid_idx, ts_idx):
    """Roznica (czas transakcyjny - event payment_succeeded UTC) w minutach vs oczekiwany offset PL."""
    buckets = Counter()
    by_season = Counter()
    no_ev = multi = 0
    for r in rows:
        sid, ts = r[sid_idx], dt(r[ts_idx])
        ev, n = single_payment(sid)
        if n == 0:
            no_ev += 1
            continue
        if n > 1:
            multi += 1
            continue
        diff = round((ts - ev).total_seconds() / 60)
        exp = waw_offset_h(ev) * 60
        b = "= offset PL (CET/CEST)" if abs(diff - exp) <= 2 else (
            "= 0 (UTC)" if abs(diff) <= 2 else (
                "= +60 stale (CET bez DST)" if abs(diff - 60) <= 2 else f"inne ({diff:+d} min)"))
        if b.startswith("inne"):
            b = "inne"
        buckets[b] += 1
        by_season[("CEST" if exp == 120 else "CET", diff)] += 1
    tested = sum(buckets.values())
    rows_out = [[k, f"{v:,}", pct(v, tested)] for k, v in buckets.most_common()]
    h(f"{label}: porownanie z `payment_succeeded` (UTC) w tej samej sesji", 3)
    table(["wynik", "n", "%"], rows_out)
    top = by_season.most_common(6)
    p(f"Przetestowano {tested:,}; bez eventu payment_succeeded: {no_ev:,}; z >1 payment_succeeded: {multi:,} "
      f"(pominiete). Najczestsze pary (sezon, roznica min): " + ", ".join(f"{k}: {v:,}" for k, v in top))
    METRICS.setdefault("tz_test", {})[label] = {"tested": tested, **dict(buckets), "no_event": no_ev,
                                                "multi_event": multi}


offset_test("orders.created_at", list(orders.values()), O["session_id"], O["created_at"])
offset_test("go_memberships.purchased_at", list(gos.values()), G["session_id"], G["purchased_at"])

# users.registered_at vs pierwszy account_completed w sesji z tym user_id
first_acc = {}
for sid, evs in events_by_sid.items():
    s = sessions.get(sid)
    if not s or not s[S["user_id"]]:
        continue
    for n, t in evs:
        if n == "account_completed":
            u = s[S["user_id"]]
            if u not in first_acc or t < first_acc[u]:
                first_acc[u] = t
reg_b = Counter()
for u, t in first_acc.items():
    if u not in users:
        continue
    diff = round((dt(users[u][U["registered_at"]]) - t).total_seconds() / 60)
    exp = waw_offset_h(t) * 60
    reg_b["= offset PL" if abs(diff - exp) <= 2 else ("= 0 (UTC)" if abs(diff) <= 2 else
                                                      ("rejestracja wczesniej niz 1. account_completed" if diff < exp else "inne"))] += 1
h("users.registered_at vs pierwszy `account_completed` uzytkownika (UTC)", 3)
table(["wynik", "n", "%"], [[k, f"{v:,}", pct(v, sum(reg_b.values()))] for k, v in reg_b.most_common()])
p("Uwaga: pacjent zalogowany na wejsciu nie ma account_completed, a account_completed moze byc logowaniem - "
  "stad czesc 'rejestracja wczesniej'.")
METRICS["tz_test"]["users.registered_at"] = dict(reg_b)

# marketing_spend.date: dzien PL czy UTC? Porownanie klikniec z sesjami platnymi
paid_utc = Counter()
paid_waw = Counter()
for s in sessions.values():
    camp = s[S["utm_campaign"]]
    if s[S["utm_medium"]] in ("cpc", "paid_social"):
        paid_utc[(s[ST].date().isoformat(), camp)] += 1
        paid_waw[(utc_to_waw(s[ST]).date().isoformat(), camp)] += 1
clicks = {(r[M["date"]], r[M["utm_campaign"]]): int(r[M["clicks"]]) for r in MKT}


def corr(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    return cov / math.sqrt(vx * vy) if vx and vy else float("nan")


mkt_rows = []
for lbl, sess_cnt in (("dzien UTC", paid_utc), ("dzien Europe/Warsaw", paid_waw)):
    keys = sorted(clicks)
    xs = [clicks[k] for k in keys]
    ys = [sess_cnt.get(k, 0) for k in keys]
    mae = sum(abs(x - y) for x, y in zip(xs, ys)) / len(keys)
    ratio = sum(ys) / sum(xs)
    mkt_rows.append([lbl, f"{corr(xs, ys):.4f}", f"{mae:.2f}", f"{ratio:.3f}"])
    METRICS.setdefault("tz_test", {})[f"marketing_spend vs sessions ({lbl})"] = {
        "corr": round(corr(xs, ys), 4), "mae": round(mae, 2), "sessions_per_click": round(ratio, 3)}
h("marketing_spend.date: clicks vs liczba sesji platnych (dzien x kampania)", 3)
table(["agregacja sesji", "korelacja", "MAE (klik/dzien/kampania)", "sesje / klik"], mkt_rows)

# sesje platne z kampania nieobecna w marketing_spend i odwrotnie
mkt_camps = {r[M["utm_campaign"]] for r in MKT}
ses_camps = Counter(s[S["utm_campaign"]] for s in sessions.values() if s[S["utm_medium"]] in ("cpc", "paid_social"))
missing = {c: v for c, v in ses_camps.items() if c not in mkt_camps}
if missing:
    p("Kampanie platne w sesjach bez kosztu w marketing_spend: " + ", ".join(f"`{k}`={v:,}" for k, v in missing.items()))
spend_no_sessions = sum(1 for k, v in clicks.items() if v > 0 and paid_waw.get(k, 0) == 0)
p(f"Dni x kampanie z klikami > 0, ale bez zadnej sesji platnej (dzien PL): {spend_no_sessions:,} z {len(clicks):,}.")

# --- Nocne przesuniecia ---------------------------------------------------
h("Przesuniecia dnia/miesiaca kohortowego po konwersji do Europe/Warsaw", 3)
n_night = n_dayshift = n_monthshift = 0
for s in sessions.values():
    loc = utc_to_waw(s[ST])
    if loc.hour >= 22 or loc.hour < 2:
        n_night += 1
    if loc.date() != s[ST].date():
        n_dayshift += 1
        if month(loc) != month(s[ST]):
            n_monthshift += 1
total_s = len(sessions)

o_night = o_dayshift = o_monthshift = o_ses_mismatch = 0
for r in orders.values():
    loc = dt(r[O["created_at"]])
    utc = waw_to_utc(loc)
    if loc.hour >= 22 or loc.hour < 2:
        o_night += 1
    if loc.date() != utc.date():
        o_dayshift += 1
        if month(loc) != month(utc):
            o_monthshift += 1
    s = sessions.get(r[O["session_id"]])
    # "naiwny" join: dzien sesji w UTC vs dzien zamowienia w PL
    if s and s[ST].date() != loc.date():
        o_ses_mismatch += 1

# kohorta pierwszego zamowienia uzytkownika: UTC vs PL
first_order = {}
for r in orders.values():
    u, t = r[O["user_id"]], dt(r[O["created_at"]])
    if u not in first_order or t < first_order[u][0]:
        first_order[u] = (t, r[O["order_id"]])
coh_day = coh_month = 0
for u, (t, _) in first_order.items():
    utc = waw_to_utc(t)
    if utc.date() != t.date():
        coh_day += 1
        if month(utc) != month(t):
            coh_month += 1

table(["miara", "n", "% bazy"], [
    ["Sesje: lokalnie 22:00-02:00 (PL)", f"{n_night:,}", pct(n_night, total_s)],
    ["Sesje: zmiana dnia UTC -> PL", f"{n_dayshift:,}", pct(n_dayshift, total_s)],
    ["Sesje: zmiana miesiaca UTC -> PL", f"{n_monthshift:,}", pct(n_monthshift, total_s)],
    ["Zamowienia: lokalnie 22:00-02:00 (PL)", f"{o_night:,}", pct(o_night, len(orders))],
    ["Zamowienia: dzien PL != dzien UTC", f"{o_dayshift:,}", pct(o_dayshift, len(orders))],
    ["Zamowienia: miesiac PL != miesiac UTC", f"{o_monthshift:,}", pct(o_monthshift, len(orders))],
    ["Zamowienia: naiwny join (dzien sesji UTC != dzien zamowienia PL)", f"{o_ses_mismatch:,}",
     pct(o_ses_mismatch, len(orders))],
    ["Pacjenci: dzien kohorty 1. zamowienia zmienia sie UTC vs PL", f"{coh_day:,}", pct(coh_day, len(first_order))],
    ["Pacjenci: MIESIAC kohorty 1. zamowienia zmienia sie UTC vs PL", f"{coh_month:,}",
     pct(coh_month, len(first_order))],
])
METRICS["night_shift"] = {"sessions_total": total_s, "sessions_night_22_02": n_night,
                          "sessions_day_shift": n_dayshift, "sessions_month_shift": n_monthshift,
                          "orders_total": len(orders), "orders_night_22_02": o_night,
                          "orders_day_shift": o_dayshift, "orders_month_shift": o_monthshift,
                          "orders_naive_join_day_mismatch": o_ses_mismatch,
                          "first_order_cohort_day_shift": coh_day, "first_order_cohort_month_shift": coh_month}

# ===========================================================================
# 4. IDENTITY STITCHING
# ===========================================================================
print("4. Identity stitching...")
h("4. Identity stitching (visitor_id <-> user_id)")

vis_users = defaultdict(set)
user_vis = defaultdict(set)
user_sessions = defaultdict(list)
vis_sessions = defaultdict(list)
for sid, s in sessions.items():
    v, u = s[S["visitor_id"]], s[S["user_id"]]
    vis_sessions[v].append(sid)
    if u:
        vis_users[v].add(u)
        user_vis[u].add(v)
        user_sessions[u].append(sid)

n_vis = len(vis_sessions)
vis_multi_user = sum(1 for v in vis_users.values() if len(v) > 1)
dist = Counter(min(len(v), 5) for v in user_vis.values())
table(["visitor_id na pacjenta", "pacjenci", "%"],
      [[("5+" if k == 5 else k), f"{v:,}", pct(v, len(user_vis))] for k, v in sorted(dist.items())])
p(f"Visitor_id ogolem: {n_vis:,}; z kiedykolwiek zalogowanym user_id: {len(vis_users):,} "
  f"({pct(len(vis_users), n_vis)}); visitor_id wspoldzielony przez >1 pacjenta: {vis_multi_user:,}.")

# Kiedy pojawia sie user_id: anonimowe sesje tych samych visitor_id PRZED pierwsza sesja zalogowana
users_with_pre_anon = 0
pre_anon_sessions = 0
anon_total = sum(1 for s in sessions.values() if not s[S["user_id"]])
anon_of_known = 0
lag_days = []
first_logged = {}
for u, sids in user_sessions.items():
    first_logged[u] = min(sessions[x][ST] for x in sids)
for v, sids in vis_sessions.items():
    us = vis_users.get(v)
    if not us:
        continue
    for sid in sids:
        if not sessions[sid][S["user_id"]]:
            anon_of_known += 1
for u, vs in user_vis.items():
    fl = first_logged[u]
    pre = [sessions[x][ST] for v in vs for x in vis_sessions[v]
           if not sessions[x][S["user_id"]] and sessions[x][ST] < fl]
    if pre:
        users_with_pre_anon += 1
        pre_anon_sessions += len(pre)
        lag_days.append((fl - min(pre)).total_seconds() / 86400)
lag_days.sort()
med_lag = lag_days[len(lag_days) // 2] if lag_days else 0
table(["miara", "wartosc"], [
    ["Pacjenci z sesjami (user_id w sesjach)", f"{len(user_vis):,}"],
    ["Pacjenci z anonimowymi sesjami PRZED 1. sesja zalogowana", f"{users_with_pre_anon:,} ({pct(users_with_pre_anon, len(user_vis))})"],
    ["Liczba takich anonimowych sesji (do wstecznego zmapowania)", f"{pre_anon_sessions:,}"],
    ["Mediana dni od 1. anonimowego dotyku do 1. logowania", f"{med_lag:.1f}"],
    ["Sesje anonimowe ogolem", f"{anon_total:,}"],
    ["...z visitor_id, ktory kiedykolwiek byl zalogowany (mapowalne wstecz/wprzod)", f"{anon_of_known:,} ({pct(anon_of_known, anon_total)})"],
])
METRICS["identity"] = {"visitors": n_vis, "visitors_ever_logged": len(vis_users),
                       "visitors_multi_user": vis_multi_user, "users_in_sessions": len(user_vis),
                       "user_visitor_dist": {str(k): v for k, v in dist.items()},
                       "users_with_pre_login_anon": users_with_pre_anon,
                       "pre_login_anon_sessions": pre_anon_sessions, "median_lag_days": round(med_lag, 1),
                       "anon_sessions": anon_total, "anon_sessions_of_known_visitor": anon_of_known}

# --- Zawyzanie "nowych" -------------------------------------------------------
h("Jak brak stitchingu zawyza 'nowych' pacjentow", 3)
first_seen_vis = {v: min(sessions[x][ST] for x in sids) for v, sids in vis_sessions.items()}
# visitor-based: kazdy visitor_id z oplaconym zamowieniem = "nowy pacjent"
buying_vis = set()
ord_new_vis_returning_user = 0
order_users = set()
user_orders = defaultdict(list)
for r in orders.values():
    user_orders[r[O["user_id"]]].append(r)
for u, rs in user_orders.items():
    rs.sort(key=lambda r: r[O["created_at"]])
for u, rs in user_orders.items():
    order_users.add(u)
    for i, r in enumerate(rs):
        s = sessions.get(r[O["session_id"]])
        if not s:
            continue
        v = s[S["visitor_id"]]
        newv = v not in buying_vis
        buying_vis.add(v)
        if i > 0 and newv:
            ord_new_vis_returning_user += 1
p(f"Pacjenci z zamowieniem (user_id): **{len(order_users):,}**; distinct visitor_id, ktore zaplacily: "
  f"**{len(buying_vis):,}** -> licznik na cookie zawyza 'kupujacych' o {pct(len(buying_vis) - len(order_users), len(order_users))}.")
p(f"Zamowienia powracajacych pacjentow (2.+ zamowienie) zlozone z NOWEGO visitor_id (widocznego jako nowy klient "
  f"w analityce bez stitchingu): **{ord_new_vis_returning_user:,}** z {sum(len(v) - 1 for v in user_orders.values()):,} "
  f"powtornych zamowien.")
METRICS["identity"]["paying_users"] = len(order_users)
METRICS["identity"]["paying_visitors"] = len(buying_vis)
METRICS["identity"]["repeat_orders_on_new_visitor"] = ord_new_vis_returning_user

# --- First-touch vs Last-touch ---------------------------------------------
h("Atrybucja pozyskania: First-Touch (z/bez stitchingu) vs Last-Touch", 3)
ft_logged = Counter()
ft_stitched = Counter()
lt = Counter()
pair = Counter()
diff_ft_lt = diff_ft_methods = n_attr = 0
for u, (t, oid) in first_order.items():
    r = orders[oid]
    sid = r[O["session_id"]]
    if sid not in sessions or u not in user_sessions:
        continue
    n_attr += 1
    c_lt = ses_channel(sid)
    cand_logged = [x for x in user_sessions[u]]
    c_ftl = ses_channel(min(cand_logged, key=lambda x: sessions[x][ST]))
    cand_st = set(cand_logged)
    for v in user_vis[u]:
        cand_st.update(vis_sessions[v])
    # ograniczamy do sesji do momentu 1. zamowienia (z dokladnoscia do sesji)
    lim = sessions[sid][ST]
    cand_st = [x for x in cand_st if sessions[x][ST] <= lim] or [sid]
    c_fts = ses_channel(min(cand_st, key=lambda x: sessions[x][ST]))
    ft_logged[c_ftl] += 1
    ft_stitched[c_fts] += 1
    lt[c_lt] += 1
    pair[(c_fts, c_lt)] += 1
    diff_ft_lt += c_fts != c_lt
    diff_ft_methods += c_fts != c_ftl
chans = sorted(set(ft_logged) | set(ft_stitched) | set(lt), key=lambda c: -lt.get(c, 0))
table(["kanal", "Last-Touch (sesja 1. zamowienia)", "First-Touch tylko sesje zalogowane",
       "First-Touch ze stitchingiem visitor_id"],
      [[c, f"{lt[c]:,} ({pct(lt[c], n_attr)})", f"{ft_logged[c]:,} ({pct(ft_logged[c], n_attr)})",
        f"{ft_stitched[c]:,} ({pct(ft_stitched[c], n_attr)})"] for c in chans])
p(f"Nowi pacjenci z atrybucja: {n_attr:,}. Kanal FT(stitched) != LT: **{diff_ft_lt:,} ({pct(diff_ft_lt, n_attr)})**. "
  f"FT(stitched) != FT(tylko zalogowane): **{diff_ft_methods:,} ({pct(diff_ft_methods, n_attr)})**.")
p("Najczestsze przejscia FT(stitched) -> LT (gdy rozne): " +
  ", ".join(f"{a}->{b}: {v:,}" for (a, b), v in pair.most_common() if a != b)[:900])
METRICS["attribution"] = {"n": n_attr, "lt": dict(lt), "ft_logged": dict(ft_logged), "ft_stitched": dict(ft_stitched),
                          "ft_ne_lt": diff_ft_lt, "ft_stitched_ne_ft_logged": diff_ft_methods}

# ===========================================================================
# 5. BRUDNE DANE I ANOMALIE
# ===========================================================================
print("5. Anomalie...")
h("5. Brudne dane i anomalie")

# --- spojnosc referencyjna ---------------------------------------------------
o_no_sid = o_sid_missing = o_user_mismatch = o_no_payev = o_user_missing = o_before_reg = o_before_session = 0
o_sid_missing_months = Counter()
for r in orders.values():
    sid, u = r[O["session_id"]], r[O["user_id"]]
    if not sid:
        o_no_sid += 1
        continue
    s = sessions.get(sid)
    if not s:
        o_sid_missing += 1
        o_sid_missing_months[r[O["created_at"]][:7]] += 1
        continue
    if s[S["user_id"]] and s[S["user_id"]] != u:
        o_user_mismatch += 1
    if not any(n == "payment_succeeded" for n, _ in events_by_sid.get(sid, [])):
        o_no_payev += 1
    if waw_to_utc(dt(r[O["created_at"]])) < s[ST] - timedelta(minutes=1):
        o_before_session += 1
for r in orders.values():
    u = r[O["user_id"]]
    if u not in users:
        o_user_missing += 1
    elif dt(r[O["created_at"]]) < dt(users[u][U["registered_at"]]) - timedelta(minutes=1):
        o_before_reg += 1

ev_orphan = sum(len(v) for k, v in events_by_sid.items() if k not in sessions)
ev_before_start = sum(1 for k, v in events_by_sid.items() if k in sessions
                      for n, t in v if t < sessions[k][ST] - timedelta(seconds=1))
ses_no_ev = sum(1 for k in sessions if k not in events_by_sid)

STEPS = ["service_selected", "slot_selected", "account_completed", "payment_started", "payment_succeeded"]
funnel_viol = Counter()
pay_ok_sessions = set()
for k, v in events_by_sid.items():
    names = {n for n, _ in v}
    if "payment_succeeded" in names:
        pay_ok_sessions.add(k)
        if "payment_started" not in names:
            funnel_viol["payment_succeeded bez payment_started"] += 1
    if "payment_started" in names and "service_selected" not in names and "account_completed" in names:
        funnel_viol["payment_started + account_completed bez service_selected"] += 1
    if "slot_selected" in names and "service_selected" not in names:
        funnel_viol["slot_selected bez service_selected"] += 1
    order_seq = [STEPS.index(n) for n, t in sorted(v, key=lambda x: x[1]) if n in STEPS]
    if order_seq != sorted(order_seq):
        funnel_viol["kroki w zlej kolejnosci czasowej"] += 1
unknown_ev = Counter(n for v in events_by_sid.values() for n, _ in v if n not in STEPS)

order_sids = {r[O["session_id"]] for r in orders.values()}
go_sids = {r[G["session_id"]] for r in gos.values()}
pay_without_tx = len(pay_ok_sessions - order_sids - go_sids)
pay_without_tx_months = Counter(min(t for n, t in events_by_sid[k] if n == "payment_succeeded").strftime("%Y-%m")
                                for k in pay_ok_sessions - order_sids - go_sids)

table(["kontrola", "n", "% bazy"], [
    ["Zamowienia bez session_id", f"{o_no_sid:,}", pct(o_no_sid, len(orders))],
    ["Zamowienia z session_id nieistniejacym w sessions", f"{o_sid_missing:,}", pct(o_sid_missing, len(orders))],
    ["Zamowienia: user_id sesji != user_id zamowienia", f"{o_user_mismatch:,}", pct(o_user_mismatch, len(orders))],
    ["Zamowienia: sesja bez eventu payment_succeeded", f"{o_no_payev:,}", pct(o_no_payev, len(orders))],
    ["Zamowienia: user_id nieistniejacy w users", f"{o_user_missing:,}", pct(o_user_missing, len(orders))],
    ["Zamowienia: created_at przed registered_at", f"{o_before_reg:,}", pct(o_before_reg, len(orders))],
    ["Zamowienia: created_at (->UTC) przed startem sesji", f"{o_before_session:,}", pct(o_before_session, len(orders))],
    ["Eventy bez sesji (orphan)", f"{ev_orphan:,}", pct(ev_orphan, len(EV))],
    ["Eventy wczesniej niz start sesji", f"{ev_before_start:,}", pct(ev_before_start, len(EV))],
    ["Sesje bez zadnego eventu (bounce wg README)", f"{ses_no_ev:,}", pct(ses_no_ev, len(sessions))],
    ["Sesje z payment_succeeded bez zamowienia i bez GO", f"{pay_without_tx:,}", pct(pay_without_tx, len(pay_ok_sessions))],
] + [[f"Lejek: {k}", f"{v:,}", pct(v, len(events_by_sid))] for k, v in funnel_viol.items()])
if unknown_ev:
    p("Nieznane nazwy eventow: " + ", ".join(f"`{k}`={v}" for k, v in unknown_ev.items()))
if o_sid_missing_months:
    p("Zamowienia z brakujaca sesja per miesiac: " + ", ".join(f"{k}: {v}" for k, v in sorted(o_sid_missing_months.items())))
if pay_without_tx_months:
    p("payment_succeeded bez transakcji per miesiac: " + ", ".join(f"{k}: {v}" for k, v in sorted(pay_without_tx_months.items())))

METRICS["integrity"] = {"orders_no_session_id": o_no_sid, "orders_session_missing": o_sid_missing,
                        "orders_user_mismatch": o_user_mismatch, "orders_no_payment_event": o_no_payev,
                        "orders_user_missing": o_user_missing, "orders_before_registration": o_before_reg,
                        "orders_before_session": o_before_session, "events_orphan": ev_orphan,
                        "events_before_session": ev_before_start, "sessions_no_events": ses_no_ev,
                        "payment_success_without_tx": pay_without_tx, "funnel_violations": dict(funnel_viol)}

# --- spojnosc biznesowa zamowien ------------------------------------------
h("Spojnosc biznesowa zamowien", 3)
go_by_user = defaultdict(list)
for r in gos.values():
    go_by_user[r[G["user_id"]]].append((dt(r[G["purchased_at"]]), date.fromisoformat(r[G["valid_until"]])))
biz = Counter()
promo_by_month = defaultdict(Counter)
for r in orders.values():
    st, started = r[O["status"]], r[O["started_at"]]
    lp, paid, ref = float(r[O["list_price"]]), float(r[O["amount_paid"]]), float(r[O["refund_amount"]] or 0)
    disc, t = r[O["discount_type"]], dt(r[O["created_at"]])
    if st in ("completed", "refunded") and not started:
        biz[f"{st} bez started_at"] += 1
    if st in ("cancelled", "no_show") and started:
        biz[f"{st} z started_at"] += 1
    if st == "cancelled" and abs(ref - paid) > 0.01:
        biz["cancelled: refund != amount_paid"] += 1
    if st == "refunded" and ref <= 0:
        biz["refunded: refund_amount = 0"] += 1
    if st in ("completed", "no_show") and ref > 0:
        biz[f"{st}: refund_amount > 0"] += 1
    if disc == "none" and abs(paid - lp) > 0.01:
        biz["discount=none, ale amount_paid != list_price"] += 1
    if disc == "promo" and not r[O["promo_code"]]:
        biz["discount=promo bez promo_code"] += 1
    if disc != "promo" and r[O["promo_code"]]:
        biz["promo_code przy discount!=promo"] += 1
    if paid > lp + 0.01:
        biz["amount_paid > list_price"] += 1
    if paid <= 0:
        biz["amount_paid <= 0"] += 1
    if disc == "go":
        exp = lp * (0.5 if r[O["specialization"]] == "internista" else 0.8)
        if abs(paid - exp) > 0.6:
            biz["GO: kwota nie zgadza sie z 50%/20% rabatu"] += 1
        if not any(p_ <= t + timedelta(minutes=1) and t.date() <= vu for p_, vu in go_by_user.get(r[O["user_id"]], [])):
            biz["GO: brak aktywnego czlonkostwa w chwili zamowienia"] += 1
    if r[O["rating"]] and st in ("cancelled", "no_show"):
        biz["ocena przy wizycie, ktora sie nie odbyla"] += 1
    if r[O["scheduled_at"]] and dt(r[O["scheduled_at"]]) < t - timedelta(minutes=1):
        biz["scheduled_at przed created_at"] += 1
    if disc == "promo":
        promo_by_month[r[O["created_at"]][:7]][r[O["promo_code"]]] += 1
table(["kontrola", "n", "% zamowien"], [[k, f"{v:,}", pct(v, len(orders))] for k, v in biz.most_common()] or [["brak", 0, "0%"]])
METRICS["business_checks"] = dict(biz)

go_bad_validity = sum(1 for r in gos.values()
                      if (date.fromisoformat(r[G["valid_until"]]) - dt(r[G["purchased_at"]]).date()).days not in (365, 366))
go_overlap = 0
for u, lst in go_by_user.items():
    lst.sort()
    for (a, av), (b, bv) in zip(lst, lst[1:]):
        if b.date() <= av:
            go_overlap += 1
go_bad_order = sum(1 for r in gos.values() if r[G["order_id"]] and r[G["order_id"]] not in orders)
go_amount = Counter(r[G["amount_paid"]] for r in gos.values())
p(f"GO: waznosc != 12 mies.: {go_bad_validity:,}; nakladajace sie czlonkostwa tego samego pacjenta: {go_overlap:,}; "
  f"order_id GO nieistniejacy w orders: {go_bad_order:,}; kwoty: {dict(go_amount)}.")
METRICS["go_checks"] = {"bad_validity": go_bad_validity, "overlap": go_overlap, "bad_order_ref": go_bad_order}

h("Kody promocyjne per miesiac (top 3)", 3)
table(["miesiac", "zamowienia promo", "top kody"],
      [[m_, f"{sum(c.values()):,}", ", ".join(f"{k}={v}" for k, v in c.most_common(3))]
       for m_, c in sorted(promo_by_month.items())])

# --- konta testowe, okno duplikatow, GO standalone, jakosc kodow ---------------
h("Konta testowe (TEST-QA) i jakosc kodow promocyjnych", 3)
TEST_USERS = {r[O["user_id"]] for r in orders.values() if r[O["promo_code"]] == "TEST-QA"}
tq = [r for r in orders.values() if r[O["promo_code"]] == "TEST-QA"]
tq_all = [r for r in orders.values() if r[O["user_id"]] in TEST_USERS]
p(f"Zamowienia z kodem TEST-QA: **{len(tq):,}** od **{len(TEST_USERS)}** kont; kwoty zaplacone: "
  f"{dict(Counter(r[O['amount_paid']] for r in tq))}; statusy: {dict(Counter(r[O['status']] for r in tq))}; "
  f"specjalizacje: {dict(Counter(r[O['specialization']] for r in tq))}. Wszystkie zamowienia tych kont: "
  f"{len(tq_all):,} (srednio {len(tq_all) / max(len(TEST_USERS), 1):.0f} na konto). "
  f"Koszt lekarza (25 zl x completed) przy przychodzie 1 zl/wizyte: ~{25 * len(tq) - len(tq):,} zl straty.")
code_rows = []
for code in sorted({r[O["promo_code"]] for r in orders.values() if r[O["promo_code"]]}):
    rs = [r for r in orders.values() if r[O["promo_code"]] == code]
    st_ = Counter(r[O["status"]] for r in rs)
    first_cnt = sum(1 for u, (t, oid) in first_order.items() if orders[oid][O["promo_code"]] == code)
    disc_ = Counter(round(1 - float(r[O["amount_paid"]]) / float(r[O["list_price"]]), 2) for r in rs).most_common(1)[0][0]
    code_rows.append([code, f"{len(rs):,}", min(r[O["created_at"]] for r in rs)[:10], f"{disc_:.0%}",
                      pct(first_cnt, len(rs)), pct(st_["refunded"], len(rs)), pct(st_["cancelled"], len(rs)),
                      pct(st_["no_show"], len(rs))])
base = [r for r in orders.values() if r[O["discount_type"]] != "promo"]
bst = Counter(r[O["status"]] for r in base)
code_rows.append(["(bez kodu)", f"{len(base):,}", "", "", "", pct(bst["refunded"], len(base)),
                  pct(bst["cancelled"], len(base)), pct(bst["no_show"], len(base))])
table(["kod", "zamowienia", "pierwsze uzycie", "dominujacy rabat", "% jako 1. zamowienie pacjenta",
       "% refunded", "% cancelled", "% no_show"], code_rows)
METRICS["test_accounts"] = {"users": sorted(TEST_USERS), "test_qa_orders": len(tq), "all_orders_of_test_users": len(tq_all)}

dup_days = Counter()
for v in ord_dups.values():
    dup_days[v[0][O["created_at"]][:10]] += len(v) - 1
if dup_days:
    win_orders = sum(1 for r in orders.values() if min(dup_days) <= r[O["created_at"]][:10] <= max(dup_days))
    p(f"Okno duplikatow zamowien: {min(dup_days)} .. {max(dup_days)} ({len(dup_days)} dni), "
      f"{sum(dup_days.values()):,} zdublowanych z {win_orders:,} unikalnych zamowien w oknie "
      f"({pct(sum(dup_days.values()), win_orders)}) - wyglada na podwojny load ETL.")
    METRICS["orders_dup_window"] = {"from": min(dup_days), "to": max(dup_days), "dups": sum(dup_days.values()),
                                    "unique_in_window": win_orders}

go_standalone_m = Counter(r[G["purchased_at"]][:7] for r in gos.values() if not r[G["order_id"]])
p("GO kupione osobno (bez zamowienia) per miesiac: " +
  ", ".join(f"{k}: {v}" for k, v in sorted(go_standalone_m.items())))

# --- skoki wolumenow -----------------------------------------------------------
h("Podejrzane skoki dziennych wolumenow (dzien PL, vs mediana +/-14 dni)", 3)
daily = defaultdict(Counter)
for s in sessions.values():
    d = utc_to_waw(s[ST]).date()
    daily["sessions"][d] += 1
    if not s[S["user_id"]] and s[S["visitor_id"]] and first_seen_vis[s[S["visitor_id"]]] == s[ST]:
        daily["new_visitors"][d] += 1
for k, v in events_by_sid.items():
    for n, t in v:
        if n == "payment_succeeded":
            daily["payment_succeeded"][utc_to_waw(t).date()] += 1
for r in orders.values():
    d = dt(r[O["created_at"]]).date()
    daily["orders"][d] += 1
    if r[O["discount_type"]] == "promo":
        daily["orders_promo"][d] += 1
    if r[O["status"]] in ("cancelled", "refunded"):
        daily["orders_cancel_refund"][d] += 1
for r in USR:
    daily["registrations"][dt(r[U["registered_at"]]).date()] += 1
for r in gos.values():
    daily["go_purchases"][dt(r[G["purchased_at"]]).date()] += 1
for r in MKT:
    daily["spend_pln"][date.fromisoformat(r[M["date"]])] += float(r[M["spend_pln"]])

start, end = date(2024, 10, 1), date(2026, 9, 30)
days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
spikes = []
for metric, ser in daily.items():
    vals = [ser.get(d, 0) for d in days]
    for i, d in enumerate(days):
        win = vals[max(0, i - 14):i] + vals[i + 1:i + 15]
        win = sorted(win)
        med = win[len(win) // 2] if win else 0
        if med < 5:
            continue
        ratio = vals[i] / med
        if ratio >= 1.8 or ratio <= 0.5:
            spikes.append((abs(math.log(max(ratio, 1e-3))), metric, d, vals[i], med, ratio))
spikes.sort(reverse=True)
# skoki w gore sa wazniejsze; spadki tylko przy duzej bazie (male liczniki = szum Poissona)
ups = sorted([s_ for s_ in spikes if s_[5] >= 1.8], key=lambda s_: -s_[5])
downs = [s_ for s_ in spikes if s_[5] <= 0.5 and s_[4] >= 20]
table(["metryka", "dzien", "wartosc", "mediana okna", "x mediany"],
      [[m_, d.isoformat(), f"{v:,.0f}", f"{md:,.0f}", f"{r:.2f}"] for _, m_, d, v, md, r in ups[:30] + downs[:10]])
p(f"Lacznie flag: {len(spikes):,} (w gore: {len(ups)}, istotne spadki przy medianie >= 20: {len(downs)}). "
  "Per metryka: " + ", ".join(f"{k}={v}" for k, v in Counter(s[1] for s in spikes).most_common()) +
  ". Spadki przy medianie < 20 to glownie szum malych licznikow.")
spikes = ups + downs
zero_days = {m_: [d.isoformat() for d in days if daily[m_].get(d, 0) == 0] for m_ in ("sessions", "orders", "payment_succeeded", "spend_pln")}
for m_, zd in zero_days.items():
    if zd:
        p(f"Dni z zerem `{m_}`: {len(zd)} ({', '.join(zd[:10])}{'...' if len(zd) > 10 else ''})")
METRICS["spikes"] = [{"metric": m_, "date": d.isoformat(), "value": v, "median": md, "ratio": round(r, 2)}
                     for _, m_, d, v, md, r in spikes[:40]]

# miesieczne wolumeny - kontekst
h("Wolumeny miesieczne (PL)", 3)
mon = defaultdict(Counter)
for metric in ("sessions", "new_visitors", "payment_succeeded", "orders", "orders_promo", "orders_cancel_refund",
               "registrations", "go_purchases", "spend_pln"):
    for d, v in daily[metric].items():
        mon[d.strftime("%Y-%m")][metric] += v
cols = ["sessions", "new_visitors", "payment_succeeded", "orders", "orders_promo", "orders_cancel_refund",
        "registrations", "go_purchases", "spend_pln"]
table(["miesiac"] + cols, [[m_] + [f"{mon[m_][c]:,.0f}" for c in cols] for m_ in sorted(mon)])

# boty / ciezcy uzytkownicy
top_vis = sorted(vis_sessions.items(), key=lambda kv: -len(kv[1]))[:5]
p("Top visitor_id wg liczby sesji: " + ", ".join(f"{v}={len(s_)}" for v, s_ in top_vis))

# ===========================================================================
# 6. KONTEKST: "+52% pacjentow YoY" na surowych vs oczyszczonych danych
# ===========================================================================
print("6. YoY kontekst...")
h("6. Kontekst YoY (rok 1: 2024-10..2025-09, rok 2: 2025-10..2026-09; czas PL)")


def year_of(d):
    return 1 if d < date(2025, 10, 1) else 2


yo = {1: Counter(), 2: Counter()}
pay_u = {1: set(), 2: set()}
pay_u_raw = {1: set(), 2: set()}
for r in ORD:  # surowe (z duplikatami)
    y = year_of(dt(r[O["created_at"]]).date())
    yo[y]["orders_raw"] += 1
    pay_u_raw[y].add(r[O["user_id"]])
for r in orders.values():
    y = year_of(dt(r[O["created_at"]]).date())
    yo[y]["orders_dedup"] += 1
    if r[O["status"]] != "cancelled":
        yo[y]["orders_not_cancelled"] += 1
    if r[O["status"]] == "completed":
        yo[y]["orders_completed"] += 1
    pay_u[y].add(r[O["user_id"]])
    yo[y]["revenue_net_pln"] += float(r[O["amount_paid"]]) - float(r[O["refund_amount"]] or 0)
    if r[O["user_id"]] not in TEST_USERS:
        yo[y]["orders_dedup_no_test"] += 1
        if r[O["status"]] in ("refunded", "cancelled"):
            yo[y]["orders_refunded_or_cancelled_no_test"] += 1
for u, (t, _) in first_order.items():
    yo[year_of(t.date())]["new_paying_users"] += 1
    if u not in TEST_USERS:
        yo[year_of(t.date())]["new_paying_users_no_test"] += 1
for r in USR:
    yo[year_of(dt(r[U["registered_at"]]).date())]["registrations"] += 1
for s in sessions.values():
    yo[year_of(utc_to_waw(s[ST]).date())]["sessions"] += 1
vis_y = {1: set(), 2: set()}
for s in sessions.values():
    vis_y[year_of(utc_to_waw(s[ST]).date())].add(s[S["visitor_id"]])
for r in MKT:
    yo[year_of(date.fromisoformat(r[M["date"]]))]["spend_pln"] += float(r[M["spend_pln"]])
for r in gos.values():
    yo[year_of(dt(r[G["purchased_at"]]).date())]["go_purchases"] += 1
yo[2]["returning_users_from_y1"] = len({u for u in pay_u[2] if first_order[u][0].date() < date(2025, 10, 1)})
for y in (1, 2):
    yo[y]["paying_users"] = len(pay_u[y])
    yo[y]["paying_users_raw"] = len(pay_u_raw[y])
    yo[y]["distinct_visitors"] = len(vis_y[y])
keys = ["sessions", "distinct_visitors", "registrations", "orders_raw", "orders_dedup", "orders_dedup_no_test",
        "orders_not_cancelled", "orders_completed", "orders_refunded_or_cancelled_no_test", "paying_users",
        "new_paying_users", "new_paying_users_no_test", "returning_users_from_y1", "revenue_net_pln", "go_purchases", "spend_pln"]
table(["metryka", "rok 1", "rok 2", "YoY"],
      [[k, f"{yo[1][k]:,.0f}", f"{yo[2][k]:,.0f}", f"{(yo[2][k] / yo[1][k] - 1) * 100:+.1f}%" if yo[1][k] else "n/a"]
       for k in keys])
METRICS["yoy"] = {k: {"y1": round(yo[1][k], 2), "y2": round(yo[2][k], 2)} for k in keys}

# ---------------------------------------------------------------------------
with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("# 01 - Audyt higieny danych (wygenerowane przez scripts/01_data_audit.py)\n")
    f.write(f"\nWygenerowano: {datetime.now():%Y-%m-%d %H:%M}\n")
    f.write("\n".join(REPORT) + "\n")
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(METRICS, f, ensure_ascii=False, indent=2, default=str)
print("\n".join(REPORT))
print(f"\nZapisano: {OUT_MD}\nZapisano: {OUT_JSON}")
