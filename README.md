# Formula 1 Championship Analysis using SQL (Modern Era: 2010-2024)

SQL-based analysis of Formula 1 race data using the Ergast F1 dataset.
Covers driver performance, constructor battles, qualifying trends, pit stop strategy, championship battles, and circuit analysis, all visualized in an interactive self-contained dashboard.

---

## Outcomes

**Scope:** Queried across 300+ race weekends and 15 seasons of championship data to answer concrete analytical questions: which drivers consistently outperformed their grid position, how pit stop strategy correlates with finishing position, which constructors dominated across eras versus a single season, and how close the title fights were year by year.

**Iterative development:** Each module was built incrementally, refining queries through multiple attempts before arriving at the final version. The process reflects genuine analytical thinking: defining the right question, structuring the query, validating the output, and iterating until the result was correct.

**End-to-end pipeline:** The project delivers a fully interactive, self-contained dashboard built directly from SQL output, covering the complete analyst workflow from data modeling and querying through to a shareable data product.

---

## What This Project Does

17 SQL queries across 6 analytical modules, written in SQLite and organized by topic. The queries live as standalone files in `queries/` (one file per module) and are also logged in `QUERY_LOG.md` alongside mistakes made and patterns learned.

A Python pipeline extracts query results into JSON, then builds a fully self-contained `dashboard.html` with no server or dependencies: just open the file in a browser.

---

## Dataset Setup

1. Download the dataset from Kaggle:
   https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020

2. Extract the CSVs into a `data/` folder inside this project.

3. Run the setup script to load everything into a local SQLite database:
   ```bash
   pip install -r requirements.txt
   python setup.py
   python validate.py   # optional: run 17 data-quality checks
   ```
   This creates `f1.db` in the project root.

4. Open `f1.db` with any SQL client (DBeaver, TablePlus, DB Browser for SQLite) or run queries via Python.

---

## Dataset Schema

| Table | Description |
|-------|-------------|
| `races` | Race name, year, round, circuit, date |
| `results` | Finishing position, points, grid, laps, status per driver per race |
| `drivers` | Driver name, nationality, date of birth |
| `constructors` | Team name, nationality |
| `qualifying` | Q1/Q2/Q3 times per driver per race |
| `lap_times` | Lap-by-lap times for every driver |
| `pit_stops` | Stop number, lap, and duration per driver per race |
| `circuits` | Circuit name, location, country |
| `driver_standings` | Points and position after each race |
| `constructor_standings` | Constructor points and position after each race |
| `status` | Finish status (Finished, Accident, Engine, etc.) |

---

## SQL Modules

### Module 1: Driver Performance (Q1-Q5)

| Query | Task | Key Concepts |
|-------|------|--------------|
| Q1 | Total wins per driver | `GROUP BY`, `COUNT`, `JOIN` |
| Q2 | Podium breakdown (W/P2/P3) | `SUM(CASE WHEN)`, `HAVING` |
| Q3 | Avg points per race | `AVG`, `ROUND`, `HAVING` |
| Q4 | DNF rate per driver | `status NOT LIKE '+%'`, percentage calc |
| Q5 | Win rate per driver | `SUM(CASE WHEN)`, `100.0` division |

### Module 2: Constructor Battles (Q6-Q8)

| Query | Task | Key Concepts |
|-------|------|--------------|
| Q6 | Total wins per constructor per season | `GROUP BY year, constructorId` |
| Q7 | Championship final standings per season | CTE + "latest row per group" pattern |
| Q8 | Most dominant constructor (win %) | CTE for race count, `100.0` division |

### Module 3: Qualifying vs Race (Q9-Q11)

| Query | Task | Key Concepts |
|-------|------|--------------|
| Q9 | Avg grid vs finish position per driver | `AVG(grid - positionOrder)` |
| Q10 | Most positions gained in a single race | Row-level calc, no aggregation |
| Q11 | Pole-to-win conversion rate | `grid = 1` filter, `SUM(CASE WHEN)` |

### Module 4: Pit Stop Strategy (Q12-Q13)

| Query | Task | Key Concepts |
|-------|------|--------------|
| Q12 | Avg pit stop duration per constructor | `CAST(duration AS REAL)`, dual-key JOIN |
| Q13 | Pit stop count vs final position | CTE aggregation, self-join on raceId + driverId |

### Module 5: Championship Battles (Q14-Q15)

| Query | Task | Key Concepts |
|-------|------|--------------|
| Q14 | Points gap between P1 and P2 per season | CTE self-join to get two rows on one line |
| Q15 | Cumulative points through a season | Filter CTE + per-round standings join |

### Module 6: Circuit Analysis (Q16-Q17)

| Query | Task | Key Concepts |
|-------|------|--------------|
| Q16 | Most wins per circuit | `RANK() OVER (PARTITION BY circuitId)` |
| Q17 | Home race advantage per driver | `AVG(CASE WHEN nationality = country)` |

---

## Key SQL Patterns

```sql
-- Conditional column split (wins / podiums / DNFs as separate columns)
SUM(CASE WHEN condition THEN 1 ELSE 0 END) AS column_name

-- Latest row per group (e.g. final standings of each season)
WITH last_round AS (
    SELECT year, MAX(round) AS last_round
    FROM races
    GROUP BY year
)
JOIN last_round lr ON r.year = lr.year AND r.round = lr.last_round

-- Self-join a CTE to put P1 and P2 on the same row
FROM standings p1
JOIN standings p2 ON p1.year = p2.year AND p2.position = 2
WHERE p1.position = 1

-- AVG ignoring non-matching rows without a subquery
AVG(CASE WHEN condition THEN value END)

-- F1-specific: detect a DNF (excludes lapped finishes)
status.status != 'Finished' AND status.status NOT LIKE '+%'
```

---

## Dashboard

An interactive data dashboard built with vanilla JS + Chart.js, styled with the GRIDLINE design system. Self-contained as a single HTML file (no server required).

**To build the dashboard:**
```bash
pip install pandas
python extract_data.py   # runs all 17 queries, outputs dashboard_data.json
python build_dashboard.py  # embeds JSON + JS into dashboard.html
```

Then open `dashboard.html` in any browser.

**Features:**
- 6 views: Drivers, Constructors, Qualifying, Strategy, Championship, Circuits
- Season picker: filter all views to any single year (2010-2024) or all seasons
- Dynamic hero stat: top-line number updates based on current view and selected season
- Compare mode: side-by-side driver comparison across key metrics
- Dark/light theme toggle
- Charts: stacked bar (constructor wins), line chart (cumulative points), horizontal bar charts

---

## Project Structure

```
F1 SQL Analysis/
├── README.md
├── CHANGES.md             # Log of repo improvements
├── QUERY_LOG.md           # All 17 queries + mistakes + patterns learned
├── requirements.txt       # Python dependencies
├── queries/               # The 17 queries as standalone .sql files (per module)
├── setup.py               # Loads CSVs into SQLite (run once)
├── validate.py            # Data-quality checks against f1.db
├── extract_data.py        # Runs all queries, outputs dashboard_data.json
├── build_dashboard.py     # Builds self-contained dashboard.html from JSON
├── f1.db                  # Generated SQLite database (after setup.py)
├── dashboard_data.json    # Generated query results (after extract_data.py)
├── dashboard.html         # Final interactive dashboard (after build_dashboard.py)
└── data/                  # Place downloaded CSVs here
    ├── races.csv
    ├── results.csv
    ├── drivers.csv
    ├── constructors.csv
    ├── qualifying.csv
    ├── lap_times.csv
    ├── pit_stops.csv
    ├── circuits.csv
    ├── driver_standings.csv
    ├── constructor_standings.csv
    └── status.csv
```

---

## Key Filter

All queries are scoped to the modern era (2010-2024):
```sql
WHERE races.year >= 2010
```
