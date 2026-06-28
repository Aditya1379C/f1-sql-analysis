-- ============================================================
-- MODULE 1: DRIVER PERFORMANCE (Q1–Q5)
-- Scope: modern era, races.year >= 2010
-- ============================================================

-- Q1 — Total wins per driver
SELECT
    drivers.forename || ' ' || drivers.surname AS driver_name,
    COUNT(*) AS total_race_wins
FROM results
JOIN drivers ON results.driverId = drivers.driverId
JOIN races   ON results.raceId   = races.raceId
WHERE results.position = 1
  AND races.year >= 2010
GROUP BY drivers.driverId
ORDER BY total_race_wins DESC;


-- Q2 — Podium breakdown per driver (wins / P2 / P3)
SELECT
    d.forename || ' ' || d.surname AS driver_name,
    COUNT(*) AS total_podiums,
    SUM(CASE WHEN res.position = 1 THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN res.position = 2 THEN 1 ELSE 0 END) AS p2,
    SUM(CASE WHEN res.position = 3 THEN 1 ELSE 0 END) AS p3
FROM results res
JOIN drivers d ON res.driverId = d.driverId
JOIN races r   ON res.raceId   = r.raceId
WHERE res.position IN (1, 2, 3)
  AND r.year >= 2010
GROUP BY d.driverId
HAVING COUNT(*) >= 10
ORDER BY total_podiums DESC;


-- Q3 — Average points per race per driver
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
ORDER BY avg_points DESC;


-- Q4 — DNF rate per driver
-- A DNF excludes both classified finishes ('Finished') and lapped
-- finishes (status like '+1 Lap'), so retirement rates aren't inflated.
SELECT
    drivers.forename || ' ' || drivers.surname AS driver_name,
    COUNT(*) AS total_races,
    SUM(CASE WHEN status.status != 'Finished'
              AND status.status NOT LIKE '+%' THEN 1 ELSE 0 END) AS total_dnfs,
    ROUND(100.0 * SUM(CASE WHEN status.status != 'Finished'
                            AND status.status NOT LIKE '+%' THEN 1 ELSE 0 END)
                / COUNT(*), 1) AS dnf_pct
FROM results
JOIN drivers ON results.driverId = drivers.driverId
JOIN races   ON results.raceId   = races.raceId
JOIN status  ON results.statusId = status.statusId
WHERE races.year >= 2010
GROUP BY drivers.driverId
HAVING COUNT(*) >= 20
ORDER BY dnf_pct DESC;


-- Q5 — Win rate per driver
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
ORDER BY win_pct DESC;
