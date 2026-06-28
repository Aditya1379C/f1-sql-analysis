-- ============================================================
-- MODULE 5: CHAMPIONSHIP BATTLES (Q14–Q15)
-- Scope: modern era, races.year >= 2010
-- ============================================================

-- Q14 — Points gap between P1 and P2 per season
-- Self-join the final standings CTE to put champion and runner-up
-- on the same row.
WITH last_round AS (
    SELECT year, MAX(round) AS last_round
    FROM races
    WHERE year >= 2010
    GROUP BY year
),
final_standings AS (
    SELECT r.year, ds.driverId, ds.points, ds.position
    FROM driver_standings ds
    JOIN races r       ON ds.raceId = r.raceId
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
ORDER BY p1.year DESC;


-- Q15 — Cumulative points through the 2021 season (top drivers)
-- Filter CTE picks drivers who finished the season with > 100 points,
-- then pull their per-round standings to chart the title race.
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
    r.round AS race_round,
    r.name  AS race_name,
    d.forename || ' ' || d.surname AS driver_name,
    ds.points AS cumulative_points
FROM driver_standings ds
JOIN races r        ON ds.raceId   = r.raceId
JOIN drivers d      ON ds.driverId = d.driverId
JOIN top_drivers td ON ds.driverId = td.driverId
WHERE r.year = 2021
ORDER BY r.round ASC, ds.points DESC;
