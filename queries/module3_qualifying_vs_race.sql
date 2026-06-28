-- ============================================================
-- MODULE 3: QUALIFYING VS RACE (Q9–Q11)
-- Scope: modern era, races.year >= 2010
-- ============================================================

-- Q9 — Average grid vs finish position per driver
SELECT
    drivers.forename || ' ' || drivers.surname AS driver_name,
    ROUND(AVG(results.grid), 2)                         AS avg_start_pos,
    ROUND(AVG(results.positionOrder), 2)                AS avg_end_pos,
    ROUND(AVG(results.grid - results.positionOrder), 2) AS avg_pos_change,
    COUNT(*) AS total_races
FROM results
JOIN drivers ON results.driverId = drivers.driverId
JOIN races   ON results.raceId   = races.raceId
WHERE races.year >= 2010
  AND results.grid > 0          -- exclude pit-lane starts recorded as grid 0
GROUP BY drivers.driverId
HAVING COUNT(*) >= 30
ORDER BY avg_pos_change DESC;


-- Q10 — Biggest single-race position gains
SELECT
    drivers.forename || ' ' || drivers.surname AS driver_name,
    races.name                             AS race_name,
    races.year                             AS race_year,
    results.grid                           AS start_position,
    results.positionOrder                  AS finish_position,
    (results.grid - results.positionOrder) AS positions_gained
FROM results
JOIN drivers ON results.driverId = drivers.driverId
JOIN races   ON results.raceId   = races.raceId
WHERE races.year >= 2010
  AND results.grid > 0
  AND results.positionOrder > 0
ORDER BY positions_gained DESC
LIMIT 20;


-- Q11 — Pole-to-win conversion rate (grid = 1)
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
ORDER BY conv_rate DESC;
