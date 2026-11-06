import os
import sqlite3
import pandas as pd

def export_tableau_csvs():
    # Create output directory
    output_dir = "tableau_data"
    os.makedirs(output_dir, exist_ok=True)

    conn = sqlite3.connect("f1.db")

    print("Extracting Modern Era (2010-2024) data for Tableau Public...")

    # 1. Base races table (filtered to >= 2010)
    races_df = pd.read_sql_query(
        "SELECT * FROM races WHERE year >= 2010", conn
    )
    races_df.to_csv(f"{output_dir}/races.csv", index=False)
    
    # Get valid race IDs to filter child tables cleanly
    valid_race_ids = tuple(races_df["raceId"].tolist())

    # 2. Fact tables filtered by valid raceIds
    fact_tables = ["results", "pit_stops", "qualifying"]
    for table in fact_tables:
        query = f"SELECT * FROM {table} WHERE raceId IN {valid_race_ids}"
        df = pd.read_sql_query(query, conn)
        df.to_csv(f"{output_dir}/{table}.csv", index=False)
        print(f" -> Exported {table}.csv ({len(df):,} rows)")

    # 3. Dimension tables (export full tables)
    dim_tables = ["drivers", "constructors", "circuits", "status"]
    for table in dim_tables:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        df.to_csv(f"{output_dir}/{table}.csv", index=False)
        print(f" -> Exported {table}.csv ({len(df):,} rows)")

    conn.close()
    print(f"\nSuccess! All files saved to ./{output_dir}/")

if __name__ == "__main__":
    export_tableau_csvs()