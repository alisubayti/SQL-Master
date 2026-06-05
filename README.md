# SQL Master 🗄️

**A free, browser-based course that takes you from `SELECT *` to recursive CTEs and window functions — 277 hands-on problems, instant feedback, no signup, no install.**

### ▶️ [Play it now → alisubayti.github.io/sql-master-game](https://alisubayti.github.io/sql-master-game/)

Write real SQL, run it against a real SQLite database in your browser, and get graded instantly. Everything runs client-side — your queries never leave your machine.

---

## What it is

277 problems organized into 10 progressive levels, each building on the last. You write a query, it executes against an actual SQLite engine running in your browser (compiled to WebAssembly), and your result is compared against the expected output. Right or wrong, you know immediately.

It's built to be *learned from*: hints when you're stuck, full solutions when you want them, and deliberately-placed "gotcha" problems that teach the traps real SQL throws at you (NULL handling, case sensitivity, the difference between `LIKE` and `=`).

## The 10 levels

| Level | Topic | Problems |
|------:|-------|:--------:|
| 1 | SELECT, WHERE, ORDER BY, LIKE, BETWEEN | 32 |
| 2 | Sorting, NULLs & set operations | 26 |
| 3 | Aggregation & grouping | 30 |
| 4 | JOINs — inner, left, self, multi-table | 30 |
| 5 | Subqueries | 30 |
| 6 | String functions | 30 |
| 7 | Date/time & CASE | 30 |
| 8 | CTEs, including recursive | 23 |
| 9 | Window functions | 24 |
| 10 | Capstone — conditional aggregation & pivots | 22 |

Each level ramps from a gentle introduction of the concept to problems that combine everything you've learned so far.

## Features

- **Runs entirely in your browser** — real SQLite via WebAssembly, no backend, nothing to install
- **Instant grading** — your query's output is compared against the expected result
- **Hints & solutions** — toggle them when you want them, ignore them when you don't
- **Jump to any problem** — grid view, no clicking through one at a time
- **Concept filters** — drill into JOINs, GROUP BY, subqueries, and more within a level
- **Progress saved locally** — your solved problems persist between sessions
- **Quality-of-life touches** — auto-paired quotes, optional autocomplete

## How the grading works

The interesting part. A correct query isn't just "returns the right rows" — the comparison engine handles the things that trip up naive checkers:

- **Order sensitivity** — problems that test `ORDER BY` verify row *sequence*; problems that don't are order-independent, so any correct ordering passes.
- **Floating-point tolerance** — computed values (averages, running totals) compare within tolerance, so `61.24` and `61.2400001` aren't falsely marked wrong.
- **NULL-safe comparison** — result sets containing NULLs compare correctly instead of crashing.

The browser grading engine is verified against a reference implementation: all 277 problems are run through both engines, with correct *and* deliberately-wrong queries, and every verdict must match. ([`verify_parity.py`](verify_parity.py))

## Tech

| | |
|---|---|
| SQL engine | [sql.js](https://github.com/sql-js/sql.js) v1.14.1 (SQLite compiled to WebAssembly) |
| Frontend | Single-file HTML/JS, no framework |
| Hosting | Static — GitHub Pages |
| Persistence | Browser `localStorage` |
| Total size | ~1.1 MB |

No server, no database to provision, no runtime dependencies. The whole app is static files.

## Run it locally

```bash
git clone https://github.com/alisubayti/sql-master-game.git
cd sql-master-game/docs
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## License

[MIT](LICENSE) — free to use, fork, and learn from.
