"""
common.py - wspolny dataset "Clean Production" dla krokow 02+ (telemedi-growth-audit).

Reguly czyszczenia (DECISION_LOG, KROK 2, C1-C3):
  C1. Deduplikacja orders po order_id (604 duplikaty ETL z 2026-06-10..24).
  C2. Konta testowe = user_id, ktore kiedykolwiek uzyly TEST-QA. Wszystkie ich zamowienia, GO i sesje
      wypadaja z metryk produkcyjnych; zostaja w TEST_ORDERS do sekcji anomalii.
  C3. Wszystkie daty w Europe/Warsaw; sesje/eventy konwertowane z UTC. Atrybucja po identity stitchingu.

Tylko stdlib. Europe/Warsaw liczona regula DST UE (brak tzdata w srodowisku).
"""
import csv
import glob
import os
from collections import defaultdict
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA = os.path.join(ROOT, "docs", "input", "dane")
OUT = os.path.join(ROOT, "docs", "output")

Y2_START = date(2025, 10, 1)
DOCTOR_COST = {"internista": 25.0, "psychiatra": 200.0}  # pozostali: 100 zl (README)
DOCTOR_COST_DEFAULT = 100.0
AFFILIATE_FEE = 25.0
GO_FEE = 89.0
PAID_MEDIA = ("cpc", "paid_social")

# ---------------------------------------------------------------------------
# Europe/Warsaw
# ---------------------------------------------------------------------------
_DST = {}


def _last_sunday(y, m):
    d = date(y, m + 1, 1) - timedelta(days=1)
    while d.weekday() != 6:
        d -= timedelta(days=1)
    return d


def waw_offset_h(utc):
    y = utc.year
    if y not in _DST:
        s, e = _last_sunday(y, 3), _last_sunday(y, 10)
        _DST[y] = (datetime(y, s.month, s.day, 1), datetime(y, e.month, e.day, 1))
    s, e = _DST[y]
    return 2 if s <= utc < e else 1


def utc_to_waw(utc):
    return utc + timedelta(hours=waw_offset_h(utc))


def dt(s):
    return datetime.fromisoformat(s) if s else None


def month(d):
    return d.strftime("%Y-%m")


def year_of(d):
    if isinstance(d, datetime):
        d = d.date()
    return "Y1" if d < Y2_START else "Y2"


# ---------------------------------------------------------------------------
# Kanaly
# ---------------------------------------------------------------------------
def channel(src, med):
    if not src and not med:
        return "direct"
    if med == "cpc":
        return "google_cpc"
    if med == "paid_social":
        return src
    if med == "organic":
        return "seo"
    return med


def doctor_cost(spec):
    return DOCTOR_COST.get(spec, DOCTOR_COST_DEFAULT)


# ---------------------------------------------------------------------------
# Wczytanie
# ---------------------------------------------------------------------------
def _read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _read_parts(pattern):
    rows = []
    for path in sorted(glob.glob(os.path.join(DATA, pattern))):
        rows.extend(_read(path))
    return rows


class Dataset:
    """Clean Production + wydzielone dane testowe."""

    def __init__(self, doctor_cost_no_show=False):
        raw_orders = _read(os.path.join(DATA, "orders.csv"))
        self.raw_order_rows = len(raw_orders)

        # C1: deduplikacja
        orders = {}
        for r in raw_orders:
            orders.setdefault(r["order_id"], r)
        self.etl_duplicates = self.raw_order_rows - len(orders)

        # C2: konta testowe
        self.test_users = {r["user_id"] for r in orders.values() if r["promo_code"] == "TEST-QA"}

        # sesje (C3: czas PL)
        self.sessions = {}
        for r in _read_parts("sessions_*.csv"):
            utc = dt(r["started_at_utc"])
            self.sessions[r["session_id"]] = {
                "sid": r["session_id"], "visitor": r["visitor_id"], "user": r["user_id"],
                "utc": utc, "t": utc_to_waw(utc), "src": r["utm_source"], "med": r["utm_medium"],
                "camp": r["utm_campaign"], "device": r["device"], "os": r["os"], "browser": r["browser"],
                "landing": r["landing_page"], "channel": channel(r["utm_source"], r["utm_medium"]),
            }

        self.orders, self.test_orders = [], []
        for r in orders.values():
            o = self._order(r, doctor_cost_no_show)
            (self.test_orders if o["uid"] in self.test_users else self.orders).append(o)
        self.orders.sort(key=lambda o: o["t"])

        self.go, self.test_go = [], []
        for r in _read(os.path.join(DATA, "go_memberships.csv")):
            g = {"mid": r["membership_id"], "uid": r["user_id"], "t": dt(r["purchased_at"]),
                 "valid_until": date.fromisoformat(r["valid_until"]), "fee": float(r["amount_paid"]),
                 "oid": r["order_id"], "sid": r["session_id"]}
            (self.test_go if g["uid"] in self.test_users else self.go).append(g)

        self.users = {r["user_id"]: r for r in _read(os.path.join(DATA, "users.csv"))
                      if r["user_id"] not in self.test_users}
        self.spend = [{"date": date.fromisoformat(r["date"]), "src": r["utm_source"], "med": r["utm_medium"],
                       "camp": r["utm_campaign"], "clicks": int(r["clicks"]), "spend": float(r["spend_pln"])}
                      for r in _read(os.path.join(DATA, "marketing_spend.csv"))]

        self._stitch()
        self._attribute()

    @staticmethod
    def _order(r, no_show_cost):
        lp, paid = float(r["list_price"]), float(r["amount_paid"])
        refund = float(r["refund_amount"] or 0)
        st = r["status"]
        doc_paid = st in ("completed", "refunded") or (no_show_cost and st == "no_show")
        doc = doctor_cost(r["specialization"]) if doc_paid else 0.0
        t = dt(r["created_at"])
        return {
            "oid": r["order_id"], "uid": r["user_id"], "sid": r["session_id"], "t": t, "month": month(t),
            "year": year_of(t), "spec": r["specialization"], "purpose": r["visit_purpose"],
            "mode": r["consultation_mode"], "status": st, "disc_type": r["discount_type"],
            "code": r["promo_code"], "gross": lp, "discount": lp - paid, "billed": paid, "refund": refund,
            "net": paid - refund, "doctor": doc, "cm1": paid - refund - doc,
            "duration": r["duration_min"], "started": r["started_at"], "scheduled": r["scheduled_at"],
            "payment": r["payment_method"], "rating": r["rating"],
        }

    # -- identity stitching ------------------------------------------------------
    def _stitch(self):
        self.vis_sessions = defaultdict(list)
        self.user_vis = defaultdict(set)
        self.user_sessions = defaultdict(list)
        for s in self.sessions.values():
            self.vis_sessions[s["visitor"]].append(s)
            if s["user"]:
                self.user_vis[s["user"]].add(s["visitor"])
                self.user_sessions[s["user"]].append(s)
        # wsteczne mapowanie: visitor -> user (visitor nigdy nie jest wspoldzielony, KROK 1)
        self.vis_user = {v: u for u, vs in self.user_vis.items() for v in vs}

    def stitched_user(self, s):
        return s["user"] or self.vis_user.get(s["visitor"])

    # -- atrybucja pacjentow ---------------------------------------------------------
    def _attribute(self):
        self.user_orders = defaultdict(list)
        for o in self.orders:
            self.user_orders[o["uid"]].append(o)
        self.patients = {}
        for uid, os_ in self.user_orders.items():
            first = os_[0]
            fs = self.sessions[first["sid"]]
            cands = list(self.user_sessions.get(uid, []))
            for v in self.user_vis.get(uid, ()):
                cands.extend(self.vis_sessions[v])
            cands = [s for s in cands if s["utc"] <= fs["utc"]] or [fs]
            ft = min(cands, key=lambda s: s["utc"])
            self.patients[uid] = {
                "uid": uid, "first_t": first["t"], "cohort": first["month"], "year": first["year"],
                "first_oid": first["oid"], "first_code": first["code"] or ("GO" if first["disc_type"] == "go" else "brak"),
                "ft_channel": ft["channel"], "ft_key": self.cost_key(ft),
                "lt_channel": fs["channel"], "lt_key": self.cost_key(fs),
                "orders": os_,
            }

    @staticmethod
    def cost_key(s):
        """Klucz puli kosztowej: kampania platna albo kanal."""
        return s["camp"] if s["med"] in PAID_MEDIA else s["channel"]

    def is_test_session(self, s):
        return self.stitched_user(s) in self.test_users


def compute_cac(ds):
    """Pule kosztow (kampania x miesiac kohorty; afiliacja 25 zl za 1. zamowienie z sesji afiliacyjnej, A12)
    rozdzielone rowno na nowych pacjentow przypisanych do puli (A13). Ustawia p['cac_ft'] i p['cac_lt']."""
    pool = defaultdict(float)
    for r in ds.spend:
        pool[(r["camp"], month(r["date"]))] += r["spend"]
    aff_lt = [p for p in ds.patients.values() if p["lt_channel"] == "affiliate"]
    aff_ft = [p for p in ds.patients.values() if p["ft_channel"] == "affiliate"]
    for p in aff_lt:
        pool[("affiliate", p["cohort"])] += AFFILIATE_FEE
    unalloc = {}
    for key_field in ("ft_key", "lt_key"):
        cnt = defaultdict(int)
        for p in ds.patients.values():
            cnt[(p[key_field], p["cohort"])] += 1
        unalloc[key_field] = sum(v for k, v in pool.items() if cnt.get(k, 0) == 0)
        for p in ds.patients.values():
            k = (p[key_field], p["cohort"])
            p["cac_" + key_field[:2]] = pool.get(k, 0.0) / cnt[k]
    return {"pool": pool, "unalloc_ft": unalloc["ft_key"], "unalloc_lt": unalloc["lt_key"],
            "aff_lt": aff_lt, "aff_ft": aff_ft}


DATA_END = date(2026, 9, 30)
WINDOWS = (7, 14, 30, 60, 90, 180, 365)
L4_CODES = {"L4SZYBKO20", "TIKTOK25"}
IN_APP = {"Instagram", "Facebook", "TikTok"}


def code_group(c):
    if c in L4_CODES:
        return "kod L4"
    return {"brak": "brak kodu", "GO": "rabat GO"}.get(c, "inne kody")


def bgroup(b):
    return "in_app" if b in IN_APP else ("chrome/safari" if b in ("Chrome", "Safari") else "inne")


def enrich_patients(ds):
    """Segmenty kohortowe i okna D+k (A17). Wymaga compute_cac(ds). p['win'][k] = (powrot, net, cm1, cm2)."""
    go_by_user = defaultdict(list)
    for g in ds.go:
        go_by_user[g["uid"]].append(g)
    for p in ds.patients.values():
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
    return go_by_user


def session_funnel(ds, ev_by_sid):
    """Flagi lejka per sesja produkcyjna (A19): s['f'] = (S1, S2, S3, S4, S5, zamowienie)."""
    order_sids = {o["sid"] for o in ds.orders}
    prod, inconsist = [], defaultdict(int)
    for s in ds.sessions.values():
        if ds.is_test_session(s):
            continue
        ev = ev_by_sid.get(s["sid"], {})
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
        prod.append(s)
    return prod, dict(inconsist)


def survival(ds):
    """Kaplan-Meier czasu do 2. zamowienia + odstepy do kolejnego zamowienia (z pelnym 365-dniowym okresem)."""
    end_dt = datetime(DATA_END.year, DATA_END.month, DATA_END.day) + timedelta(days=1)
    obs = []
    for p in ds.patients.values():
        if p["ret_days"]:
            obs.append((p["ret_days"][0], 1))
        else:
            obs.append(((end_dt - p["first_t"]).total_seconds() / 86400, 0))
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
    gaps = []
    for p in ds.patients.values():
        os_ = p["orders"]
        for j, o in enumerate(os_):
            if o["t"] + timedelta(days=365) > end_dt:
                continue
            gaps.append((os_[j + 1]["t"] - o["t"]).total_seconds() / 86400 if j + 1 < len(os_) else float("inf"))
    return km, gaps


def km_at(km, day):
    s = 1.0
    for t, v in km:
        if t > day:
            break
        s = v
    return s


def load_events():
    """session_id -> {event_name: pierwszy moment (Europe/Warsaw)}. Eventy sa bez duplikatow (KROK 1)."""
    ev = defaultdict(dict)
    for r in _read_parts("events_*.csv"):
        t = utc_to_waw(dt(r["event_at_utc"]))
        d = ev[r["session_id"]]
        if r["event_name"] not in d or t < d[r["event_name"]]:
            d[r["event_name"]] = t
    return ev


# ---------------------------------------------------------------------------
# Raport
# ---------------------------------------------------------------------------
class Report:
    def __init__(self):
        self.lines = []

    def h(self, title, level=2):
        self.lines.append(f"\n{'#' * level} {title}\n")

    def p(self, text=""):
        self.lines.append(text)

    def table(self, headers, rows):
        self.lines.append("| " + " | ".join(str(x) for x in headers) + " |")
        self.lines.append("|" + "---|" * len(headers))
        for r in rows:
            self.lines.append("| " + " | ".join(str(x) for x in r) + " |")
        self.lines.append("")

    def write(self, path, title):
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\nWygenerowano: {datetime.now():%Y-%m-%d %H:%M}\n")
            f.write("\n".join(self.lines) + "\n")


def zl(x):
    return f"{x:,.0f}".replace(",", " ")


def zl2(x):
    return f"{x:,.2f}".replace(",", " ")


def pct(a, b):
    return f"{100.0 * a / b:.1f}%" if b else "n/a"
