import pandas as pd
import sqlite3
import os

# CSV files to load (must be in the data/ folder)
CSV_FILES = [
    "races",
    "results",
    "drivers",
    "constructors",
    "qualifying",
    "lap_times",
    "pit_stops",
    "circuits",
    "driver_standings",
    "constructor_standings",
    "status",
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(os.path.dirname(__file__), "f1.db")


def load_data():
    conn = sqlite3.connect(DB_PATH)
    print(f"Connected to database: {DB_PATH}\n")

    for table in CSV_FILES:
        csv_path = os.path.join(DATA_DIR, f"{table}.csv")

        if not os.path.exists(csv_path):
            print(f"  SKIPPED: {table}.csv not found in data/")
            continue

        df = pd.read_csv(csv_path)
        df.to_sql(table, conn, if_exists="replace", index=False)
        print(f"  Loaded: {table} ({len(df):,} rows)")

    conn.close()
    print(f"\nDone! Database saved to: f1.db")
    print("Open f1.db with DBeaver, TablePlus, or DB Browser for SQLite to run your queries.")


if __name__ == "__main__":
    load_data()
