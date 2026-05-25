"""
Run the data quality rules from docs/data_quality_rules.md against the
cleaned daily ridership data.

Prints a pass/fail summary and writes per-row results to
data/clean/dq_results.csv so the dashboard can pick it up.
"""

import os
import pandas as pd

CLEAN = os.path.join(
    os.path.dirname(__file__), "..", "data", "clean", "daily_ridership.csv",
)
OUT = os.path.join(
    os.path.dirname(__file__), "..", "data", "clean", "dq_results.csv",
)


def rule_completeness(df: pd.DataFrame) -> pd.Series:
    """DQ-001. Critical fields must not be null."""
    critical = [c for c in df.columns if "ridership" in c or c == "date"]
    return df[critical].notna().all(axis=1)


def rule_uniqueness(df: pd.DataFrame) -> pd.Series:
    """DQ-005. No duplicate dates."""
    return ~df.duplicated(subset=["date"], keep=False)


def rule_range_subway(df: pd.DataFrame) -> pd.Series:
    """DQ-003. Daily subway ridership in a plausible band."""
    col = next((c for c in df.columns if "subways" in c and "ridership" in c), None)
    if col is None:
        return pd.Series(True, index=df.index)
    return df[col].between(50_000, 6_500_000)


def rule_no_future_dates(df: pd.DataFrame) -> pd.Series:
    """DQ-002. No future-dated rows."""
    today = pd.Timestamp.today().normalize()
    return df["date"] <= today


RULES = {
    "DQ-001 completeness": rule_completeness,
    "DQ-002 no_future_dates": rule_no_future_dates,
    "DQ-003 subway_range": rule_range_subway,
    "DQ-005 uniqueness": rule_uniqueness,
}


def main():
    df = pd.read_csv(CLEAN, parse_dates=["date"])
    results = pd.DataFrame({"date": df["date"]})

    for name, fn in RULES.items():
        results[name] = fn(df)
        passed = results[name].sum()
        total = len(results)
        pct = 100 * passed / total
        print(f"{name:30s}  {passed:>6,}/{total:,}  ({pct:5.1f}% pass)")

    results.to_csv(OUT, index=False)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
