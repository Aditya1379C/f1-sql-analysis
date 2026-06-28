-- ============================================================
-- MODULE 4: PIT STOP STRATEGY (Q12–Q13)
-- Scope: modern era, races.year >= 2010
-- ============================================================

-- Q12 — Average pit stop duration per constructor
-- duration is stored as text; CAST to REAL before averaging.
-- pit_stops joins results on the dual key (raceId + driverId).
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
ORDER BY avg_pit_stop ASC;


-- Q13 — Number of pit stops vs average final position
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
ORDER BY total_stops.stops ASC;
