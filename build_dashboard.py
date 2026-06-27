"""
build_dashboard.py
Reads dashboard_data.json and writes a self-contained dashboard.html
with all 17 queries rendered across 7 interactive views + per-year filtering.
"""
import json, os

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(WORKSPACE, "dashboard_data.json")
OUT_PATH  = os.path.join(WORKSPACE, "dashboard.html")

with open(DATA_PATH) as f:
    data = json.load(f)

DATA_JSON = json.dumps(data)

HTML = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark" data-mood="Carbon">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>GRIDLINE · F1 Stats Explorer</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
/* ── RESET ── */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
button,select{{font-family:inherit}}

/* ── TOKENS DARK ── */
:root[data-theme="dark"]{{
  --ink:#fff; --ink-2:rgba(255,255,255,.92); --ink-mut:rgba(255,255,255,.55);
  --ink-faint:rgba(255,255,255,.28); --panel-bg:rgba(22,18,24,.42);
  --panel-border:rgba(255,255,255,.09); --divider:rgba(255,255,255,.08);
  --line-strong:rgba(255,255,255,.85); --header-bg:rgba(11,10,14,.55);
  --header-border:rgba(255,255,255,.08); --pill-border:rgba(255,255,255,.22);
  --bar-track:rgba(255,255,255,.12); --eyebrow:#FF6A3D; --vs:rgba(255,255,255,.3);
  --compare-card-bg:rgba(255,255,255,.05); --compare-card-border:rgba(255,255,255,.12);
  --chip-active-bg:#fff; --chip-active-text:#16130F;
  --chip-mut-text:rgba(255,255,255,.6); --chip-mut-border:rgba(255,255,255,.25);
  --vignette:rgba(0,0,0,.35); --row-hover:rgba(255,255,255,.025);
  --th-active:#fff; --grain-opacity:0.055; background-color:#0B0A0E;
}}
/* ── TOKENS LIGHT ── */
:root[data-theme="light"]{{
  --ink:#16130F; --ink-2:rgba(22,19,15,.86); --ink-mut:rgba(22,19,15,.5);
  --ink-faint:rgba(22,19,15,.25); --panel-bg:rgba(255,255,255,.5);
  --panel-border:rgba(22,19,15,.1); --divider:rgba(22,19,15,.1);
  --line-strong:#16130F; --header-bg:rgba(246,245,242,.62);
  --header-border:rgba(22,19,15,.1); --pill-border:rgba(22,19,15,.22);
  --bar-track:rgba(22,19,15,.12); --eyebrow:#E10600; --vs:rgba(22,19,15,.3);
  --compare-card-bg:rgba(255,255,255,.62); --compare-card-border:rgba(22,19,15,.1);
  --chip-active-bg:#16130F; --chip-active-text:#fff;
  --chip-mut-text:rgba(22,19,15,.5); --chip-mut-border:rgba(22,19,15,.22);
  --vignette:rgba(0,0,0,.05); --row-hover:rgba(0,0,0,.03);
  --th-active:#16130F; --grain-opacity:0.08; background-color:#F1EFEB;
}}
/* ── GRADIENTS ── */
:root[data-theme="dark"][data-mood="Carbon"]{{--grad:radial-gradient(130% 110% at 80% -8%,rgba(120,132,152,.42),transparent 60%),radial-gradient(120% 120% at 5% 115%,rgba(205,30,20,.34),transparent 58%),linear-gradient(160deg,#181A1F 0%,#111316 55%,#0B0C0E 100%)}}
:root[data-theme="light"][data-mood="Carbon"]{{--grad:radial-gradient(130% 110% at 80% -8%,rgba(120,132,152,.22),transparent 60%),radial-gradient(120% 120% at 5% 115%,rgba(205,30,20,.12),transparent 58%),linear-gradient(160deg,#F2F3F5 0%,#ECEDEF 55%,#E7E8EA 100%)}}
:root[data-theme="dark"][data-mood="Ember"]{{--grad:radial-gradient(130% 110% at 80% -8%,rgba(235,45,18,.80),transparent 60%),radial-gradient(120% 120% at 5% 115%,rgba(140,14,32,.62),transparent 58%),linear-gradient(160deg,#250B0C 0%,#170608 55%,#0D0406 100%)}}
:root[data-theme="dark"][data-mood="Midnight"]{{--grad:radial-gradient(130% 110% at 80% -8%,rgba(40,110,225,.70),transparent 60%),radial-gradient(120% 120% at 5% 115%,rgba(16,150,150,.50),transparent 58%),linear-gradient(160deg,#0B1430 0%,#08101F 55%,#060A12 100%)}}
:root[data-theme="dark"][data-mood="Crimson"]{{--grad:radial-gradient(130% 110% at 80% -8%,rgba(240,28,16,.90),transparent 60%),radial-gradient(120% 120% at 5% 115%,rgba(120,8,16,.70),transparent 58%),linear-gradient(160deg,#2E0608 0%,#1C0405 55%,#0D0203 100%)}}
:root[data-theme="light"][data-mood="Ember"]{{--grad:radial-gradient(130% 110% at 80% -8%,rgba(235,45,18,.18),transparent 60%),radial-gradient(120% 120% at 5% 115%,rgba(140,14,32,.12),transparent 58%),linear-gradient(160deg,#F5EFEE 0%,#EFE8E7 55%,#EAE3E2 100%)}}
:root[data-theme="light"][data-mood="Midnight"]{{--grad:radial-gradient(130% 110% at 80% -8%,rgba(40,110,225,.14),transparent 60%),radial-gradient(120% 120% at 5% 115%,rgba(16,150,150,.10),transparent 58%),linear-gradient(160deg,#EEF1F5 0%,#E8ECF0 55%,#E3E7EA 100%)}}
:root[data-theme="light"][data-mood="Crimson"]{{--grad:radial-gradient(130% 110% at 80% -8%,rgba(240,28,16,.14),transparent 60%),radial-gradient(120% 120% at 5% 115%,rgba(120,8,16,.10),transparent 58%),linear-gradient(160deg,#F5EEEE 0%,#EFE7E7 55%,#EAE2E2 100%)}}

/* ── BASE ── */
html{{scroll-behavior:smooth}}
body{{font-family:'Archivo',sans-serif;color:var(--ink);min-height:100vh;position:relative;transition:background-color .3s}}

/* ── FIXED BG ── */
.bg-gradient{{position:fixed;inset:0;z-index:0;pointer-events:none;background:var(--grad);background-size:130% 130%;animation:gridDrift 34s ease-in-out infinite;transition:background .6s}}
.bg-vignette{{position:fixed;inset:0;z-index:0;pointer-events:none;background:radial-gradient(120% 120% at 50% 38%,transparent 62%,var(--vignette) 100%)}}
.bg-grain{{position:fixed;inset:0;z-index:0;pointer-events:none;mix-blend-mode:overlay;opacity:var(--grain-opacity);background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)'/%3E%3C/svg%3E");background-size:220px 220px}}
@keyframes gridDrift{{0%,100%{{background-position:0% 0%}}50%{{background-position:100% 100%}}}}

/* ── LAYOUT ── */
.page-content{{position:relative;z-index:1}}
.col{{max-width:1200px;margin:0 auto;padding:0 40px}}

/* ── HEADER ── */
.header{{position:sticky;top:0;z-index:5;background:var(--header-bg);backdrop-filter:blur(22px);-webkit-backdrop-filter:blur(22px);border-bottom:1px solid var(--header-border)}}
.header-inner{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;padding:18px 40px;max-width:1200px;margin:0 auto}}
.brand{{display:flex;align-items:center;gap:10px;text-decoration:none;flex-shrink:0}}
.brand-dot{{width:10px;height:10px;border-radius:50%;background:#E10600;box-shadow:0 0 14px rgba(225,6,0,.9);flex-shrink:0}}
.brand-name{{font-size:16px;font-weight:800;letter-spacing:.16em;color:var(--ink);text-transform:uppercase}}
.header-controls{{display:flex;align-items:center;gap:8px}}
.pill{{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;padding:9px 13px;border-radius:4px;border:1px solid var(--pill-border);background:transparent;color:var(--ink);cursor:pointer;transition:border-color .15s;white-space:nowrap}}
.pill:hover{{border-color:var(--ink-mut)}}
.btn-compare{{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;letter-spacing:.06em;padding:9px 14px;border-radius:4px;border:none;background:#E10600;color:#fff;cursor:pointer;text-transform:uppercase;white-space:nowrap}}
.btn-compare:hover{{opacity:.85}}

/* ── HERO ── */
.hero{{padding:72px 0 48px;border-bottom:1px solid var(--divider)}}
.hero-eyebrow{{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:500;letter-spacing:.18em;color:var(--eyebrow);text-transform:uppercase;margin-bottom:28px}}
.hero-inner{{display:flex;align-items:flex-start;gap:48px;flex-wrap:wrap}}
.hero-big{{font-size:clamp(96px,13vw,168px);font-weight:900;line-height:.8;letter-spacing:-.04em;color:var(--ink);text-shadow:0 8px 60px rgba(225,6,0,.35);flex-shrink:0;transition:all .25s}}
.hero-right{{flex:1;min-width:260px;padding-top:8px}}
.hero-sub{{font-size:23px;font-weight:500;line-height:1.35;color:var(--ink-2);max-width:440px;margin-bottom:24px}}
.view-chips{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px}}
.chip{{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;padding:11px 16px;border-radius:22px;border:1px solid var(--chip-mut-border);background:transparent;color:var(--chip-mut-text);cursor:pointer;transition:all .15s}}
.chip.active{{background:var(--chip-active-bg);color:var(--chip-active-text);border-color:var(--chip-active-bg)}}
.chip:not(.active):hover{{border-color:var(--ink-mut);color:var(--ink)}}
.season-select-wrap{{display:flex;align-items:center;gap:10px;margin-top:14px}}
.season-label{{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-faint)}}
.season-select{{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;letter-spacing:.04em;padding:8px 36px 8px 14px;border-radius:22px;border:1px solid var(--chip-mut-border);background:transparent;color:var(--ink);cursor:pointer;appearance:none;-webkit-appearance:none;outline:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' fill='none'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23888' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center;transition:border-color .15s}}
.season-select:hover{{border-color:var(--ink-mut)}}
.season-select option{{background:#1a1a1f;color:#fff}}

/* ── VIEWS ── */
.view{{display:none}}.view.active{{display:block}}

/* ── PANEL ── */
.panel{{margin:40px 0 40px;background:var(--panel-bg);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border:1px solid var(--panel-border);border-radius:18px;padding:10px 30px 18px}}
.panel+.panel{{margin-top:0}}
.panel:last-child{{margin-bottom:80px}}
.panel-header{{display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid var(--line-strong);padding:24px 0 16px}}
.panel-title{{font-size:19px;font-weight:800;color:var(--ink)}}
.panel-sub{{font-size:12px;font-family:'JetBrains Mono',monospace;color:var(--ink-mut);margin-top:4px}}
.sort-btn{{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;letter-spacing:.1em;color:var(--ink-mut);background:none;border:none;cursor:pointer;padding:4px 0;transition:color .15s;text-transform:uppercase;white-space:nowrap}}
.sort-btn:hover{{color:var(--ink)}}

/* ── DRIVER STATS TABLE ── */
.driver-stats-header,.driver-stats-row{{
  display:grid;
  grid-template-columns:52px 1fr 150px 68px 68px 80px 88px 68px;
  gap:16px;align-items:center;
}}
.driver-stats-header{{border-bottom:1px solid var(--line-strong);padding:16px 0 12px;margin-top:8px}}
.driver-stats-row{{padding:18px 0;border-bottom:1px solid var(--divider);transition:background .12s;border-radius:4px}}
.driver-stats-row:last-child{{border-bottom:none}}
.driver-stats-row:hover{{background:var(--row-hover)}}
.th{{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;letter-spacing:.12em;color:var(--ink-mut);text-transform:uppercase;cursor:pointer;transition:color .15s;user-select:none;text-align:right}}
.th:nth-child(2){{text-align:left}}.th:nth-child(3){{text-align:left}}
.th:hover,.th.active{{color:var(--th-active)}}
.th.active::after{{content:" ▾"}}
.d-pos{{font-size:38px;font-weight:300;color:var(--ink-faint);line-height:1;font-variant-numeric:tabular-nums}}
.d-name{{font-size:22px;font-weight:700;letter-spacing:-.01em;color:var(--ink)}}
.d-team{{display:flex;align-items:center;gap:7px}}
.team-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0}}
.team-label{{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;color:var(--ink-mut)}}
.d-num{{font-family:'JetBrains Mono',monospace;font-size:22px;font-weight:700;color:var(--ink);text-align:right;font-variant-numeric:tabular-nums}}
.d-num.highlight{{color:#FF5A2A}}

/* ── CONSTRUCTOR ROW ── */
.con-row{{display:grid;grid-template-columns:52px 200px 1fr 90px;gap:20px;align-items:center;padding:20px 0;border-bottom:1px solid var(--divider)}}
.con-row:last-child{{border-bottom:none}}
.con-row:hover{{background:var(--row-hover)}}
.con-pos{{font-size:38px;font-weight:300;color:var(--ink-faint);line-height:1}}
.con-name-wrap{{display:flex;align-items:center;gap:10px}}
.con-accent{{width:5px;height:26px;border-radius:3px;flex-shrink:0}}
.con-name{{font-size:22px;font-weight:700;color:var(--ink)}}
.bar-track{{height:8px;background:var(--bar-track);border-radius:4px;overflow:hidden}}
.bar-fill{{height:100%;border-radius:4px;transition:width .7s ease}}
.con-stat{{font-family:'JetBrains Mono',monospace;font-size:24px;font-weight:700;color:var(--ink);text-align:right}}

/* ── CHART CONTAINER ── */
.chart-wrap{{position:relative;width:100%;padding:24px 0 8px}}

/* ── GENERIC TABLE ── */
.data-table{{width:100%;border-collapse:collapse;margin-top:8px}}
.data-table th{{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;letter-spacing:.12em;color:var(--ink-mut);text-transform:uppercase;padding:14px 0 10px;text-align:right;border-bottom:1px solid var(--line-strong)}}
.data-table th:first-child{{text-align:left}}
.data-table th:nth-child(2){{text-align:left}}
.data-table td{{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:500;color:var(--ink);padding:14px 0;border-bottom:1px solid var(--divider);text-align:right;font-variant-numeric:tabular-nums;vertical-align:middle}}
.data-table td:first-child{{text-align:left;font-size:13px;color:var(--ink-faint);width:36px}}
.data-table td:nth-child(2){{text-align:left;font-family:'Archivo',sans-serif;font-size:16px;font-weight:700;color:var(--ink)}}
.data-table tr:last-child td{{border-bottom:none}}
.data-table tr:hover td{{background:var(--row-hover)}}
.accent-val{{color:#FF5A2A;font-weight:700}}
.muted-val{{color:var(--ink-mut)}}

/* ── GAINS LIST ── */
.gain-row{{display:grid;grid-template-columns:28px 1fr 1fr auto;gap:16px;align-items:center;padding:14px 0;border-bottom:1px solid var(--divider)}}
.gain-row:last-child{{border-bottom:none}}
.gain-idx{{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--ink-faint)}}
.gain-driver{{font-size:15px;font-weight:700;color:var(--ink)}}
.gain-race{{font-size:12px;font-family:'JetBrains Mono',monospace;color:var(--ink-mut);margin-top:2px}}
.gain-positions{{font-family:'JetBrains Mono',monospace;font-size:22px;font-weight:700;color:#FF5A2A;text-align:right;white-space:nowrap}}
.gain-arrow{{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--ink-mut)}}

/* ── CHAMP GAPS ── */
.champ-row{{display:grid;grid-template-columns:48px 1fr 56px;align-items:center;gap:12px;margin:10px 0}}
.champ-year{{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;color:var(--ink-mut)}}
.champ-bars{{position:relative;height:28px;background:rgba(255,255,255,.06);border-radius:3px;overflow:hidden}}
:root[data-theme="light"] .champ-bars{{background:rgba(0,0,0,.06)}}
.champ-bar-w{{position:absolute;left:0;top:0;height:100%;display:flex;align-items:center;padding-left:8px;font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;white-space:nowrap;overflow:hidden;border-radius:3px 0 0 3px}}
.champ-bar-r{{position:absolute;top:0;height:100%;background:rgba(255,255,255,.1);display:flex;align-items:center;padding-left:6px;font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--ink-mut);white-space:nowrap;overflow:hidden}}
:root[data-theme="light"] .champ-bar-r{{background:rgba(0,0,0,.08)}}
.champ-gap{{font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:700;color:var(--ink-mut);text-align:right}}
.champ-gap.tight{{color:#FF5A2A}}

/* ── CIRCUIT CARDS ── */
.circuit-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:12px;padding:20px 0 4px}}
.circuit-card{{background:rgba(255,255,255,.04);border:1px solid var(--panel-border);border-radius:12px;padding:18px;transition:border-color .2s,transform .15s;position:relative;overflow:hidden}}
:root[data-theme="light"] .circuit-card{{background:rgba(255,255,255,.5)}}
.circuit-card::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;background:#E10600;transform:scaleX(0);transform-origin:left;transition:transform .3s}}
.circuit-card:hover{{border-color:rgba(255,255,255,.2);transform:translateY(-2px)}}
.circuit-card:hover::after{{transform:scaleX(1)}}
:root[data-theme="light"] .circuit-card:hover{{border-color:rgba(0,0,0,.2)}}
.cc-name{{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--ink);margin-bottom:2px}}
.cc-country{{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--ink-mut);margin-bottom:14px}}
.cc-driver{{font-size:16px;font-weight:700;color:var(--ink);margin-bottom:4px}}
.cc-wins{{font-family:'JetBrains Mono',monospace;font-size:32px;font-weight:700;color:#E10600;line-height:1}}
.cc-wins-label{{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--ink-mut);text-transform:uppercase;letter-spacing:1px}}

/* ── RACE RESULTS LIST ── */
.race-result-row{{display:grid;grid-template-columns:28px 48px 1fr auto;gap:14px;align-items:center;padding:12px 0;border-bottom:1px solid var(--divider)}}
.race-result-row:last-child{{border-bottom:none}}
.rr-round{{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--ink-faint)}}
.rr-flag{{font-size:18px}}
.rr-race{{font-size:14px;font-weight:700;color:var(--ink)}}
.rr-country{{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--ink-mut);margin-top:2px}}
.rr-winner{{font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:700;color:#FF5A2A;text-align:right;white-space:nowrap}}

/* ── COMPARE ── */
.compare-cards{{display:grid;grid-template-columns:1fr 64px 1fr;gap:18px;align-items:center;padding:28px 0 0;margin-bottom:8px}}
.compare-card{{background:var(--compare-card-bg);border:1px solid var(--compare-card-border);border-top:4px solid transparent;border-radius:12px;padding:26px}}
.compare-card.right{{text-align:right}}
.compare-selector{{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;background:transparent;border:none;outline:none;color:var(--ink-mut);cursor:pointer;appearance:none;-webkit-appearance:none;width:100%;display:block;margin-bottom:8px}}
.compare-card.right .compare-selector{{text-align-last:right}}
.compare-driver-name{{font-size:34px;font-weight:800;color:var(--ink);line-height:1.1;margin-bottom:12px}}
.compare-pts{{font-family:'JetBrains Mono',monospace;font-size:60px;font-weight:700;line-height:1}}
.compare-pts-suffix{{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:500;color:var(--ink-mut);margin-left:4px;vertical-align:middle}}
.vs-label{{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:700;color:var(--vs);text-align:center}}
.stat-rows{{margin-top:0}}
.stat-row{{display:grid;grid-template-columns:1fr 200px 1fr;align-items:center;padding:18px 0;border-bottom:1px solid var(--divider)}}
.stat-row:last-child{{border-bottom:none}}
.stat-val{{font-family:'JetBrains Mono',monospace;font-size:30px;font-weight:500;color:var(--ink)}}
.stat-val.right{{text-align:right}}
.stat-val.winner{{color:#FF5A2A;font-weight:800}}
.stat-label{{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;letter-spacing:.14em;color:var(--ink-mut);text-align:center;text-transform:uppercase}}

/* ── TWO-COL GRID ── */
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:0;margin-bottom:80px}}
.two-col .panel{{margin-bottom:0;border-radius:0}}
.two-col .panel:first-child{{border-radius:18px 0 0 18px;border-right:none}}
.two-col .panel:last-child{{border-radius:0 18px 18px 0}}

/* ── EMPTY STATE ── */
.empty-state{{padding:40px 0;text-align:center;font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--ink-faint)}}

/* ── MOOD DOCK ── */
.mood-dock{{position:fixed;bottom:24px;right:24px;z-index:10;display:flex;gap:4px;background:var(--header-bg);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid var(--pill-border);border-radius:8px;padding:6px}}
.mood-btn{{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;letter-spacing:.08em;padding:6px 10px;border-radius:4px;border:1px solid transparent;background:transparent;color:var(--ink-mut);cursor:pointer;transition:all .15s;text-transform:uppercase}}
.mood-btn:hover{{color:var(--ink);border-color:var(--pill-border)}}
.mood-btn.active{{background:var(--chip-active-bg);color:var(--chip-active-text)}}

@media(max-width:900px){{
  .col{{padding:0 20px}}
  .header-inner{{padding:14px 20px}}
  .nav{{display:none}}
  .hero{{padding:48px 0 36px}}
  .hero-big{{font-size:clamp(72px,18vw,120px)}}
  .hero-sub{{font-size:18px}}
  .driver-stats-header,.driver-stats-row{{grid-template-columns:40px 1fr 68px 68px;gap:10px}}
  .th:nth-child(3),.th:nth-child(5),.th:nth-child(7),.th:nth-child(8),
  .d-team,.d-num:nth-child(5),.d-num:nth-child(7),.d-num:nth-child(8){{display:none}}
  .con-row{{grid-template-columns:40px 1fr 80px;gap:12px}}
  .bar-track{{display:none}}
  .two-col{{grid-template-columns:1fr}}
  .two-col .panel:first-child{{border-radius:18px 18px 0 0;border-right:1px solid var(--panel-border);border-bottom:none}}
  .two-col .panel:last-child{{border-radius:0 0 18px 18px}}
  .compare-cards{{grid-template-columns:1fr 40px 1fr;gap:10px}}
  .compare-pts{{font-size:36px}}
  .compare-driver-name{{font-size:22px}}
  .stat-row{{grid-template-columns:1fr 120px 1fr}}
  .stat-val{{font-size:22px}}
  .gain-row{{grid-template-columns:24px 1fr auto}}
  .gain-arrow{{display:none}}
  .mood-dock{{bottom:12px;right:12px}}
}}
</style>
</head>
<body>
<div class="bg-gradient"></div>
<div class="bg-vignette"></div>
<div class="bg-grain"></div>

<div class="page-content">

<!-- HEADER -->
<header class="header">
  <div class="header-inner">
    <div class="brand"><div class="brand-dot"></div><span class="brand-name">GRIDLINE</span></div>
    <nav class="nav"></nav>
    <div class="header-controls">
      <button class="pill" id="themeToggle">☾ DARK</button>
      <button class="btn-compare" id="btnCompare">COMPARE</button>
    </div>
  </div>
</header>

<!-- HERO -->
<div class="col">
  <section class="hero">
    <p class="hero-eyebrow" id="heroEyebrow">THE CLOSEST FIGHT · MODERN ERA 2010-2024</p>
    <div class="hero-inner">
      <div class="hero-big" id="heroBig">+8</div>
      <div class="hero-right">
        <p class="hero-sub" id="heroSub">Max Verstappen beat Lewis Hamilton by eight points in 2021, the most dramatic title fight of the modern era.</p>
        <div class="view-chips" id="viewChips">
          <button class="chip active" data-view="drivers">Drivers</button>
          <button class="chip" data-view="constructors">Constructors</button>
          <button class="chip" data-view="qualifying">Qualifying</button>
          <button class="chip" data-view="strategy">Strategy</button>
          <button class="chip" data-view="championships">Championship</button>
          <button class="chip" data-view="circuits">Circuits</button>
        </div>
        <div class="season-select-wrap">
          <span class="season-label">Season</span>
          <select class="season-select" id="seasonSelect">
            <option value="all">All Seasons</option>
            <option value="2024">2024</option>
            <option value="2023">2023</option>
            <option value="2022">2022</option>
            <option value="2021">2021</option>
            <option value="2020">2020</option>
            <option value="2019">2019</option>
            <option value="2018">2018</option>
            <option value="2017">2017</option>
            <option value="2016">2016</option>
            <option value="2015">2015</option>
            <option value="2014">2014</option>
            <option value="2013">2013</option>
            <option value="2012">2012</option>
            <option value="2011">2011</option>
            <option value="2010">2010</option>
          </select>
        </div>
      </div>
    </div>
  </section>
</div>

<!-- VIEWS -->
<div class="col">

<!-- ── VIEW: DRIVERS ── -->
<div class="view active" id="view-drivers">
  <div class="panel">
    <div class="panel-header">
      <div><div class="panel-title" id="driversTitle">Driver Stats · Modern Era</div><div class="panel-sub">Wins · Win% · Podiums · Avg Points · DNF%</div></div>
    </div>
    <div class="driver-stats-header">
      <div class="th">#</div>
      <div class="th" style="text-align:left">DRIVER</div>
      <div class="th" style="text-align:left">TEAM</div>
      <div class="th active" data-sort="wins">WINS</div>
      <div class="th" data-sort="win_pct">WIN%</div>
      <div class="th" data-sort="podiums">PODIUMS</div>
      <div class="th" data-sort="avg_pts">AVG PTS</div>
      <div class="th" data-sort="dnf_pct">DNF%</div>
    </div>
    <div id="driversTable"></div>
  </div>
</div>

<!-- ── VIEW: CONSTRUCTORS ── -->
<div class="view" id="view-constructors">
  <div class="panel">
    <div class="panel-header">
      <div><div class="panel-title" id="conChartTitle">Race Wins by Season</div><div class="panel-sub" id="conChartSub">Q6: wins per constructor per year</div></div>
    </div>
    <div class="chart-wrap" style="height:300px"><canvas id="chartConstructorSeason"></canvas></div>
  </div>
  <div class="two-col">
    <div class="panel">
      <div class="panel-header">
        <div><div class="panel-title" id="conStandingsTitle">2024 Championship Standings</div><div class="panel-sub">Q7: final constructor points</div></div>
      </div>
      <div id="constructorStandingsTable"></div>
    </div>
    <div class="panel">
      <div class="panel-header">
        <div><div class="panel-title" id="conDomTitle">Season Dominance</div><div class="panel-sub">Q8: highest win % per season</div></div>
      </div>
      <div id="constructorDominanceTable"></div>
    </div>
  </div>
</div>

<!-- ── VIEW: QUALIFYING ── -->
<div class="view" id="view-qualifying">
  <div class="panel">
    <div class="panel-header">
      <div><div class="panel-title">Grid vs Finish Position</div><div class="panel-sub" id="q9Sub">Q9: avg positions gained from qualifying</div></div>
      <button class="sort-btn" id="q9SortBtn">SORT: POS GAINED ▾</button>
    </div>
    <table class="data-table" id="gridFinishTable">
      <thead><tr>
        <th>#</th><th>DRIVER</th>
        <th>AVG START</th><th>AVG FINISH</th><th>AVG GAINED</th><th>RACES</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </div>
  <div class="two-col">
    <div class="panel">
      <div class="panel-header">
        <div><div class="panel-title" id="q10Title">Biggest Single-Race Gains</div><div class="panel-sub" id="q10Sub">Q10: top 20 positions gained in one race</div></div>
      </div>
      <div id="biggestGainsList"></div>
    </div>
    <div class="panel">
      <div class="panel-header">
        <div><div class="panel-title">Pole → Win Conversion</div><div class="panel-sub" id="q11Sub">Q11: % of poles converted to race wins</div></div>
      </div>
      <table class="data-table" id="poleConvTable">
        <thead><tr><th>#</th><th>DRIVER</th><th>POLES</th><th>WINS</th><th>CONV%</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>
</div>

<!-- ── VIEW: STRATEGY ── -->
<div class="view" id="view-strategy">
  <div class="panel">
    <div class="panel-header">
      <div><div class="panel-title">Avg Pit Stop Duration by Constructor</div><div class="panel-sub" id="q12Sub">Q12: seconds · fastest first</div></div>
    </div>
    <div class="chart-wrap" style="height:340px"><canvas id="chartPitStop"></canvas></div>
  </div>
  <div class="panel" style="margin-bottom:80px">
    <div class="panel-header">
      <div><div class="panel-title">Pit Stops vs Finishing Position</div><div class="panel-sub" id="q13Sub">Q13: avg finish position by number of stops</div></div>
    </div>
    <table class="data-table" id="stopsFinishTable">
      <thead><tr><th>#</th><th>STOPS</th><th>AVG FINISH POS</th><th>SAMPLE SIZE</th></tr></thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<!-- ── VIEW: CHAMPIONSHIPS ── -->
<div class="view" id="view-championships">
  <div class="panel">
    <div class="panel-header">
      <div><div class="panel-title" id="q14Title">Championship Points Gap</div><div class="panel-sub">Q14: P1 vs P2 at season end · <span style="color:#FF5A2A">red = under 20 pts</span></div></div>
    </div>
    <div id="champGapsList" style="padding:16px 0"></div>
  </div>
  <div class="panel" style="margin-bottom:80px">
    <div class="panel-header">
      <div><div class="panel-title" id="q15Title">2021 Title Race · Round by Round</div><div class="panel-sub" id="q15Sub">Q15: cumulative points through the season</div></div>
    </div>
    <div class="chart-wrap" style="height:320px"><canvas id="chart2021"></canvas></div>
  </div>
</div>

<!-- ── VIEW: CIRCUITS ── -->
<div class="view" id="view-circuits">
  <div class="panel">
    <div class="panel-header">
      <div><div class="panel-title" id="q16Title">Circuit Dominance</div><div class="panel-sub" id="q16Sub">Q16: top driver per circuit · min 2 wins</div></div>
    </div>
    <div id="circuitGrid"></div>
  </div>
  <div class="panel" style="margin-bottom:80px">
    <div class="panel-header">
      <div><div class="panel-title">Home Race Advantage</div><div class="panel-sub" id="q17Sub">Q17: avg finish at home vs away · lower = better</div></div>
    </div>
    <table class="data-table" id="homeAdvTable">
      <thead><tr><th>#</th><th>DRIVER</th><th>HOME AVG</th><th>AWAY AVG</th><th>ADVANTAGE</th></tr></thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<!-- ── VIEW: COMPARE ── -->
<div class="view" id="view-compare">
  <div class="panel" style="margin-bottom:80px">
    <div class="panel-header"><div class="panel-title">Head to Head <span id="compareYearLabel" style="font-size:14px;font-weight:400;color:var(--ink-mut)"></span></div></div>
    <div class="compare-cards">
      <div class="compare-card" id="cardA">
        <select class="compare-selector" id="selectA"></select>
        <div class="compare-driver-name" id="nameA"></div>
        <div><span class="compare-pts" id="ptsA"></span><span class="compare-pts-suffix">WINS</span></div>
      </div>
      <div class="vs-label">VS</div>
      <div class="compare-card right" id="cardB">
        <select class="compare-selector" id="selectB"></select>
        <div class="compare-driver-name" id="nameB"></div>
        <div><span class="compare-pts" id="ptsB"></span><span class="compare-pts-suffix">WINS</span></div>
      </div>
    </div>
    <div class="stat-rows" id="statRows"></div>
  </div>
</div>

</div><!-- /col -->
</div><!-- /page-content -->

<!-- MOOD DOCK -->
<div class="mood-dock" id="moodDock">
  <button class="mood-btn active" data-mood="Carbon">Carbon</button>
  <button class="mood-btn" data-mood="Ember">Ember</button>
  <button class="mood-btn" data-mood="Midnight">Midnight</button>
  <button class="mood-btn" data-mood="Crimson">Crimson</button>
</div>

<script>
// ─── EMBEDDED DATA ────────────────────────────────────────────────────────────
const F1_DATA = {DATA_JSON};

// ─── TEAM COLORS ─────────────────────────────────────────────────────────────
const TEAM_COLOR = {{
  'Mercedes':'#27F4D2','Red Bull':'#5E8FE6','Ferrari':'#FF2D4B',
  'McLaren':'#FF8000','Renault':'#FFD700','Alpine F1 Team':'#0090FF',
  'AlphaTauri':'#6692FF','Racing Point':'#F596C8','Lotus F1':'#FFE200',
  'Toro Rosso':'#6692FF','Force India':'#F596C8','Williams':'#64C4FF',
  'Haas F1 Team':'#B6BABD','Alfa Romeo':'#9B0000','Sauber':'#52E252',
  'Aston Martin':'#3FC79A','RB F1 Team':'#6692FF','Kick Sauber':'#52E252',
}};
const DRIVER_TEAM = {{
  'Lewis Hamilton':'Mercedes','Max Verstappen':'Red Bull',
  'Sebastian Vettel':'Red Bull','Nico Rosberg':'Mercedes',
  'Fernando Alonso':'Aston Martin','Valtteri Bottas':'Mercedes',
  'Charles Leclerc':'Ferrari','Daniel Ricciardo':'Red Bull',
  'Jenson Button':'McLaren','Mark Webber':'Red Bull',
  'Sergio Pérez':'Red Bull','Lando Norris':'McLaren',
  'Carlos Sainz':'Ferrari','George Russell':'Mercedes',
  'Kimi Räikkönen':'Ferrari','Nico Hülkenberg':'Force India',
  'Romain Grosjean':'Lotus F1','Robert Kubica':'Williams',
  'Oscar Piastri':'McLaren','Lance Stroll':'Aston Martin',
}};

// ─── HERO: computed from data ────────────────────────────────────────────────
// Returns {{ big, sub, eyebrow }} based on current view + year
function computeHero() {{
  const d    = yd();
  const yr   = state.year;
  const isAll = yr === 'all';
  const yrLabel = isAll ? '2010-2024' : yr;

  switch (state.view) {{

    case 'drivers': {{
      const wins = (d ? d.q1_driver_wins : F1_DATA.q1_driver_wins) || [];
      if (!wins.length) break;
      const top = wins[0];
      return {{
        big: String(top.total_race_wins),
        sub: top.driver_name + ' leads with ' + top.total_race_wins + ' wins' + (isAll ? ' across the modern era.' : ' in ' + yr + '.'),
        eyebrow: 'DRIVER WINS · ' + yrLabel,
      }};
    }}

    case 'constructors': {{
      if (isAll) {{
        // Most wins by any constructor in a single season
        const best = F1_DATA.q6_constructor_season_wins.reduce(
          (m, r) => r.total_wins > m.total_wins ? r : m,
          F1_DATA.q6_constructor_season_wins[0]
        );
        return {{
          big: String(best.total_wins),
          sub: best.constructor + ' won ' + best.total_wins + ' races in ' + best.year + ', the most dominant single season of the modern era.',
          eyebrow: 'SINGLE-SEASON RECORD · ' + yrLabel,
        }};
      }} else {{
        const rows = F1_DATA.q6_constructor_season_wins.filter(r => String(r.year) === yr)
          .sort((a,b) => b.total_wins - a.total_wins);
        if (!rows.length) break;
        return {{
          big: String(rows[0].total_wins),
          sub: rows[0].constructor + ' led all constructors with ' + rows[0].total_wins + ' wins in ' + yr + '.',
          eyebrow: 'CONSTRUCTOR WINS · ' + yr,
        }};
      }}
    }}

    case 'qualifying': {{
      const poles = (d ? d.q11_pole_conversion : F1_DATA.q11_pole_conversion) || [];
      if (!poles.length) break;
      const top = poles[0];
      return {{
        big: top.conv_rate + '%',
        sub: top.driver_name + ' converted ' + top.conv_rate + '% of pole positions into wins' + (isAll ? ' in the modern era' : ' in ' + yr) + ', best of anyone with multiple poles.',
        eyebrow: 'POLE CONVERSION · ' + yrLabel,
      }};
    }}

    case 'strategy': {{
      const pits = (d ? d.q12_pit_duration : F1_DATA.q12_pit_duration) || [];
      if (!pits.length) break;
      const top = pits[0];
      return {{
        big: parseFloat(top.avg_pit_stop).toFixed(1) + 's',
        sub: top.constructor + ' averaged the fastest pit stops' + (isAll ? ' across the modern era' : ' in ' + yr) + ' at ' + top.avg_pit_stop + 's per stop.',
        eyebrow: 'FASTEST PIT CREW · ' + yrLabel,
      }};
    }}

    case 'championships': {{
      const allGaps = F1_DATA.q14_championship_gaps;
      if (isAll) {{
        const tightest = allGaps.reduce((m, r) => r.points_gap < m.points_gap ? r : m, allGaps[0]);
        return {{
          big: '+' + tightest.points_gap,
          sub: tightest.winner.split(' ').pop() + ' beat ' + tightest.runner_up.split(' ').pop() + ' by ' + tightest.points_gap + ' points in ' + tightest.year + ', the closest title fight of the modern era.',
          eyebrow: 'CLOSEST TITLE FIGHT · ' + yrLabel,
        }};
      }} else {{
        const gap = allGaps.find(r => String(r.year) === yr);
        if (!gap) break;
        return {{
          big: '+' + gap.points_gap,
          sub: gap.winner + ' beat ' + gap.runner_up + ' by ' + gap.points_gap + ' points to win the ' + yr + ' championship.',
          eyebrow: 'CHAMPIONSHIP GAP · ' + yr,
        }};
      }}
    }}

    case 'circuits': {{
      if (isAll) {{
        const n = F1_DATA.q16_circuit_dominance.length;
        return {{
          big: String(n),
          sub: n + ' circuits have had a dominant driver win there at least twice in the modern era.',
          eyebrow: 'CIRCUITS COVERED · ' + yrLabel,
        }};
      }} else {{
        const races = (d ? d.q16_race_winners : []);
        return {{
          big: String(races.length),
          sub: races.length + ' races on the ' + yr + ' calendar across ' + new Set(races.map(r => r.circuit_country)).size + ' countries.',
          eyebrow: 'RACE CALENDAR · ' + yr,
        }};
      }}
    }}

    case 'compare': {{
      const tightest = F1_DATA.q14_championship_gaps.reduce(
        (m, r) => r.points_gap < m.points_gap ? r : m,
        F1_DATA.q14_championship_gaps[0]
      );
      return {{
        big: '+' + tightest.points_gap,
        sub: tightest.winner.split(' ').pop() + ' vs ' + tightest.runner_up.split(' ').pop() + ', ' + tightest.year + '. The numbers tell the story.',
        eyebrow: 'HEAD TO HEAD · ' + yrLabel,
      }};
    }}
  }}

  // fallback
  return {{
    big: '+8', sub: 'Select a tab to explore the data.', eyebrow: 'GRIDLINE · ' + yrLabel,
  }};
}}

// ─── STATE ────────────────────────────────────────────────────────────────────
const state = {{ view:'drivers', driverSort:'wins', theme:'dark', mood:'Carbon', year:'all' }};
const $ = id => document.getElementById(id);
const pad = n => String(n).padStart(2,'0');

// ─── YEAR DATA ACCESSOR ───────────────────────────────────────────────────────
function yd() {{
  return state.year === 'all' ? null : F1_DATA.by_year[state.year];
}}
function isYear() {{ return state.year !== 'all'; }}

// ─── HERO UPDATE ─────────────────────────────────────────────────────────────
function updateHero() {{
  const h = computeHero();
  $('heroBig').textContent     = h.big;
  $('heroSub').textContent     = h.sub;
  $('heroEyebrow').textContent = h.eyebrow;
}}

// ─── CHART TEARDOWN ──────────────────────────────────────────────────────────
let chartConstructorSeason=null, chartPitStop=null, chart2021=null;
function destroyAllCharts() {{
  if (chartConstructorSeason) {{ chartConstructorSeason.destroy(); chartConstructorSeason=null; }}
  if (chartPitStop) {{ chartPitStop.destroy(); chartPitStop=null; }}
  if (chart2021) {{ chart2021.destroy(); chart2021=null; }}
}}

// ─── VIEW ────────────────────────────────────────────────────────────────────
function setView(v) {{
  state.view = v;
  document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
  $('view-'+v).classList.add('active');
  document.querySelectorAll('#viewChips .chip').forEach(c =>
    c.classList.toggle('active', c.dataset.view === v));
  updateHero();
  renderCurrentView();
}}

function renderCurrentView() {{
  const v = state.view;
  if (v==='drivers')       renderDrivers();
  if (v==='constructors')  {{ destroyAllCharts(); initConstructorCharts(); }}
  if (v==='qualifying')    renderQualifying();
  if (v==='strategy')      {{ destroyAllCharts(); initStrategyCharts(); }}
  if (v==='championships') {{ destroyAllCharts(); renderChampionshipGaps(); initChampionshipCharts(); }}
  if (v==='circuits')      renderCircuits();
  if (v==='compare')       renderCompare();
}}

// ─── YEAR ────────────────────────────────────────────────────────────────────
function setYear(y) {{
  state.year = y;
  updateHero();
  destroyAllCharts();
  renderCurrentView();
}}

// ─── THEME / MOOD ────────────────────────────────────────────────────────────
function setTheme(t) {{
  state.theme = t;
  document.documentElement.setAttribute('data-theme', t);
  $('themeToggle').textContent = t==='dark' ? '☾ DARK' : '☀ LIGHT';
}}
function setMood(m) {{
  state.mood = m;
  document.documentElement.setAttribute('data-mood', m);
  document.querySelectorAll('#moodDock .mood-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.mood===m));
}}

// ─── HELPERS ─────────────────────────────────────────────────────────────────
function lookup(arr, name, field) {{
  return arr.find(d => d.driver_name===name)?.[field] ?? null;
}}

// ─── DRIVERS VIEW (Q1-Q5) ────────────────────────────────────────────────────
function buildDriverRows() {{
  const d = yd();
  const wins    = d ? d.q1_driver_wins   : F1_DATA.q1_driver_wins;
  const pods    = d ? d.q2_podiums       : F1_DATA.q2_podiums;
  const pts     = d ? d.q3_avg_points    : F1_DATA.q3_avg_points;
  const dnf     = d ? d.q4_dnf_rate      : F1_DATA.q4_dnf_rate;
  const wr      = d ? d.q5_win_rate      : F1_DATA.q5_win_rate;

  return wins.map(w => ({{
    name:    w.driver_name,
    wins:    w.total_race_wins,
    win_pct: lookup(wr,  w.driver_name,'win_pct')  ?? null,
    podiums: lookup(pods,w.driver_name,'total_podiums') ?? null,
    avg_pts: lookup(pts, w.driver_name,'avg_points') ?? null,
    dnf_pct: lookup(dnf, w.driver_name,'dnf_pct')  ?? null,
    team:    DRIVER_TEAM[w.driver_name] || '',
  }}));
}}

function sortDrivers(rows) {{
  const k = state.driverSort;
  return [...rows].sort((a,b) => {{
    const va = a[k]!=null ? a[k] : -999;
    const vb = b[k]!=null ? b[k] : -999;
    return vb - va;
  }});
}}

function renderDrivers() {{
  const yearLabel = isYear() ? ` · ${{state.year}}` : ' · Modern Era';
  $('driversTitle').textContent = 'Driver Stats' + yearLabel;

  const rows = sortDrivers(buildDriverRows());
  if (!rows.length) {{ $('driversTable').innerHTML = '<div class="empty-state">No data for this season</div>'; return; }}

  const topVal = rows[0]?.[state.driverSort];
  $('driversTable').innerHTML = rows.map((d,i) => {{
    const color  = TEAM_COLOR[d.team]||'#888';
    const isTop  = d[state.driverSort]===topVal && topVal!=null;
    const fmt = (v,suffix='') => v!=null ? v+suffix : '-';
    return `<div class="driver-stats-row">
      <div class="d-pos">${{pad(i+1)}}</div>
      <div class="d-name">${{d.name}}</div>
      <div class="d-team"><div class="team-dot" style="background:${{color}}"></div><span class="team-label">${{d.team}}</span></div>
      <div class="d-num${{state.driverSort==='wins'&&isTop?' highlight':''}}">${{d.wins}}</div>
      <div class="d-num${{state.driverSort==='win_pct'&&isTop?' highlight':''}}">${{fmt(d.win_pct,'%')}}</div>
      <div class="d-num${{state.driverSort==='podiums'&&isTop?' highlight':''}}">${{fmt(d.podiums)}}</div>
      <div class="d-num${{state.driverSort==='avg_pts'&&isTop?' highlight':''}}">${{fmt(d.avg_pts)}}</div>
      <div class="d-num${{state.driverSort==='dnf_pct'&&isTop?' highlight':''}}">${{fmt(d.dnf_pct,'%')}}</div>
    </div>`;
  }}).join('');

  document.querySelectorAll('.th[data-sort]').forEach(th =>
    th.classList.toggle('active', th.dataset.sort===state.driverSort));
}}

document.querySelectorAll('.th[data-sort]').forEach(th => {{
  th.addEventListener('click', () => {{ state.driverSort=th.dataset.sort; renderDrivers(); }});
}});

// ─── CONSTRUCTORS VIEW (Q6-Q8) ───────────────────────────────────────────────
function initConstructorCharts() {{
  if (chartConstructorSeason) return;
  const TOP = ['Mercedes','Red Bull','Ferrari','McLaren'];
  const COLORS = {{'Mercedes':'#27F4D2','Red Bull':'#5E8FE6','Ferrari':'#FF2D4B','McLaren':'#FF8000','Others':'#444'}};

  if (isYear()) {{
    // ─ Single year: simple bar by constructor ─
    const yr = +state.year;
    const wins = F1_DATA.q6_constructor_season_wins
      .filter(d => d.year===yr)
      .sort((a,b) => b.total_wins-a.total_wins);

    $('conChartTitle').textContent = `Race Wins · ${{state.year}}`;
    $('conChartSub').textContent  = 'Q6: wins per constructor';

    const ctx = $('chartConstructorSeason').getContext('2d');
    chartConstructorSeason = new Chart(ctx, {{
      type:'bar',
      data:{{
        labels: wins.map(d=>d.constructor),
        datasets:[{{
          data: wins.map(d=>d.total_wins),
          backgroundColor: wins.map(d=>TEAM_COLOR[d.constructor]||'#5E8FE6'),
          borderWidth:0, borderRadius:4,
        }}],
      }},
      options:{{
        responsive:true, maintainAspectRatio:false,
        plugins:{{ legend:{{display:false}}, tooltip:{{callbacks:{{label:c=>` ${{c.raw}} wins`}}}} }},
        scales:{{
          x:{{grid:{{display:false}},ticks:{{color:'#555',font:{{size:11}}}}}},
          y:{{grid:{{color:'rgba(255,255,255,.06)'}},ticks:{{color:'#555',font:{{size:11}},stepSize:1}}}},
        }},
      }},
    }});

    // Year standings
    const yr_st = F1_DATA.q7_constructor_standings.filter(d=>d.year===yr).sort((a,b)=>a.final_position-b.final_position);
    $('conStandingsTitle').textContent = `${{state.year}} Championship Standings`;
    const maxP = yr_st[0]?.final_points||1;
    $('constructorStandingsTable').innerHTML = yr_st.map((c,i)=>`
      <div class="con-row">
        <div class="con-pos">${{pad(i+1)}}</div>
        <div class="con-name-wrap"><div class="con-accent" style="background:${{TEAM_COLOR[c.constructor]||'#888'}}"></div><span class="con-name">${{c.constructor}}</span></div>
        <div class="bar-track"><div class="bar-fill" style="width:${{(c.final_points/maxP*100).toFixed(1)}}%;background:${{TEAM_COLOR[c.constructor]||'#888'}}"></div></div>
        <div class="con-stat">${{c.final_points}}</div>
      </div>`).join('');

    // Year dominance: all constructors with wins
    const yr_dom = F1_DATA.q8_constructor_dominance.filter(d=>d.year===yr).sort((a,b)=>b.win_pct-a.win_pct);
    $('conDomTitle').textContent = `${{state.year}} Win %`;
    $('constructorDominanceTable').innerHTML = `<table class="data-table">
      <thead><tr><th>#</th><th>TEAM</th><th>WINS</th><th>WIN%</th></tr></thead><tbody>`+
      yr_dom.map((c,i)=>`<tr>
        <td>${{pad(i+1)}}</td>
        <td><span style="display:inline-flex;align-items:center;gap:6px"><span style="width:8px;height:8px;border-radius:50%;background:${{TEAM_COLOR[c.constructor]||'#888'}};display:inline-block"></span>${{c.constructor}}</span></td>
        <td>${{c.total_wins}}</td>
        <td class="accent-val">${{c.win_pct}}%</td>
      </tr>`).join('')+'</tbody></table>';

  }} else {{
    // ─ All years: stacked bar ─
    $('conChartTitle').textContent = 'Race Wins by Season';
    $('conChartSub').textContent   = 'Q6: wins per constructor per year';
    const years = [...new Set(F1_DATA.q6_constructor_season_wins.map(d=>d.year))].sort((a,b)=>a-b);
    const datasets = [...TOP,'Others'].map(team=>{{
      const color = COLORS[team];
      return {{
        label: team, backgroundColor: color,
        data: years.map(yr=>{{
          const yd2 = F1_DATA.q6_constructor_season_wins.filter(d=>d.year===yr);
          if (team==='Others') return yd2.filter(d=>!TOP.includes(d.constructor)).reduce((s,d)=>s+d.total_wins,0);
          return yd2.find(d=>d.constructor===team)?.total_wins||0;
        }}),
        borderWidth:0,
      }};
    }});
    const ctx = $('chartConstructorSeason').getContext('2d');
    chartConstructorSeason = new Chart(ctx,{{
      type:'bar',
      data:{{labels:years,datasets}},
      options:{{
        responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{position:'top',labels:{{color:'#888',boxWidth:10,font:{{size:11,family:"'JetBrains Mono'"}}}}}}}},
        scales:{{
          x:{{stacked:true,grid:{{display:false}},ticks:{{color:'#555',font:{{size:11}}}}}},
          y:{{stacked:true,grid:{{color:'rgba(255,255,255,.06)'}},ticks:{{color:'#555',font:{{size:11}}}}}},
        }},
      }},
    }});

    // 2024 standings
    const latest = Math.max(...F1_DATA.q7_constructor_standings.map(d=>d.year));
    const yr_st = F1_DATA.q7_constructor_standings.filter(d=>d.year===latest).sort((a,b)=>a.final_position-b.final_position);
    $('conStandingsTitle').textContent = `${{latest}} Championship Standings`;
    const maxP = yr_st[0]?.final_points||1;
    $('constructorStandingsTable').innerHTML = yr_st.map((c,i)=>`
      <div class="con-row">
        <div class="con-pos">${{pad(i+1)}}</div>
        <div class="con-name-wrap"><div class="con-accent" style="background:${{TEAM_COLOR[c.constructor]||'#888'}}"></div><span class="con-name">${{c.constructor}}</span></div>
        <div class="bar-track"><div class="bar-fill" style="width:${{(c.final_points/maxP*100).toFixed(1)}}%;background:${{TEAM_COLOR[c.constructor]||'#888'}}"></div></div>
        <div class="con-stat">${{c.final_points}}</div>
      </div>`).join('');

    // Dominance: top per season
    const seasons = [...new Set(F1_DATA.q8_constructor_dominance.map(d=>d.year))].sort((a,b)=>b-a);
    $('conDomTitle').textContent = 'Season Dominance';
    $('constructorDominanceTable').innerHTML = `<table class="data-table">
      <thead><tr><th>YEAR</th><th>TEAM</th><th>WINS</th><th>WIN%</th></tr></thead><tbody>`+
      seasons.map(yr=>{{
        const top = F1_DATA.q8_constructor_dominance.find(d=>d.year===yr);
        if(!top) return '';
        return `<tr>
          <td>${{yr}}</td>
          <td><span style="display:inline-flex;align-items:center;gap:6px"><span style="width:8px;height:8px;border-radius:50%;background:${{TEAM_COLOR[top.constructor]||'#888'}};display:inline-block"></span>${{top.constructor}}</span></td>
          <td>${{top.total_wins}}</td>
          <td class="accent-val">${{top.win_pct}}%</td>
        </tr>`;
      }}).join('')+'</tbody></table>';
  }}
}}

// ─── QUALIFYING VIEW (Q9-Q11) ────────────────────────────────────────────────
let q9Sort = 'avg_pos_change';

function renderQualifying() {{
  const d   = yd();
  const q9  = d ? d.q9_grid_vs_finish   : F1_DATA.q9_grid_vs_finish;
  const q11 = d ? d.q11_pole_conversion : F1_DATA.q11_pole_conversion;
  const q10_raw = F1_DATA.q10_biggest_gains;
  const q10 = isYear() ? q10_raw.filter(d2=>String(d2.race_year)===state.year) : q10_raw;
  const yearSuffix = isYear() ? ` · ${{state.year}}` : ' · min 30 races';

  $('q9Sub').textContent  = `Q9: avg positions gained${{isYear() ? ' · '+state.year : ' · min 30 races'}}`;
  $('q10Title').textContent = `Biggest Gains${{isYear()?' · '+state.year:''}}`;
  $('q10Sub').textContent   = `Q10: ${{q10.length}} results`;
  $('q11Sub').textContent   = `Q11: % of poles converted${{isYear()?' · '+state.year:' · min 5 poles'}}`;

  // Q9 table
  const sorted9 = [...q9].sort((a,b)=>b[q9Sort]-a[q9Sort]);
  const tbody = $('gridFinishTable').querySelector('tbody');
  tbody.innerHTML = sorted9.length ? sorted9.map((d2,i)=>`<tr>
    <td>${{pad(i+1)}}</td>
    <td>${{d2.driver_name}}</td>
    <td>${{d2.avg_start_pos}}</td>
    <td>${{d2.avg_end_pos}}</td>
    <td class="${{d2.avg_pos_change>0?'accent-val':d2.avg_pos_change<0?'muted-val':''}}">${{d2.avg_pos_change>0?'+':''}}${{d2.avg_pos_change}}</td>
    <td>${{d2.total_races}}</td>
  </tr>`).join('') : '<tr><td colspan="6"><div class="empty-state">No data</div></td></tr>';

  // Q10 biggest gains
  $('biggestGainsList').innerHTML = q10.length ? q10.map((d2,i)=>`
    <div class="gain-row">
      <div class="gain-idx">${{pad(i+1)}}</div>
      <div>
        <div class="gain-driver">${{d2.driver_name}}</div>
        <div class="gain-race">${{d2.race_name.replace('Grand Prix','GP')}} · ${{d2.race_year}}</div>
      </div>
      <div class="gain-arrow">P${{d2.start_position}} → P${{d2.finish_position}}</div>
      <div class="gain-positions">+${{d2.positions_gained}}</div>
    </div>`).join('') : '<div class="empty-state">No data for this season</div>';

  // Q11 pole conversion
  $('poleConvTable').querySelector('tbody').innerHTML = q11.length ? q11.map((d2,i)=>`<tr>
    <td>${{pad(i+1)}}</td>
    <td>${{d2.driver_name}}</td>
    <td>${{d2.total_poles}}</td>
    <td>${{d2.poles_converted}}</td>
    <td class="accent-val">${{d2.conv_rate}}%</td>
  </tr>`).join('') : '<tr><td colspan="5"><div class="empty-state">No data</div></td></tr>';
}}

// Q9 sort cycle
$('q9SortBtn').addEventListener('click', ()=>{{
  const keys = ['avg_pos_change','avg_start_pos','avg_end_pos'];
  const labels = {{avg_pos_change:'POS GAINED',avg_start_pos:'START POS',avg_end_pos:'FINISH POS'}};
  q9Sort = keys[(keys.indexOf(q9Sort)+1)%keys.length];
  $('q9SortBtn').textContent = 'SORT: '+labels[q9Sort]+' ▾';
  renderQualifying();
}});

// ─── STRATEGY VIEW (Q12-Q13) ─────────────────────────────────────────────────
function initStrategyCharts() {{
  if (chartPitStop) return;
  const d   = yd();
  const q12 = d ? d.q12_pit_duration   : F1_DATA.q12_pit_duration;
  const q13 = d ? d.q13_stops_vs_finish: F1_DATA.q13_stops_vs_finish;
  const yearSfx = isYear() ? ' · '+state.year : '';

  $('q12Sub').textContent = `Q12: seconds · fastest first${{yearSfx}}`;
  $('q13Sub').textContent = `Q13: avg finish by stops${{yearSfx}}`;

  const ctx = $('chartPitStop').getContext('2d');
  chartPitStop = new Chart(ctx,{{
    type:'bar',
    data:{{
      labels: q12.map(d2=>d2.constructor),
      datasets:[{{
        data: q12.map(d2=>d2.avg_pit_stop),
        backgroundColor: q12.map(d2=>TEAM_COLOR[d2.constructor]||'#5E8FE6'),
        borderWidth:0, borderRadius:3,
      }}],
    }},
    options:{{
      indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>` ${{c.raw}}s`}}}}}},
      scales:{{
        x:{{
          min: q12.length ? Math.min(...q12.map(d2=>d2.avg_pit_stop))-1 : 0,
          grid:{{color:'rgba(255,255,255,.06)'}},ticks:{{color:'#555',font:{{size:11}},callback:v=>v+'s'}},
        }},
        y:{{grid:{{display:false}},ticks:{{color:'#aaa',font:{{size:11}}}}}},
      }},
    }},
  }});

  $('stopsFinishTable').querySelector('tbody').innerHTML = q13.length ? q13.map((d2,i)=>`<tr>
    <td>${{pad(i+1)}}</td>
    <td>${{d2.stops}} stop${{d2.stops!==1?'s':''}}</td>
    <td class="accent-val">P${{d2.avg_finish_position}}</td>
    <td class="muted-val">${{d2.sample_size.toLocaleString()}} races</td>
  </tr>`).join('') : '<tr><td colspan="4"><div class="empty-state">No data</div></td></tr>';
}}

// ─── CHAMPIONSHIPS VIEW (Q14-Q15) ────────────────────────────────────────────
function renderChampionshipGaps() {{
  const q14 = isYear()
    ? F1_DATA.q14_championship_gaps.filter(d=>String(d.year)===state.year)
    : [...F1_DATA.q14_championship_gaps].reverse();
  $('q14Title').textContent = isYear() ? `${{state.year}} Championship` : 'Championship Points Gap';
  const maxP = Math.max(...F1_DATA.q14_championship_gaps.map(d=>d.winner_points));
  $('champGapsList').innerHTML = q14.map(d=>{{
    const tight = d.points_gap <= 20;
    const wW = (d.winner_points/maxP*100).toFixed(1);
    const rW = (d.runner_up_points/maxP*100).toFixed(1);
    return `<div class="champ-row">
      <div class="champ-year">${{d.year}}</div>
      <div class="champ-bars">
        <div class="champ-bar-w" style="width:${{wW}}%;background:${{tight?'#E10600':'#333'}}">
          ${{d.winner.split(' ').pop()}} · ${{d.winner_points}}
        </div>
        <div class="champ-bar-r" style="left:${{wW}}%;width:${{Math.max(rW-wW,0).toFixed(1)}}%">
          ${{d.runner_up.split(' ').pop()}}
        </div>
      </div>
      <div class="champ-gap ${{tight?'tight':''}}">${{tight?'🔥':''}}+${{d.points_gap}}</div>
    </div>`;
  }}).join('') || '<div class="empty-state">No data</div>';
}}

function initChampionshipCharts() {{
  if (chart2021) return;
  const d = yd();
  const yearStr = isYear() ? state.year : '2021';
  const cumData = d ? d.q15_cumulative : F1_DATA.q15_cumulative_2021;

  $('q15Title').textContent = `${{yearStr}} Title Race · Round by Round`;
  $('q15Sub').textContent   = `Q15: cumulative points · top 5 championship finishers`;

  if (!cumData.length) {{
    $('chart2021').parentElement.innerHTML = '<div class="empty-state">No cumulative points data for this season</div>';
    return;
  }}

  const DRIVER_COLORS = {{
    'Max Verstappen':'#5E8FE6','Lewis Hamilton':'#27F4D2',
    'Valtteri Bottas':'#00b8a8','Sergio Pérez':'#3a5fad',
    'Sebastian Vettel':'#E10600','Charles Leclerc':'#FF6B6B',
    'Lando Norris':'#FF8000','Carlos Sainz':'#FFA040',
    'George Russell':'#1AC8A8','Fernando Alonso':'#3FC79A',
    'Oscar Piastri':'#FFB800',
  }};

  const drivers = [...new Set(cumData.map(d2=>d2.driver_name))];
  const rounds  = [...new Set(cumData.map(d2=>d2.race_round))].sort((a,b)=>a-b);
  const labels  = rounds.map(r=>cumData.find(d2=>d2.race_round===r)?.race_name.replace('Grand Prix','GP')||r);

  const datasets = drivers.map((driver,i)=>{{
    const colors = ['#5E8FE6','#27F4D2','#FF2D4B','#FF8000','#FFD700','#3FC79A','#FF6B6B','#9B59B6'];
    return {{
      label: driver.split(' ').pop(),
      data:  rounds.map(r=>cumData.find(d2=>d2.driver_name===driver&&d2.race_round===r)?.cumulative_points??null),
      borderColor: DRIVER_COLORS[driver]||colors[i%colors.length],
      backgroundColor:'transparent',
      borderWidth:2, tension:0.3, pointRadius:2, spanGaps:false,
    }};
  }});

  const ctx2 = $('chart2021').getContext('2d');
  chart2021 = new Chart(ctx2,{{
    type:'line',
    data:{{labels,datasets}},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{
        legend:{{position:'top',labels:{{color:'#888',boxWidth:10,font:{{size:11,family:"'JetBrains Mono'"}}}}}},
        tooltip:{{mode:'index',intersect:false}},
      }},
      scales:{{
        x:{{grid:{{display:false}},ticks:{{color:'#555',font:{{size:10}},maxRotation:45}}}},
        y:{{grid:{{color:'rgba(255,255,255,.06)'}},ticks:{{color:'#555',font:{{size:11}}}}}},
      }},
    }},
  }});
}}

// ─── CIRCUITS VIEW (Q16-Q17) ─────────────────────────────────────────────────
const COUNTRY_FLAG = {{
  'Australia':'🇦🇺','Austria':'🇦🇹','Azerbaijan':'🇦🇿','Bahrain':'🇧🇭','Belgium':'🇧🇪',
  'Brazil':'🇧🇷','Canada':'🇨🇦','China':'🇨🇳','France':'🇫🇷','Germany':'🇩🇪',
  'Hungary':'🇭🇺','India':'🇮🇳','Italy':'🇮🇹','Japan':'🇯🇵','Korea':'🇰🇷',
  'Mexico':'🇲🇽','Monaco':'🇲🇨','Netherlands':'🇳🇱','Portugal':'🇵🇹','Qatar':'🇶🇦',
  'Russia':'🇷🇺','Saudi Arabia':'🇸🇦','Singapore':'🇸🇬','Spain':'🇪🇸','Turkey':'🇹🇷',
  'UAE':'🇦🇪','UK':'🇬🇧','USA':'🇺🇸','Las Vegas':'🇺🇸','Miami':'🇺🇸',
}};

function renderCircuits() {{
  const d = yd();
  $('q16Sub').textContent  = isYear() ? `Q16: race winners · ${{state.year}}` : 'Q16: top driver per circuit · min 2 wins';
  $('q17Sub').textContent  = isYear() ? `Q17: home vs away · ${{state.year}}` : 'Q17: avg finish at home vs away · lower = better';

  if (isYear() && d) {{
    // ─ Single year: race-by-race results ─
    $('q16Title').textContent = `${{state.year}} Race Winners`;
    const winners = d.q16_race_winners;
    $('circuitGrid').innerHTML = '';
    const circuitList = document.createElement('div');
    circuitList.style.cssText = 'padding:12px 0';
    winners.forEach((w,i) => {{
      const flag = COUNTRY_FLAG[w.circuit_country]||'🏁';
      const row  = document.createElement('div');
      row.className = 'race-result-row';
      row.innerHTML = `
        <div class="rr-round">R${{i+1}}</div>
        <div class="rr-flag">${{flag}}</div>
        <div><div class="rr-race">${{w.race_name.replace('Grand Prix','GP')}}</div><div class="rr-country">${{w.circuit_country}}</div></div>
        <div class="rr-winner">${{w.driver_name}}</div>`;
      circuitList.appendChild(row);
    }});
    $('circuitGrid').appendChild(circuitList);
  }} else {{
    // ─ All years: dominance cards ─
    $('q16Title').textContent = 'Circuit Dominance';
    $('circuitGrid').innerHTML = F1_DATA.q16_circuit_dominance.map(c=>`
      <div class="circuit-card">
        <div class="cc-name">${{c.circuit_name}}</div>
        <div class="cc-country">${{COUNTRY_FLAG[c.circuit_country]||''}} ${{c.circuit_country}}</div>
        <div class="cc-driver">${{c.driver_name}}</div>
        <div class="cc-wins">${{c.wins}}</div>
        <div class="cc-wins-label">wins</div>
      </div>`).join('');
  }}

  // Q17 home advantage
  const q17 = d ? d.q17_home_advantage : F1_DATA.q17_home_advantage;
  const hbody = $('homeAdvTable').querySelector('tbody');
  hbody.innerHTML = q17.length ? q17.map((d2,i)=>`<tr>
    <td>${{pad(i+1)}}</td>
    <td>${{d2.driver_name}}</td>
    <td class="accent-val">P${{d2.avg_home_finish}}</td>
    <td class="muted-val">P${{d2.avg_away_finish}}</td>
    <td class="accent-val">+${{d2.home_advantage}}</td>
  </tr>`).join('') : '<tr><td colspan="5"><div class="empty-state">No home race data for this season</div></td></tr>';
}}

// ─── COMPARE VIEW ────────────────────────────────────────────────────────────
const ALL_DRIVERS = F1_DATA.q1_driver_wins.map(d=>d.driver_name);

function initCompareSelects() {{
  const opts = ALL_DRIVERS.map((name,i)=>`<option value="${{i}}">${{name.toUpperCase()}}</option>`).join('');
  $('selectA').innerHTML=opts; $('selectB').innerHTML=opts;
  $('selectA').value='0'; $('selectB').value='1';
}}

function getDriverStats(name) {{
  const d = yd();
  const wins  = d ? d.q1_driver_wins   : F1_DATA.q1_driver_wins;
  const pods  = d ? d.q2_podiums       : F1_DATA.q2_podiums;
  const poles = F1_DATA.q11_pole_conversion;  // only all-years for compare
  const wr    = d ? d.q5_win_rate      : F1_DATA.q5_win_rate;

  return {{
    wins:    lookup(wins, name,'total_race_wins')  || 0,
    podiums: lookup(pods, name,'total_podiums')    || 0,
    poles:   lookup(poles,name,'total_poles')      || 0,
    win_pct: lookup(wr,  name,'win_pct')           || 0,
  }};
}}

function renderCompare() {{
  const nameA = ALL_DRIVERS[+$('selectA').value];
  const nameB = ALL_DRIVERS[+$('selectB').value];
  const a = getDriverStats(nameA);
  const b = getDriverStats(nameB);

  const colorA = TEAM_COLOR[DRIVER_TEAM[nameA]]||'#5E8FE6';
  const colorB = TEAM_COLOR[DRIVER_TEAM[nameB]]||'#FF2D4B';

  $('cardA').style.borderTopColor=colorA; $('cardB').style.borderTopColor=colorB;
  $('nameA').textContent=nameA; $('nameB').textContent=nameB;
  $('ptsA').textContent=a.wins; $('ptsA').style.color=colorA;
  $('ptsB').textContent=b.wins; $('ptsB').style.color=colorB;
  $('compareYearLabel').textContent = isYear() ? `· ${{state.year}}` : '';

  const stats = [
    {{label:'WINS',    va:a.wins,    vb:b.wins,    lw:false}},
    {{label:'PODIUMS', va:a.podiums, vb:b.podiums, lw:false}},
    {{label:'WIN %',   va:a.win_pct, vb:b.win_pct, lw:false}},
    {{label:'POLES',   va:a.poles,   vb:b.poles,   lw:false}},
  ];
  $('statRows').innerHTML = stats.map(s=>{{
    const aW = s.va>s.vb, bW=s.vb>s.va;
    return `<div class="stat-row">
      <div class="stat-val ${{aW?'winner':''}}">${{s.va}}</div>
      <div class="stat-label">${{s.label}}</div>
      <div class="stat-val right ${{bW?'winner':''}}">${{s.vb}}</div>
    </div>`;
  }}).join('');
}}

// ─── EVENT WIRING ────────────────────────────────────────────────────────────
$('themeToggle').addEventListener('click', ()=>setTheme(state.theme==='dark'?'light':'dark'));
$('btnCompare').addEventListener('click', ()=>setView('compare'));
$('selectA').addEventListener('change', renderCompare);
$('selectB').addEventListener('change', renderCompare);
document.querySelectorAll('#viewChips .chip').forEach(c=>c.addEventListener('click',()=>setView(c.dataset.view)));
$('seasonSelect').addEventListener('change', e=>setYear(e.target.value));
document.querySelectorAll('#moodDock .mood-btn').forEach(b=>b.addEventListener('click',()=>setMood(b.dataset.mood)));

// ─── BOOT ────────────────────────────────────────────────────────────────────
Chart.defaults.color='#666';
Chart.defaults.borderColor='rgba(255,255,255,.06)';
Chart.defaults.font.family="'JetBrains Mono', monospace";

initCompareSelects();
updateHero();
renderDrivers();
renderQualifying();
renderCircuits();
renderCompare();
</script>
</body>
</html>"""

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(HTML)

size = os.path.getsize(OUT_PATH)
print(f"Built {OUT_PATH}  ({size/1024:.0f} KB)")
