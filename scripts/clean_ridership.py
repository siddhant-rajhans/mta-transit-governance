"""
Clean the daily ridership file.

The raw file from data.ny.gov has long column names with colons and
mixed case. This script:
  - normalizes column names to lowercase snake_case
  - parses the Date column (MM/DD/YYYY in the raw file) to datetime
  - drops any duplicate dates (the source occasionally re-publishes)
  - sorts by date

Output: data/clean/daily_ridership.csv
"""

import os
import pandas as pd

HERE = os.path.dirname(__file__)
RAW = os.path.join(HERE, "..", "data", "raw", "daily_ridership_2020_2025.csv")
OUT_DIR = os.path.join(HERE, "..", "data", "clean")
OUT = os.path.join(OUT_DIR, "daily_ridership.csv")

# Map the raw column names to short stable names the dashboard can use.
COLUMN_MAP = {
    "Date": "date",
    "Subways: Total Estimated Ridership": "subway_riders",
    "Subways: % of Comparable Pre-Pandemic Day": "subway_pct_prepandemic",
    "Buses: Total Estimated Ridership": "bus_riders",
    "Buses: % of Comparable Pre-Pandemic Day": "bus_pct_prepandemic",
    "LIRR: Total Estimated Ridership": "lirr_riders",
    "LIRR: % of Comparable Pre-Pandemic Day": "lirr_pct_prepandemic",
    "Metro-North: Total Estimated Ridership": "mnr_riders",
    "Metro-North: % of Comparable Pre-Pandemic Day": "mnr_pct_prepandemic",
    "Access-A-Ride: Total Scheduled Trips": "aar_trips",
    "Access-A-Ride: % of Comparable Pre-Pandemic Day": "aar_pct_prepandemic",
    "Bridges and Tunnels: Total Traffic": "bridges_tunnels_traffic",
    "Bridges and Tunnels: % of Comparable Pre-Pandemic Day": "bridges_tunnels_pct_prepandemic",
    "Staten Island Railway: Total Estimated Ridership": "sir_riders",
    "Staten Island Railway: % of Comparable Pre-Pandemic Day": "sir_pct_prepandemic",
}


def main():
    print(f"reading {RAW}")
    df = pd.read_csv(RAW)
    print(f"  raw shape: {df.shape}")

    # Rename
    df = df.rename(columns=COLUMN_MAP)

    # Parse dates. Raw format is MM/DD/YYYY.
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y", errors="coerce")
    bad = df["date"].isna().sum()
    if bad:
        print(f"  warning: {bad} rows had unparseable dates and were dropped")
        df = df.dropna(subset=["date"])

    # Dedup and sort
    before = len(df)
    df = df.drop_duplicates(subset=["date"]).sort_values("date").reset_index(drop=True)
    if len(df) < before:
        print(f"  dropped {before - len(df)} duplicate dates")

    # Add a few derived columns useful for the dashboard
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day_of_week"] = df["date"].dt.day_name()
    df["is_weekend"] = df["date"].dt.dayofweek >= 5
    df["total_transit_riders"] = (
        df["subway_riders"].fillna(0)
        + df["bus_riders"].fillna(0)
        + df["lirr_riders"].fillna(0)
        + df["mnr_riders"].fillna(0)
        + df["sir_riders"].fillna(0)
    )

    os.makedirs(OUT_DIR, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"wrote {OUT}  ({len(df):,} rows, {len(df.columns)} columns)")
    print(f"  date range: {df['date'].min().date()} to {df['date'].max().date()}")


if __name__ == "__main__":
    main()
