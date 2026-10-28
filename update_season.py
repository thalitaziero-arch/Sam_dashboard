#!/usr/bin/env python3
"""
Feed Sam's per-game video analysis (current season) from a spreadsheet into
the portfolio site, then rebuild, commit and push.

Usage:
    python3 update_season.py --init        # create the spreadsheet from the current data
    python3 update_season.py               # spreadsheet -> data/season_2026_27.json -> build -> push
    python3 update_season.py --no-push     # same, but stop before git
    python3 update_season.py /path/to/file.xlsx

One row per game. Leave a number cell empty when it was not counted. A game
with no numbers shows "coming soon" on the site. New rows become new games.
"""
import sys
import json
import subprocess
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

REPO_DIR = Path(__file__).parent
JSON_PATH = REPO_DIR / "data" / "season_2026_27.json"
DEFAULT_XLSX = Path.home() / "Desktop" / "Sam_2026_27_analise.xlsx"

COMPETITIONS = {"Community League": "community", "F League": "fleague"}

# (header shown to the coach, key in the JSON, width)
INFO_COLS = [
    ("Competition", "competition", 18), ("Round", "round", 8), ("Opponent", "opp", 20),
    ("Result (e.g. W 7-4)", "res", 18), ("Date", "date", 12), ("Video link (YouTube)", "video", 40),
]
NUM_COLS = [
    ("Shots on target (incl. goals)", "shots_on_goal", 14), ("Goals", "goals", 8),
    ("Passes OK", "passes_ok", 10), ("Passes failed", "passes_fail", 10),
    ("Passes, destination not visible", "passes_unseen", 14),
    ("Interceptions", "interceptions", 13), ("Recoveries (all)", "recoveries", 12),
    ("Pressures", "pressures", 10), ("Duels won", "duels_won", 10), ("Duels lost", "duels_lost", 10),
    ("Duels unclear", "duels_unclear", 10),
    ("Dribbles tried", "dribbles", 10), ("Dribbles OK", "dribbles_ok", 10),
    ("Wing runs right", "wing_right", 10), ("Wing runs left", "wing_left", 10),
    ("Carries", "carries", 9), ("Ball losses", "ball_losses", 10), ("Attack involvement", "attack_runs", 11),
    ("Actions reviewed (n)", "n_actions", 11),
]
TAIL_COLS = [("Note (optional)", "note", 50)]
COLS = INFO_COLS + NUM_COLS + TAIL_COLS
NUM_KEYS = [k for _, k, _ in NUM_COLS]


# ---------------------------------------------------------------- json <-> rows
def game_to_row(comp_name, g):
    an = g.get("analysis", {})
    m = an.get("m", {})
    row = {"competition": comp_name, "round": g["round"], "opp": g.get("opp", ""),
           "res": g.get("res", ""), "date": g.get("date", ""), "video": g.get("video") or ""}
    for k in NUM_KEYS:
        if k == "duels_won":
            v = m.get("duels_won", "")
        elif k == "duels_unclear":
            v = (m["duels"] - m["duels_lost"] - m.get("duels_won", 0)) if "duels" in m and "duels_lost" in m else ""
        elif k == "n_actions":
            v = an.get("n_actions", "")
        else:
            v = m.get(k, "")
        row[k] = v
    row["note"] = an.get("note", "") if an.get("m") else an.get("note", "")
    return row


def build_analysis(r, old):
    """Rebuild the analysis block from one spreadsheet row."""
    n = lambda k: int(r.get(k) or 0)
    filled = any(r.get(k) not in (None, "") for k in NUM_KEYS if k != "n_actions")
    an = {"title": "Individual video analysis · #5", "m": {}, "items": [], "read": [],
          "pending": "Numbers for this round are coming soon.", "note": str(r.get("note") or "")}
    if not filled:
        return an
    sog, goals = n("shots_on_goal"), n("goals")
    p_ok, p_bad, p_un = n("passes_ok"), n("passes_fail"), n("passes_unseen")
    d_won, d_lost, d_unc = n("duels_won"), n("duels_lost"), n("duels_unclear")
    duels = d_won + d_lost + d_unc
    wr, wl = n("wing_right"), n("wing_left")
    drib, drib_ok = n("dribbles"), n("dribbles_ok")
    m = {"shots_on_goal": sog, "goals": goals, "wing_runs": wr + wl, "wing_right": wr, "wing_left": wl,
         "dribbles": drib, "dribbles_ok": drib_ok, "recoveries": n("recoveries"),
         "interceptions": n("interceptions"), "passes": p_ok + p_bad + p_un, "passes_ok": p_ok,
         "passes_fail": p_bad, "passes_unseen": p_un, "carries": n("carries"),
         "pressures": n("pressures"), "duels": duels, "duels_won": d_won, "duels_lost": d_lost,
         "ball_losses": n("ball_losses"), "attack_runs": n("attack_runs")}
    an["m"] = m
    saved = max(sog - goals, 0)
    items = [["Shots on goal", str(sog), f"{goals} goal{'s' if goals != 1 else ''} · {saved} saved"]]
    if wr + wl:
        items.append(["Wing runs", str(wr + wl), f"right {wr} · left {wl}"])
    if drib:
        items.append(["Dribbles", f"{drib_ok}/{drib}", f"{drib_ok} successful · {drib - drib_ok} failed"])
    if n("interceptions"):
        items.append(["Interceptions", str(n("interceptions")), "passing lanes read and cut"])
    if n("recoveries"):
        items.append(["Recoveries", str(n("recoveries")), "steals, interceptions, loose balls won"])
    if m["passes"]:
        tail = f"{p_ok} completed · {p_bad} failed" + (f" · {p_un} destination off-frame" if p_un else "")
        items.append(["Passes", str(m["passes"]), tail])
    if m["carries"]:
        items.append(["Carries", str(m["carries"]), "ball carries outside the wing runs"])
    if m["pressures"]:
        items.append(["Pressure", str(m["pressures"]), "pressed the opponent on the ball"])
    if duels:
        bits = [f"{d_won} won" if d_won else "", f"{d_lost} lost" if d_lost else "", f"{d_unc} unclear" if d_unc else ""]
        items.append(["1v1 duels", str(duels), " · ".join(b for b in bits if b)])
    if m["ball_losses"]:
        items.append(["Ball losses", str(m["ball_losses"]), "includes the failed dribbles"])
    if m["attack_runs"]:
        items.append(["Attack involvement", str(m["attack_runs"]), "appeared in the box / supported the play"])
    an["items"] = items

    read = []
    if m["recoveries"] or m["pressures"]:
        read.append(f"Ball-winning: {m['recoveries']} recoveries"
                    + (f" ({m['interceptions']} interceptions)" if m["interceptions"] else "")
                    + (f" and {m['pressures']} direct pressures." if m["pressures"] else "."))
    if p_ok + p_bad:
        read.append(f"Passing: of the passes with a visible destination, {p_ok} were completed and {p_bad} failed.")
    if wr + wl:
        read.append(f"Wing runs: {wr} right, {wl} left.")
    if (drib - drib_ok) or d_lost:
        read.append(f"To improve: 1v1 situations ({drib - drib_ok} failed dribbles, {d_lost} duels lost).")
    read.append(f"{sog} shot{'s' if sog != 1 else ''} on goal, {goals} scored." if sog or goals
                else "No shots on goal in the reviewed actions.")
    an["read"] = read
    if not an["note"]:
        nn = r.get("n_actions")
        an["note"] = ((f"Verified sample of {int(nn)} actions, not 100% of the match. " if nn else
                       "Verified sample, not 100% of the match. ")
                      + "Plays far from the camera or with fast camera movement were left out, "
                        "and short quick passes tend to be undercounted.")
    if nn := r.get("n_actions"):
        an["n_actions"] = int(nn)
    # numbers unchanged since last time: keep the hand-written text of that round
    if old.get("m") and all(m.get(k) == v for k, v in old["m"].items()) and an["note"] == old.get("note"):
        return old
    return an


def apply_row(data, r):
    comp = next((c for c in data["competitions"] if c["name"] == r["competition"]), None)
    if comp is None:
        comp = {"key": COMPETITIONS.get(r["competition"], r["competition"].lower().replace(" ", "")),
                "name": r["competition"], "club": "Cockburn Wolves", "games": []}
        data["competitions"].append(comp)
    rnd = int(r["round"])
    g = next((x for x in comp["games"] if x["round"] == rnd), None)
    if g is None:
        g = {"round": rnd, "src": "video"}
        comp["games"].append(g)
        comp["games"].sort(key=lambda x: x["round"])
    for k in ("opp", "res", "date"):
        if r.get(k):
            g[k] = str(r[k]).strip()
        else:
            g.pop(k, None)
    g["video"] = str(r["video"]).strip() if r.get("video") else None
    g["analysis"] = build_analysis(r, g.get("analysis", {}))
    if g["analysis"]["m"]:
        g["goal"] = g["analysis"]["m"]["goals"]
        g["shotOT"] = g["analysis"]["m"]["shots_on_goal"]


# ---------------------------------------------------------------- excel
def write_template(path, data):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Games"
    head_fill = PatternFill("solid", fgColor="FF6417")
    for i, (h, _, w) in enumerate(COLS, 1):
        c = ws.cell(row=1, column=i, value=h)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = head_fill
        c.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 48
    r = 2
    for comp in data["competitions"]:
        for g in comp["games"]:
            row = game_to_row(comp["name"], g)
            for i, (_, k, _) in enumerate(COLS, 1):
                ws.cell(row=r, column=i, value=row.get(k, "") if row.get(k, "") != "" else None)
            r += 1
    ws.freeze_panes = "D2"
    help_ws = wb.create_sheet("How to fill")
    for line in [
        "One row per game. Competition must be 'Community League' or 'F League'.",
        "Fill only what you counted; leave the rest empty. Empty = not shown on the site.",
        "Shots on target includes goals (3 on target with 1 goal = 2 saved).",
        "Passes OK / failed = destination visible. 'Not visible' = camera did not show the receiver.",
        "Recoveries (all) already include the interceptions; the Interceptions column is the subset.",
        "Duels unclear = 1v1s with no clear winner.",
        "Add a new row for each new game. The Video link goes in as the YouTube address.",
        "Then run:  python3 update_season.py   (or ask Claude to update the site).",
    ]:
        help_ws.append([line])
    help_ws.column_dimensions["A"].width = 110
    wb.save(path)


def read_rows(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["Games"]
    rows = list(ws.iter_rows(values_only=True))
    keys = [k for _, k, _ in COLS]
    out = []
    for vals in rows[1:]:
        if not vals or all(v in (None, "") for v in vals):
            continue
        r = {k: (vals[i] if i < len(vals) else None) for i, k in enumerate(keys)}
        if not r["competition"] or r["round"] in (None, ""):
            continue
        if r["date"] is not None and hasattr(r["date"], "strftime"):
            r["date"] = r["date"].strftime("%Y-%m-%d")
        out.append(r)
    return out


def git(*args):
    subprocess.run(["git", *args], cwd=REPO_DIR, check=True)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = Path(args[0]) if args else DEFAULT_XLSX
    data = json.load(open(JSON_PATH))

    if "--init" in sys.argv:
        if path.exists():
            sys.exit(f"{path} already exists, not overwriting.")
        write_template(path, data)
        print(f"Created {path}")
        return

    if not path.exists():
        sys.exit(f"Spreadsheet not found: {path}  (create it with --init)")
    for r in read_rows(path):
        apply_row(data, r)
        print(f"  {r['competition']} R{r['round']} vs {r['opp']}: "
              f"{'numbers' if data and any(r.get(k) not in (None, '') for k in NUM_KEYS) else 'no numbers yet'}")
    json.dump(data, open(JSON_PATH, "w"), indent=2, ensure_ascii=False)

    subprocess.run([sys.executable, "build_portfolio.py"], cwd=REPO_DIR, check=True)
    if "--no-push" in sys.argv:
        print("Skipping git commit/push (--no-push).")
        return
    git("add", "sam_brady_portfolio.html", "sambrady/index.html")
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_DIR).returncode == 0:
        print("Nothing changed, skipping commit.")
        return
    git("commit", "-m", "Update Summer 2026/27 game analysis")
    git("pull", "--rebase", "origin", "main")
    git("push", "origin", "main")
    print("Published! GitHub Pages updates in 1-2 minutes.")


if __name__ == "__main__":
    main()
