# Power BI Dashboard Build Guide

Step-by-step recipe to build `MTA_Transit_Dashboard.pbix` in about 30
minutes. The result mirrors the three PNG screenshots in
`screenshots/`.

## Before you start

- Power BI Desktop installed (free).
- The cleaned CSVs at `data/clean/daily_ridership.csv` and
  `data/clean/dq_results.csv` exist. If not, run the four scripts in
  `scripts/` (see top-level README).

## Step 1: Load the data (3 min)

1. Open Power BI Desktop. New blank report.
2. Home -> Get data -> Text/CSV.
3. Pick `data/clean/daily_ridership.csv`. Click Load.
4. Repeat for `data/clean/dq_results.csv`.

You now have two tables in the Data pane: `daily_ridership` and
`dq_results`.

## Step 2: Build the date dimension (2 min)

1. Modeling -> New table. Paste:

   ```
   DateTable = CALENDAR(MIN(daily_ridership[date]), MAX(daily_ridership[date]))
   ```

2. With `DateTable` selected, add three calculated columns:

   ```
   Year = YEAR(DateTable[Date])
   Month = FORMAT(DateTable[Date], "MMM")
   DayOfWeek = FORMAT(DateTable[Date], "dddd")
   ```

3. Model view: drag `DateTable[Date]` to `daily_ridership[date]` to
   create a one-to-many relationship. Same to `dq_results[date]`.

## Step 3: Create the measures (5 min)

Modeling -> New measure for each. Put them in a new table called
`Measures` (Modeling -> New table, then `Measures = ROW("placeholder", BLANK())`,
then create the measures and delete the placeholder column).

```
Total Subway Riders = SUM(daily_ridership[subway_riders])
Total Bus Riders = SUM(daily_ridership[bus_riders])
Total LIRR Riders = SUM(daily_ridership[lirr_riders])
Total MNR Riders = SUM(daily_ridership[mnr_riders])
Avg Daily Total = AVERAGE(daily_ridership[total_transit_riders])

Latest Date = MAX(daily_ridership[date])

Subway Pre-Pandemic % =
    AVERAGE(daily_ridership[subway_pct_prepandemic]) * 100

YoY Change % =
VAR currentPeriod = AVERAGE(daily_ridership[total_transit_riders])
VAR priorPeriod =
    CALCULATE(
        AVERAGE(daily_ridership[total_transit_riders]),
        SAMEPERIODLASTYEAR(DateTable[Date])
    )
RETURN DIVIDE(currentPeriod - priorPeriod, priorPeriod) * 100

Records Evaluated = COUNTROWS(dq_results)
Records Passing = CALCULATE(COUNTROWS(dq_results), dq_results[all_rules_pass] = TRUE)
Records Failed = [Records Evaluated] - [Records Passing]
Pass Rate % = DIVIDE([Records Passing], [Records Evaluated]) * 100
```

## Step 4: Page 1 - Executive Summary (8 min)

Rename Page 1 to "Executive Summary".

**Top row, four KPI cards (Insert -> Card):**

| Card | Field | Format |
|---|---|---|
| Latest Date | `Latest Date` measure | Short date |
| Avg Daily Riders | `Avg Daily Total` measure | Display units: Millions, 2 decimal |
| YoY Change | `YoY Change %` measure | 1 decimal, % sign |
| Pre-Pandemic % | `Subway Pre-Pandemic %` measure | 1 decimal, % sign |

Arrange the four cards across the top in equal-width columns.

**Main chart (Insert -> Line chart):**

- X-axis: `DateTable[Date]` (set to Continuous, not Hierarchy)
- Y-axis: drag in `Total Subway Riders`, `Total Bus Riders`,
  `Total LIRR Riders`, `Total MNR Riders` (four lines)
- Title: "Daily Ridership by Mode, 2020 - 2025"
- Y-axis label: "Riders"
- Format Y-axis display units to Millions

**Slicer (Insert -> Slicer):**

- Field: `DateTable[Year]`
- Style: Dropdown, multi-select

## Step 5: Page 2 - System Health (7 min)

Insert -> New page -> "System Health".

**Left, horizontal bar chart:**

- Y-axis: a calculated table of mode names (easier: create six measures
  for each mode's avg and pull all six into one chart using "Add data"
  -> "Multiple values")
- Easier alternative: unpivot the modes once in Power Query so you have
  a `mode` column and a `riders` column. Then this chart is trivial.

  In Power Query (Transform data):
  - Select the daily_ridership table
  - Select the date column, right-click -> Unpivot other columns
  - Filter rows where the new "Attribute" column ends with `_riders`
  - Rename Attribute to `mode`, Value to `riders`
  - Save as a new query `ridership_long`

- Then: bar chart with Y=`mode`, X=AVERAGE(`riders`), filter date to
  last 90 days.

**Right, horizontal bar chart - recovery vs pre-pandemic:**

- Same unpivot trick on the `_pct_prepandemic` columns.
- Conditional formatting on the bars: red if <70%, amber if <90%,
  green otherwise.

**Bottom, matrix heatmap:**

- Matrix visual (Insert -> Matrix)
- Rows: `DateTable[DayOfWeek]`
- Columns: `DateTable[Year]` and `DateTable[Month]` (drill down)
- Values: `Total Subway Riders`
- Format -> Cell elements -> turn on Background color, set color scale
  white to dark blue.

## Step 6: Page 3 - Data Quality (5 min)

Insert -> New page -> "Data Quality".

**Top row, three cards:**

| Card | Field |
|---|---|
| Records Evaluated | `Records Evaluated` |
| Passing All Rules | `Records Passing` |
| Flagged for Review | `Records Failed` |

**Left, bar chart - pass rate per rule:**

You'll need one measure per rule:

```
DQ-001 Pass Rate = DIVIDE(CALCULATE(COUNTROWS(dq_results), dq_results[DQ-001 completeness] = TRUE), COUNTROWS(dq_results)) * 100
```

Repeat for DQ-002 through DQ-005. Then chart all five measures in a
clustered bar chart.

**Right, line chart - monthly pass rate over time:**

- X-axis: `DateTable[Date]` (set to Month hierarchy level)
- Y-axis: `Pass Rate %` measure
- Format Y-axis: min 95, max 102

## Step 7: Polish (2 min)

- View -> Themes -> pick a clean theme (Executive or Frontier).
- Each page: Insert -> Text box with a footer like:
  "Source: data.ny.gov MTA Daily Ridership | Built by Siddhant Rajhans"
- File -> Save As -> `dashboard/MTA_Transit_Dashboard.pbix`.

## After saving

```bash
cd mta-transit-governance
git add dashboard/MTA_Transit_Dashboard.pbix
git commit -m "Add Power BI dashboard file"
git push
```

## If something looks off

The PNG screenshots in `screenshots/` are the source of truth for what
each page should look like. If your Power BI version looks
substantially different, compare against the PNG and adjust.

The most common gotchas:

- Pre-pandemic columns are decimals (0.75 means 75 percent). Multiply
  by 100 in measures.
- Power BI sometimes auto-sums what should be averages. Right-click the
  field in the visual and explicitly pick Average.
- If the line chart looks spiky, add a quick-measure 7-day rolling
  average (Modeling -> Quick measure -> Rolling average).
