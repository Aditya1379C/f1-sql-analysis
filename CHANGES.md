# Changes Log

Improvements made to strengthen the repo for portfolio / recruiter review.
Dated 2026-06-28.

## 1. Extracted all 17 SQL queries into standalone `.sql` files

**Problem:** The `queries/` folder was empty and `QUERY_LOG.md` was gitignored,
so a recruiter cloning the repo saw **zero SQL files** — the SQL only existed
embedded inside `extract_data.py`. The headline of a "SQL analysis" project was
effectively invisible on GitHub.

**Fix:** Split the queries (verbatim from `extract_data.py`) into six readable,
commented module files under `queries/`:

| File | Queries |
|------|---------|
| `queries/module1_driver_performance.sql`   | Q1–Q5  |
| `queries/module2_constructor_battles.sql`  | Q6–Q8  |
| `queries/module3_qualifying_vs_race.sql`   | Q9–Q11 |
| `queries/module4_pit_stop_strategy.sql`    | Q12–Q13 |
| `queries/module5_championship_battles.sql` | Q14–Q15 |
| `queries/module6_circuit_analysis.sql`     | Q16–Q17 |

Each file documents the modern-era scope filter and the non-obvious logic
(DNF vs lapped-finish detection, demonym→country mapping, dual-key joins,
window-function ranking).

## 2. Un-gitignored `QUERY_LOG.md`

**Problem:** The README pointed to `QUERY_LOG.md` as the place where "all 17
queries + mistakes + patterns learned" live, but the file was gitignored as a
"private log" — so it never reached GitHub. The "mistakes made / patterns
learned" log is a differentiator and should be visible.

**Fix:** Removed the `QUERY_LOG.md` entry from `.gitignore` so it ships with
the repo.

## 3. Added `requirements.txt`

**Problem:** No pinned dependency file; setup instructions just said
`pip install pandas`.

**Fix:** Added `requirements.txt` (`pandas>=2.0`) so the environment is
reproducible with `pip install -r requirements.txt`.

## 4. Added `validate.py` data-quality checks

**Problem:** No validation or tests — nothing demonstrated that the pipeline
produced trustworthy data.

**Fix:** Added `validate.py`, which runs 17 sanity checks against `f1.db`:
table presence + row counts, no NULL foreign keys, referential integrity
(no orphaned results), modern-era window non-empty, wins ≤ races, and pit-stop
durations cast to positive numbers. Exits non-zero on failure so it can gate a
build. **All checks currently pass** (305 modern-era races, 26,759 results,
589,081 lap times).

## Suggested follow-ups (not yet done)

- Publish `dashboard.html` via **GitHub Pages** and link it at the top of the
  README so reviewers can view the dashboard without cloning.
- Add indexes / primary keys in `setup.py` for faster queries on `lap_times`.
- Squash the empty commit (`ba01928`) for a cleaner history.
