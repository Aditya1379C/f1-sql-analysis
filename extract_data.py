"""
extract_data.py
Runs all 17 F1 SQL queries against f1.db and writes the results to
dashboard_data.json — ready to embed in the dashboard HTML.
"""

import sqlite3
import json
import os

DB_PATH   = os.path.join(os.path.dirname(__file__), "f1.db")
OUT_PATH  = os.path.join(os.path.dirname(__file__), "dashboard_data.json")


def query(conn, sql):
    """Run a query and return a list of dicts."""
    cur = conn.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def main():
    conn = sqlite3.connect(DB_PATH)
    print(f"Connected to {DB_PATH}\n")

    data = {}

    # ── MODULE 1: DRIVER PERFORMANCE ────────────────────────────────────────

    # Q1 — Total wins per driver
    print("Q1  Total wins per driver...")
    data["q1_driver_wins"] = query(conn, """
        SELECT
            drivers.forename || ' ' || drivers.surname AS driver_name,
            COUNT(*) AS total_race_wins
        FROM results
        JOIN drivers      ON results.driverId    = drivers.driverId
        JOIN races        ON results.raceId      = races.raceId
        WHERE results.position = 1
          AND races.year >= 2010
        GROUP BY drivers.driverId
        ORDER BY total_race_wins DESC
    """)

    # Q2 — Podium breakdown per driver
    print("Q2  Podium breakdown...")
    data["q2_podiums"] = query(conn, """
        SELECT
            d.forename || ' ' || d.surname AS driver_name,
            COUNT(*) AS total_podiums,
            SUM(CASE WHEN res.position = 1 THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN res.position = 2 THEN 1 ELSE 0 END) AS p2,
            SUM(CASE WHEN res.position = 3 THEN 1 ELSE 0 END) AS p3
        FROM results res
        JOIN drivers d  ON res.driverId = d.driverId
        JOIN races r    ON res.raceId   = r.raceId
        WHERE res.position IN (1, 2, 3)
          AND r.year >= 2010
        GROUP BY d.driverId
        HAVING COUNT(*) >= 10
        ORDER BY total_podiums DESC
    """)

    # Q3 — Average points per race per driver
    print("Q3  Avg points per race...")
    data["q3_avg_points"] = query(conn, """
        SELECT
            drivers.forename || ' ' || drivers.surname AS driver_name,
            COUNT(*) AS races_entered,
            ROUND(AVG(results.points), 2) AS avg_points
        FROM results
        JOIN drivers ON results.driverId = drivers.driverId
        JOIN races   ON results.raceId   = races.raceId
        WHERE races.year >= 2010
        GROUP BY drivers.driverId
        HAVING COUNT(*) >= 20
        ORDER BY avg_points DESC
    """)

    # Q4 — DNF rate per driver
    print("Q4  DNF rate...")
    data["q4_dnf_rate"] = query(conn, """
        SELECT
            drivers.forename || ' ' || drivers.surname AS driver_name,
            COUNT(*) AS total_races,
            SUM(CASE WHEN status.status != 'Finished'
                      AND status.status NOT LIKE '+%' THEN 1 ELSE 0 END) AS total_dnfs,
            ROUND(100.0 * SUM(CASE WHEN status.status != 'Finished'
                                    AND status.status NOT LIKE '+%' THEN 1 ELSE 0 END)
                        / COUNT(*), 1) AS dnf_pct
        FROM results
        JOIN drivers ON results.driverId  = drivers.driverId
        JOIN races   ON results.raceId    = races.raceId
        JOIN status  ON results.statusId  = status.statusId
        WHERE races.year >= 2010
        GROUP BY drivers.driverId
        HAVING COUNT(*) >= 20
        ORDER BY dnf_pct DESC
    """)

    # Q5 — Win rate per driver
    print("Q5  Win rate...")
    data["q5_win_rate"] = query(conn, """
        SELECT
            drivers.forename || ' ' || drivers.surname AS driver_name,
            COUNT(*) AS total_races,
            SUM(CASE WHEN results.position = 1 THEN 1 ELSE 0 END) AS total_wins,
            ROUND(100.0 * SUM(CASE WHEN results.position = 1 THEN 1 ELSE 0 END)
                        / COUNT(*), 1) AS win_pct
        FROM results
        JOIN drivers ON results.driverId = drivers.driverId
        JOIN races   ON results.raceId   = races.raceId
        WHERE races.year >= 2010
        GROUP BY drivers.driverId
        HAVING COUNT(*) >= 20
        ORDER BY win_pct DESC
    """)

    # ── MODULE 2: CONSTRUCTOR BATTLES ────────────────────────────────────────

    # Q6 — Total wins per constructor per season
    print("Q6  Constructor wins per season...")
    data["q6_constructor_season_wins"] = query(conn, """
        SELECT
            races.year,
            constructors.name AS constructor,
            SUM(CASE WHEN results.position = 1 THEN 1 ELSE 0 END) AS total_wins
        FROM results
        JOIN constructors ON results.constructorId = constructors.constructorId
        JOIN races        ON results.raceId        = races.raceId
        WHERE races.year >= 2010
        GROUP BY constructors.constructorId, races.year
        HAVING total_wins > 0
        ORDER BY races.year DESC, total_wins DESC
    """)

    # Q7 — Constructor championship final standings per season
    print("Q7  Constructor final standings...")
    data["q7_constructor_standings"] = query(conn, """
        WITH last_round AS (
            SELECT year, MAX(round) AS last_round
            FROM races
            WHERE year >= 2010
            GROUP BY year
        )
        SELECT
            r.year,
            c.name AS constructor,
            cs.points AS final_points,
            cs.position AS final_position
        FROM constructor_standings cs
        JOIN races r        ON cs.raceId        = r.raceId
        JOIN constructors c ON cs.constructorId = c.constructorId
        JOIN last_round lr  ON r.year = lr.year AND r.round = lr.last_round
        ORDER BY r.year DESC, cs.position ASC
    """)

    # Q8 — Most dominant constructor per season (win %)
    print("Q8  Constructor win dominance %...")
    data["q8_constructor_dominance"] = query(conn, """
        WITH race_count AS (
            SELECT year, COUNT(raceId) AS total_races
            FROM races
            WHERE year >= 2010
            GROUP BY year
        )
        SELECT
            races.year,
            constructors.name AS constructor,
            SUM(CASE WHEN results.position = 1 THEN 1 ELSE 0 END) AS total_wins,
            rc.total_races,
            ROUND(100.0 * SUM(CASE WHEN results.position = 1 THEN 1 ELSE 0 END)
                        / rc.total_races, 1) AS win_pct
        FROM results
        JOIN races        ON results.raceId        = races.raceId
        JOIN constructors ON results.constructorId = constructors.constructorId
        JOIN race_count rc ON races.year           = rc.year
        WHERE races.year >= 2010
        GROUP BY races.year, constructors.constructorId
        HAVING total_wins > 0
        ORDER BY races.year DESC, win_pct DESC
    """)

    # ── MODULE 3: QUALIFYING VS RACE ─────────────────────────────────────────

    # Q9 — Avg grid vs finish position per driver
    print("Q9  Avg grid vs finish position...")
    data["q9_grid_vs_finish"] = query(conn, """
        SELECT
            drivers.forename || ' ' || drivers.surname AS driver_name,
            ROUND(AVG(results.grid), 2)                      AS avg_start_pos,
            ROUND(AVG(results.positionOrder), 2)             AS avg_end_pos,
            ROUND(AVG(results.grid - results.positionOrder), 2) AS avg_pos_change,
            COUNT(*) AS total_races
        FROM results
        JOIN drivers ON results.driverId = drivers.driverId
        JOIN races   ON results.raceId   = races.raceId
        WHERE races.year >= 2010
          AND results.grid > 0
        GROUP BY drivers.driverId
        HAVING COUNT(*) >= 30
        ORDER BY avg_pos_change DESC
    """)

    # Q10 — Biggest single-race position gains
    print("Q10 Biggest single-race position gains...")
    data["q10_biggest_gains"] = query(conn, """
        SELECT
            drivers.forename || ' ' || drivers.surname AS driver_name,
            races.name                                 AS race_name,
            races.year                                 AS race_year,
            results.grid                               AS start_position,
            results.positionOrder                      AS finish_position,
            (results.grid - results.positionOrder)     AS positions_gained
        FROM results
        JOIN drivers ON results.driverId = drivers.driverId
        JOIN races   ON results.raceId   = races.raceId
        WHERE races.year >= 2010
          AND results.grid > 0
          AND results.positionOrder > 0
        ORDER BY positions_gained DESC
        LIMIT 20
    """)

    # Q11 — Pole-to-win conversion rate
    print("Q11 Pole conversion rate...")
    data["q11_pole_conversion"] = query(conn, """
        SELECT
            drivers.forename || ' ' || drivers.surname AS driver_name,
            COUNT(*) AS total_poles,
            SUM(CASE WHEN results.position = 1 THEN 1 ELSE 0 END) AS poles_converted,
            ROUND(100.0 * SUM(CASE WHEN results.position = 1 THEN 1 ELSE 0 END)
                        / COUNT(*), 1) AS conv_rate
        FROM results
        JOIN drivers ON results.driverId = drivers.driverId
        JOIN races   ON results.raceId   = races.raceId
        WHERE races.year >= 2010
          AND results.grid = 1
        GROUP BY drivers.driverId
        HAVING COUNT(*) >= 5
        ORDER BY conv_rate DESC
    """)

    # ── MODULE 4: PIT STOP STRATEGY ──────────────────────────────────────────

    # Q12 — Avg pit stop duration per constructor
    print("Q12 Avg pit stop duration...")
    data["q12_pit_duration"] = query(conn, """
        SELECT
            constructors.name AS constructor,
            ROUND(AVG(CAST(pit_stops.duration AS REAL)), 3) AS avg_pit_stop,
            COUNT(*) AS total_stops
        FROM results
        JOIN races        ON results.raceId   = races.raceId
        JOIN pit_stops    ON results.raceId   = pit_stops.raceId
                         AND results.driverId = pit_stops.driverId
        JOIN constructors ON results.constructorId = constructors.constructorId
        WHERE races.year >= 2010
        GROUP BY constructors.constructorId
        HAVING COUNT(*) >= 100
        ORDER BY avg_pit_stop ASC
    """)

    # Q13 — Number of pit stops vs avg final position
    print("Q13 Pit stops vs finish position...")
    data["q13_stops_vs_finish"] = query(conn, """
        WITH total_stops AS (
            SELECT raceId, driverId, COUNT(stop) AS stops
            FROM pit_stops
            GROUP BY raceId, driverId
        )
        SELECT
            total_stops.stops,
            ROUND(AVG(results.positionOrder), 2) AS avg_finish_position,
            COUNT(*) AS sample_size
        FROM results
        JOIN races       ON results.raceId   = races.raceId
        JOIN total_stops ON results.raceId   = total_stops.raceId
                        AND results.driverId = total_stops.driverId
        WHERE races.year >= 2010
        GROUP BY total_stops.stops
        ORDER BY total_stops.stops ASC
    """)

    # ── MODULE 5: CHAMPIONSHIP BATTLES ───────────────────────────────────────

    # Q14 — Points gap between P1 and P2 per season
    print("Q14 Championship points gaps...")
    data["q14_championship_gaps"] = query(conn, """
        WITH last_round AS (
            SELECT year, MAX(round) AS last_round
            FROM races
            WHERE year >= 2010
            GROUP BY year
        ),
        final_standings AS (
            SELECT r.year, ds.driverId, ds.points, ds.position
            FROM driver_standings ds
            JOIN races r       ON ds.raceId  = r.raceId
            JOIN last_round lr ON r.year = lr.year AND r.round = lr.last_round
            WHERE ds.position IN (1, 2)
        )
        SELECT
            p1.year,
            d1.forename || ' ' || d1.surname AS winner,
            p1.points AS winner_points,
            d2.forename || ' ' || d2.surname AS runner_up,
            p2.points AS runner_up_points,
            (p1.points - p2.points) AS points_gap
        FROM final_standings p1
        JOIN final_standings p2 ON p1.year = p2.year AND p2.position = 2
        JOIN drivers d1 ON p1.driverId = d1.driverId
        JOIN drivers d2 ON p2.driverId = d2.driverId
        WHERE p1.position = 1
        ORDER BY p1.year DESC
    """)

    # Q15 — Cumulative points through 2021 (top drivers)
    print("Q15 2021 cumulative points race...")
    data["q15_cumulative_2021"] = query(conn, """
        WITH last_round AS (
            SELECT MAX(round) AS last_round
            FROM races
            WHERE year = 2021
        ),
        top_drivers AS (
            SELECT ds.driverId
            FROM driver_standings ds
            JOIN races r ON ds.raceId = r.raceId
            WHERE r.year = 2021
              AND r.round = (SELECT last_round FROM last_round)
              AND ds.points > 100
        )
        SELECT
            r.round       AS race_round,
            r.name        AS race_name,
            d.forename || ' ' || d.surname AS driver_name,
            ds.points     AS cumulative_points
        FROM driver_standings ds
        JOIN races r        ON ds.raceId   = r.raceId
        JOIN drivers d      ON ds.driverId = d.driverId
        JOIN top_drivers td ON ds.driverId = td.driverId
        WHERE r.year = 2021
        ORDER BY r.round ASC, ds.points DESC
    """)

    # ── MODULE 6: CIRCUIT ANALYSIS ───────────────────────────────────────────

    # Q16 — Most wins per circuit
    print("Q16 Circuit dominance...")
    data["q16_circuit_dominance"] = query(conn, """
        WITH wins_per_driver AS (
            SELECT results.driverId, races.circuitId, COUNT(*) AS wins_count
            FROM results
            JOIN races ON results.raceId = races.raceId
            WHERE races.year >= 2010
              AND results.position = 1
            GROUP BY results.driverId, races.circuitId
        ),
        ranked AS (
            SELECT driverId, circuitId, wins_count,
                   RANK() OVER (PARTITION BY circuitId ORDER BY wins_count DESC) AS rnk
            FROM wins_per_driver
        )
        SELECT
            circuits.name    AS circuit_name,
            circuits.country AS circuit_country,
            drivers.forename || ' ' || drivers.surname AS driver_name,
            ranked.wins_count AS wins
        FROM ranked
        JOIN circuits ON ranked.circuitId = circuits.circuitId
        JOIN drivers  ON ranked.driverId  = drivers.driverId
        WHERE ranked.rnk = 1
          AND ranked.wins_count >= 2
        ORDER BY ranked.wins_count DESC
    """)

    # Q17 — Home race performance
    # drivers.nationality uses demonyms ("British", "Dutch") while
    # circuits.country uses country names ("UK", "Netherlands") — map them.
    print("Q17 Home race advantage...")
    data["q17_home_advantage"] = query(conn, """
        WITH mapped AS (
            SELECT
                results.driverId,
                results.positionOrder,
                circuits.country AS circuit_country,
                CASE TRIM(drivers.nationality)
                    WHEN 'Australian'  THEN 'Australia'
                    WHEN 'Austrian'    THEN 'Austria'
                    WHEN 'Belgian'     THEN 'Belgium'
                    WHEN 'Brazilian'   THEN 'Brazil'
                    WHEN 'British'     THEN 'UK'
                    WHEN 'Canadian'    THEN 'Canada'
                    WHEN 'Chinese'     THEN 'China'
                    WHEN 'Dutch'       THEN 'Netherlands'
                    WHEN 'French'      THEN 'France'
                    WHEN 'German'      THEN 'Germany'
                    WHEN 'Indian'      THEN 'India'
                    WHEN 'Italian'     THEN 'Italy'
                    WHEN 'Japanese'    THEN 'Japan'
                    WHEN 'Mexican'     THEN 'Mexico'
                    WHEN 'Monegasque'  THEN 'Monaco'
                    WHEN 'Russian'     THEN 'Russia'
                    WHEN 'Spanish'     THEN 'Spain'
                    WHEN 'American'    THEN 'USA'
                END AS driver_country
            FROM results
            JOIN drivers  ON results.driverId  = drivers.driverId
            JOIN races    ON results.raceId    = races.raceId
            JOIN circuits ON races.circuitId   = circuits.circuitId
            WHERE races.year >= 2010
        )
        SELECT
            d.forename || ' ' || d.surname AS driver_name,
            TRIM(d.nationality)            AS nationality,
            ROUND(AVG(CASE WHEN m.driver_country = m.circuit_country
                           THEN m.positionOrder END), 2) AS avg_home_finish,
            ROUND(AVG(CASE WHEN m.driver_country != m.circuit_country
                           THEN m.positionOrder END), 2) AS avg_away_finish,
            ROUND(
                AVG(CASE WHEN m.driver_country != m.circuit_country
                         THEN m.positionOrder END) -
                AVG(CASE WHEN m.driver_country  = m.circuit_country
                         THEN m.positionOrder END),
            2) AS home_advantage
        FROM mapped m
        JOIN drivers d ON m.driverId = d.driverId
        WHERE m.driver_country IS NOT NULL
        GROUP BY m.driverId
        HAVING SUM(CASE WHEN m.driver_country = m.circuit_country THEN 1 ELSE 0 END) >= 3
        ORDER BY home_advantage DESC
    """)

    # ── MODULE 7: PER-YEAR DATA ──────────────────────────────────────────────
    print("\nGenerating per-year data (2010–2024)...")

    HOME_MAP = """
        CASE TRIM(drivers.nationality)
            WHEN 'Australian'  THEN 'Australia'
            WHEN 'Austrian'    THEN 'Austria'
            WHEN 'Belgian'     THEN 'Belgium'
            WHEN 'Brazilian'   THEN 'Brazil'
            WHEN 'British'     THEN 'UK'
            WHEN 'Canadian'    THEN 'Canada'
            WHEN 'Chinese'     THEN 'China'
            WHEN 'Dutch'       THEN 'Netherlands'
            WHEN 'French'      THEN 'France'
            WHEN 'German'      THEN 'Germany'
            WHEN 'Indian'      THEN 'India'
            WHEN 'Italian'     THEN 'Italy'
            WHEN 'Japanese'    THEN 'Japan'
            WHEN 'Mexican'     THEN 'Mexico'
            WHEN 'Monegasque'  THEN 'Monaco'
            WHEN 'Russian'     THEN 'Russia'
            WHEN 'Spanish'     THEN 'Spain'
            WHEN 'American'    THEN 'USA'
        END
    """

    by_year = {}
    for year in range(2010, 2025):
        y = str(year)
        print(f"  {year}...", end=" ", flush=True)
        yd = {}

        # Q1 per year
        yd["q1_driver_wins"] = query(conn, f"""
            SELECT drivers.forename || ' ' || drivers.surname AS driver_name,
                   COUNT(*) AS total_race_wins
            FROM results JOIN drivers ON results.driverId=drivers.driverId
                         JOIN races   ON results.raceId=races.raceId
            WHERE results.position=1 AND races.year={year}
            GROUP BY drivers.driverId ORDER BY total_race_wins DESC
        """)

        # Q2 per year
        yd["q2_podiums"] = query(conn, f"""
            SELECT d.forename||' '||d.surname AS driver_name,
                   COUNT(*) AS total_podiums,
                   SUM(CASE WHEN res.position=1 THEN 1 ELSE 0 END) AS wins,
                   SUM(CASE WHEN res.position=2 THEN 1 ELSE 0 END) AS p2,
                   SUM(CASE WHEN res.position=3 THEN 1 ELSE 0 END) AS p3
            FROM results res JOIN drivers d ON res.driverId=d.driverId
                             JOIN races r   ON res.raceId=r.raceId
            WHERE res.position IN (1,2,3) AND r.year={year}
            GROUP BY d.driverId ORDER BY total_podiums DESC
        """)

        # Q3 per year (lower threshold: 5 races)
        yd["q3_avg_points"] = query(conn, f"""
            SELECT drivers.forename||' '||drivers.surname AS driver_name,
                   COUNT(*) AS races_entered,
                   ROUND(AVG(results.points),2) AS avg_points
            FROM results JOIN drivers ON results.driverId=drivers.driverId
                         JOIN races   ON results.raceId=races.raceId
            WHERE races.year={year}
            GROUP BY drivers.driverId HAVING races_entered>=5
            ORDER BY avg_points DESC
        """)

        # Q4 per year
        yd["q4_dnf_rate"] = query(conn, f"""
            SELECT drivers.forename||' '||drivers.surname AS driver_name,
                   COUNT(*) AS total_races,
                   SUM(CASE WHEN status.status!='Finished'
                             AND status.status NOT LIKE '+%' THEN 1 ELSE 0 END) AS total_dnfs,
                   ROUND(100.0*SUM(CASE WHEN status.status!='Finished'
                                        AND status.status NOT LIKE '+%' THEN 1 ELSE 0 END)/COUNT(*),1) AS dnf_pct
            FROM results JOIN drivers ON results.driverId=drivers.driverId
                         JOIN races   ON results.raceId=races.raceId
                         JOIN status  ON results.statusId=status.statusId
            WHERE races.year={year}
            GROUP BY drivers.driverId HAVING total_races>=5
            ORDER BY dnf_pct DESC
        """)

        # Q5 per year
        yd["q5_win_rate"] = query(conn, f"""
            SELECT drivers.forename||' '||drivers.surname AS driver_name,
                   COUNT(*) AS total_races,
                   SUM(CASE WHEN results.position=1 THEN 1 ELSE 0 END) AS total_wins,
                   ROUND(100.0*SUM(CASE WHEN results.position=1 THEN 1 ELSE 0 END)/COUNT(*),1) AS win_pct
            FROM results JOIN drivers ON results.driverId=drivers.driverId
                         JOIN races   ON results.raceId=races.raceId
            WHERE races.year={year}
            GROUP BY drivers.driverId HAVING total_races>=5
            ORDER BY win_pct DESC
        """)

        # Q9 per year (threshold: 5 races)
        yd["q9_grid_vs_finish"] = query(conn, f"""
            SELECT drivers.forename||' '||drivers.surname AS driver_name,
                   ROUND(AVG(results.grid),2) AS avg_start_pos,
                   ROUND(AVG(results.positionOrder),2) AS avg_end_pos,
                   ROUND(AVG(results.grid-results.positionOrder),2) AS avg_pos_change,
                   COUNT(*) AS total_races
            FROM results JOIN drivers ON results.driverId=drivers.driverId
                         JOIN races   ON results.raceId=races.raceId
            WHERE races.year={year} AND results.grid>0
            GROUP BY drivers.driverId HAVING total_races>=5
            ORDER BY avg_pos_change DESC
        """)

        # Q11 per year (threshold: 2 poles)
        yd["q11_pole_conversion"] = query(conn, f"""
            SELECT drivers.forename||' '||drivers.surname AS driver_name,
                   COUNT(*) AS total_poles,
                   SUM(CASE WHEN results.position=1 THEN 1 ELSE 0 END) AS poles_converted,
                   ROUND(100.0*SUM(CASE WHEN results.position=1 THEN 1 ELSE 0 END)/COUNT(*),1) AS conv_rate
            FROM results JOIN drivers ON results.driverId=drivers.driverId
                         JOIN races   ON results.raceId=races.raceId
            WHERE races.year={year} AND results.grid=1
            GROUP BY drivers.driverId HAVING total_poles>=2
            ORDER BY conv_rate DESC
        """)

        # Q12 per year (threshold: 10 stops)
        yd["q12_pit_duration"] = query(conn, f"""
            SELECT constructors.name AS constructor,
                   ROUND(AVG(CAST(pit_stops.duration AS REAL)),3) AS avg_pit_stop,
                   COUNT(*) AS total_stops
            FROM results JOIN races        ON results.raceId=races.raceId
                         JOIN pit_stops    ON results.raceId=pit_stops.raceId
                                          AND results.driverId=pit_stops.driverId
                         JOIN constructors ON results.constructorId=constructors.constructorId
            WHERE races.year={year}
            GROUP BY constructors.constructorId HAVING total_stops>=10
            ORDER BY avg_pit_stop ASC
        """)

        # Q13 per year
        yd["q13_stops_vs_finish"] = query(conn, f"""
            WITH total_stops AS (
                SELECT ps.raceId, ps.driverId, COUNT(ps.stop) AS stops
                FROM pit_stops ps JOIN races ra ON ps.raceId=ra.raceId
                WHERE ra.year={year} GROUP BY ps.raceId, ps.driverId
            )
            SELECT ts.stops,
                   ROUND(AVG(r.positionOrder),2) AS avg_finish_position,
                   COUNT(*) AS sample_size
            FROM results r JOIN races  ON r.raceId=races.raceId
                           JOIN total_stops ts ON r.raceId=ts.raceId AND r.driverId=ts.driverId
            WHERE races.year={year}
            GROUP BY ts.stops HAVING sample_size>=3 ORDER BY ts.stops ASC
        """)

        # Q15 per year — top-5 championship finishers, cumulative points
        yd["q15_cumulative"] = query(conn, f"""
            WITH last_round AS (
                SELECT MAX(round) AS lr FROM races WHERE year={year}
            ),
            top5 AS (
                SELECT ds.driverId
                FROM driver_standings ds
                JOIN races r ON ds.raceId=r.raceId
                WHERE r.year={year} AND r.round=(SELECT lr FROM last_round)
                ORDER BY ds.position ASC LIMIT 5
            )
            SELECT r.round AS race_round, r.name AS race_name,
                   d.forename||' '||d.surname AS driver_name,
                   ds.points AS cumulative_points
            FROM driver_standings ds
            JOIN races r   ON ds.raceId=r.raceId
            JOIN drivers d ON ds.driverId=d.driverId
            JOIN top5      ON ds.driverId=top5.driverId
            WHERE r.year={year}
            ORDER BY r.round ASC, ds.points DESC
        """)

        # Q16 per year — race winners per circuit this season
        yd["q16_race_winners"] = query(conn, f"""
            SELECT races.name AS race_name,
                   circuits.country AS circuit_country,
                   drivers.forename||' '||drivers.surname AS driver_name
            FROM results
            JOIN drivers  ON results.driverId=drivers.driverId
            JOIN races    ON results.raceId=races.raceId
            JOIN circuits ON races.circuitId=circuits.circuitId
            WHERE results.position=1 AND races.year={year}
            ORDER BY races.round ASC
        """)

        # Q17 per year
        yd["q17_home_advantage"] = query(conn, f"""
            WITH mapped AS (
                SELECT results.driverId, results.positionOrder,
                       circuits.country AS circuit_country,
                       {HOME_MAP} AS driver_country
                FROM results JOIN drivers  ON results.driverId=drivers.driverId
                             JOIN races    ON results.raceId=races.raceId
                             JOIN circuits ON races.circuitId=circuits.circuitId
                WHERE races.year={year}
            )
            SELECT d.forename||' '||d.surname AS driver_name,
                   TRIM(d.nationality) AS nationality,
                   ROUND(AVG(CASE WHEN m.driver_country=m.circuit_country THEN m.positionOrder END),2) AS avg_home_finish,
                   ROUND(AVG(CASE WHEN m.driver_country!=m.circuit_country THEN m.positionOrder END),2) AS avg_away_finish,
                   ROUND(AVG(CASE WHEN m.driver_country!=m.circuit_country THEN m.positionOrder END)-
                         AVG(CASE WHEN m.driver_country =m.circuit_country THEN m.positionOrder END),2) AS home_advantage
            FROM mapped m JOIN drivers d ON m.driverId=d.driverId
            WHERE m.driver_country IS NOT NULL
            GROUP BY m.driverId
            HAVING SUM(CASE WHEN m.driver_country=m.circuit_country THEN 1 ELSE 0 END)>=1
            ORDER BY home_advantage DESC
        """)

        by_year[y] = yd
        print("done")

    data["by_year"] = by_year

    conn.close()

    # ── WRITE OUTPUT ─────────────────────────────────────────────────────────
    with open(OUT_PATH, "w") as f:
        json.dump(data, f)   # no indent — keeps file compact

    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"\nDone! Wrote {OUT_PATH}  ({size_kb:.0f} KB)")
    for key in data:
        if key != "by_year":
            print(f"  {key}: {len(data[key])} rows")
    print(f"  by_year: {len(by_year)} seasons")


if __name__ == "__main__":
    main()
