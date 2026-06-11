"""
Tests for the data quality rules and the cleaned dataset itself.

Two layers:
1. Unit tests: each DQ rule against small hand-built DataFrames where the
   expected pass/fail outcome is obvious.
2. Contract test: the committed cleaned CSV must pass every rule — if a
   future re-run of the pipeline commits bad data, CI catches it.
"""

import os
import sys

import pandas as pd
import pytest

# scripts/ is not a package; make its modules importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from data_quality_checks import (
    rule_completeness,
    rule_no_future_dates,
    rule_pct_plausible,
    rule_subway_range,
    rule_uniqueness,
)

CLEAN_CSV = os.path.join(
    os.path.dirname(__file__), "..", "data", "clean", "daily_ridership.csv"
)


def make_df(**overrides) -> pd.DataFrame:
    """A two-row frame that passes every rule unless overridden."""
    base = {
        "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "subway_riders": [3_000_000, 3_100_000],
        "bus_riders": [1_200_000, 1_250_000],
        "subway_pct_prepandemic": [0.75, 0.78],
    }
    base.update(overrides)
    return pd.DataFrame(base)


class TestRules:
    def test_clean_frame_passes_everything(self):
        df = make_df()
        for rule in (rule_completeness, rule_no_future_dates,
                     rule_subway_range, rule_pct_plausible, rule_uniqueness):
            assert rule(df).all(), rule.__name__

    def test_completeness_flags_null_ridership(self):
        df = make_df(subway_riders=[3_000_000, None])
        result = rule_completeness(df)
        assert result.tolist() == [True, False]

    def test_future_dates_flagged(self):
        future = pd.Timestamp.today() + pd.Timedelta(days=30)
        df = make_df(date=pd.to_datetime(["2024-01-01", future]))
        result = rule_no_future_dates(df)
        assert result.tolist() == [True, False]

    def test_subway_range_flags_order_of_magnitude_errors(self):
        df = make_df(subway_riders=[3_000_000, 60_000_000])  # 10x too high
        result = rule_subway_range(df)
        assert result.tolist() == [True, False]

    def test_subway_range_flags_near_zero(self):
        df = make_df(subway_riders=[3_000_000, 500])
        result = rule_subway_range(df)
        assert result.tolist() == [True, False]

    def test_pct_plausible_flags_broken_baseline(self):
        df = make_df(subway_pct_prepandemic=[0.75, 4.2])  # 420% of pre-pandemic
        result = rule_pct_plausible(df)
        assert result.tolist() == [True, False]

    def test_uniqueness_flags_duplicate_dates(self):
        df = make_df(date=pd.to_datetime(["2024-01-01", "2024-01-01"]))
        result = rule_uniqueness(df)
        assert not result.any()


class TestCommittedData:
    """The cleaned CSV in the repo is a contract — it must stay valid."""

    @pytest.fixture(scope="class")
    def df(self):
        if not os.path.exists(CLEAN_CSV):
            pytest.skip("cleaned CSV not present")
        return pd.read_csv(CLEAN_CSV, parse_dates=["date"])

    def test_has_expected_shape(self, df):
        assert len(df) >= 1700
        assert "subway_riders" in df.columns
        assert "total_transit_riders" in df.columns

    def test_all_rules_pass_on_committed_data(self, df):
        for rule in (rule_completeness, rule_no_future_dates,
                     rule_subway_range, rule_pct_plausible, rule_uniqueness):
            pct = rule(df).mean() * 100
            assert pct == 100.0, f"{rule.__name__}: {pct:.1f}% pass"

    def test_derived_total_is_consistent(self, df):
        recomputed = (
            df["subway_riders"].fillna(0)
            + df["bus_riders"].fillna(0)
            + df["lirr_riders"].fillna(0)
            + df["mnr_riders"].fillna(0)
            + df["sir_riders"].fillna(0)
        )
        assert (df["total_transit_riders"] - recomputed).abs().max() < 1e-6
