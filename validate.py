"""
validate.py
Lightweight data-quality checks against f1.db. Run after setup.py to
confirm the database loaded cleanly before building the dashboard.

Usage:  python validate.py
Exits non-zero if any check fails.
"""

import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), "f1.db")

EXPECTED_TABLES = [
    "races", "results", "drivers", "constructors", "qualifying",
    "lap_times", "pit_stops", "circuits", "driver_standings",
    "constructor_standings", "status",
]


def scalar(conn, sql):
    return conn.execute(sql).fetchone()[0]


def main():
    if not os.path.exists(DB_PATH):
        sys.exit("f1.db not found — run `python setup.py` first.")

    conn = sqlite3.connect(DB_PATH)
    failures = []

    def check(name, condition, detail=""):
        status = "PASS" if condition else "FAIL"
        print(f"  [{status}] {name}{(' — ' + detail) if detail else ''}")
        if not condition:
            failures.append(name)

    print("Running data-quality checks...\n")

    # 1. All expected tables exist and are non-empty.
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    for t in EXPECTED_TABLES:
        present = t in tables
        rows = scalar(conn, f"SELECT COUNT(*) FROM {t}") if present else 0
        check(f"table '{t}' present and non-empty", present and rows > 0,
              f"{rows:,} rows" if present else "missing")

    # 2. No NULL foreign keys in results (every result maps to a real entity).
    check("results.driverId has no NULLs",
          scalar(conn, "SELECT COUNT(*) FROM results WHERE driverId IS NULL") == 0)
    check("results.raceId has no NULLs",
          scalar(conn, "SELECT COUNT(*) FROM results WHERE raceId IS NULL") == 0)

    # 3. Referential integrity: every result.driverId exists in drivers.
    orphans = scalar(conn, """
        SELECT COUNT(*) FROM results
        WHERE driverId NOT IN (SELECT driverId FROM drivers)
    """)
    check("no orphaned results (driverId)", orphans == 0, f"{orphans} orphans")

    # 4. Modern-era window actually has data.
    modern = scalar(conn, "SELECT COUNT(*) FROM races WHERE year >= 2010")
    check("modern era (>=2010) has races", modern > 0, f"{modern} races")

    # 5. Win counts are sane: total wins cannot exceed total races.
    total_races = scalar(conn, "SELECT COUNT(*) FROM races WHERE year >= 2010")
    total_wins = scalar(conn, """
        SELECT COUNT(*) FROM results r
        JOIN races ra ON r.raceId = ra.raceId
        WHERE r.position = 1 AND ra.year >= 2010
    """)
    check("wins <= races (modern era)", total_wins <= total_races,
          f"{total_wins} wins / {total_races} races")

    # 6. Pit stop durations are numeric and positive after CAST.
    bad_durations = scalar(conn, """
        SELECT COUNT(*) FROM pit_stops
        WHERE CAST(duration AS REAL) <= 0
    """)
    check("all pit stop durations cast to a positive number", bad_durations == 0,
          f"{bad_durations} bad")

    conn.close()
    print()
    if failures:
        sys.exit(f"{len(failures)} check(s) FAILED: {', '.join(failures)}")
    print("All checks passed.")


if __name__ == "__main__":
    main()
