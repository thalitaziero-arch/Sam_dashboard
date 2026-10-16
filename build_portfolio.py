#!/usr/bin/env python3
"""Builds sam_brady_portfolio.html — the public-facing version of the deck.

Public slides (anyone, phone-friendly): Hero, Overview, Career Record,
Defensive Profile, Attacking Profile.
Behind the PIN in My Area: the CURRENT season (2026/27), the Training Log, and
an Archive of finished seasons (Summer 25/26, Winter 2026, Soccer 2026).

Data lives in data/ (git-ignored on purpose: it is the private detail):
  data/archive.json          finished seasons: futsal rows + soccer rows
  data/season_2026_27.json   the live season, per competition, per round
  data/logo.b64              TZR wordmark
Every public total is computed from those files, so adding a round to
season_2026_27.json and re-running this script updates the whole page.

Shares CSS with build_v2.py by reading the pieces it exports. build_v2.py stays
untouched as the reference version.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data"
OUT = HERE / "sam_brady_portfolio.html"

# analysis images + training log come straight from the dashboard file in the repo
_dash = (HERE / "tzr_sam_dashboard.html").read_text()


def _dash_var(var):
    si = _dash.index(f"let {var}")
    m = re.search(r"\)\s*\|\|\s*([\[\{])", _dash[si:si + 400])
    s0 = si + m.start(1)
    close = "];\n" if m.group(1) == "[" else "};\n"
    return json.loads(_dash[s0:_dash.index(close, s0) + 1])


A = {v: _dash_var(v) for v in ["coachImgData", "coachCapsData", "wImgByGame", "wCapsByGame"]}
A["logo"] = (DATA / "logo.b64").read_text().strip()
TRAINING = json.loads(re.search(r"let TRAINING = (\[.*?\]);", _dash, re.DOTALL).group(1))
ARCHIVE = json.load(open(DATA / "archive.json"))
CURRENT = json.load(open(DATA / "season_2026_27.json"))
PLAYLIST = "https://www.youtube.com/playlist?list=PLCiTolkeqpjdu0zgk4ok0wzRsKHx8I0dH"

# ---- reuse the styling and data blocks from the v2 builder ----
_v2 = (HERE / "build_v2.py").read_text()


def _grab(pattern):
    return re.search(pattern, _v2, re.DOTALL).group(1)


CSS = _grab(r'CSS = """(.*?)"""')
STAT_ROW_CSS = _grab(r'STAT_ROW_CSS = """(.*?)"""')
JS_DATA = _grab(r'JS_DATA = """(.*?)"""')

ARCS = _grab(r"ARCS = '''(.*?)'''")
WAVES = _grab(r"WAVES = '''(.*?)'''")

WINTER_GAMES = ["Internationale", "Perth United", "SPA"]


def fig(src, cap):
    return f'<figure class="an-fig"><img src="{src}" alt="{cap}"><figcaption>{cap}</figcaption></figure>'


summer_figs = "".join(fig(s, c) for s, c in zip(A["coachImgData"], A["coachCapsData"]) if s)

winter_figs = ""
for i, g in enumerate(WINTER_GAMES):
    imgs = A["wImgByGame"].get(f"g{i}", [])
    caps = A["wCapsByGame"].get(f"g{i}", [])
    winter_figs += (f'<h3 class="an-head">{g}</h3><div class="an-grid">'
                    + "".join(fig(s, c) for s, c in zip(imgs, caps) if s) + "</div>")


def hl(k, big, sub, rows):
    r = "".join(f'<span class="hl-row"><b>{v}</b>{lbl}</span>' for v, lbl in rows)
    return (f'<div class="hl"><div class="hl-k">{k}</div><span class="hl-big">{big}</span>'
            f'<span class="hl-sub">{sub}</span><div class="hl-rows">{r}</div></div>')


# ------------------------------------------------------------ totals (computed)
# Nothing below is typed by hand: every public number is derived from the data
# files, so a new round in season_2026_27.json flows through the whole page.
def tot(rows, key):
    return sum(r.get(key, 0) for r in rows)


def per(n, d, nd=1):
    return f"{n / d:.{nd}f}" if d else "—"


ARCH_FUTSAL = ARCHIVE["futsal"]
ARCH_SOCCER = ARCHIVE["soccer"]
SUMMER = [f for f in ARCH_FUTSAL if f["s"] == "Summer"]
WINTER = [f for f in ARCH_FUTSAL if f["s"] == "Winter"]
CUR_GAMES = [g for c in CURRENT["competitions"] for g in c["games"]]
FUTSAL_ALL = ARCH_FUTSAL + CUR_GAMES

N_FUT, N_SOC = len(FUTSAL_ALL), len(ARCH_SOCCER)
FUT_G, FUT_A = tot(FUTSAL_ALL, "goal"), tot(FUTSAL_ALL, "assist")
FUT_INT, FUT_REC, FUT_LOST = tot(FUTSAL_ALL, "int"), tot(FUTSAL_ALL, "rec"), tot(FUTSAL_ALL, "lost")
FUT_SHOT, FUT_SHOT_OT, FUT_PASS = tot(FUTSAL_ALL, "shot"), tot(FUTSAL_ALL, "shotOT"), tot(FUTSAL_ALL, "pass")
SOC_G, SOC_A = tot(ARCH_SOCCER, "goal"), tot(ARCH_SOCCER, "assist")
SOC_INT, SOC_MIN = tot(ARCH_SOCCER, "intercept"), tot(ARCH_SOCCER, "min")
SOC_REC = tot(ARCH_SOCCER, "recOwn") + tot(ARCH_SOCCER, "recOpp")
SOC_DW, SOC_DT = tot(ARCH_SOCCER, "duelW"), tot(ARCH_SOCCER, "duelT")
SOC_SHOT, SOC_SHOT_OT = tot(ARCH_SOCCER, "shot"), tot(ARCH_SOCCER, "shotOT")
WIN_G, WIN_SHOT_OT = tot(WINTER, "goal"), tot(WINTER, "shotOT")
# assists split by season, e.g. "6+2" (+ a third term once 2026/27 has data)
_parts = [tot(SUMMER, "assist"), tot(WINTER, "assist")] + ([tot(CUR_GAMES, "assist")] if CUR_GAMES else [])
FUT_ASSIST_SPLIT = "+".join(str(p) for p in _parts)
FUT_ASSIST_LABEL = "summer + winter" + (" + 26/27" if CUR_GAMES else "")


def futsal_cards(rows, creation_third, defensive_third):
    """The three Finishing / Creation / Defensive cards for a set of futsal games."""
    g, ot, shot = tot(rows, "goal"), tot(rows, "shotOT"), tot(rows, "shot")
    rec, it = tot(rows, "rec"), tot(rows, "int")
    return (
        hl("Finishing", per(ot, g), "shots on target per goal",
           [(shot, "total shots"), (ot, "on target"), (g, "goals")])
        + hl("Creation", tot(rows, "assist"), "assists",
             [(tot(rows, "pass"), "accurate passes"),
              (round(tot(rows, "pass") / len(rows)), "passes / game"), creation_third])
        + hl("Defensive", rec + it, "recoveries + intercepts",
             [(rec, "recoveries"), (it, "interceptions"), defensive_third])
    )


SUMMER_CARDS = futsal_cards(SUMMER, (round(tot(SUMMER, "min")), "minutes"),
                            (tot(SUMMER, "lost"), "losses"))
WINTER_CARDS = futsal_cards(WINTER, (tot(WINTER, "lost"), "losses"),
                            (tot(WINTER, "block"), "blocks"))


# ---------------------------------------------------------------- career rows
# One table for both codes. Only columns that exist for every row, so there
# are no empty dashes: minutes/starts differ between soccer and futsal and
# live in the summary cards instead.
# (season, code, club, competition, position, apps, goals); club None = unknown
CAREER = []
for _c in CURRENT["competitions"]:
    _gm = _c["games"]
    # club not confirmed yet -> the competition itself is the headline of the row
    CAREER.append((
        "2026/27", "Futsal", _c["club"] or _c["name"],
        f"{_c['name']} · Summer" if _c["club"] else CURRENT["label"],
        "Fixo · Ala" if _c["club"] else "—",
        len(_gm) if _gm else "", tot(_gm, "goal") if _gm else ""))
CAREER += [
    ("2026",    "Soccer", "Fremantle City",  "WA NPL Women",       "LAMF · LAMR", N_SOC, SOC_G),
    ("2026",    "Futsal", "Cockburn Wolves", "Supa-Liga · Winter", "Fixo · Ala",  len(WINTER), WIN_G),
    ("2025/26", "Futsal", "Cockburn Wolves", "Supa-Liga · Summer", "Fixo · Ala",  len(SUMMER), tot(SUMMER, "goal")),
]
_NO_CLUB = {c["name"] for c in CURRENT["competitions"] if not c["club"]}
CAREER_SEASONS = len({r[0] for r in CAREER})
CAREER_CLUBS = len({r[2] for r in CAREER if r[2] not in _NO_CLUB})


def career_rows(rows):
    out = ""
    for season, code, club, comp, pos, apps, goals in rows:
        cls = "soccer" if code == "Soccer" else "futsal"
        # Rows with no stats yet get one quiet note instead of empty dashes.
        if apps == "":
            stats = '<span class="c-soon">Season in progress</span>'
        else:
            stats = (f'<span class="c-v" data-k="Apps">{apps}</span>'
                     f'<span class="c-v hot" data-k="Goals">{goals}</span>')
        out += ('<div class="c-row">'
                f'<span class="c-season">{season}</span>'
                f'<span class="c-code {cls}">{code}</span>'
                f'<span class="c-club">{club}<span class="c-comp">{comp}</span></span>'
                f'<span class="c-pos">{"" if pos == "—" else pos}</span>'
                f'{stats}'
                '</div>')
    return out


CAREER_HEAD = ('<div class="c-row head"><span>Season</span><span>Code</span><span>Club</span>'
               '<span>Position</span><span>Apps</span><span>Goals</span></div>')

# ------------------------------------------------------------ honours
# Year -> list of (code, headline, detail, is_major)
HONOURS = [
    ("2026", [
        ("Soccer", "Fremantle FC — WNPL", "Signed as a paid contracted player", True),
        ("Futsal", "FAF Women's team — Association side", "Federation of Australian Futsal · won the Indonesian Cup in Surabaya (June)", True),
        ("Futsal", "National Futsal Championships — Gold Coast", "Open Women's team (January)", False),
    ]),
    ("2025", [
        ("Futsal", "Cockburn Wolves — WSFL", "Returned to the club", False),
        ("Soccer", "WNPL with NTC (Football West)", "U18s squad", False),
    ]),
    ("2024", [
        ("Futsal", "AFA U16 — Captain", "Australian Futsal Association side, selected from club championships for the "
         "International Futsal Alliance World Championships in Malaysia", True),
        ("Futsal", "Captain — Futsal WA U15 &amp; U16", "State teams", True),
        ("Futsal", "Futsal WA state teams — U15 &amp; U16", "Also named to play in the Women's Youth Team", False),
        ("Soccer", "NTC (Football West) U16s", "Playing up in the U21 women's grade", False),
        ("Soccer", "WA — National Youth Championships", "Selected to represent the state", False),
    ]),
    ("2023", [
        ("Futsal", "League MVP", "Women's B grade — Supa-Liga Summer Season 22/23", True),
    ]),
]


def honours_html():
    out = ""
    for year, items in HONOURS:
        rows = "".join(
            f'<div class="h-item{" major" if major else ""}">'
            f'<span class="h-top"><span class="c-code {code.lower()}">{code}</span>'
            f'<span class="h-head">{head}</span></span>'
            + (f'<span class="h-det">{det}</span>' if det else "")
            + "</div>"
            for code, head, det, major in items
        )
        out += f'<div class="h-year"><span class="h-y">{year}</span><div class="h-items">{rows}</div></div>'
    return out


# ------------------------------------------------- split-by-code helper
def split_block(soccer_rows, futsal_rows):
    """Two side-by-side cards so soccer and futsal numbers are never mixed."""
    def card(code, games, rows):
        cls = "soccer" if code == "Soccer" else "futsal"
        body = "".join(
            f'<div class="sp-row"><span class="sp-v">{v}</span>'
            f'<span class="sp-l">{lbl}</span></div>' for v, lbl in rows)
        return (f'<div class="sp-card"><div class="sp-head">'
                f'<span class="c-code {cls}">{code}</span>'
                f'<span class="sp-games">{games}</span></div>{body}</div>')
    return ('<div class="split">'
            + card("Soccer", f"{N_SOC} games", soccer_rows)
            + card("Futsal", f"{N_FUT} games", futsal_rows)
            + '</div>')

# ---------------------------------------------------------------- extra CSS
EXTRA_CSS = """
/* CAREER RECORD */
.c-table{margin-top:24px;border-top:2px solid var(--ink)}
.c-row{display:grid;grid-template-columns:.75fr .7fr 1.9fr 1.1fr .55fr .55fr;
  gap:14px;align-items:center;padding:15px 0;border-bottom:1px solid var(--line)}
.c-code{font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;
  padding:5px 9px;text-align:center;white-space:nowrap}
.c-code.soccer{background:var(--ink);color:#fff}
.dark .c-code.soccer{background:transparent;color:#fff;box-shadow:inset 0 0 0 1px rgba(255,255,255,.45)}
.c-code.futsal{background:var(--orange);color:#fff}
.c-row.head{font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;
  color:var(--grey);padding:10px 0;border-bottom:1px solid var(--ink)}
.c-season{font-family:'Anton',sans-serif;font-size:19px}
.c-club{font-size:15px;font-weight:700}
.c-comp{display:block;font-size:11.5px;color:var(--grey);font-weight:400}
.c-pos{font-size:12.5px;color:var(--steel);letter-spacing:.04em}
.c-v{font-family:'Anton',sans-serif;font-size:19px}
.c-v.hot{color:var(--orange)}
.c-soon{grid-column:span 2;font-size:12px;color:var(--grey);font-style:italic}
.c-tot{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:26px}
.c-tot .t{border:1px solid var(--line);background:var(--paper);padding:18px 20px 16px}
.bone .c-tot .t{background:#FAFAF8}
.c-tot .tk{font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:var(--grey)}
.c-tot .tv{font-family:'Anton',sans-serif;font-size:34px;color:var(--orange);line-height:1.1;margin-top:5px;display:block}

.rank-note{display:flex;align-items:center;gap:12px;margin-top:26px;
  font-size:12px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;
  color:rgba(255,255,255,.5)}

/* SPLIT BY CODE */
.split{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:30px}
.sp-card{border:1px solid var(--line-dark);padding:20px 22px 8px}
.sp-head{display:flex;align-items:center;gap:12px;padding-bottom:14px;margin-bottom:6px;
  border-bottom:1px solid var(--line-dark)}
.sp-games{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;
  color:rgba(255,255,255,.45)}
.sp-row{display:flex;align-items:baseline;gap:12px;padding:11px 0;
  border-bottom:1px solid rgba(255,255,255,.07)}
.sp-row:last-child{border-bottom:none}
.sp-v{font-family:'Anton',sans-serif;font-size:24px;color:var(--orange);min-width:74px}
.sp-l{font-size:13.5px;color:rgba(255,255,255,.6);line-height:1.35}
@media(max-width:700px){.split{grid-template-columns:1fr;gap:12px}}

/* HONOURS TIMELINE */
.honours{margin-top:26px;border-top:2px solid var(--ink)}
.h-year{display:grid;grid-template-columns:110px 1fr;gap:24px;padding:24px 0;
  border-bottom:1px solid var(--line)}
.h-year:last-child{border-bottom:none}
.h-y{font-family:'Anton',sans-serif;font-size:34px;color:var(--orange);line-height:1}
.h-items{display:flex;flex-direction:column;gap:14px}
.h-item{padding-left:18px;position:relative}
.h-item::before{content:"";position:absolute;left:0;top:8px;width:8px;height:8px;
  background:var(--line);border-radius:50%}
.h-item.major::before{background:var(--orange)}
.h-top{display:flex;align-items:baseline;gap:11px;flex-wrap:wrap}
.h-head{font-size:15.5px;font-weight:700;line-height:1.35}
.h-item.major .h-head{font-size:16.5px}
.h-det{display:block;font-size:13.5px;color:var(--steel);margin-top:3px;line-height:1.45}

/* HIGHLIGHT BADGES */
.badges{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:34px}
.badge{border:1px solid var(--line-dark);padding:18px 18px 20px}
.badge span{display:block}
.badge .b-k{font-size:10px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;
  color:var(--orange);margin-bottom:9px}
.badge .b-v{font-family:'Anton',sans-serif;font-size:19px;color:#fff;line-height:1.15}
.badge .b-u{font-size:12px;color:rgba(255,255,255,.5);margin-top:5px;line-height:1.4}

@media(max-width:900px){
  .h-year{grid-template-columns:1fr;gap:12px;padding:20px 0}
  .h-y{font-size:28px}
  .badges{grid-template-columns:1fr 1fr;gap:10px}
}

/* MY AREA SUB-TABS */
.sub-tabs{display:flex;gap:8px;flex-wrap:wrap;margin:22px 0 4px}
.sub-tab{background:none;border:1px solid var(--line);color:var(--steel);
  font-family:'Archivo',sans-serif;font-size:11px;letter-spacing:.14em;text-transform:uppercase;
  font-weight:700;padding:9px 15px;cursor:pointer;transition:all .2s}
.sub-tab:hover{border-color:var(--orange);color:var(--orange)}
.sub-tab.on{background:var(--orange);border-color:var(--orange);color:#fff}
.sub-panel{display:none;padding-top:8px}
.sub-panel.on{display:block}

@media(max-width:900px){
  .c-tot{grid-template-columns:1fr 1fr;gap:12px}
}
"""


# --------------------------------------------------- private (encrypted)
# Everything below the PIN. Built as normal HTML here, then AES-GCM encrypted
# at the bottom of this file so it never ships readable. Training data rides
# along inside a JSON <script> tag so it is encrypted too.
PRIVATE_HTML = f"""<script type="application/json" id="training-data">__TRAINING_JSON__</script>
<script type="application/json" id="season-data">__SEASON_JSON__</script>
        <p class="lede">Hi Sam — everything from your sessions and seasons in one place.</p>

        <a class="yt-link" href="{PLAYLIST}" target="_blank" rel="noopener">
          <span class="yt-ico">&#9654;</span>
          <span>Full video playlist — match analysis (YouTube)</span>
        </a>

        <div class="sub-tabs">
          <button class="sub-tab on" data-p="p-current">2026/27</button>
          <button class="sub-tab" data-p="p-train">Training Log</button>
          <span class="sub-sep">Archive</span>
          <button class="sub-tab alt" data-p="p-summer">Summer 25/26</button>
          <button class="sub-tab alt" data-p="p-winter">Winter 2026</button>
          <button class="sub-tab alt" data-p="p-soccer">Soccer 2026</button>
        </div>

        <div class="sub-panel on" id="p-current">
          <div class="season-banner" id="cur-head"></div>
          <div id="cur-body"></div>
        </div>

        <div class="sub-panel" id="p-train"><div id="tlog"></div></div>

        <div class="sub-panel" id="p-summer">
          <div class="arch-note"><b>Archive</b> Summer 2025/26 · Supa-Liga · season complete</div>
          <div class="hl-grid">{SUMMER_CARDS}</div>
          <div class="tbl tbl-futsal" id="tbl-summer"></div>
          <div class="chart-grid">
            <div class="chart-box"><div class="ct">Goals &amp; assists per game</div><canvas id="su-ga"></canvas></div>
            <div class="chart-box"><div class="ct">Shots — total vs on target</div><canvas id="su-shot"></canvas></div>
          </div>
          <div class="sec-rule"><span>Match Analysis</span></div>
          <div class="an-grid">{summer_figs}</div>
        </div>

        <div class="sub-panel" id="p-winter">
          <div class="arch-note"><b>Archive</b> Winter 2026 · Supa-Liga · season complete</div>
          <div class="hl-grid">{WINTER_CARDS}</div>
          <div class="tbl tbl-futsal" id="tbl-winter"></div>
          <div class="chart-grid">
            <div class="chart-box"><div class="ct">Goals &amp; assists per game</div><canvas id="wi-ga"></canvas></div>
            <div class="chart-box"><div class="ct">Recoveries &amp; interceptions</div><canvas id="wi-def"></canvas></div>
          </div>
        </div>

        <div class="sub-panel" id="p-soccer">
          <div class="arch-note"><b>Archive</b> Soccer 2026 · Fremantle City · WA NPL Women · season complete</div>
          <div class="blk-grid" id="sm-totals"></div>
          <div class="chart-box" style="margin-top:20px"><div class="ct">Interceptions — avg per 5-match block</div><canvas id="sm-int"></canvas></div>
          <div class="chart-box" style="margin-top:16px"><div class="ct">Recoveries — avg per 5-match block</div><canvas id="sm-rec"></canvas></div>
          <div class="chart-box" style="margin-top:16px"><div class="ct">Minutes — avg per 5-match block</div><canvas id="sm-min"></canvas><div class="chart-note"><span><b>{per(SOC_MIN, N_SOC)}</b>average minutes / game</span><span><b>{SOC_MIN}</b>total minutes</span><span><b>{max(g["min"] for g in ARCH_SOCCER)}</b>longest match</span></div></div>
          <div class="ct" style="margin-top:26px">Best matches — interceptions</div>
          <div class="lead" id="sm-lead-int"></div>
          <div class="sec-rule"><span>Game by Game</span></div>
          <div class="tbl tbl-soccer" id="tbl-soccer"></div>
        </div>"""


# Current season + archive styling
EXTRA_CSS += """
.sub-sep{align-self:center;font-size:10px;letter-spacing:.2em;text-transform:uppercase;
  font-weight:700;color:var(--grey);padding:2px 6px 2px 14px;margin-left:6px;
  border-left:1px solid var(--line)}
.sub-tab.alt{background:var(--bone)}
.sub-tab.alt.on{background:var(--orange)}
.arch-note{display:flex;align-items:center;gap:12px;margin:22px 0 0;padding:11px 16px;
  background:var(--bone);border-left:3px solid var(--grey);font-size:12.5px;color:var(--steel)}
.arch-note b{font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--ink)}
.season-banner{display:flex;align-items:center;flex-wrap:wrap;gap:14px;margin-top:24px;
  padding:18px 22px;background:var(--ink);color:#fff}
.season-banner .sb-t{font-family:'Anton',sans-serif;font-size:26px;text-transform:uppercase;line-height:1}
.season-banner .sb-s{font-size:11px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;
  color:var(--orange);margin-left:auto}
.cur-block-title{font-size:11px;letter-spacing:.2em;text-transform:uppercase;font-weight:700;
  color:var(--steel);margin:30px 0 4px;display:flex;align-items:center;gap:10px}
.cur-block-title::before{content:"";width:19px;height:3px;background:var(--orange)}
.comp-head{display:flex;align-items:baseline;flex-wrap:wrap;gap:6px 14px;margin-top:34px;
  padding-bottom:12px;border-bottom:2px solid var(--ink)}
.comp-n{font-family:'Anton',sans-serif;font-size:28px;text-transform:uppercase;line-height:1}
.comp-c{font-size:13px;color:var(--steel);font-weight:600}
.comp-r{font-size:11px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;
  color:var(--grey);margin-left:auto}
.cur-empty{margin-top:16px;padding:26px 24px;border:1px dashed var(--line);background:#FAFAF8;
  color:var(--steel);font-size:14px;text-align:center}
@media(max-width:700px){
  .sub-sep{flex-basis:100%;border-left:none;margin:10px 0 0;padding:0}
  .season-banner .sb-s{margin-left:0;flex-basis:100%}
  .comp-r{margin-left:0;flex-basis:100%}
}
"""

# Career table stays tabular down to phone width, where it stacks into cards.
EXTRA_CSS += """
@media(max-width:700px){
  .c-row{grid-template-columns:1fr 1fr;gap:10px 12px;padding:18px 0}
  .c-row.head{display:none}
  .c-season{font-size:22px}
  .c-code{justify-self:start}
  .c-club{grid-column:1/-1}
  .c-pos{grid-column:1/-1;padding-bottom:4px}
  .c-v{font-size:20px}
  .c-v::after{content:attr(data-k);display:block;font-family:'Archivo',sans-serif;font-size:9px;
    font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--grey);margin-top:2px}
}
"""

# ---------------------------------------------------------------- slides
SLIDES = [
    # 1 · HERO
    ('dark hero-slide', ARCS, f"""<div class="wrap hero">
      <div class="hero-meta"><span>Sam Brady</span><span>2024 – 2026</span></div>
      <h1 class="display">SAM<br><em>BRADY</em></h1>
      <p class="origin">Perth · '08</p>
      <p class="strap">Performance Dashboard</p>
      <div class="clubs">
        <div class="club"><span class="club-k">Soccer · current club</span>
          <span class="club-n">Fremantle City</span><span class="club-c">NPLW</span>
          <span class="club-p">LAMF · LAMR</span></div>
        <div class="club"><span class="club-k">Futsal · current club</span>
          <span class="club-n">Cockburn Wolves</span><span class="club-c">Supa-Liga</span>
          <span class="club-p">Fixo · Ala</span></div>
      </div>
      <img src="{A['logo']}" alt="TZR Futsal Coaching" class="tzr-logo">
    </div>"""),

    # 2 · OVERVIEW
    ('dark', WAVES, f"""<div class="wrap">
      <div class="eyebrow">Career at a Glance</div>
      <h2 class="display">Combined Output</h2>
      <p class="lede">{N_FUT} futsal games and {N_SOC} soccer games tracked to date.</p>
      <div class="scoreboard">
        <div class="cell"><span class="num">{N_FUT + N_SOC}</span><span class="k">Total Games</span><span class="lbl">{N_FUT} futsal<br>{N_SOC} soccer</span></div>
        <div class="cell"><span class="num">{FUT_G + SOC_G}</span><span class="k">Goals</span><span class="lbl">{FUT_G} futsal<br>{SOC_G} soccer</span></div>
        <div class="cell"><span class="num">{FUT_A + SOC_A}</span><span class="k">Assists</span><span class="lbl">{FUT_A} futsal<br>{SOC_A} soccer</span></div>
        <div class="cell"><span class="num">{FUT_INT + SOC_INT}</span><span class="k">Interceptions</span><span class="lbl">{FUT_INT} futsal<br>{SOC_INT} soccer</span></div>
        <div class="cell"><span class="num">{FUT_REC + SOC_REC}</span><span class="k">Recoveries</span><span class="lbl">{FUT_REC} futsal<br>{SOC_REC} soccer</span></div>
      </div>

      <div class="badges">
        <div class="badge"><span class="b-k">Representative</span>
          <span class="b-v">Association</span>
          <span class="b-u">AFA U16 &amp; FAF Women's sides</span></div>
        <div class="badge"><span class="b-k">Leadership</span>
          <span class="b-v">Captain</span>
          <span class="b-u">AFA U16 &amp; Futsal WA state teams</span></div>
        <div class="badge"><span class="b-k">2026</span>
          <span class="b-v">Contracted</span>
          <span class="b-u">Paid player at Fremantle FC, WNPL</span></div>
        <div class="badge"><span class="b-k">Honours</span>
          <span class="b-v">League MVP</span>
          <span class="b-u">Supa-Liga Women's B, 22/23</span></div>
      </div>
    </div>"""),

    # 3 · CAREER RECORD
    ('bone', ARCS, f"""<div class="wrap">
      <div class="eyebrow">Career Record</div>
      <h2 class="display">Clubs &amp; Seasons</h2>
      <p class="lede">Senior record across NPL Women soccer and futsal.</p>
      <div class="c-tot">
        <div class="t"><span class="tk">Seasons</span><span class="tv">{CAREER_SEASONS}</span></div>
        <div class="t"><span class="tk">Clubs</span><span class="tv">{CAREER_CLUBS}</span></div>
        <div class="t"><span class="tk">Soccer minutes</span><span class="tv">{SOC_MIN}</span></div>
        <div class="t"><span class="tk">Soccer apps</span><span class="tv">{N_SOC}</span></div>
      </div>
      <div class="sec-rule"><span>Clubs by season</span></div>
      <div class="c-table">{CAREER_HEAD}{career_rows(CAREER)}</div>

      <div class="sec-rule"><span>Honours &amp; Selections</span></div>
      <div class="honours">{honours_html()}</div>
    </div>"""),

    # 4 · DEFENSIVE PROFILE
    ('dark', WAVES, f"""<div class="wrap">
      <div class="eyebrow">Player Profile</div>
      <h2 class="display">Defensive<br><em style="font-style:normal;color:var(--orange)">Profile</em></h2>
      <p class="lede">Ball-winning is the strongest part of her game — she is involved in defensive actions constantly in both codes.</p>

      {split_block(
        [(SOC_INT, f"Interceptions · {per(SOC_INT, N_SOC)} per game"),
         (SOC_REC, f"Recoveries · {per(SOC_REC, N_SOC)} per game"),
         (SOC_DW, f"Duels won of {SOC_DT} contested"),
         (SOC_MIN, "Minutes played")],
        [(FUT_INT, f"Interceptions · {per(FUT_INT, N_FUT)} per game"),
         (FUT_REC, f"Recoveries · {per(FUT_REC, N_FUT)} per game"),
         (FUT_LOST, "Balls lost"),
         (N_FUT, "Games analysed")])}

      <div style="margin-top:34px;border-top:2px solid var(--orange)">
        <div class="stat-row"><span class="n">01</span><h3>Duels</h3>
          <p>{SOC_DW} duels won from {SOC_DT} contested in soccer — a {round(100 * SOC_DW / SOC_DT)}% success rate across {N_SOC} games in 2026. She competes for everything.</p></div>
        <div class="stat-row"><span class="n">02</span><h3>Recoveries</h3>
          <p>{SOC_REC} in soccer and {FUT_REC} in futsal, {SOC_REC + FUT_REC} in total. Works both halves of the pitch, not just behind the ball.</p></div>
        <div class="stat-row" style="border-bottom:none"><span class="n">03</span><h3>Interceptions</h3>
          <p>{SOC_INT} in soccer and {FUT_INT} in futsal. Reads passing lanes early rather than reacting late.</p></div>
      </div>
    </div>"""),

    # 5 · ATTACKING PROFILE
    ('dark', ARCS, f"""<div class="wrap">
      <div class="eyebrow">Player Profile</div>
      <h2 class="display">Attacking<br><em style="font-style:normal;color:var(--orange)">Profile</em></h2>
      <p class="lede">Sharpest in futsal — {FUT_G} goals and {FUT_A} assists in {N_FUT} games, at {per(WIN_SHOT_OT, WIN_G)} shots on target per goal in the Winter season.</p>

      <div class="rank-note"><span class="c-code futsal">Futsal</span>Where the attacking output comes from</div>
      <div class="prof-grid">
        <div class="prof"><span class="prof-rank">{FUT_G + SOC_G}</span><span class="prof-k">Goals</span>
          <span class="prof-v">{FUT_G}+{SOC_G}</span><span class="prof-u">futsal + soccer</span></div>
        <div class="prof"><span class="prof-rank">{FUT_A}</span><span class="prof-k">Assists</span>
          <span class="prof-v">{FUT_ASSIST_SPLIT}</span><span class="prof-u">{FUT_ASSIST_LABEL} futsal</span></div>
        <div class="prof"><span class="prof-rank">{per(WIN_SHOT_OT, WIN_G)}</span><span class="prof-k">Shot Efficiency</span>
          <span class="prof-v">{round(100 * FUT_SHOT_OT / FUT_SHOT)}%</span><span class="prof-u">futsal on-target rate</span></div>
      </div>

      {split_block(
        [(SOC_G, "Goals"),
         (SOC_A, "Assists"),
         (SOC_SHOT, f"Shots · {SOC_SHOT_OT} on target"),
         (SOC_MIN, "Minutes played")],
        [(FUT_G, "Goals"),
         (FUT_A, "Assists"),
         (FUT_SHOT, f"Shots · {FUT_SHOT_OT} on target"),
         (FUT_PASS, "Accurate passes")])}

      <div style="margin-top:34px;border-top:2px solid var(--orange)">
        <div class="stat-row"><span class="n">01</span><h3>Finishing</h3>
          <p>Winter 2026 futsal: <strong>{WIN_G} goals from {WIN_SHOT_OT} shots on target</strong> — {per(WIN_SHOT_OT, WIN_G)} shots on target per goal. Ruthless once the chance is created.</p></div>
        <div class="stat-row"><span class="n">02</span><h3>Volume &amp; Creation</h3>
          <p>{FUT_SHOT} futsal shots across {N_FUT} games ({per(FUT_SHOT, N_FUT)} per game) plus {FUT_A} assists. In soccer the role is deeper: {SOC_SHOT} shots across {N_SOC} games in 2026.</p></div>
        <div class="stat-row" style="border-bottom:none"><span class="n">03</span><h3>Distribution</h3>
          <p>{FUT_PASS} accurate futsal passes, {round(FUT_PASS / N_FUT)} per game. Consistently involved in build-up rather than only at the end of moves.</p></div>
      </div>
    </div>"""),

    # 6 · MY AREA — locked; contents are decrypted into #pin-content
    ('paper', WAVES, """<div class="wrap">
      <div class="eyebrow">Private</div>
      <h2 class="display">My Area</h2>
      <div id="pin-gate">
        <p class="lede">Enter your PIN to see your training log, season data and analysis videos.</p>
        <div class="pin-box">
          <input id="pin-input" type="password" inputmode="numeric" pattern="[0-9]*"
                 maxlength="8" placeholder="&bull;&bull;&bull;&bull;" autocomplete="off">
          <button id="pin-go" class="pin-btn">Enter</button>
          <p id="pin-err" class="pin-err"></p>
        </div>
      </div>
      <div id="pin-content" hidden></div>
    </div>"""),
]

SECTIONS = [("Overview", 0, 2), ("Career", 2, 3), ("Defensive", 3, 4),
            ("Attacking", 4, 5), ("My Area", 5, 6)]

slides_html = "\n".join(
    f'  <div class="slide {cls}{" active" if i == 0 else ""}">\n    {bg}\n    {body}\n  </div>\n'
    for i, (cls, bg, body) in enumerate(SLIDES)
)
sections_js = ",\n  ".join(f'{{label:"{l}",start:{s},end:{e}}}' for l, s, e in SECTIONS)

JS_MAIN = r"""
const MOBILE = window.matchMedia('(max-width:700px)').matches;
const CHARTS = [];
const O='#FF6B00', Osoft='rgba(255,107,0,.30)', INK='#0B0B0C', GREY='#C4C4C6';
Chart.defaults.font.family="'Archivo',system-ui,sans-serif";
Chart.defaults.color='#5C5C60';

function cell(v,label,hot){
  const cls = v===0 ? 'v zero' : (hot ? 'v hot' : 'v');
  return '<span class="'+cls+'" data-k="'+label+'">'+v+'</span>';
}
function mk(id, labels, datasets){
  const el=document.getElementById(id); if(!el) return;
  if(MOBILE){
    const h = Math.max(200, labels.length*(datasets.length>1?26:20) + 56);
    const holder=document.createElement('div');
    holder.style.cssText='position:relative;width:100%;height:'+h+'px';
    el.replaceWith(holder); holder.appendChild(el);
  }
  const cat = {grid:{display:false},ticks:{font:{size:MOBILE?11:10},color:'#5C5C60',
               maxRotation:MOBILE?0:60,minRotation:MOBILE?0:60,autoSkip:false}};
  const val = {grid:{color:'rgba(0,0,0,.07)'},ticks:{font:{size:11.5},color:'#5C5C60',precision:0},beginAtZero:true};
  CHARTS.push(new Chart(el,{
    type:'bar', data:{labels, datasets},
    options:{indexAxis: MOBILE ? 'y' : 'x', responsive:true, maintainAspectRatio:false,
      plugins:{legend:{display:datasets.length>1,labels:{boxWidth:11,font:{size:11.5},color:'#333',padding:12}}},
      scales: MOBILE ? {x:val, y:cat} : {x:cat, y:val}}
  }));
}
function mkBlocks(id, labels, data, colour){
  const el=document.getElementById(id); if(!el) return;
  const holder=document.createElement('div');
  holder.style.cssText='position:relative;width:100%;height:210px';
  el.replaceWith(holder); holder.appendChild(el);
  CHARTS.push(new Chart(el,{
    type:'bar', data:{labels, datasets:[{data, backgroundColor:colour, borderRadius:2}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},
      scales:{x:{grid:{display:false},ticks:{font:{size:10},maxRotation:45,minRotation:45}},
              y:{grid:{color:'rgba(0,0,0,.07)'},ticks:{font:{size:11}},beginAtZero:true}}}
  }));
}

/* ---- MY AREA: the payload is encrypted; the PIN is the decryption key ---- */
const ENC = __ENCRYPTED_BLOB__;
const b64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));

async function decryptArea(pin){
  const base = await crypto.subtle.importKey('raw', new TextEncoder().encode(pin),
    'PBKDF2', false, ['deriveKey']);
  const key = await crypto.subtle.deriveKey(
    {name:'PBKDF2', salt:b64(ENC.salt), iterations:ENC.iter, hash:'SHA-256'},
    base, {name:'AES-GCM', length:256}, false, ['decrypt']);
  const plain = await crypto.subtle.decrypt({name:'AES-GCM', iv:b64(ENC.nonce)}, key, b64(ENC.data));
  return new TextDecoder().decode(plain);
}

function buildArea(){
  const TRAINING = JSON.parse(document.getElementById('training-data').textContent);
  const SEASON = JSON.parse(document.getElementById('season-data').textContent);
  const FUTSAL = SEASON.futsal, SOCCER = SEASON.soccer;
  const esc = v => (v||'')
    .replace(/</g,'&lt;').replace(/\*\*/g,'')
    .replace(/^[ \t]*\*[ \t]+/gm,'').replace(/\n{3,}/g,'\n\n').trim();

  document.getElementById('tlog').innerHTML =
    [...TRAINING].sort((a,b)=>(b.date||'').localeCompare(a.date||'')).map(t=>
      '<div class="tsession"><div class="thead"><span class="tdate">'+esc(t.date)+'</span>'
      +'<span class="tmeta"><b>'+esc(t.load)+'</b>load</span>'
      +'<span class="tmeta"><b>'+esc(t.hours)+'</b>duration</span></div><div class="tcols">'
      +'<div><h4>Content</h4><p>'+esc(t.content)+'</p></div>'
      +(t.why?'<div><h4>Why this training</h4><p>'+esc(t.why)+'</p></div>':'')
      +'</div></div>').join('');

  const SUM = FUTSAL.filter(f=>f.s==='Summer'), WIN = FUTSAL.filter(f=>f.s==='Winter');
  const FHEAD = '<div class="t-row head"><span>Game</span><span>Goals</span><span>Assists</span><span>Shots</span><span>Passes</span><span>Recov.</span><span>Intercept</span></div>';
  const fRows = arr => arr.map(f=>'<div class="t-row"><span class="gm">'+f.g+'</span>'
    +cell(f.goal,'Goals',true)+cell(f.assist,'Assists')+cell(f.shot,'Shots')
    +cell(f.pass,'Passes')+cell(f.rec,'Recov.')+cell(f.int,'Intercept')+'</div>').join('');
  document.getElementById('tbl-summer').innerHTML = FHEAD + fRows(SUM);
  document.getElementById('tbl-winter').innerHTML = FHEAD + fRows(WIN);

  const SUL=SUM.map(f=>f.g), WIL=WIN.map(f=>f.g);
  mk('su-ga',SUL,[{label:'Goals',data:SUM.map(f=>f.goal),backgroundColor:O,borderRadius:2},
                  {label:'Assists',data:SUM.map(f=>f.assist),backgroundColor:Osoft,borderRadius:2}]);
  mk('su-shot',SUL,[{label:'Total shots',data:SUM.map(f=>f.shot),backgroundColor:Osoft,borderRadius:2},
                    {label:'On target',data:SUM.map(f=>f.shotOT),backgroundColor:O,borderRadius:2}]);
  mk('wi-ga',WIL,[{label:'Goals',data:WIN.map(f=>f.goal),backgroundColor:O,borderRadius:2},
                  {label:'Assists',data:WIN.map(f=>f.assist),backgroundColor:Osoft,borderRadius:2}]);
  mk('wi-def',WIL,[{label:'Recoveries',data:WIN.map(f=>f.rec),backgroundColor:O,borderRadius:2},
                   {label:'Interceptions',data:WIN.map(f=>f.int),backgroundColor:INK,borderRadius:2}]);

  const SR=[...SOCCER].reverse();
  const sum=f=>SR.reduce((a,g)=>a+f(g),0), rec=g=>g.recOwn+g.recOpp;
  document.getElementById('sm-totals').innerHTML = [
    ['Interceptions', sum(g=>g.intercept), (sum(g=>g.intercept)/SR.length).toFixed(1)+' per game'],
    ['Recoveries',    sum(rec),            (sum(rec)/SR.length).toFixed(1)+' per game'],
    ['Minutes',       sum(g=>g.min),       (sum(g=>g.min)/SR.length).toFixed(1)+' per game'],
    ['Duels won',     sum(g=>g.duelW),     'of '+sum(g=>g.duelT)+' contested']
  ].map(([k,v,u])=>'<div class="blk"><span class="bk">'+k+'</span><span class="bv">'+v+'</span><span class="bu">'+u+'</span></div>').join('');

  const CH=5, blocks=[];
  for(let i=0;i<SR.length;i+=CH){
    const part=SR.slice(i,i+CH);
    const mean=f=>+(part.reduce((a,g)=>a+f(g),0)/part.length).toFixed(1);
    blocks.push({lbl:'M'+(i+1)+'–'+(i+part.length), int:mean(g=>g.intercept), rec:mean(rec), min:mean(g=>g.min)});
  }
  const BL=blocks.map(b=>b.lbl);
  mkBlocks('sm-int', BL, blocks.map(b=>b.int), O);
  mkBlocks('sm-rec', BL, blocks.map(b=>b.rec), O);
  mkBlocks('sm-min', BL, blocks.map(b=>b.min), INK);

  const top=SR.map((g,n)=>({...g,n:n+1})).sort((a,b)=>b.intercept-a.intercept).slice(0,5);
  document.getElementById('sm-lead-int').innerHTML = top.map((g,i)=>
    '<div class="lead-row"><span class="pos">'+(i+1)+'</span>'
    +'<span class="nm">'+g.g+'<span class="dt">Match '+g.n+' · '+g.d+'</span></span>'
    +'<span class="val">'+g.intercept+'</span></div>').join('');

  document.getElementById('tbl-soccer').innerHTML =
    '<div class="t-row head"><span>Game</span><span>Min</span><span>Goals</span><span>Shots</span><span>Passes</span><span>Duels W</span><span>Recov.</span><span>Intercept</span></div>' +
    SOCCER.map(s=>'<div class="t-row"><span class="gm">'+s.g+'<span class="dt">'+s.d+'</span></span>'
      +cell(s.min,'Min')+cell(s.goal,'Goals',true)+cell(s.shot,'Shots')+cell(s.pass,'Passes')
      +cell(s.duelW,'Duels W')+cell(s.recOwn+s.recOpp,'Recov.')+cell(s.intercept,'Intercept')+'</div>').join('');

  /* ---- current season: one block per competition, one row per round ---- */
  const sumK=(a,k)=>a.reduce((s,r)=>s+(r[k]||0),0);
  const perN=(n,d)=>d?(n/d).toFixed(1):'—';
  const hlHtml=(k,big,sub,rows)=>'<div class="hl"><div class="hl-k">'+k+'</div><span class="hl-big">'+big
    +'</span><span class="hl-sub">'+sub+'</span><div class="hl-rows">'
    +rows.map(r=>'<span class="hl-row"><b>'+r[0]+'</b>'+r[1]+'</span>').join('')+'</div></div>';
  const futsalCards=a=>{
    const g=sumK(a,'goal'), ot=sumK(a,'shotOT'), sh=sumK(a,'shot'), ps=sumK(a,'pass');
    const rc=sumK(a,'rec'), it=sumK(a,'int');
    return '<div class="hl-grid">'
      +hlHtml('Finishing',perN(ot,g),'shots on target per goal',[[sh,'total shots'],[ot,'on target'],[g,'goals']])
      +hlHtml('Creation',sumK(a,'assist'),'assists',[[ps,'accurate passes'],[Math.round(ps/a.length),'passes / game'],[a.length,'games']])
      +hlHtml('Defensive',rc+it,'recoveries + intercepts',[[rc,'recoveries'],[it,'interceptions'],[sumK(a,'lost'),'balls lost']])
      +'</div>';
  };
  const roundLabel=r=>r.round?('Round '+r.round):(r.g||'Game');
  const CUR=SEASON.current, curAll=CUR.competitions.flatMap(c=>c.games);
  document.getElementById('cur-head').innerHTML=
    '<span class="c-code futsal">Futsal</span><span class="sb-t">'+CUR.label+'</span>'
    +'<span class="sb-s">'+(curAll.length?curAll.length+' game'+(curAll.length>1?'s':'')+' logged':'Season in progress')+'</span>';
  let cur='';
  if(curAll.length>1 && CUR.competitions.filter(c=>c.games.length).length>1){
    cur+='<div class="cur-block-title">Season total · all competitions</div>'+futsalCards(curAll);
  }
  CUR.competitions.forEach(c=>{
    cur+='<div class="comp-head"><span class="comp-n">'+c.name+'</span>'
      +(c.club?'<span class="comp-c">'+c.club+'</span>':'')
      +'<span class="comp-r">'+(c.games.length?c.games.length+' round'+(c.games.length>1?'s':'')+' logged':'No rounds logged yet')+'</span></div>';
    if(!c.games.length){ cur+='<div class="cur-empty">Round data coming soon.</div>'; return; }
    cur+=futsalCards(c.games)
      +'<div class="tbl tbl-futsal">'
      +'<div class="t-row head"><span>Round</span><span>Goals</span><span>Assists</span><span>Shots</span><span>Passes</span><span>Recov.</span><span>Intercept</span></div>'
      +c.games.map(r=>'<div class="t-row"><span class="gm">'+roundLabel(r)
          +'<span class="dt">'+[r.opp,r.res,r.d].filter(Boolean).join(' · ')+'</span></span>'
          +cell(r.goal||0,'Goals',true)+cell(r.assist||0,'Assists')+cell(r.shot||0,'Shots')
          +cell(r.pass||0,'Passes')+cell(r.rec||0,'Recov.')+cell(r.int||0,'Intercept')+'</div>').join('')
      +'</div>'
      +'<div class="chart-grid">'
      +'<div class="chart-box"><div class="ct">Goals &amp; assists per round</div><canvas id="cur-'+c.key+'-ga"></canvas></div>'
      +'<div class="chart-box"><div class="ct">Shots — total vs on target</div><canvas id="cur-'+c.key+'-sh"></canvas></div>'
      +'</div>';
  });
  document.getElementById('cur-body').innerHTML=cur;
  CUR.competitions.forEach(c=>{
    if(!c.games.length) return;
    const L=c.games.map(roundLabel);
    mk('cur-'+c.key+'-ga',L,[{label:'Goals',data:c.games.map(r=>r.goal||0),backgroundColor:O,borderRadius:2},
                            {label:'Assists',data:c.games.map(r=>r.assist||0),backgroundColor:Osoft,borderRadius:2}]);
    mk('cur-'+c.key+'-sh',L,[{label:'Total shots',data:c.games.map(r=>r.shot||0),backgroundColor:Osoft,borderRadius:2},
                            {label:'On target',data:c.games.map(r=>r.shotOT||0),backgroundColor:O,borderRadius:2}]);
  });

  document.querySelectorAll('.sub-tab').forEach(btn=>{
    btn.onclick=()=>{
      document.querySelectorAll('.sub-tab').forEach(b=>b.classList.toggle('on', b===btn));
      document.querySelectorAll('.sub-panel').forEach(p=>p.classList.toggle('on', p.id===btn.dataset.p));
      requestAnimationFrame(()=>CHARTS.forEach(c=>c.resize()));
    };
  });
  requestAnimationFrame(()=>CHARTS.forEach(c=>c.resize()));
}

(function pinGate(){
  const input=document.getElementById('pin-input');
  const btn=document.getElementById('pin-go');
  const err=document.getElementById('pin-err');
  const gate=document.getElementById('pin-gate');
  const content=document.getElementById('pin-content');
  if(!input) return;

  async function open(pin, remember){
    if(!pin) return;
    btn.disabled=true; err.style.color=''; err.textContent='Unlocking…';
    try{
      content.innerHTML = await decryptArea(pin);
      gate.hidden=true; content.hidden=false; err.textContent='';
      if(remember){ try{ sessionStorage.setItem('tzr_pin', pin); }catch(e){} }
      buildArea();
    }catch(e){
      err.textContent='Wrong PIN — try again.';
      input.value=''; input.focus();
      try{ sessionStorage.removeItem('tzr_pin'); }catch(e2){}
    }finally{ btn.disabled=false; }
  }
  btn.onclick=()=>open(input.value.trim(), true);
  input.addEventListener('keydown',e=>{ if(e.key==='Enter') open(input.value.trim(), true); });
  try{ const saved=sessionStorage.getItem('tzr_pin'); if(saved) open(saved, false); }catch(e){}
})();

/* NAV */
const slides=[...document.querySelectorAll('.slide')];
const dotsEl=document.getElementById('dots'), tabsEl=document.getElementById('tabs');
const counter=document.getElementById('counter');
const prevBtn=document.getElementById('prev'), nextBtn=document.getElementById('next');
let i=0;
SECTIONS.forEach((s,n)=>{
  const b=document.createElement('button');
  b.className='tab'+(n===0?' on':''); b.textContent=s.label;
  b.onclick=()=>go(s.start); tabsEl.appendChild(b);
});
const tabs=[...tabsEl.children];
slides.forEach((_,n)=>{
  const d=document.createElement('div');
  d.className='dot'+(n===0?' on':''); d.onclick=()=>go(n); dotsEl.appendChild(d);
});
const dots=[...dotsEl.children];
function go(n){
  if(n<0||n>=slides.length)return;
  slides[i].classList.remove('active'); dots[i].classList.remove('on');
  i=n;
  slides[i].classList.add('active'); slides[i].scrollTop=0; dots[i].classList.add('on');
  counter.textContent=(i+1)+' / '+slides.length;
  prevBtn.disabled=i===0; nextBtn.disabled=i===slides.length-1;
  const act=SECTIONS.findIndex(s=>i>=s.start&&i<s.end);
  tabs.forEach((t,n)=>t.classList.toggle('on',n===act));
  requestAnimationFrame(()=>{
    CHARTS.forEach(c=>{ if(slides[i].contains(c.canvas)) c.resize(); });
  });
}
window.addEventListener('resize',()=>CHARTS.forEach(c=>c.resize()));
prevBtn.onclick=()=>go(i-1); nextBtn.onclick=()=>go(i+1);
document.addEventListener('keydown',e=>{
  if(e.target.tagName==='INPUT')return;
  if(e.key==='ArrowRight'||e.key===' '||e.key==='PageDown')go(i+1);
  if(e.key==='ArrowLeft'||e.key==='PageUp')go(i-1);
  if(e.key==='Home')go(0);
  if(e.key==='End')go(slides.length-1);
});
let x0=null;
document.addEventListener('touchstart',e=>x0=e.touches[0].clientX,{passive:true});
document.addEventListener('touchend',e=>{
  if(x0===null)return;
  const dx=e.changedTouches[0].clientX-x0;
  if(Math.abs(dx)>55) dx<0?go(i+1):go(i-1);
  x0=null;
},{passive:true});
go(0);
"""

html = f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Sam Brady · Performance Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>{CSS}{STAT_ROW_CSS}{EXTRA_CSS}</style>
</head>
<body>

<div class="tabs" id="tabs"></div>

<div class="deck" id="deck">
{slides_html}</div>

<div class="nav">
  <button class="nav-btn" id="prev">← Prev</button>
  <div class="dots" id="dots"></div>
  <button class="nav-btn" id="next">Next →</button>
  <span class="counter" id="counter">1 / {len(SLIDES)}</span>
</div>

<script>
const SECTIONS=[
  {sections_js}
];
{JS_MAIN}
</script>
</body>
</html>
"""

# Encrypt the private payload with the PIN before it ever reaches the file.
from encrypt_area import encrypt
PIN = "2109"
season = {"futsal": ARCH_FUTSAL, "soccer": ARCH_SOCCER, "current": CURRENT}
private_filled = (PRIVATE_HTML
    .replace("__TRAINING_JSON__", json.dumps(TRAINING, ensure_ascii=False))
    .replace("__SEASON_JSON__", json.dumps(season, ensure_ascii=False)))
html = html.replace("__ENCRYPTED_BLOB__", json.dumps(encrypt(private_filled, PIN)))

OUT.write_text(html, encoding="utf-8")
# Same page under a clean per-athlete path: <domain>/sambrady/
athlete_dir = HERE / "sambrady"
athlete_dir.mkdir(exist_ok=True)
(athlete_dir / "index.html").write_text(html, encoding="utf-8")
print(f"Built {OUT} — {len(SLIDES)} slides, {len(html)/1024/1024:.2f} MB")
print(f"Private payload encrypted: {len(private_filled)} chars -> AES-GCM, PBKDF2 x600k")
