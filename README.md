# TZR — Sam Brady Dashboard

Athlete performance dashboard for Sam Brady (TZR Futsal Coaching).

## Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to share.streamlit.io → New app
3. Select repo, branch main, file app.py
4. Deploy

## Weekly update

1. Update `tzr_sam_dashboard.html` with new data
2. Commit and push to GitHub
3. Streamlit redeploys automatically

## Portfolio page (`/sambrady/`)

`build_portfolio.py` builds `sambrady/index.html` (and `sam_brady_portfolio.html`).
The private detail lives in `data/`, which is **git-ignored on purpose** — keep it
on the machine that runs the build:

- `data/archive.json` — finished seasons (Summer 25/26, Winter 2026, Soccer 2026)
- `data/season_2026_27.json` — the live season, per competition, one entry per round
- `data/logo.b64` — TZR wordmark

After adding a round to `season_2026_27.json`, run `python3 build_portfolio.py`,
then commit `sambrady/index.html` and `sam_brady_portfolio.html`. Every public
total is recomputed from the data files.

## Current-season game analysis

`python3 update_season.py` reads `~/Desktop/Sam_2026_27_analise.xlsx` (one row per game: shots on target,
goals, passes, interceptions, duels, ...), updates `data/season_2026_27.json`, rebuilds the site and pushes.
`--init` creates the spreadsheet, `--no-push` stops before git.
