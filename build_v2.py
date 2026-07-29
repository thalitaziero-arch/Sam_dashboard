#!/usr/bin/env python3
"""Builds sam_brady_v2.html — the slide-deck dashboard for Sam Brady.

Reads the analysis images + logo from /tmp/sam_assets.json (extracted from the
main dashboard). Re-run after changing data or layout.
"""
import json
from pathlib import Path

OUT = Path(__file__).parent / "sam_brady_v2.html"
A = json.load(open("/tmp/sam_assets.json"))
TRAINING = json.load(open("/tmp/training_for_deck.json"))
PLAYLIST = "https://www.youtube.com/playlist?list=PLCiTolkeqpjdu0zgk4ok0wzRsKHx8I0dH"

WINTER_GAMES = ["Internationale", "Perth United", "SPA"]

ARCS = '''<div class="bg-lines"><svg viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
<g class="g1"><circle cx="880" cy="60" r="430"/><circle cx="880" cy="60" r="392" opacity=".6"/></g>
<g class="g2"><path d="M-120 470 C 260 400, 700 330, 1330 250"/><path d="M-120 545 C 280 470, 760 395, 1330 320" opacity=".7"/><path d="M-120 640 L 1330 470" opacity=".55"/></g>
<g class="g3"><ellipse cx="180" cy="720" rx="520" ry="300" opacity=".6"/><path d="M-40 120 C 300 210, 520 240, 900 175" opacity=".6"/></g>
</svg></div>'''

WAVES = '''<div class="bg-lines"><svg viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
<g class="w1"><path d="M-150 250 C 150 170, 450 330, 750 250 S 1050 170, 1350 250"/><path d="M-150 300 C 150 220, 450 380, 750 300 S 1050 220, 1350 300" opacity=".65"/></g>
<g class="w2"><path d="M-150 480 C 200 400, 400 560, 750 480 S 1100 400, 1350 480" opacity=".8"/><path d="M-150 540 C 200 460, 400 620, 750 540 S 1100 460, 1350 540" opacity=".5"/></g>
<g class="w3"><path d="M-150 690 C 180 620, 480 760, 780 690 S 1080 620, 1350 690" opacity=".6"/><circle cx="1050" cy="120" r="330" opacity=".45"/></g>
</svg></div>'''


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


CSS = """
:root{
  --ink:#0B0B0C;--paper:#FFFFFF;--bone:#F4F3EF;
  --orange:#FF6B00;--orange-soft:rgba(255,107,0,.28);
  --grey:#8A8A8E;--steel:#5C5C60;--line:#E2E1DC;
  --line-dark:rgba(255,255,255,.15);--max:1180px;
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Archivo',system-ui,sans-serif;color:var(--ink);background:var(--ink);
  line-height:1.6;font-size:16px;-webkit-font-smoothing:antialiased;overflow:hidden}

.deck{position:relative;width:100vw;height:100vh;overflow:hidden}
.slide{position:absolute;inset:0;opacity:0;visibility:hidden;
  transition:opacity .4s ease, transform .4s ease;transform:translateX(26px);
  overflow-y:auto;display:flex;align-items:flex-start;padding:100px 0 88px}
.slide.active{opacity:1;visibility:visible;transform:none}
.slide.paper{background:var(--paper)}
.slide.bone{background:var(--bone)}
.slide.dark{background:var(--ink);color:var(--paper)}
.wrap{max-width:var(--max);margin:0 auto;padding:0 40px;width:100%}
.slide>.wrap{position:relative;z-index:1;margin-top:auto;margin-bottom:auto;min-width:0}
.chart-box,.chart-single,.tbl,.an-grid,.hl-grid,.chart-grid{min-width:0}
.chart-box canvas,.chart-single canvas{max-width:100%}

/* BACKGROUND LINES */
.bg-lines{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:0}
.bg-lines svg{position:absolute;width:150%;height:150%;left:-25%;top:-25%;overflow:visible}
.bg-lines path,.bg-lines circle,.bg-lines ellipse{
  fill:none;stroke:rgba(255,255,255,.085);stroke-width:1;vector-effect:non-scaling-stroke}
.paper .bg-lines path,.paper .bg-lines circle,.paper .bg-lines ellipse,
.bone  .bg-lines path,.bone  .bg-lines circle,.bone  .bg-lines ellipse{stroke:rgba(11,11,12,.055)}
.bg-lines .g1{animation:drift1 34s ease-in-out infinite alternate}
.bg-lines .g2{animation:drift2 46s ease-in-out infinite alternate}
.bg-lines .g3{animation:drift3 40s ease-in-out infinite alternate}
@keyframes drift1{from{transform:translate3d(0,0,0) rotate(0deg)} to{transform:translate3d(-2.5%,2%,0) rotate(2.2deg)}}
@keyframes drift2{from{transform:translate3d(0,0,0) rotate(0deg)} to{transform:translate3d(3%,-1.5%,0) rotate(-1.8deg)}}
@keyframes drift3{from{transform:translate3d(0,1.5%,0) scale(1)}  to{transform:translate3d(-1.5%,-1.5%,0) scale(1.05)}}
.bg-lines .w1{animation:wave1 28s ease-in-out infinite}
.bg-lines .w2{animation:wave2 36s ease-in-out infinite}
.bg-lines .w3{animation:wave3 44s ease-in-out infinite}
@keyframes wave1{0%,100%{transform:translate3d(0,0,0) skewY(0deg)}33%{transform:translate3d(-1.4%,2.2%,0) skewY(.9deg)}66%{transform:translate3d(1.4%,-1.8%,0) skewY(-.9deg)}}
@keyframes wave2{0%,100%{transform:translate3d(0,0,0) skewY(0deg)}30%{transform:translate3d(1.8%,-2.4%,0) skewY(-1.1deg)}70%{transform:translate3d(-1.8%,2%,0) skewY(1.1deg)}}
@keyframes wave3{0%,100%{transform:translate3d(0,0,0) scaleY(1)}50%{transform:translate3d(0,-2.6%,0) scaleY(1.06)}}
@media (prefers-reduced-motion:reduce){.bg-lines g{animation:none !important}}

.display{font-family:'Anton',sans-serif;text-transform:uppercase;line-height:.95;letter-spacing:.005em;font-weight:400}
.eyebrow{font-size:12px;letter-spacing:.28em;text-transform:uppercase;font-weight:700;color:var(--ink);
  display:flex;align-items:center;gap:14px;margin-bottom:18px}
.eyebrow::before{content:"";width:32px;height:3px;background:var(--orange);flex:none}
.dark .eyebrow{color:var(--orange)}
.lede{max-width:62ch;color:var(--steel);font-size:16.5px;margin-top:12px}
.dark .lede{color:rgba(255,255,255,.68)}
h2.display{font-size:clamp(28px,3.8vw,46px)}

/* TABS */
.tabs{position:fixed;top:0;left:0;right:0;height:64px;z-index:100;
  background:rgba(11,11,12,.95);backdrop-filter:blur(10px);border-bottom:1px solid var(--line-dark);
  display:flex;align-items:center;justify-content:center;gap:9px;padding:0 24px;overflow-x:auto}
.tab{background:none;border:1px solid rgba(255,255,255,.2);color:rgba(255,255,255,.6);
  font-family:'Archivo',sans-serif;font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;
  font-weight:700;padding:10px 18px;cursor:pointer;white-space:nowrap;transition:all .2s;
  display:flex;align-items:center;gap:8px}
.tab::before{content:"";width:7px;height:7px;background:rgba(255,255,255,.3);flex:none}
.tab:hover{border-color:var(--orange);color:var(--orange)}
.tab.on{background:var(--orange);border-color:var(--orange);color:#fff}
.tab.on::before{background:#fff}

/* NAV */
.nav{position:fixed;bottom:0;left:0;right:0;height:68px;background:rgba(11,11,12,.95);
  backdrop-filter:blur(10px);border-top:1px solid var(--line-dark);display:flex;
  align-items:center;justify-content:space-between;padding:0 32px;z-index:100}
.nav-btn{background:none;border:1px solid var(--orange);color:var(--orange);
  font-family:'Archivo',sans-serif;font-size:12px;letter-spacing:.16em;text-transform:uppercase;
  font-weight:700;padding:11px 22px;cursor:pointer;transition:all .2s}
.nav-btn:hover:not(:disabled){background:var(--orange);color:#fff}
.nav-btn:disabled{opacity:.25;cursor:default}
.dots{display:flex;gap:8px;align-items:center}
.dot{width:8px;height:8px;background:rgba(255,255,255,.22);cursor:pointer;transition:all .2s}
.dot.on{background:var(--orange);transform:scale(1.4)}
.counter{font-family:'Anton',sans-serif;font-size:15px;color:var(--orange);letter-spacing:.08em;
  min-width:66px;text-align:right}

/* HERO */
.hero-meta{display:flex;flex-wrap:wrap;gap:10px 26px;font-size:12px;letter-spacing:.24em;
  text-transform:uppercase;font-weight:700;color:var(--orange);margin-bottom:32px}
.hero-meta span{display:flex;align-items:center;gap:10px}
.hero-meta span::before{content:"";width:7px;height:7px;background:var(--orange);flex:none}
.hero h1{font-size:clamp(54px,9.5vw,132px);margin-bottom:14px;color:#fff}
.hero h1 em{font-style:normal;color:var(--orange)}
.hero .strap{font-size:clamp(15px,1.7vw,18px);font-weight:600;color:rgba(255,255,255,.78);
  max-width:56ch;margin-bottom:38px}
.origin{font-size:13px;letter-spacing:.24em;text-transform:uppercase;font-weight:700;
  color:rgba(255,255,255,.55);margin-bottom:12px}
.tzr-logo{height:52px;width:auto;display:block}

/* CURRENT CLUBS */
.clubs{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:34px}
.club{border:1px solid var(--line-dark);padding:16px 22px 18px;min-width:190px}
.club span{display:block}
.club-k{font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;
  color:var(--orange);margin-bottom:8px}
.club-n{font-family:'Anton',sans-serif;font-size:24px;color:#fff;line-height:1.05}
.club-c{font-size:11px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;
  color:rgba(255,255,255,.75);margin-top:5px}
.club-p{font-size:12.5px;color:rgba(255,255,255,.5);margin-top:3px;letter-spacing:.06em}
@media(max-width:700px){.clubs{flex-direction:column;gap:10px}.club{min-width:0}}

/* SCOREBOARD */
.scoreboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));margin-top:40px;
  border-top:1px solid var(--line-dark)}
.scoreboard .cell{padding:30px 18px 0;border-right:1px solid var(--line-dark)}
.scoreboard .cell:last-child{border-right:none}
.scoreboard .num{font-family:'Anton',sans-serif;font-size:clamp(34px,4vw,54px);line-height:1;
  display:block;margin-bottom:9px;color:var(--orange)}
.scoreboard .k{font-size:12px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;
  display:block;margin-bottom:6px}
.scoreboard .lbl{font-size:12px;color:rgba(255,255,255,.5);line-height:1.5}

/* HIGHLIGHT CARDS */
.hl-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:26px}
.hl{background:var(--bone);border:1px solid var(--line);padding:26px 24px 24px;text-align:center}
.paper .hl{background:#FAFAF8}
.hl .hl-k{font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;
  color:var(--ink);display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:14px}
.hl .hl-k::before{content:"";width:7px;height:7px;background:var(--orange);border-radius:50%;flex:none}
.hl .hl-big{font-family:'Anton',sans-serif;font-size:clamp(46px,5.4vw,64px);line-height:1;
  color:var(--orange);display:block}
.hl .hl-sub{font-size:12.5px;color:var(--grey);margin-top:8px;font-weight:500}
.hl .hl-rows{margin-top:18px;border-top:1px solid var(--line);padding-top:14px;
  display:flex;flex-direction:column;gap:7px}
.hl .hl-row{font-size:13.5px;color:var(--steel)}
.hl .hl-row b{font-family:'Anton',sans-serif;font-size:17px;color:var(--orange);margin-right:6px}

/* SECTION RULE */
.sec-rule{display:flex;align-items:center;gap:16px;margin:46px 0 6px}
.sec-rule::before,.sec-rule::after{content:"";height:1px;background:var(--line);flex:1}
.sec-rule span{font-size:11.5px;letter-spacing:.24em;text-transform:uppercase;font-weight:700;color:var(--steel)}
.an-head{font-family:'Anton',sans-serif;text-transform:uppercase;font-size:20px;font-weight:400;
  margin:26px 0 12px;color:var(--ink);display:flex;align-items:center;gap:12px}
.an-head::before{content:"";width:22px;height:3px;background:var(--orange);flex:none}

/* ANALYSIS IMAGES */
.an-grid{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:16px}
.an-fig{border:1px solid var(--line);background:var(--paper)}
.an-fig img{width:100%;height:230px;object-fit:contain;display:block;background:#FAFAF8;padding:10px}
.an-fig figcaption{padding:12px 16px;font-size:12px;font-weight:600;color:var(--steel);
  border-top:1px solid var(--line);line-height:1.45}

/* TABLE */
.tbl{margin-top:26px;border-top:2px solid var(--ink)}
.t-row{display:grid;padding:11px 0;border-bottom:1px solid var(--line);align-items:center;font-size:14px}
.t-row.head{font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;
  color:var(--grey);padding:10px 0;border-bottom:1px solid var(--ink)}
.t-row .gm{font-weight:700;font-size:14px}
.t-row .dt{font-size:11.5px;color:var(--grey);font-weight:400;display:block}
.t-row .v{font-family:'Anton',sans-serif;font-size:18px;color:var(--ink)}
.t-row .v.hot{color:var(--orange)}
.t-row .v.zero{color:#C9C9C9}
.tbl-futsal .t-row{grid-template-columns:1.7fr repeat(6,1fr)}
.tbl-soccer .t-row{grid-template-columns:1.9fr repeat(7,1fr)}

/* RESPONSIVE SWAP + OPTION-B BLOCKS */
.only-narrow{display:none}
.blk-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:22px}
.blk{border:1px solid var(--line);background:var(--paper);padding:16px 16px 14px;min-width:0}
.blk span{display:block}
.blk .bk{font-size:10px;letter-spacing:.12em;text-transform:uppercase;font-weight:700;color:var(--grey)}
.blk .bv{font-family:'Anton',sans-serif;font-size:32px;color:var(--orange);line-height:1.1;margin:5px 0 2px}
.blk .bu{font-size:11.5px;color:var(--steel);line-height:1.35}
.lead{border-top:1px solid var(--line);margin-top:10px}
.lead-row{display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid var(--line)}
.lead-row .pos{font-family:'Anton',sans-serif;font-size:15px;color:var(--grey);width:22px;flex:none}
.lead-row .nm{flex:1;min-width:0;font-size:13.5px;font-weight:600}
.lead-row .dt{display:block;font-size:11px;color:var(--grey);font-weight:400}
.lead-row .val{font-family:'Anton',sans-serif;font-size:22px;color:var(--orange);flex:none}

/* MY AREA — PIN GATE + TRAINING LOG */
.pin-box{margin-top:26px;max-width:340px}
#pin-input{width:100%;font-family:'Anton',sans-serif;font-size:34px;letter-spacing:.5em;
  text-align:center;padding:16px 12px;border:1px solid var(--line);background:var(--paper);
  color:var(--ink);outline:none}
#pin-input:focus{border-color:var(--orange)}
.pin-btn{width:100%;margin-top:12px;background:var(--orange);color:#fff;border:none;
  font-family:'Archivo',sans-serif;font-size:13px;letter-spacing:.18em;text-transform:uppercase;
  font-weight:700;padding:15px;cursor:pointer}
.pin-btn:hover{background:#e55f00}
.pin-err{margin-top:12px;font-size:13.5px;color:#C0392B;min-height:20px}

.yt-link{display:flex;align-items:center;gap:14px;background:var(--ink);color:#fff;
  padding:20px 24px;text-decoration:none;font-size:16px;font-weight:700;margin-top:24px}
.yt-link:hover{background:#222}
.yt-ico{background:#FF0000;padding:7px 12px;font-size:18px;flex:none}

.tsession{border:1px solid var(--line);background:var(--paper);padding:20px 22px;margin-bottom:14px}
.tsession .thead{display:flex;align-items:baseline;justify-content:space-between;gap:12px;
  flex-wrap:wrap;padding-bottom:12px;margin-bottom:14px;border-bottom:1px solid var(--line)}
.tsession .tdate{font-family:'Anton',sans-serif;font-size:20px}
.tsession .tmeta{font-size:12px;letter-spacing:.12em;text-transform:uppercase;font-weight:700;color:var(--grey)}
.tsession .tmeta b{color:var(--orange);font-family:'Anton',sans-serif;font-size:15px;margin-right:5px}
.tcols{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.tcols h4{font-size:11px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;
  color:var(--grey);margin-bottom:7px}
.tcols p{font-size:14px;color:var(--steel);white-space:pre-wrap;line-height:1.55}
@media(max-width:700px){.tcols{grid-template-columns:1fr;gap:16px}}

/* CHARTS */
.chart-grid{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:22px}
.chart-box{border:1px solid var(--line);background:var(--paper);padding:22px 24px 18px}
.ct{font-size:11px;letter-spacing:.2em;text-transform:uppercase;font-weight:700;
  color:var(--steel);display:flex;align-items:center;gap:10px;margin-bottom:14px}
.ct::before{content:"";width:19px;height:3px;background:var(--orange);flex:none}
.chart-box canvas{height:225px !important}
.chart-single{border:1px solid var(--line);background:var(--paper);padding:26px 30px 22px;margin-top:22px}
.chart-single canvas{height:300px !important}
/* soccer data slide: full-width, taller charts (33 bars need the room) */
#soccer-data .chart-grid{grid-template-columns:1fr;gap:22px}
#soccer-data .chart-box{padding:26px 30px 22px}
#soccer-data .chart-box canvas{height:330px !important}
#soccer-data .chart-single canvas{height:340px !important}
.chart-note{display:flex;gap:34px;flex-wrap:wrap;justify-content:center;margin-top:18px;\n  padding-top:16px;border-top:1px solid var(--line)}
.chart-note span{font-size:13px;color:var(--steel)}
.chart-note b{font-family:'Anton',sans-serif;font-size:20px;color:var(--orange);margin-right:8px}

@media(max-width:900px){
  .slide{padding:76px 0 88px}
  .wrap{padding:0 20px}
  .scoreboard{grid-template-columns:repeat(2,1fr)}
  .scoreboard .cell{border-bottom:1px solid var(--line-dark);padding-bottom:22px}
  .hl-grid,.an-grid,.chart-grid{grid-template-columns:1fr}
  /* game tables become cards: one per match, stat chips inside */
  .tbl{border-top:none;margin-top:18px}
  .tbl-futsal .t-row,.tbl-soccer .t-row{
    grid-template-columns:repeat(3,1fr);gap:12px 8px;padding:16px 16px 14px;
    border:1px solid var(--line);background:var(--paper);margin-bottom:12px}
  .bone .tbl .t-row{background:#FAFAF8}
  .t-row .gm{grid-column:1/-1;padding-bottom:10px;margin-bottom:2px;
    border-bottom:1px solid var(--line);font-size:15px}
  .t-row .dt{margin-top:2px}
  .t-row.head{display:none}
  .t-row .v{font-size:22px;display:block;line-height:1}
  .t-row .v::after{content:attr(data-k);display:block;font-family:'Archivo',sans-serif;font-size:9px;
    font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--grey);margin-top:3px}
  .only-wide{display:none}
  .only-narrow{display:block}
  /* charts: JS wraps the canvas in .chart-holder and sizes that; the
     !important here beats the inline height Chart.js writes on each resize */
  .chart-holder canvas,
  #soccer-data .chart-holder canvas,
  #soccer-data .chart-box .chart-holder canvas,
  #soccer-data .chart-single .chart-holder canvas{
    height:100% !important;width:100% !important;max-width:none !important}
  .chart-box,.chart-single{padding:20px 16px 16px}
  .chart-note{gap:18px;justify-content:flex-start}
  .an-fig img{height:190px}
  .nav{padding:0 14px;height:60px}
  .nav-btn{padding:9px 13px;font-size:11px}
  .dots{display:none}
  .tabs{height:56px;gap:6px;padding:0 12px;justify-content:flex-start}
  .tab{padding:8px 12px;font-size:10px;letter-spacing:.09em}
}
"""

SLIDES = [
    # 1 · HERO
    ('dark hero-slide', ARCS, f'''<div class="wrap hero">
      <div class="hero-meta"><span>Sam Brady</span><span>2024 – 2026</span></div>
      <h1 class="display">SAM<br><em>BRADY</em></h1>
      <p class="origin">Perth · 08</p>
      <p class="strap">Performance Dashboard</p>
      <div class="clubs">
        <div class="club"><span class="club-k">Soccer · current club</span>
          <span class="club-n">Fremantle City</span><span class="club-c">NPLW</span><span class="club-p">LAMF · LAMR</span></div>
        <div class="club"><span class="club-k">Futsal · current club</span>
          <span class="club-n">Wolves</span><span class="club-c">Social Supa-Liga</span><span class="club-p">Fixo · Ala</span></div>
      </div>
      <img src="{A['logo']}" alt="TZR Futsal Coaching" class="tzr-logo">
    </div>'''),

    # 2 · COMBINED
    ('dark', WAVES, '''<div class="wrap">
      <div class="eyebrow">Career at a Glance</div>
      <h2 class="display">Combined Output</h2>
      <p class="lede">11 futsal games and 33 soccer games tracked across 2024–2026.</p>
      <div class="scoreboard">
        <div class="cell"><span class="num">44</span><span class="k">Total Games</span><span class="lbl">11 futsal<br>33 soccer</span></div>
        <div class="cell"><span class="num">9</span><span class="k">Goals</span><span class="lbl">7 futsal<br>2 soccer</span></div>
        <div class="cell"><span class="num">8</span><span class="k">Assists</span><span class="lbl">8 futsal<br>0 soccer</span></div>
        <div class="cell"><span class="num">97</span><span class="k">Interceptions</span><span class="lbl">19 futsal<br>78 soccer</span></div>
        <div class="cell"><span class="num">200</span><span class="k">Recoveries</span><span class="lbl">67 futsal<br>133 soccer</span></div>
      </div>
    </div>'''),

    # 3 · SUMMER (everything)
    ('bone', ARCS, f'''<div class="wrap">
      <div class="eyebrow">Futsal · Summer 2025/26</div>
      <h2 class="display">Summer Season</h2>
      <p class="lede">8 games tracked with LiveTag · full campaign.</p>
      <div class="hl-grid">
        {hl('Output','2.7','shots per game',[(53,'total shots'),(20,'on target'),(2,'goals')])}
        {hl('Creation','6','assists',[(225,'accurate passes'),(28,'passes / game'),(196,'minutes')])}
        {hl('Defensive','61','recoveries + intercepts',[(45,'recoveries'),(16,'interceptions'),(25,'losses')])}
      </div>
      <div class="tbl tbl-futsal" id="tbl-summer"></div>
      <div class="chart-grid">
        <div class="chart-box"><div class="ct">Goals &amp; assists per game</div><canvas id="su-ga"></canvas></div>
        <div class="chart-box"><div class="ct">Shots — total vs on target</div><canvas id="su-shot"></canvas></div>
      </div>
      <div class="chart-grid">
        <div class="chart-box"><div class="ct">Accurate passes per game</div><canvas id="su-pass"></canvas></div>
        <div class="chart-box"><div class="ct">Recoveries &amp; interceptions</div><canvas id="su-def"></canvas></div>
      </div>
      <div class="sec-rule"><span>Match Analysis</span></div>
      <div class="an-grid">{summer_figs}</div>
    </div>'''),

    # 4 · WINTER (everything)
    ('paper', WAVES, f'''<div class="wrap">
      <div class="eyebrow">Futsal · Winter 2026</div>
      <h2 class="display">Winter Season</h2>
      <p class="lede">3 games analysed with LiveTag · current season.</p>
      <div class="hl-grid">
        {hl('Finishing','1.1','shots on target per goal',[(16,'total shots'),(8,'on target'),(7,'goals')])}
        {hl('Creation','2','assists',[(87,'accurate passes'),(29,'passes / game'),(11,'losses')])}
        {hl('Defensive','41','recoveries + intercepts',[(22,'recoveries'),(19,'interceptions'),(5,'blocks')])}
      </div>
      <div class="tbl tbl-futsal" id="tbl-winter"></div>
      <div class="chart-grid">
        <div class="chart-box"><div class="ct">Goals &amp; assists per game</div><canvas id="wi-ga"></canvas></div>
        <div class="chart-box"><div class="ct">Recoveries &amp; interceptions</div><canvas id="wi-def"></canvas></div>
      </div>
    </div>'''),

    # 5 · SOCCER overview
    ('dark', ARCS, '''<div class="wrap">
      <div class="eyebrow">Soccer · NPL Women</div>
      <h2 class="display">Soccer Season</h2>
      <p class="lede">33 games for Fremantle City and West NTC across NPL Women, 2024–2026. Wyscout tracking.</p>
      <div class="scoreboard">
        <div class="cell"><span class="num">33</span><span class="k">Games</span><span class="lbl">2024 – 2026</span></div>
        <div class="cell"><span class="num">1765</span><span class="k">Minutes</span><span class="lbl">avg 53.5 / game</span></div>
        <div class="cell"><span class="num">78</span><span class="k">Interceptions</span><span class="lbl">2.4 per game</span></div>
        <div class="cell"><span class="num">133</span><span class="k">Recoveries</span><span class="lbl">4.0 per game</span></div>
        <div class="cell"><span class="num">167</span><span class="k">Duels Won</span><span class="lbl">of 349 total</span></div>
      </div>
    </div>'''),

    # 6 · SOCCER everything
    ('bone', WAVES, '''<div class="wrap" id="soccer-data">
      <div class="eyebrow">Soccer · Defensive Actions</div>
      <h2 class="display">Full Season Data</h2>
      <p class="lede">All 33 games · Fremantle City &amp; West NTC.</p>
      <!-- desktop: full per-match charts -->
      <div class="only-wide">
        <div class="chart-grid">
          <div class="chart-box"><div class="ct">Interceptions per game</div><canvas id="s-int"></canvas></div>
          <div class="chart-box"><div class="ct">Recoveries — own vs opp half</div><canvas id="s-rec"></canvas></div>
        </div>
        <div class="chart-grid">
          <div class="chart-box"><div class="ct">Duels — total vs won</div><canvas id="s-duel"></canvas></div>
          <div class="chart-box"><div class="ct">Passes — accurate vs failed</div><canvas id="s-pass"></canvas></div>
        </div>
        <div class="chart-single"><div class="ct">Minutes played per game</div><canvas id="s-min"></canvas><div class="chart-note"><span><b>53.5</b>average minutes / game</span><span><b>1765</b>total minutes</span><span><b>97</b>longest match</span></div></div>
      </div>

      <!-- phone: season totals, 5-match block averages, best matches -->
      <div class="only-narrow">
        <div class="blk-grid" id="sm-totals"></div>
        <div class="chart-box" style="margin-top:20px"><div class="ct">Interceptions — avg per 5-match block</div><canvas id="sm-int"></canvas></div>
        <div class="chart-box" style="margin-top:16px"><div class="ct">Recoveries — avg per 5-match block</div><canvas id="sm-rec"></canvas></div>
        <div class="chart-box" style="margin-top:16px"><div class="ct">Minutes — avg per 5-match block</div><canvas id="sm-min"></canvas><div class="chart-note"><span><b>53.5</b>average minutes / game</span><span><b>1765</b>total minutes</span><span><b>97</b>longest match</span></div></div>
        <div class="ct" style="margin-top:26px">Best matches — interceptions</div>
        <div class="lead" id="sm-lead-int"></div>
        <div class="ct" style="margin-top:26px">Best matches — recoveries</div>
        <div class="lead" id="sm-lead-rec"></div>
      </div>
      <div class="sec-rule"><span>Game by Game</span></div>
      <div class="tbl tbl-soccer" id="tbl-soccer"></div>
    </div>'''),

    # 7 · DEFENSIVE PROFILE
    ('dark', ARCS, '''<div class="wrap">
      <div class="eyebrow">Player Profile</div>
      <h2 class="display">Defensive<br><em style="font-style:normal;color:var(--orange)">Profile</em></h2>
      <p class="lede">Ball-winning is the strongest part of her game — top-5 in WA NPLW across every defensive metric tracked.</p>
      <div class="prof-grid">
        <div class="prof"><span class="prof-rank">#1</span><span class="prof-k">Defensive Duels</span>
          <span class="prof-v">10.77</span><span class="prof-u">per 90 · 69% won</span></div>
        <div class="prof"><span class="prof-rank">#4</span><span class="prof-k">Recoveries</span>
          <span class="prof-v">13.79</span><span class="prof-u">per 90 · 200 total</span></div>
        <div class="prof"><span class="prof-rank">#5</span><span class="prof-k">Interceptions</span>
          <span class="prof-v">6.86</span><span class="prof-u">per 90 · 97 total</span></div>
      </div>
      <div style="margin-top:34px;border-top:2px solid var(--orange)">
        <div class="stat-row"><span class="n">01</span><h3>Duels</h3>
          <p>167 duels won from 349 contested in soccer, plus 7 in futsal. <strong>#1 in WA NPLW</strong> for defensive duels per 90 — she competes for everything.</p></div>
        <div class="stat-row"><span class="n">02</span><h3>Recoveries</h3>
          <p>133 soccer + 67 futsal recoveries. Peaks of 10 in a single match. Works both halves of the pitch, not just behind the ball.</p></div>
        <div class="stat-row" style="border-bottom:none"><span class="n">03</span><h3>Interceptions</h3>
          <p>78 in soccer, 19 in futsal. Best game: 11 interceptions vs West NTC. Reads passing lanes early rather than reacting late.</p></div>
      </div>
    </div>'''),

    # 8 · ATTACKING PROFILE
    ('dark', WAVES, '''<div class="wrap">
      <div class="eyebrow">Player Profile</div>
      <h2 class="display">Attacking<br><em style="font-style:normal;color:var(--orange)">Profile</em></h2>
      <p class="lede">Sharpest in futsal — 7 goals in 3 Winter games at 1.1 shots on target per goal.</p>
      <div class="prof-grid">
        <div class="prof"><span class="prof-rank">9</span><span class="prof-k">Goals</span>
          <span class="prof-v">7+2</span><span class="prof-u">futsal + soccer</span></div>
        <div class="prof"><span class="prof-rank">8</span><span class="prof-k">Assists</span>
          <span class="prof-v">6+2</span><span class="prof-u">summer + winter</span></div>
        <div class="prof"><span class="prof-rank">1.1</span><span class="prof-k">Shot Efficiency</span>
          <span class="prof-v">35%</span><span class="prof-u">on-target rate</span></div>
      </div>
      <div style="margin-top:34px;border-top:2px solid var(--orange)">
        <div class="stat-row"><span class="n">01</span><h3>Finishing</h3>
          <p>Winter 2026: <strong>7 goals from 8 shots on target</strong> — 1.1 shots on target per goal. Ruthless once the chance is created.</p></div>
        <div class="stat-row"><span class="n">02</span><h3>Volume &amp; Creation</h3>
          <p>69 futsal shots across 11 games (6.3 per game) plus 8 assists across both futsal seasons. She generates chances for herself and others.</p></div>
        <div class="stat-row" style="border-bottom:none"><span class="n">03</span><h3>Distribution</h3>
          <p>312 accurate futsal passes and 3.57 xG in soccer. Consistently involved in build-up rather than only at the end of moves.</p></div>
      </div>
    </div>'''),

    # 9 · MY AREA (PIN)
    ('paper', WAVES, '''<div class="wrap">
      <div class="eyebrow">Private</div>
      <h2 class="display">My Area</h2>

      <div id="pin-gate">
        <p class="lede">Enter your PIN to see your training log and analysis videos.</p>
        <div class="pin-box">
          <input id="pin-input" type="password" inputmode="numeric" pattern="[0-9]*"
                 maxlength="4" placeholder="••••" autocomplete="off">
          <button id="pin-go" class="pin-btn">Enter</button>
          <p id="pin-err" class="pin-err"></p>
        </div>
      </div>

      <div id="pin-content" hidden>
        <p class="lede">Hi Sam — everything from your sessions in one place.</p>

        <a class="yt-link" href="''' + PLAYLIST + '''" target="_blank" rel="noopener">
          <span class="yt-ico">&#9654;</span>
          <span>Full video playlist — match analysis (YouTube)</span>
        </a>

        <div class="sec-rule"><span>Training Log</span></div>
        <div id="tlog"></div>
      </div>
    </div>'''),
]

STAT_ROW_CSS = """
.stat-row{display:grid;grid-template-columns:76px 240px 1fr;gap:28px;align-items:baseline;
  padding:22px 0;border-bottom:1px solid var(--line-dark)}
.stat-row .n{font-family:'Anton',sans-serif;font-size:32px;color:transparent;-webkit-text-stroke:1.5px var(--orange)}
.stat-row h3{font-size:16.5px;font-weight:700;color:#fff}
.stat-row p{color:rgba(255,255,255,.62);font-size:14.5px}
.stat-row p strong{color:var(--orange)}
.prof-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:30px}
.prof{border:1px solid var(--line-dark);padding:24px 26px 26px;background:rgba(255,255,255,.03)}
.prof-rank{font-family:'Anton',sans-serif;font-size:44px;line-height:1;color:var(--orange);display:block}
.prof-k{font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;
  color:#fff;display:block;margin:10px 0 16px;padding-bottom:12px;border-bottom:1px solid var(--line-dark)}
.prof-v{font-family:'Anton',sans-serif;font-size:26px;color:#fff;display:block}
.prof-u{font-size:12.5px;color:rgba(255,255,255,.5);display:block;margin-top:4px}
@media(max-width:900px){
  .stat-row{grid-template-columns:54px 1fr;gap:8px 16px}.stat-row p{grid-column:2}
  .prof-grid{grid-template-columns:1fr}
}
"""

slides_html = "\n".join(
    f'  <div class="slide {cls}{" active" if i == 0 else ""}">\n    {bg}\n    {body}\n  </div>\n'
    for i, (cls, bg, body) in enumerate(SLIDES)
)

SECTIONS = [("Overview", 0, 2), ("Summer", 2, 3), ("Winter", 3, 4), ("Soccer", 4, 6), ("Defensive", 6, 7), ("Attacking", 7, 8), ("My Area", 8, 9)]
sections_js = ",\n  ".join(f'{{label:"{l}",start:{s},end:{e}}}' for l, s, e in SECTIONS)

JS_DATA = """
const FUTSAL=[
{s:"Summer",g:"Cobras",min:25.5,pass:23,shot:7,shotOT:3,goal:1,assist:1,rec:6,lost:4,int:0},
{s:"Summer",g:"SPA",min:24.7,pass:28,shot:6,shotOT:2,goal:0,assist:1,rec:7,lost:1,int:0},
{s:"Summer",g:"Cumbre",min:19.1,pass:22,shot:6,shotOT:2,goal:0,assist:2,rec:10,lost:2,int:2},
{s:"Summer",g:"Perth United",min:29.6,pass:36,shot:7,shotOT:2,goal:0,assist:1,rec:7,lost:2,int:3},
{s:"Summer",g:"Cobras 2",min:29.6,pass:38,shot:11,shotOT:4,goal:0,assist:0,rec:2,lost:4,int:5},
{s:"Summer",g:"Internacional (B)",min:27.7,pass:14,shot:8,shotOT:3,goal:0,assist:0,rec:7,lost:3,int:0},
{s:"Summer",g:"Cobras Semi-Final",min:21.1,pass:37,shot:2,shotOT:2,goal:1,assist:1,rec:5,lost:4,int:2},
{s:"Summer",g:"SPA (Final B)",min:18.75,pass:27,shot:6,shotOT:2,goal:0,assist:0,rec:1,lost:5,int:4},
{s:"Winter",g:"Internationale",min:0,pass:34,shot:3,shotOT:0,goal:2,assist:2,rec:15,lost:7,int:8},
{s:"Winter",g:"Perth United",min:0,pass:20,shot:10,shotOT:7,goal:2,assist:0,rec:3,lost:2,int:5},
{s:"Winter",g:"SPA",min:0,pass:33,shot:3,shotOT:1,goal:3,assist:0,rec:4,lost:2,int:6}
];

const SOCCER=[{"g":"Subiaco 2:0","d":"2026-07-19","min":97,"goal":0,"pass":18,"passFail":8,"intercept":1,"recOwn":3,"recOpp":9,"duelT":29,"duelW":13,"shot":2,"shotOT":1},{"g":"Perth RedStar 2:0","d":"2026-07-12","min":48,"goal":0,"pass":12,"passFail":7,"intercept":5,"recOwn":0,"recOpp":4,"duelT":14,"duelW":3,"shot":1,"shotOT":1},{"g":"West NTC 1:2","d":"2026-07-04","min":30,"goal":0,"pass":5,"passFail":5,"intercept":1,"recOwn":2,"recOpp":2,"duelT":10,"duelW":5,"shot":0,"shotOT":0},{"g":"Perth 2:1","d":"2026-06-28","min":20,"goal":0,"pass":3,"passFail":4,"intercept":1,"recOwn":1,"recOpp":0,"duelT":1,"duelW":1,"shot":1,"shotOT":0},{"g":"Sorrento 3:4","d":"2026-06-21","min":95,"goal":0,"pass":21,"passFail":2,"intercept":3,"recOwn":2,"recOpp":4,"duelT":6,"duelW":5,"shot":2,"shotOT":0},{"g":"Balcatta 3:3","d":"2026-05-15","min":46,"goal":0,"pass":4,"passFail":4,"intercept":0,"recOwn":2,"recOpp":0,"duelT":6,"duelW":3,"shot":0,"shotOT":0},{"g":"West NTC 0:1","d":"2026-05-03","min":96,"goal":0,"pass":24,"passFail":14,"intercept":11,"recOwn":5,"recOpp":6,"duelT":31,"duelW":11,"shot":1,"shotOT":0},{"g":"Perth RedStar 1:2","d":"2026-04-26","min":93,"goal":1,"pass":18,"passFail":12,"intercept":7,"recOwn":6,"recOpp":2,"duelT":8,"duelW":3,"shot":1,"shotOT":1},{"g":"Sorrento 4:0","d":"2026-04-19","min":56,"goal":0,"pass":23,"passFail":3,"intercept":3,"recOwn":1,"recOpp":5,"duelT":13,"duelW":8,"shot":3,"shotOT":2},{"g":"Perth 0:0","d":"2026-04-10","min":95,"goal":0,"pass":23,"passFail":6,"intercept":3,"recOwn":0,"recOpp":1,"duelT":14,"duelW":6,"shot":0,"shotOT":0},{"g":"Subiaco 2:1","d":"2026-04-05","min":94,"goal":0,"pass":19,"passFail":9,"intercept":7,"recOwn":2,"recOpp":4,"duelT":26,"duelW":14,"shot":1,"shotOT":0},{"g":"UWA Nedlands 5:0","d":"2026-03-29","min":14,"goal":0,"pass":3,"passFail":1,"intercept":1,"recOwn":0,"recOpp":1,"duelT":2,"duelW":2,"shot":0,"shotOT":0},{"g":"Perth RedStar 2:2","d":"2026-03-22","min":49,"goal":0,"pass":9,"passFail":5,"intercept":1,"recOwn":2,"recOpp":1,"duelT":6,"duelW":4,"shot":1,"shotOT":0},{"g":"Perth 4:2","d":"2025-08-24","min":11,"goal":0,"pass":0,"passFail":1,"intercept":2,"recOwn":1,"recOpp":0,"duelT":0,"duelW":0,"shot":0,"shotOT":0},{"g":"Subiaco 1:2","d":"2025-08-16","min":46,"goal":0,"pass":12,"passFail":5,"intercept":2,"recOwn":1,"recOpp":1,"duelT":4,"duelW":4,"shot":0,"shotOT":0},{"g":"Perth RedStar 4:1","d":"2025-08-13","min":7,"goal":0,"pass":2,"passFail":1,"intercept":0,"recOwn":0,"recOpp":0,"duelT":1,"duelW":0,"shot":0,"shotOT":0},{"g":"UWA Nedlands 1:1","d":"2025-08-10","min":63,"goal":0,"pass":25,"passFail":11,"intercept":2,"recOwn":3,"recOpp":4,"duelT":20,"duelW":9,"shot":0,"shotOT":0},{"g":"Murdoch Uni 0:4","d":"2025-08-03","min":95,"goal":0,"pass":9,"passFail":5,"intercept":3,"recOwn":3,"recOpp":1,"duelT":12,"duelW":6,"shot":3,"shotOT":1},{"g":"West NTC 5:1","d":"2025-07-27","min":89,"goal":0,"pass":18,"passFail":10,"intercept":7,"recOwn":10,"recOpp":1,"duelT":9,"duelW":5,"shot":0,"shotOT":0},{"g":"Perth 0:4","d":"2025-07-06","min":48,"goal":0,"pass":15,"passFail":5,"intercept":1,"recOwn":4,"recOpp":3,"duelT":8,"duelW":7,"shot":0,"shotOT":0},{"g":"UWA Nedlands 12:2","d":"2025-06-25","min":92,"goal":1,"pass":20,"passFail":12,"intercept":3,"recOwn":4,"recOpp":4,"duelT":24,"duelW":14,"shot":2,"shotOT":1},{"g":"Subiaco 3:5","d":"2025-06-15","min":13,"goal":0,"pass":1,"passFail":1,"intercept":0,"recOwn":0,"recOpp":0,"duelT":1,"duelW":1,"shot":0,"shotOT":0},{"g":"Murdoch Uni 4:0","d":"2025-06-07","min":93,"goal":0,"pass":16,"passFail":11,"intercept":5,"recOwn":2,"recOpp":3,"duelT":16,"duelW":2,"shot":1,"shotOT":0},{"g":"West NTC 2:4","d":"2025-06-01","min":7,"goal":0,"pass":0,"passFail":0,"intercept":0,"recOwn":0,"recOpp":0,"duelT":1,"duelW":0,"shot":0,"shotOT":0},{"g":"Perth RedStar 2:3","d":"2025-05-24","min":20,"goal":0,"pass":4,"passFail":3,"intercept":1,"recOwn":2,"recOpp":0,"duelT":8,"duelW":7,"shot":0,"shotOT":0},{"g":"Perth 3:0","d":"2025-05-04","min":13,"goal":0,"pass":1,"passFail":2,"intercept":0,"recOwn":1,"recOpp":0,"duelT":2,"duelW":0,"shot":0,"shotOT":0},{"g":"Subiaco 1:3","d":"2025-04-27","min":68,"goal":0,"pass":19,"passFail":11,"intercept":3,"recOwn":1,"recOpp":2,"duelT":13,"duelW":6,"shot":2,"shotOT":0},{"g":"UWA Nedlands 1:4","d":"2025-04-20","min":49,"goal":0,"pass":14,"passFail":4,"intercept":3,"recOwn":5,"recOpp":2,"duelT":9,"duelW":5,"shot":0,"shotOT":0},{"g":"Murdoch Uni 0:4","d":"2025-04-13","min":35,"goal":0,"pass":7,"passFail":5,"intercept":0,"recOwn":2,"recOpp":0,"duelT":7,"duelW":3,"shot":0,"shotOT":0},{"g":"Perth RedStar 1:2","d":"2025-03-30","min":9,"goal":0,"pass":2,"passFail":1,"intercept":1,"recOwn":0,"recOpp":0,"duelT":2,"duelW":2,"shot":0,"shotOT":0},{"g":"Balcatta 3:0","d":"2025-03-23","min":7,"goal":0,"pass":1,"passFail":1,"intercept":1,"recOwn":1,"recOpp":0,"duelT":0,"duelW":0,"shot":0,"shotOT":0},{"g":"Perth 0:4","d":"2024-06-29","min":86,"goal":0,"pass":4,"passFail":3,"intercept":0,"recOwn":2,"recOpp":2,"duelT":16,"duelW":9,"shot":1,"shotOT":0},{"g":"Balcatta 3:0","d":"2024-06-21","min":81,"goal":0,"pass":16,"passFail":5,"intercept":0,"recOwn":1,"recOpp":2,"duelT":23,"duelW":9,"shot":0,"shotOT":0}];
"""

JS_MAIN = r"""
const O='#FF6B00', Osoft='rgba(255,107,0,.30)', INK='#0B0B0C', GREY='#C4C4C6';
Chart.defaults.font.family="'Archivo',system-ui,sans-serif";
Chart.defaults.color='#5C5C60';

function cell(v,label,hot){
  const cls = v===0 ? 'v zero' : (hot ? 'v hot' : 'v');
  return '<span class="'+cls+'" data-k="'+label+'">'+v+'</span>';
}
const MOBILE = window.matchMedia('(max-width:700px)').matches;
const CHARTS = [];

function mk(id, labels, datasets){
  const el=document.getElementById(id); if(!el) return;
  // On phones, flip to horizontal bars: 33 matches read as a vertical list
  // instead of unreadable hair-thin columns.
  if(MOBILE){
    const rowPx = datasets.length>1 ? 26 : 20;
    const h = Math.max(200, labels.length * rowPx + 56);
    const holder = document.createElement('div');
    holder.className = 'chart-holder';
    holder.style.cssText = 'position:relative;width:100%;height:'+h+'px';
    el.replaceWith(holder); holder.appendChild(el);
    el.style.setProperty('height', '100%', 'important');
    el.style.setProperty('width', '100%', 'important');
  }
  const cat = {grid:{display:false},ticks:{font:{size:MOBILE?11:10},color:'#5C5C60',
               maxRotation:MOBILE?0:60,minRotation:MOBILE?0:60,autoSkip:false}};
  const val = {grid:{color:'rgba(0,0,0,.07)'},ticks:{font:{size:11.5},color:'#5C5C60',precision:0},beginAtZero:true};
  const chart = new Chart(el,{
    type:'bar', data:{labels, datasets},
    options:{
      indexAxis: MOBILE ? 'y' : 'x',
      responsive:true, maintainAspectRatio:false,
      plugins:{legend:{display:datasets.length>1,labels:{boxWidth:11,font:{size:11.5},color:'#333',padding:12}}},
      scales: MOBILE ? {x:val, y:cat} : {x:cat, y:val}
    }
  });
  CHARTS.push(chart);
}

const SUM = FUTSAL.filter(f=>f.s==='Summer');
const WIN = FUTSAL.filter(f=>f.s==='Winter');
const FHEAD = '<div class="t-row head"><span>Game</span><span>Goals</span><span>Assists</span><span>Shots</span><span>Passes</span><span>Recov.</span><span>Intercept</span></div>';
function futsalRows(arr){
  return arr.map(f=>'<div class="t-row"><span class="gm">'+f.g+'</span>'
    +cell(f.goal,'Goals',true)+cell(f.assist,'Assists')+cell(f.shot,'Shots')
    +cell(f.pass,'Passes')+cell(f.rec,'Recov.')+cell(f.int,'Intercept')+'</div>').join('');
}
document.getElementById('tbl-summer').innerHTML = FHEAD + futsalRows(SUM);
document.getElementById('tbl-winter').innerHTML = FHEAD + futsalRows(WIN);

document.getElementById('tbl-soccer').innerHTML =
  '<div class="t-row head"><span>Game</span><span>Min</span><span>Goals</span><span>Shots</span><span>Passes</span><span>Duels W</span><span>Recov.</span><span>Intercept</span></div>' +
  SOCCER.map(s=>'<div class="t-row"><span class="gm">'+s.g+'<span class="dt">'+s.d+'</span></span>'
    +cell(s.min,'Min')+cell(s.goal,'Goals',true)+cell(s.shot,'Shots')+cell(s.pass,'Passes')
    +cell(s.duelW,'Duels W')+cell(s.recOwn+s.recOpp,'Recov.')+cell(s.intercept,'Intercept')+'</div>').join('');

const SUL=SUM.map(f=>f.g), WIL=WIN.map(f=>f.g);
mk('su-ga',SUL,[{label:'Goals',data:SUM.map(f=>f.goal),backgroundColor:O,borderRadius:2},
                {label:'Assists',data:SUM.map(f=>f.assist),backgroundColor:Osoft,borderRadius:2}]);
mk('su-shot',SUL,[{label:'Total shots',data:SUM.map(f=>f.shot),backgroundColor:Osoft,borderRadius:2},
                  {label:'On target',data:SUM.map(f=>f.shotOT),backgroundColor:O,borderRadius:2}]);
mk('su-pass',SUL,[{label:'Accurate passes',data:SUM.map(f=>f.pass),backgroundColor:O,borderRadius:2}]);
mk('su-def',SUL,[{label:'Recoveries',data:SUM.map(f=>f.rec),backgroundColor:O,borderRadius:2},
                 {label:'Interceptions',data:SUM.map(f=>f.int),backgroundColor:INK,borderRadius:2}]);
mk('wi-ga',WIL,[{label:'Goals',data:WIN.map(f=>f.goal),backgroundColor:O,borderRadius:2},
                {label:'Assists',data:WIN.map(f=>f.assist),backgroundColor:Osoft,borderRadius:2}]);
mk('wi-def',WIL,[{label:'Recoveries',data:WIN.map(f=>f.rec),backgroundColor:O,borderRadius:2},
                 {label:'Interceptions',data:WIN.map(f=>f.int),backgroundColor:INK,borderRadius:2}]);

const SR=[...SOCCER].reverse(), SL=SR.map((s,n)=>'Match '+(n+1));

if(!MOBILE){
  mk('s-int',SL,[{label:'Interceptions',data:SR.map(s=>s.intercept),backgroundColor:O,borderRadius:2}]);
  mk('s-rec',SL,[{label:'Own half',data:SR.map(s=>s.recOwn),backgroundColor:Osoft,borderRadius:2},
                 {label:'Opp half',data:SR.map(s=>s.recOpp),backgroundColor:O,borderRadius:2}]);
  mk('s-duel',SL,[{label:'Total duels',data:SR.map(s=>s.duelT),backgroundColor:Osoft,borderRadius:2},
                  {label:'Won',data:SR.map(s=>s.duelW),backgroundColor:O,borderRadius:2}]);
  mk('s-pass',SL,[{label:'Accurate',data:SR.map(s=>s.pass),backgroundColor:O,borderRadius:2},
                  {label:'Failed',data:SR.map(s=>s.passFail),backgroundColor:GREY,borderRadius:2}]);
  mk('s-min',SL,[{label:'Minutes',data:SR.map(s=>s.min),backgroundColor:INK,borderRadius:2}]);
} else {
  // Phone view: 33 per-match bars are unreadable, so summarise the season —
  // totals, 5-match block averages, and the standout games.
  const sum=(f)=>SR.reduce((a,g)=>a+f(g),0);
  const rec=(g)=>g.recOwn+g.recOpp;
  const totals=[
    ['Interceptions', sum(g=>g.intercept), (sum(g=>g.intercept)/SR.length).toFixed(1)+' per game'],
    ['Recoveries',    sum(rec),            (sum(rec)/SR.length).toFixed(1)+' per game'],
    ['Minutes',       sum(g=>g.min),       (sum(g=>g.min)/SR.length).toFixed(1)+' per game'],
    ['Duels won',     sum(g=>g.duelW),     'of '+sum(g=>g.duelT)+' contested']
  ];
  document.getElementById('sm-totals').innerHTML = totals.map(([k,v,u])=>
    '<div class="blk"><span class="bk">'+k+'</span><span class="bv">'+v+'</span><span class="bu">'+u+'</span></div>'
  ).join('');

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

  leaders('sm-lead-int', g=>g.intercept);
  leaders('sm-lead-rec', rec);

  function leaders(id, f){
    const top=SR.map((g,n)=>({...g,n:n+1})).sort((a,b)=>f(b)-f(a)).slice(0,5);
    document.getElementById(id).innerHTML = top.map((g,i)=>
      '<div class="lead-row"><span class="pos">'+(i+1)+'</span>'
      +'<span class="nm">'+g.g+'<span class="dt">Match '+g.n+' · '+g.d+'</span></span>'
      +'<span class="val">'+f(g)+'</span></div>').join('');
  }
}

// Compact vertical-bar chart for the phone block summaries (only 7 bars, so
// upright columns stay readable).
function mkBlocks(id, labels, data, colour){
  const el=document.getElementById(id); if(!el) return;
  const holder=document.createElement('div');
  holder.className='chart-holder';
  holder.style.cssText='position:relative;width:100%;height:210px';
  el.replaceWith(holder); holder.appendChild(el);
  CHARTS.push(new Chart(el,{
    type:'bar',
    data:{labels, datasets:[{data, backgroundColor:colour, borderRadius:2}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},
      scales:{x:{grid:{display:false},ticks:{font:{size:10},maxRotation:45,minRotation:45}},
              y:{grid:{color:'rgba(0,0,0,.07)'},ticks:{font:{size:11}},beginAtZero:true}}}
  }));
}

/* MY AREA */
const TRAINING = __TRAINING_JSON__;
const PIN = '2109';

function renderTraining(){
  const el = document.getElementById('tlog');
  if(!el) return;
  const sorted = [...TRAINING].sort((a,b)=>(b.date||'').localeCompare(a.date||''));
  el.innerHTML = sorted.map(t=>{
    // the spreadsheet cells carry stray markdown (**bold**, leading '* ')
    const esc = v => (v||'')
      .replace(/</g,'&lt;')
      .replace(/\*\*/g,'')
      .replace(/^[ \t]*\*[ \t]+/gm,'')
      .replace(/\n{3,}/g,'\n\n')
      .trim();
    return '<div class="tsession">'
      +'<div class="thead"><span class="tdate">'+esc(t.date)+'</span>'
      +'<span class="tmeta"><b>'+esc(t.load)+'</b>load</span>'
      +'<span class="tmeta"><b>'+esc(t.hours)+'</b>duration</span></div>'
      +'<div class="tcols">'
      +'<div><h4>Content</h4><p>'+esc(t.content)+'</p></div>'
      +(t.why?'<div><h4>Why this training</h4><p>'+esc(t.why)+'</p></div>':'')
      +'</div></div>';
  }).join('');
}

(function pinGate(){
  const input=document.getElementById('pin-input');
  const btn=document.getElementById('pin-go');
  const err=document.getElementById('pin-err');
  const gate=document.getElementById('pin-gate');
  const content=document.getElementById('pin-content');
  if(!input) return;

  function unlock(){
    gate.hidden=true; content.hidden=false;
    try{ sessionStorage.setItem('tzr_myarea','1'); }catch(e){}
    renderTraining();
  }
  function check(){
    if(input.value.trim()===PIN){ err.textContent=''; unlock(); }
    else { err.textContent='Wrong PIN — try again.'; input.value=''; input.focus(); }
  }
  btn.onclick=check;
  input.addEventListener('keydown',e=>{ if(e.key==='Enter') check(); });
  try{ if(sessionStorage.getItem('tzr_myarea')==='1') unlock(); }catch(e){}
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
<style>{CSS}{STAT_ROW_CSS}</style>
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
{JS_DATA}
const SECTIONS=[
  {sections_js}
];
{JS_MAIN}
</script>
</body>
</html>
"""

html = html.replace("__TRAINING_JSON__", json.dumps(TRAINING, ensure_ascii=False))
OUT.write_text(html, encoding="utf-8")
print(f"Built {OUT} — {len(SLIDES)} slides, {len(html)/1024/1024:.2f} MB")
