"""
Clean the daily ridership file.

Mostly handles three things the raw data gets wrong:
  - inconsistent column names (spaces, mixed case)
  - date parsing (some rows are MM/DD/YYYY, others ISO)
  - Access-A-Ride column has at least three different spellings
    depending on which export you grab

Output goes to data/clean/daily_ridership.csv.
"""

import os
import pandas as pd

RAW = os.path.join(
    os.path.dirname(__file__), "..", "data", "raw",
    "daily_ridership_2020_2025.csv",
)
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "clean")
OUT = os.path.join(OUT_DIR, "daily_ridership.csv")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace(":", "")
    )
    # Access-A-Ride alias zoo
    aliases = {
        "access_a_ride_total_scheduled_trips": "aar_scheduled",
        "access_a_ride__total_scheduled_trips": "aar_scheduled",
        "access_a_ride_total_trips": "aar_trips",
    }
    df = df.rename(columns={k: v for k, v in aliases.items() if k in df.columns})
    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    if "date" not in df.columns:
        raise ValueError("expected a 'date' column after normalization")
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    bad = df["date"].isna().sum()
    if bad:
        print(f"warning: {bad} rows had unparseable dates and were dropped")
    return df.dropna(subset=["date"])


def main():
    print(f"reading {RAW}")
    df = pd.read_csv(RAW)
    print(f"  {len(df):,} rows, {len(df.columns)} columns")

    df = normalize_columns(df)
    df = parse_dates(df)

    before = len(df)
    df = df.drop_duplicates(subset=["date"])
    if len(df) < before:
        print(f"  dropped {before - len(df)} duplicate dates")

    df = df.sort_values("date").reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"wrote {OUT}  ({len(df):,} rows)")


if __name__ == "__main__":
    main()
