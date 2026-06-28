-- ============================================================
-- MODULE 2: CONSTRUCTOR BATTLES (Q6–Q8)
-- Scope: modern era, races.year >= 2010
-- ============================================================

-- Q6 — Total wins per constructor per season
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
ORDER BY races.year DESC, total_wins DESC;


-- Q7 — Constructor championship final standings per season
-- "Latest row per group" pattern: join each season to its final round.
WITH last_round AS (
    SELECT year, MAX(round) AS last_round
    FROM races
    WHERE year >= 2010
    GROUP BY year
)
SELECT
    r.year,
    c.name AS constructor,
    cs.points   AS final_points,
    cs.position AS final_position
FROM constructor_standings cs
JOIN races r        ON cs.raceId        = r.raceId
JOIN constructors c ON cs.constructorId = c.constructorId
JOIN last_round lr  ON r.year = lr.year AND r.round = lr.last_round
ORDER BY r.year DESC, cs.position ASC;


-- Q8 — Most dominant constructor per season (win %)
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
JOIN races         ON results.raceId        = races.raceId
JOIN constructors  ON results.constructorId = constructors.constructorId
JOIN race_count rc ON races.year            = rc.year
WHERE races.year >= 2010
GROUP BY races.year, constructors.constructorId
HAVING total_wins > 0
ORDER BY races.year DESC, win_pct DESC;
