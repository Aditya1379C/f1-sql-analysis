# F1 SQL Query Log
A record of every query written, the correct solution, and mistakes made along the way.

---

## Module 1: Driver Performance

---

### Q1 — Total Wins Per Driver (2010–present)

**Task:** Return each driver's full name and total race wins from 2010 onwards, sorted by most wins first.

**Correct Query:**
```sql
SELECT
    drivers.forename || ' ' || drivers.surname AS driver_name,
    COUNT(*) AS total_race_wins
FROM results
JOIN drivers ON results.driverId = drivers.driverId
JOIN races ON results.raceId = races.raceId
WHERE results.position = 1
  AND races.year >= 2010
GROUP BY drivers.driverId
ORDER BY total_race_wins DESC;
```

**Mistakes Made:**
- Used `+` instead of `||` for string concatenation — in SQL, `||` joins strings
- Missing `JOIN races` — needed to filter by `year >= 2010`
- Wrote `GROUPBY` instead of `GROUP BY` (two separate words)
- Trailing comma after last column in SELECT causing syntax error
- Missing `ORDER BY`

---

### Q2 — Podium Breakdown Per Driver (2010–present)

**Task:** Return each driver's name, total podiums, and wins/P2/P3 as separate columns. Min 10 podiums.

**Correct Query:**
```sql
SELECT
    d.forename || ' ' || d.surname AS driver_name,
    COUNT(*) AS total_podiums,
    SUM(CASE WHEN res.position = 1 THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN res.position = 2 THEN 1 ELSE 0 END) AS p2,
    SUM(CASE WHEN res.position = 3 THEN 1 ELSE 0 END) AS p3
FROM results res
JOIN drivers d ON res.driverId = d.driverId
JOIN races r ON res.raceId = r.raceId
WHERE res.position IN (1, 2, 3)
  AND r.year >= 2010
GROUP BY d.driverId
HAVING COUNT(*) >= 10
ORDER BY total_podiums DESC;
```

**Mistakes Made:**
- Tried to use a CTE with just a bare `CASE` — a CTE must contain a full `SELECT` statement
- CASE WHEN values were unquoted (`P1` instead of `'P1'`) and had semicolons inside
- Used `COUNT(podium_category)` — to get separate columns, the correct pattern is `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`
- Used `WHERE COUNT(...) >= 10` — aggregates must go in `HAVING`, not `WHERE`
- Missing `JOIN races` for the year filter

**Key Pattern Learned:**
```sql
-- Counting conditional rows into separate columns:
SUM(CASE WHEN condition THEN 1 ELSE 0 END) AS column_name
```

---

### Q3 — Average Points Per Race Per Driver (2010–present)

**Task:** Return driver name, races entered, and avg points per race (rounded to 2dp). Min 20 races.

**Correct Query:**
```sql
SELECT
    drivers.forename || ' ' || drivers.surname AS driver_name,
    COUNT(*) AS races_entered,
    ROUND(AVG(results.points), 2) AS avg_points
FROM results
JOIN drivers ON results.driverId = drivers.driverId
JOIN races ON results.raceId = races.raceId
WHERE races.year >= 2010
GROUP BY drivers.driverId
HAVING COUNT(*) >= 20
ORDER BY avg_points DESC;
```

**Mistakes Made:**
- `GROUP BY driverId, raceId` — grouping by both columns gives one row per driver per race, breaking the aggregation. Group only by `driverId` to get one row per driver
- Missing `WHERE races.year >= 2010`
- Used `> 20` instead of `>= 20` for "at least 20 races"

**Key Rule Learned:**
> Group by whatever makes **one row per entity you're measuring**. Here: one row per driver = `GROUP BY driverId` only.

---

### Q4 — DNF Rate Per Driver (2010–present)

**Task:** Return driver name, total races, total DNFs, and DNF % (rounded to 1dp). Min 20 races.

**Correct Query:**
```sql
SELECT
    drivers.forename || ' ' || drivers.surname AS driver_name,
    COUNT(*) AS total_races,
    SUM(CASE WHEN status.status != 'Finished' AND status.status NOT LIKE '+%' THEN 1 ELSE 0 END) AS total_dnfs,
    ROUND(100.0 * SUM(CASE WHEN status.status != 'Finished' AND status.status NOT LIKE '+%' THEN 1 ELSE 0 END) / COUNT(*), 1) AS dnf_pct
FROM results
JOIN drivers ON results.driverId = drivers.driverId
JOIN races ON results.raceId = races.raceId
JOIN status ON results.statusId = status.statusId
WHERE races.year >= 2010
GROUP BY drivers.driverId
HAVING COUNT(*) >= 20
ORDER BY dnf_pct DESC;
```

**Mistakes Made:**
- DNF condition only checked `status != 'Finished'` — this incorrectly counted lapped finishes (`+1 Lap`, `+2 Laps`) as DNFs. Fix: add `AND status NOT LIKE '+%'`
- Missing the DNF % column entirely
- Missing `HAVING COUNT(*) >= 20`
- Missing `ORDER BY`

**F1-Specific Trick:**
```sql
-- A driver DNF'd if their status is not 'Finished' AND not a lapped finish:
status.status != 'Finished' AND status.status NOT LIKE '+%'
```

---

### Q5 — Win Rate Per Driver (2010–present)

**Task:** Return driver name, total races, total wins, and win % (rounded to 1dp). Min 20 races.

**Correct Query:**
```sql
SELECT
    drivers.forename || ' ' || drivers.surname AS driver_name,
    COUNT(*) AS total_races,
    SUM(CASE WHEN results.position = 1 THEN 1 ELSE 0 END) AS total_wins,
    ROUND(100.0 * SUM(CASE WHEN results.position = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS win_pct
FROM results
JOIN drivers ON results.driverId = drivers.driverId
JOIN races ON results.raceId = races.raceId
WHERE races.year >= 2010
GROUP BY drivers.driverId
HAVING COUNT(*) >= 20
ORDER BY win_pct DESC;
```

**Mistakes Made:**
- Missing `END` to close the `CASE WHEN` expressions
- Used `position = '1'` (string) — position is an integer, no quotes needed
- Tried to use alias `total_races` inside the same SELECT — aliases aren't available within the same SELECT, repeat `COUNT(*)`
- Missing `WHERE races.year >= 2010`
- Missing `GROUP BY drivers.driverId`
- Used `100` instead of `100.0` — causes integer division, giving 0 for most drivers
- Missing decimal argument in `ROUND` — should be `ROUND(..., 1)`

---

## Module 2: Constructor Battles

---

### Q6 — Total Wins Per Constructor Per Season (2010–present)

**Task:** Return year, constructor name, and total wins that season. Sort by year desc, wins desc.

**Correct Query:**
```sql
SELECT
    races.year,
    constructors.name AS constructor,
    SUM(CASE WHEN results.position = 1 THEN 1 ELSE 0 END) AS total_wins
FROM results
JOIN constructors ON results.constructorId = constructors.constructorId
JOIN races ON results.raceId = races.raceId
WHERE races.year >= 2010
GROUP BY constructors.constructorId, races.year
ORDER BY races.year DESC, total_wins DESC;
```

**Mistakes Made:**
- Referenced `constructors.name` but forgot `JOIN constructors`
- Added an unnecessary `JOIN drivers` — not needed for constructor queries
- Missing `ORDER BY`
- `GROUP BY constructors.name` — safer to use `constructors.constructorId` in case two teams ever share a name

---

### Q7 — Constructor Championship Final Standings Per Season (2010–present)

**Task:** Return year, constructor, final points, and final position for each season. Sort by year desc, position asc.

**Correct Query:**
```sql
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
JOIN races r ON cs.raceId = r.raceId
JOIN constructors c ON cs.constructorId = c.constructorId
JOIN last_round lr ON r.year = lr.year AND r.round = lr.last_round
ORDER BY r.year DESC, cs.position ASC;
```

**Mistakes Made:**
- CTE used `MAX(round)` without `GROUP BY year` — gives a single global max, not the last round per season
- CTE didn't SELECT `year`, so it couldn't be joined back on year
- Tried to use `WHERE races.round = final_round` instead of properly JOINing the CTE
- Missing `races.year` in the main SELECT
- Two typos: `constuctorId` (missing 'r') and `final_postion` (missing 'i')

**Key Pattern Learned:**
```sql
-- "Latest row per group" pattern:
WITH last_round AS (
    SELECT year, MAX(round) AS last_round
    FROM races
    GROUP BY year          -- always GROUP BY the key
)
-- Then JOIN back on BOTH the group key AND the max value
JOIN last_round lr ON r.year = lr.year AND r.round = lr.last_round
```

---

### Q8 — Most Dominant Constructor Per Season (Win %)

**Task:** Return year, constructor, wins, total races that season, and win % (rounded to 1dp). Sort by year desc, win % desc.

**Correct Query:**
```sql
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
    ROUND(100.0 * SUM(CASE WHEN results.position = 1 THEN 1 ELSE 0 END) / rc.total_races, 1) AS win_pct
FROM results
JOIN races ON results.raceId = races.raceId
JOIN constructors ON results.constructorId = constructors.constructorId
JOIN race_count rc ON races.year = rc.year
WHERE races.year >= 2010
GROUP BY races.year, constructors.constructorId
ORDER BY races.year DESC, win_pct DESC;
```

**Mistakes Made:**
- CTE selected `COUNT(round)` but forgot to SELECT `year` — can't join back without it
- Used `HAVING year >= 2010` in CTE — since year isn't an aggregate, use `WHERE`
- Missing comma between `total_wins` and `ROUND` columns in SELECT
- Tried `JOIN race_count ON results.year = races.year` — `results` has no `year` column, join on `races.year`
- Referenced `constructors.name` but forgot `JOIN constructors`
- Unnecessary `JOIN drivers`
- `GROUP BY constructors.constructorId` only — needs `races.year` too for one row per constructor per season
- Used `100` instead of `100.0` — integer division
- Missing decimal argument in `ROUND(..., 1)`

---

## Module 3: Qualifying vs Race

---

### Q9 — Average Grid vs Finish Position Per Driver (2010–present)

**Task:** Return driver name, avg grid position, avg finish position, and avg positions gained. Min 30 races. Sort by most positions gained.

**Correct Query:**
```sql
SELECT
    drivers.forename || ' ' || drivers.surname AS driver_name,
    ROUND(AVG(results.grid), 2) AS avg_start_pos,
    ROUND(AVG(results.positionOrder), 2) AS avg_end_pos,
    ROUND(AVG(results.grid - results.positionOrder), 2) AS avg_pos_change,
    COUNT(*) AS total_races
FROM results
JOIN drivers ON results.driverId = drivers.driverId
JOIN races ON results.raceId = races.raceId
WHERE races.year >= 2010
  AND results.grid > 0
GROUP BY drivers.driverId
HAVING COUNT(*) >= 30
ORDER BY avg_pos_change DESC;
```

**Mistakes Made:**
- Started with an unnecessary CTE — `AVG(grid - positionOrder)` can be computed directly in SELECT
- CTE was missing `driverId` so couldn't be joined back
- Used `WHERE total_races >= 30` — aggregates go in HAVING, not WHERE
- Missing `WHERE races.year >= 2010` and `results.grid > 0`
- Missing `ROUND`

---

### Q10 — Drivers Who Gained Most Positions in a Single Race (2010–present)

**Task:** Return driver name, race name, year, start/finish position, and positions gained. Top 20. No aggregation needed.

**Correct Query:**
```sql
SELECT
    drivers.forename || ' ' || drivers.surname AS driver_name,
    races.name AS race_name,
    races.year AS race_year,
    results.grid AS start_position,
    results.positionOrder AS finish_position,
    (results.grid - results.positionOrder) AS positions_gained
FROM results
JOIN drivers ON results.driverId = drivers.driverId
JOIN races ON results.raceId = races.raceId
WHERE races.year >= 2010
  AND results.grid > 0
  AND results.positionOrder > 0
ORDER BY positions_gained DESC
LIMIT 20;
```

**Mistakes Made:**
- Added unnecessary `GROUP BY` — no aggregation means no GROUP BY needed

---

### Q11 — Pole Position to Win Conversion Rate (2010–present)

**Task:** Return driver name, total poles, poles converted to wins, and conversion % (1dp). Min 5 poles.

**Correct Query:**
```sql
SELECT
    drivers.forename || ' ' || drivers.surname AS driver_name,
    COUNT(*) AS total_poles,
    SUM(CASE WHEN results.position = 1 THEN 1 ELSE 0 END) AS poles_converted,
    ROUND(100.0 * SUM(CASE WHEN results.position = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS conv_rate
FROM results
JOIN drivers ON results.driverId = drivers.driverId
JOIN races ON results.raceId = races.raceId
WHERE races.year >= 2010
  AND results.grid = 1
GROUP BY drivers.driverId
HAVING COUNT(*) >= 5
ORDER BY conv_rate DESC;
```

**Mistakes Made:**
- `HAVING` written before `GROUP BY` — correct order is WHERE → GROUP BY → HAVING → ORDER BY
- Used `100` instead of `100.0` — integer division
- Used alias in HAVING — safer to repeat the expression: `HAVING COUNT(*) >= 5`

---

## Module 4: Pit Stop Strategy

---

### Q12 — Average Pit Stop Duration Per Constructor (2010–present)

**Task:** Return constructor name and avg pit stop duration (3dp). Min 100 pit stops. Sort fastest first.

**Correct Query:**
```sql
SELECT
    constructors.name AS constructor,
    ROUND(AVG(CAST(pit_stops.duration AS REAL)), 3) AS avg_pit_stop
FROM results
JOIN races ON results.raceId = races.raceId
JOIN pit_stops ON results.raceId = pit_stops.raceId AND results.driverId = pit_stops.driverId
JOIN constructors ON results.constructorId = constructors.constructorId
WHERE races.year >= 2010
GROUP BY constructors.constructorId
HAVING COUNT(*) >= 100
ORDER BY avg_pit_stop ASC;
```

**Mistakes Made:**
- Wrong CAST syntax: `AVG(pit_stops.duration AS REAL)` — correct is `AVG(CAST(pit_stops.duration AS REAL))`
- Used `HAVING COUNT(*) AS pit_stops >= 100` — can't use AS alias inside HAVING
- Typo: `contructorId` missing 'r'
- Missing `WHERE races.year >= 2010`

**Key Pattern:**
```sql
-- JOIN pit_stops on BOTH raceId AND driverId to identify the constructor:
JOIN pit_stops ON results.raceId = pit_stops.raceId AND results.driverId = pit_stops.driverId
```

---

### Q13 — Number of Pit Stops vs Final Position (2010–present)

**Task:** Return stop count and avg finishing position for each stop count. Sort by stops ascending.

**Correct Query:**
```sql
WITH total_stops AS (
    SELECT raceId, driverId, COUNT(stop) AS stops
    FROM pit_stops
    GROUP BY raceId, driverId
)
SELECT
    total_stops.stops,
    ROUND(AVG(results.positionOrder), 2) AS avg_finish_position
FROM results
JOIN races ON results.raceId = races.raceId
JOIN total_stops ON results.raceId = total_stops.raceId
    AND results.driverId = total_stops.driverId
WHERE races.year >= 2010
GROUP BY total_stops.stops
ORDER BY total_stops.stops ASC;
```

**Mistakes Made:**
- CTE missing `driverId` in SELECT — needed to join back correctly
- JOIN on `raceId` only — must join on both `raceId AND driverId`
- Unnecessary `JOIN pit_stops` in main query — data already in CTE

**Key Rule:** When a CTE groups by multiple columns, always SELECT all of them so you can join back on them.

---

## Module 5: Championship Battles

---

### Q14 — Points Gap Between P1 and P2 Per Season (2010–present)

**Task:** For each season, return winner name, winner points, runner-up name, runner-up points, and points gap.

**Correct Query:**
```sql
WITH last_round AS (
    SELECT year, MAX(round) AS last_round
    FROM races
    WHERE year >= 2010
    GROUP BY year
),
final_standings AS (
    SELECT r.year, ds.driverId, ds.points, ds.position
    FROM driver_standings ds
    JOIN races r ON ds.raceId = r.raceId
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
```

**Mistakes Made:**
- CASE WHEN syntax backwards: wrote `alias AS CASE` instead of `CASE ... END AS alias`
- `ELSE END` without a value is invalid — omit ELSE or write `ELSE NULL`
- Trailing comma before FROM and semicolon in middle of query
- Didn't get winner and runner-up on the same row — needs a self-join on the CTE
- Missing points gap calculation

**Key Pattern — Self-join a CTE to get two rows on one line:**
```sql
FROM final_standings p1
JOIN final_standings p2 ON p1.year = p2.year AND p2.position = 2
```

---

### Q15 — Cumulative Points Through a Season (2021)

**Task:** For 2021, show each race round, race name, driver name, and cumulative points — only for drivers who finished with > 100 points.

**Correct Query:**
```sql
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
    r.name AS race_name,
    d.forename || ' ' || d.surname AS driver_name,
    ds.points AS cumulative_points
FROM driver_standings ds
JOIN races r ON ds.raceId = r.raceId
JOIN drivers d ON ds.driverId = d.driverId
JOIN top_drivers td ON ds.driverId = td.driverId
WHERE r.year = 2021
ORDER BY r.round ASC, ds.points DESC;
```

**Mistakes Made:**
- CTE used `COUNT(points)` instead of getting actual final points
- Missing `driver_standings.points` in main SELECT
- Trailing comma after driver_name
- Missing `WHERE races.year = 2021`
- `ORDER BY final_points DESC` — referenced CTE name instead of column

**Key Idea:** Use the first CTE to identify *which drivers qualify*, then the main query pulls all their per-round data.

---

## Module 6: Circuit Analysis

---

### Q16 — Most Wins Per Circuit (2010–present)

**Task:** For each circuit, return circuit name, country, top driver, and their win count. Min 2 wins. Sort by wins desc.

**Correct Query:**
```sql
WITH wins_per_driver AS (
    SELECT results.driverId, races.circuitId, COUNT(*) AS wins_count
    FROM results
    JOIN races ON results.raceId = races.raceId
    WHERE races.year >= 2010 AND results.position = 1
    GROUP BY results.driverId, races.circuitId
),
ranked AS (
    SELECT driverId, circuitId, wins_count,
           RANK() OVER (PARTITION BY circuitId ORDER BY wins_count DESC) AS rnk
    FROM wins_per_driver
)
SELECT
    circuits.name AS circuit_name,
    circuits.country AS circuit_country,
    drivers.forename || ' ' || drivers.surname AS driver_name,
    ranked.wins_count AS wins
FROM ranked
JOIN circuits ON ranked.circuitId = circuits.circuitId
JOIN drivers ON ranked.driverId = drivers.driverId
WHERE ranked.rnk = 1 AND ranked.wins_count >= 2
ORDER BY ranked.wins_count DESC;
```

**Mistakes Made:**
- `COUNT(*) WHERE position = 1` — invalid syntax, filter goes in the CTE's WHERE clause
- `RANK()` missing alias in second CTE
- Second CTE missing `wins_count` in SELECT
- Main query started FROM `results` — should start FROM the CTEs
- `results` has no `circuitId` column — that's in `races`
- Missing driver name in SELECT
- Missing year filter and `position = 1` in CTE

**Key Rule:** Once you have all data in CTEs, the main SELECT should JOIN from CTEs — not go back to raw tables.

---

### Q17 — Home Race Performance (2010–present)

**Task:** Compare each driver's avg finish at home vs away. Return driver, nationality, avg home finish, avg away finish, and home advantage. Min 3 home races.

**Correct Query:**
```sql
SELECT
    drivers.forename || ' ' || drivers.surname AS driver_name,
    drivers.nationality,
    ROUND(AVG(CASE WHEN drivers.nationality = circuits.country THEN results.positionOrder END), 2) AS avg_home_finish,
    ROUND(AVG(CASE WHEN drivers.nationality != circuits.country THEN results.positionOrder END), 2) AS avg_away_finish,
    ROUND(
        AVG(CASE WHEN drivers.nationality != circuits.country THEN results.positionOrder END) -
        AVG(CASE WHEN drivers.nationality = circuits.country THEN results.positionOrder END)
    , 2) AS home_advantage
FROM results
JOIN races ON results.raceId = races.raceId
JOIN circuits ON races.circuitId = circuits.circuitId
JOIN drivers ON results.driverId = drivers.driverId
WHERE races.year >= 2010
GROUP BY drivers.driverId
HAVING SUM(CASE WHEN drivers.nationality = circuits.country THEN 1 ELSE 0 END) >= 3
ORDER BY home_advantage DESC;
```

**Key Pattern:**
```sql
-- AVG with CASE WHEN and no ELSE automatically ignores non-matching rows (they return NULL):
AVG(CASE WHEN condition THEN value END)
```

---

## Recurring Mistakes to Watch

| Mistake | Fix |
|---------|-----|
| String concat with `+` | Use `\|\|` in SQL |
| `WHERE` for aggregates | Use `HAVING` |
| `100` in division | Use `100.0` to avoid integer division |
| Alias used in same SELECT | Repeat the expression instead |
| Missing `END` in CASE WHEN | Every `CASE` needs `END` |
| CTE missing GROUP BY key | Always SELECT + GROUP BY the column you join on |
| GROUP BY too many columns | Group only by the entity you're measuring |
| JOIN table you reference | Every table in SELECT must be JOINed |
| Joining unnecessary tables | Only JOIN tables you actually need |
| `ROUND(val)` | Always specify decimals: `ROUND(val, 1)` |
