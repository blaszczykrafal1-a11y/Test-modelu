"""
04_smoke_test.py - test dymny dashboardu index.html (bez instalowania pakietow).

1. `node --check` na skrypcie aplikacji (skladnia JS).
2. Przegladarka headless (Edge/Chrome) laduje kopie strony z wstrzyknietym testem: przeklikuje wszystkie zakladki,
   selecty, przelaczniki, wiersze tabel i oba motywy; zbiera bledy JS i szuka 'NaN' / 'undefined' w tresci.
3. Zrzuty ekranu kazdej zakladki (do obejrzenia).

Uruchomienie: python docs/output/scripts/04_smoke_test.py [katalog_wyjsciowy]
"""
import json
import os
import re
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
INDEX = os.path.join(ROOT, "index.html")
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "telemedi_smoke")
os.makedirs(OUTDIR, exist_ok=True)
BROWSERS = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe"]
BROWSER = next(b for b in BROWSERS if os.path.exists(b))

with open(INDEX, encoding="utf-8") as f:
    page = f.read()
print(f"index.html: {os.path.getsize(INDEX) / 1024 / 1024:.2f} MB")

# 1. skladnia JS
app = re.search(r'<script>\s*("use strict";.*?)</script>', page, re.S).group(1)
js_path = os.path.join(OUTDIR, "app.js")
with open(js_path, "w", encoding="utf-8") as f:
    f.write(app)
chk = subprocess.run(["node", "--check", js_path], capture_output=True, text=True)
print("node --check:", "OK" if chk.returncode == 0 else chk.stderr)
json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', page, re.S).group(1))
print("JSON danych: OK")

# 2. test interakcji w przegladarce
CATCH = "<script>window.__errs=[];addEventListener('error',e=>__errs.push(String(e.message)+' @'+e.lineno));</script>"
TEST = r"""<script>
(function(){
  const log = [], fail = [];
  const step = (name, fn) => { try { fn(); log.push(name); } catch (e) { fail.push(name + ': ' + e.message); } };
  const fire = el => el.dispatchEvent(new Event('change', {bubbles:true}));
  function exercise(tab) {
    step('show ' + tab, () => show(tab));
    const sec = document.getElementById(tab);
    sec.querySelectorAll('.seg button').forEach((b, i) => step(tab + ' seg ' + b.textContent, () => b.click()));
    sec.querySelectorAll('select').forEach(s => {
      const vals = [...s.options].map(o => o.value);
      vals.forEach(v => step(tab + ' ' + s.id + '=' + v, () => { s.value = v; fire(s); }));
      if (vals.length) { s.value = vals[0]; fire(s); }
    });
    sec.querySelectorAll('.seg').forEach(g => { const b = g.querySelector('button'); if (b) step(tab + ' reset', () => b.click()); });
  }
  ['t1','t2','t3','t4','t5'].forEach(exercise);
  step('kohorty dzien', () => { show('t2'); document.querySelector('#cAgg button[data-v=day]').click(); });
  step('kohorty segmenty', () => { const d = document.getElementById('cDim'); d.value = 'ft_channel'; fire(d); document.querySelector('#cAgg button[data-v=week]').click(); });
  step('zdarzenie klik', () => document.querySelector('#evTable tr[data-n]').click());
  step('typ zdarzen off', () => { const c = document.querySelector('#tKinds input'); c.checked = false; fire(c); });
  step('plan sort', () => { show('t4'); document.querySelector('#planTable th[data-k=central]').click(); });
  step('plan rozwin', () => document.querySelector('#planTable tr[data-id]').click());
  step('szukaj', () => { show('t5'); const s = document.getElementById('aSearch'); s.value = 'stitching'; s.dispatchEvent(new Event('input')); });
  step('motyw ciemny', () => setTheme('dark'));
  ['t1','t2','t3','t4','t5'].forEach(t => step('dark ' + t, () => show(t)));
  step('motyw jasny', () => setTheme('light'));
  const text = document.body.innerText;
  const bad = (text.match(/NaN|undefined|Infinity/g) || []).length;
  const counts = {
    heatRows: document.querySelectorAll('#heat tbody tr').length,
    planRows: document.querySelectorAll('#planTable tbody tr').length,
    events: document.querySelectorAll('#evTable tbody tr').length,
    assumptions: document.querySelectorAll('#hAssum tbody tr').length,
    unknowns: document.querySelectorAll('#unknowns .unk').length,
    charts: Object.keys(charts).length,
  };
  document.body.setAttribute('data-test', JSON.stringify({ok: log.length, fail, errs: window.__errs, bad, counts}));
})();
</script>"""
test_page = page.replace("<head>", "<head>" + CATCH, 1).replace("</body>", TEST + "</body>", 1)
test_path = os.path.join(OUTDIR, "test.html")
with open(test_path, "w", encoding="utf-8") as f:
    f.write(test_page)
url = "file:///" + test_path.replace("\\", "/")
flags = ["--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars", "--virtual-time-budget=20000",
         f"--user-data-dir={os.path.join(OUTDIR, 'profile')}"]
dom = subprocess.run([BROWSER, *flags, "--dump-dom", url], capture_output=True, text=True, encoding="utf-8", timeout=180).stdout
m = re.search(r"data-test=\"(.*?)\"", dom)
if not m:
    print("BLAD: brak wyniku testu (skrypt nie doszedl do konca)")
    sys.exit(1)
res = json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&"))
print(f"akcje OK: {res['ok']}, nieudane: {len(res['fail'])}, bledy JS: {len(res['errs'])}, 'NaN/undefined/Infinity' w tekscie: {res['bad']}")
for x in res["fail"][:20] + res["errs"][:20]:
    print("  !", x)
print("liczniki:", res["counts"])

# 3. zrzuty ekranu
idx_url = "file:///" + INDEX.replace("\\", "/")
for tab in ("t1", "t2", "t3", "t4", "t5"):
    shot = os.path.join(OUTDIR, f"{tab}.png")
    subprocess.run([BROWSER, *flags, "--window-size=1440,2600", f"--screenshot={shot}", f"{idx_url}#{tab}"],
                   capture_output=True, timeout=180)
    print("zrzut:", shot, "OK" if os.path.exists(shot) else "BRAK")
sys.exit(0 if not res["fail"] and not res["errs"] and not res["bad"] and chk.returncode == 0 else 1)
