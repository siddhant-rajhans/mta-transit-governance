"""
Run the data quality rules from docs/data_quality_rules.md against the
cleaned daily ridership data.

Prints a pass/fail summary and writes per-row results to
data/clean/dq_results.csv so the dashboard can read it.
"""

import os
import pandas as pd

HERE = os.path.dirname(__file__)
CLEAN = os.path.join(HERE, "..", "data", "clean", "daily_ridership.csv")
OUT = os.path.join(HERE, "..", "data", "clean", "dq_results.csv")


def rule_completeness(df: pd.DataFrame) -> pd.Series:
    """DQ-001. Date and the main subway/bus columns must not be null."""
    return df[["date", "subway_riders", "bus_riders"]].notna().all(axis=1)


def rule_no_future_dates(df: pd.DataFrame) -> pd.Series:
    """DQ-002. No future-dated rows."""
    today = pd.Timestamp.today().normalize()
    return df["date"] <= today


def rule_subway_range(df: pd.DataFrame) -> pd.Series:
    """DQ-003. Daily subway ridership in a plausible band."""
    return df["subway_riders"].between(10_000, 6_500_000)


def rule_pct_plausible(df: pd.DataFrame) -> pd.Series:
    """DQ-004. Pre-pandemic percent within 0 - 200."""
    return df["subway_pct_prepandemic"].between(0, 2.0)


def rule_uniqueness(df: pd.DataFrame) -> pd.Series:
    """DQ-005. No duplicate dates."""
    return ~df.duplicated(subset=["date"], keep=False)


RULES = {
    "DQ-001 completeness": rule_completeness,
    "DQ-002 no_future_dates": rule_no_future_dates,
    "DQ-003 subway_range": rule_subway_range,
    "DQ-004 pct_plausible": rule_pct_plausible,
    "DQ-005 uniqueness": rule_uniqueness,
}


def main():
    df = pd.read_csv(CLEAN, parse_dates=["date"])
    results = pd.DataFrame({"date": df["date"]})

    for name, fn in RULES.items():
        results[name] = fn(df)
        passed = int(results[name].sum())
        total = len(results)
        pct = 100 * passed / total
        status = "OK" if pct >= 99.5 else ("WARN" if pct >= 95 else "FAIL")
        print(f"  [{status}] {name:30s} {passed:>6,}/{total:,}  ({pct:5.1f}% pass)")

    # Add a column that tells the dashboard which rows have any failure
    rule_cols = [c for c in results.columns if c.startswith("DQ-")]
    results["all_rules_pass"] = results[rule_cols].all(axis=1)

    results.to_csv(OUT, index=False)
    print(f"\nwrote {OUT}")
    print(f"  rows passing all rules: {int(results['all_rules_pass'].sum()):,}/{len(results):,}")


if __name__ == "__main__":
    main()
