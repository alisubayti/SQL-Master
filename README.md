# SQL Master Game — Static Edition

**277 curated SQL problems** across 10 progressive levels. Runs entirely in the browser — no server, no install (except sql.js). Same content as the Flask version, ported to sql.js WebAssembly for standalone static deployment.

## How to Run Locally

```bash
cd sql-game-static/
python3 -m http.server 8767
```

Then open **http://localhost:8767** in your browser.

No Python dependencies. No Flask. No install. Just a browser and this folder.

## Features

- **10 levels** — SELECT basics → advanced window functions → capstone pivots
- **Concept filters** — filter problems by topic within each level
- **Instant feedback** — correct/incorrect with expected output comparison
- **Progress tracking** — saved to `localStorage` (same key as the Flask version)
- **Jump-to-problem** — grid view of all problems in the current level
- **Next/Previous** — loops within the current level
- **Quote auto-pairing** — `"` and `'` insert matching pairs automatically
- **Autocomplete toggle** — off by default, opt-in for speed
- **Float tolerance** — 6-decimal rounding on ordered and unordered comparisons

## File Structure

```
sql-game-static/
├── index.html          # Main application (single HTML file)
├── problems.json       # 277 problems with schema, data, solutions
├── sql-wasm.js         # sql.js v1.14.1 WebAssembly loader
├── sql-wasm.wasm       # sql.js WASM binary (SQLite compiled to WebAssembly)
├── verify_parity.py    # Parity test: proves JS engine matches Python
├── README.md           # This file
└── node_modules/       # sql.js for parity testing (not needed at runtime)
```

## Deploy to Cloudflare Pages (Preferred)

1. Go to **Cloudflare Dashboard → Pages → Create a project**
2. Connect your Git repository (or upload directly)
3. **Build settings:** None needed — it's a static site
   - Framework preset: **None**
   - Build command: leave blank
   - Build output directory: `.` (the root)
4. Deploy. Your site will be live at `https://<project>.pages.dev`

That's it. No build step. No config file needed.

## Deploy to GitHub Pages

1. Push the `sql-game-static/` folder to a GitHub repository
2. Go to **Settings → Pages**
3. Source: **Deploy from a branch**
4. Branch: `main`, folder: `sql-game-static/`
5. Save. Your site will be live at `https://<username>.github.io/<repo>/`

## Parity

The `verify_parity.py` script proves the JS comparison engine (used in-browser) produces identical pass/fail verdicts as the Python reference engine (in `../sql-game/`). It runs all 277 problems through both engines with both correct and deliberately-wrong queries — **277×2 = 554 verdicts** must match.

```bash
python3 verify_parity.py
```

This is the Stage 2 gate. It must pass 277/277 on correct solutions and 277/277 on wrong queries before any content changes.

## Technical Details

| Component | Technology |
|-----------|-----------|
| SQL Engine | sql.js v1.14.1 (SQLite 3.44+ via WebAssembly) |
| Comparison | Ordered/unordered with float tolerance (1e-6) |
| Persistence | `localStorage` key `sql_master_solved` |
| Dependencies | None at runtime (sql.js WASM is self-contained) |
| File size | ~1.1 MB total (.wasm is 645 KB, problems JSON is 399 KB) |

## Level Map

| Level | Topic | Problems |
|-------|-------|----------|
| 1 | SELECT, WHERE, ORDER BY, LIKE, BETWEEN | 32 |
| 2 | ORDER BY, NULLs, Set Operations | 26 |
| 3 | Aggregation & Grouping | 30 |
| 4 | JOINs | 30 |
| 5 | Subqueries | 30 |
| 6 | String Functions | 30 |
| 7 | Date/Time & CASE | 30 |
| 8 | CTEs (incl. recursive) | 23 |
| 9 | Window Functions | 24 |
| 10 | Capstone (conditional aggregation, pivots) | 22 |
| **Total** | | **277** |

## Credits

Built for the SQL Master Game project. Flask reference version preserved in `../sql-game/`.
