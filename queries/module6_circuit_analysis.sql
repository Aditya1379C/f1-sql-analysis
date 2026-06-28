-- ============================================================
-- MODULE 6: CIRCUIT ANALYSIS (Q16–Q17)
-- Scope: modern era, races.year >= 2010
-- ============================================================

-- Q16 — Most wins per circuit
-- RANK() OVER (PARTITION BY circuitId) finds the top winner at each track.
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
ORDER BY ranked.wins_count DESC;


-- Q17 — Home race advantage per driver
-- drivers.nationality uses demonyms ('British', 'Dutch') while
-- circuits.country uses country names ('UK', 'Netherlands'), so the
-- two are mapped before comparing. home_advantage = avg away finish
-- minus avg home finish (positive = better at home, since lower
-- positionOrder is better).
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
    JOIN drivers  ON results.driverId = drivers.driverId
    JOIN races    ON results.raceId   = races.raceId
    JOIN circuits ON races.circuitId  = circuits.circuitId
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
ORDER BY home_advantage DESC;
