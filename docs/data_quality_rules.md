# Data Quality Rules

Five rules. Each one runs on the cleaned daily ridership table and
produces a boolean column in `dq_results.csv`. The dashboard reads that
file directly.

I kept the rule set small on purpose. Five rules that actually get checked
are more useful than fifty rules nobody runs.

## DQ-001 Completeness

**What it checks:** The `date` column and every column containing
"ridership" must be non-null.

**Why:** If we don't have a date or a ridership number, the row is
useless to the dashboard. There's no point flagging it for review when
the only sensible action is to drop it.

**Severity:** Critical
**Action on fail:** Drop the row in the cleaning step. Log the count.

## DQ-002 No future dates

**What it checks:** `date` is on or before today.

**Why:** A future date in the file means the source had a typo or a
timezone error. It happens occasionally.

**Severity:** High
**Action on fail:** Drop the row and email opendata@mta.info.

## DQ-003 Subway ridership range

**What it checks:** Daily subway ridership is between 50,000 and 6.5
million.

**Why:** The lower bound catches days where the source put a near-zero
estimate that probably means "we didn't have data." The upper bound is
above the all-time peak (about 6.2M on weekdays before the pandemic).
Anything above 6.5M is almost certainly an order-of-magnitude error.

**Severity:** Medium
**Action on fail:** Flag in the dashboard, do not drop. Manual review.

## DQ-004 Pre-pandemic percent is plausible

**What it checks:** `subways_pct_pre_pandemic` is between 0 and 200.

**Why:** Values above 200 mean the 2019 baseline was wrong (maybe a
holiday in one year but not the other). Negative values would mean
something is very broken.

**Severity:** Low
**Action on fail:** Flag in dashboard.

## DQ-005 Date uniqueness

**What it checks:** No duplicate `date` values in the cleaned table.

**Why:** The daily table should have one row per date. Duplicates mean
the source export was rerun mid-week and concatenated, which I've seen
happen.

**Severity:** Critical
**Action on fail:** Keep the row with the most recent ingestion
timestamp. Log the dropped row.

## What I'm not checking, and why

A few rules I considered and dropped:

- **Cross-mode consistency** (e.g., LIRR ridership should track Metro-North
  loosely). Too noisy. Storms and service changes break the correlation
  in legitimate ways.
- **Weekday vs weekend pattern checks.** The patterns are real but writing
  a robust check for them is more work than it's worth for a portfolio
  project.
- **Anomaly detection via z-scores.** Tempting, but z-scores assume a
  stationary distribution, and ridership clearly is not stationary. A
  rolling-median approach would be better, and it's on the list if I keep
  building.
