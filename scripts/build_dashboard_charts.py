"""
Build the dashboard chart screenshots.

These mirror what the Power BI dashboard shows. They are also useful
as a sanity check that the cleaned data tells the story it should.

Outputs to dashboard/screenshots/.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

HERE = os.path.dirname(__file__)
CLEAN = os.path.join(HERE, "..", "data", "clean", "daily_ridership.csv")
DQ = os.path.join(HERE, "..", "data", "clean", "dq_results.csv")
OUT_DIR = os.path.join(HERE, "..", "dashboard", "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)


def setup_style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linewidth": 0.6,
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
    })


def page1_executive_summary(df):
    """KPIs + daily ridership trend."""
    fig = plt.figure(figsize=(13, 7.5))
    fig.suptitle(
        "MTA Transit Ridership: Executive Summary",
        fontsize=15, fontweight="bold", y=0.995,
    )

    # ---- KPI row across the top ----
    gs = fig.add_gridspec(3, 4, height_ratios=[1, 4, 0.3], hspace=0.4,
                          left=0.05, right=0.98, top=0.92, bottom=0.06)

    latest = df.iloc[-1]
    latest_30 = df.tail(30)
    latest_total = int(latest_30["total_transit_riders"].mean())

    yoy_window = df[df["date"] >= (df["date"].max() - pd.Timedelta(days=30))]
    yoy_prior = df[(df["date"] >= (df["date"].max() - pd.Timedelta(days=395))) &
                   (df["date"] < (df["date"].max() - pd.Timedelta(days=365)))]
    yoy_pct = (yoy_window["total_transit_riders"].mean() /
               max(yoy_prior["total_transit_riders"].mean(), 1) - 1) * 100

    pre_pct = latest_30["subway_pct_prepandemic"].mean() * 100

    kpis = [
        ("Latest Date", latest["date"][:10] if isinstance(latest["date"], str)
         else latest["date"].strftime("%Y-%m-%d"), "#1f4e79"),
        ("Avg Daily Riders (last 30d)", f"{latest_total/1e6:.2f}M", "#2c7a3e"),
        ("YoY Change", f"{yoy_pct:+.1f}%", "#c0392b" if yoy_pct < 0 else "#2c7a3e"),
        ("Subway vs Pre-Pandemic", f"{pre_pct:.1f}%", "#1f4e79"),
    ]

    for i, (label, value, color) in enumerate(kpis):
        ax = fig.add_subplot(gs[0, i])
        ax.text(0.5, 0.65, value, ha="center", va="center",
                fontsize=22, fontweight="bold", color=color,
                transform=ax.transAxes)
        ax.text(0.5, 0.2, label, ha="center", va="center",
                fontsize=10, color="#444",
                transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("#ccc")

    # ---- Main chart: daily ridership trend ----
    ax = fig.add_subplot(gs[1, :])
    modes = [
        ("subway_riders", "Subway", "#1f77b4"),
        ("bus_riders", "Bus", "#ff7f0e"),
        ("lirr_riders", "LIRR", "#2ca02c"),
        ("mnr_riders", "Metro-North", "#d62728"),
    ]

    # Use 7-day rolling average to smooth daily noise
    for col, label, color in modes:
        smoothed = df[col].rolling(7, min_periods=1).mean()
        ax.plot(df["date"], smoothed / 1e6, label=label, color=color, linewidth=1.5)

    ax.set_title("Daily Ridership by Mode, 2020 - 2025 (7-day rolling)",
                 loc="left", pad=8)
    ax.set_ylabel("Ridership (millions)")
    ax.set_xlabel("")
    ax.legend(loc="upper left", frameon=False, ncols=4, fontsize=9)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # Annotate the COVID dip
    covid_x = pd.Timestamp("2020-04-15")
    if df["date"].min() <= covid_x <= df["date"].max():
        ax.axvline(covid_x, color="#999", linestyle=":", linewidth=0.8)
        ax.text(covid_x, ax.get_ylim()[1] * 0.95, "  COVID lockdown",
                fontsize=8, color="#666", ha="left", va="top")

    # Footer note
    fig.text(0.05, 0.02,
             "Source: data.ny.gov MTA Daily Ridership Data 2020-2025  |  "
             "Built by Siddhant Rajhans  |  github.com/siddhant-rajhans/mta-transit-governance",
             fontsize=8, color="#666")

    out = os.path.join(OUT_DIR, "page1_executive_summary.png")
    fig.savefig(out)
    plt.close(fig)
    print(f"wrote {out}")


def page2_system_health(df):
    """Ridership by mode + day-of-week x month heatmap + recovery."""
    fig = plt.figure(figsize=(13, 8))
    fig.suptitle(
        "MTA Transit Ridership: System Health by Mode",
        fontsize=15, fontweight="bold", y=0.995,
    )

    gs = fig.add_gridspec(2, 2, hspace=0.45, wspace=0.28,
                          left=0.07, right=0.98, top=0.92, bottom=0.08)

    # ---- Top-left: average ridership by mode (last 90 days) ----
    ax = fig.add_subplot(gs[0, 0])
    recent = df.tail(90)
    modes_avg = {
        "Subway": recent["subway_riders"].mean(),
        "Bus": recent["bus_riders"].mean(),
        "LIRR": recent["lirr_riders"].mean(),
        "Metro-North": recent["mnr_riders"].mean(),
        "SIR": recent["sir_riders"].mean(),
        "Access-A-Ride": recent["aar_trips"].mean(),
    }
    bars = ax.barh(
        list(modes_avg.keys()),
        [v / 1e6 for v in modes_avg.values()],
        color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
    )
    ax.set_title("Average Daily Ridership by Mode (last 90 days)", loc="left", pad=6)
    ax.set_xlabel("Riders per day (millions)")
    ax.bar_label(bars, fmt="%.2fM", padding=3, fontsize=9)
    ax.invert_yaxis()

    # ---- Top-right: pre-pandemic recovery by mode ----
    ax = fig.add_subplot(gs[0, 1])
    recovery = {
        "Subway": recent["subway_pct_prepandemic"].mean() * 100,
        "Bus": recent["bus_pct_prepandemic"].mean() * 100,
        "LIRR": recent["lirr_pct_prepandemic"].mean() * 100,
        "Metro-North": recent["mnr_pct_prepandemic"].mean() * 100,
        "SIR": recent["sir_pct_prepandemic"].mean() * 100,
        "Access-A-Ride": recent["aar_pct_prepandemic"].mean() * 100,
    }
    colors_rec = ["#c0392b" if v < 70 else "#f39c12" if v < 90 else "#2c7a3e"
                  for v in recovery.values()]
    bars = ax.barh(list(recovery.keys()), list(recovery.values()), color=colors_rec)
    ax.axvline(100, color="#333", linestyle="--", linewidth=0.8)
    ax.set_title("Recovery vs Pre-Pandemic (last 90 days, %)", loc="left", pad=6)
    ax.set_xlabel("Percent of comparable pre-pandemic day")
    ax.bar_label(bars, fmt="%.0f%%", padding=3, fontsize=9)
    ax.invert_yaxis()

    # ---- Bottom: heatmap of subway ridership by month and day-of-week ----
    ax = fig.add_subplot(gs[1, :])
    # last 2 years for readability
    recent2 = df[df["date"] >= df["date"].max() - pd.Timedelta(days=730)].copy()
    recent2["month_label"] = recent2["date"].dt.to_period("M").astype(str)
    pivot = recent2.pivot_table(
        index="day_of_week", columns="month_label",
        values="subway_riders", aggfunc="mean",
    )
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]
    pivot = pivot.reindex(dow_order)

    im = ax.imshow(pivot.values / 1e6, aspect="auto", cmap="YlGnBu")
    ax.set_yticks(range(len(dow_order)))
    ax.set_yticklabels(dow_order)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
    ax.set_title("Subway Ridership Heatmap: Day of Week x Month (riders, millions)",
                 loc="left", pad=6)
    cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cbar.set_label("Riders (millions)", fontsize=9)

    fig.text(0.07, 0.015,
             "Source: data.ny.gov MTA Daily Ridership Data  |  "
             "Built by Siddhant Rajhans  |  github.com/siddhant-rajhans/mta-transit-governance",
             fontsize=8, color="#666")

    out = os.path.join(OUT_DIR, "page2_system_health.png")
    fig.savefig(out)
    plt.close(fig)
    print(f"wrote {out}")


def page3_data_quality(df, dq):
    """Data quality monitor: pass rates per rule + over-time."""
    fig = plt.figure(figsize=(13, 7.5))
    fig.suptitle(
        "MTA Transit Ridership: Data Quality Monitor",
        fontsize=15, fontweight="bold", y=0.995,
    )

    gs = fig.add_gridspec(2, 3, hspace=0.45, wspace=0.35,
                          left=0.07, right=0.98, top=0.92, bottom=0.08)

    rule_cols = [c for c in dq.columns if c.startswith("DQ-")]

    # ---- KPI cards ----
    total = len(dq)
    pass_all = int(dq["all_rules_pass"].sum())
    fail_any = total - pass_all

    kpis = [
        ("Records Evaluated", f"{total:,}", "#1f4e79"),
        ("Passing All Rules", f"{pass_all:,}",
         "#2c7a3e" if pass_all == total else "#f39c12"),
        ("Flagged for Review", f"{fail_any:,}",
         "#2c7a3e" if fail_any == 0 else "#c0392b"),
    ]
    for i, (label, value, color) in enumerate(kpis):
        ax = fig.add_subplot(gs[0, i])
        ax.text(0.5, 0.65, value, ha="center", va="center",
                fontsize=24, fontweight="bold", color=color,
                transform=ax.transAxes)
        ax.text(0.5, 0.2, label, ha="center", va="center",
                fontsize=10, color="#444", transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color("#ccc")

    # ---- Bottom-left: pass rate per rule ----
    ax = fig.add_subplot(gs[1, 0:2])
    rule_pct = (dq[rule_cols].sum() / total * 100).sort_values()
    colors = ["#2c7a3e" if p >= 99.5 else "#f39c12" if p >= 95 else "#c0392b"
              for p in rule_pct.values]
    bars = ax.barh(rule_pct.index, rule_pct.values, color=colors)
    ax.axvline(100, color="#333", linestyle="--", linewidth=0.8)
    ax.set_xlim(0, 105)
    ax.set_title("Pass Rate by Rule", loc="left", pad=6)
    ax.set_xlabel("Percent of records passing")
    ax.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=9)

    # ---- Bottom-right: monthly pass rate over time ----
    ax = fig.add_subplot(gs[1, 2])
    dq2 = dq.copy()
    dq2["date"] = pd.to_datetime(dq2["date"])
    dq2["year_month"] = dq2["date"].dt.to_period("M")
    monthly = dq2.groupby("year_month")["all_rules_pass"].mean() * 100
    monthly.index = monthly.index.to_timestamp()
    ax.plot(monthly.index, monthly.values, marker="o", markersize=3,
            color="#1f4e79", linewidth=1.2)
    ax.set_ylim(min(monthly.min() - 2, 95), 102)
    ax.set_title("Monthly Pass Rate", loc="left", pad=6)
    ax.set_ylabel("% passing all rules")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    fig.text(0.07, 0.015,
             "Data quality rules defined in docs/data_quality_rules.md  |  "
             "Built by Siddhant Rajhans  |  github.com/siddhant-rajhans/mta-transit-governance",
             fontsize=8, color="#666")

    out = os.path.join(OUT_DIR, "page3_data_quality.png")
    fig.savefig(out)
    plt.close(fig)
    print(f"wrote {out}")


def main():
    setup_style()
    df = pd.read_csv(CLEAN, parse_dates=["date"])
    dq = pd.read_csv(DQ, parse_dates=["date"])
    page1_executive_summary(df)
    page2_system_health(df)
    page3_data_quality(df, dq)
    print(f"\nAll charts saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
