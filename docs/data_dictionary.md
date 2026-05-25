# Data Dictionary

Covers the cleaned daily ridership table at `data/clean/daily_ridership.csv`.
Hourly tables are documented separately because the schema is different.

## Source

The raw file comes from data.ny.gov, dataset ID `vxuj-8kew`. MTA refreshes
it on roughly a weekly cadence (the published schedule says weekly but the
actual gap between updates has been 5 to 11 days). The cleaning script
takes care of column renaming and date parsing; nothing else is altered.

## Schema

| Column | Type | Description | Example | Notes |
|---|---|---|---|---|
| `date` | DATE | Calendar date of the observation, Eastern Time. | 2024-03-15 | One row per date. |
| `subways_total_estimated_ridership` | INT | Estimated subway entries that day. Combines turnstile and OMNY counts. | 3,847,291 | OMNY-only stations are extrapolated; expect a 1-3% systematic uncertainty. |
| `subways_pct_pre_pandemic` | FLOAT | Subway ridership as a percent of the same calendar day in 2019. | 78.4 | Useful for COVID recovery tracking. |
| `buses_total_estimated_ridership` | INT | Estimated bus boardings that day. | 1,422,008 | Includes local, express, and Select Bus Service. |
| `buses_pct_pre_pandemic` | FLOAT | Same idea, for buses. | 65.1 | |
| `lirr_total_estimated_ridership` | INT | Long Island Rail Road ridership. | 213,506 | |
| `mnr_total_estimated_ridership` | INT | Metro-North Railroad ridership. | 198,772 | |
| `aar_scheduled` | INT | Access-A-Ride scheduled trips. | 35,118 | The raw file uses three different column names for this; the cleaner normalizes them. |
| `bridges_tunnels_total_traffic` | INT | Vehicle crossings on MTA bridges and tunnels. | 854,123 | Not ridership in the usual sense, but published in the same dataset. |

## Known issues with the source

1. The "estimated" in column names is doing real work. These are not raw
   counts. The methodology is in MTA's open data documentation, but the
   short version: turnstile counts plus OMNY tap counts plus an estimate
   for back-ended turnstiles, with adjustments.

2. Numbers from early 2020 (March through May) include some manually
   entered estimates because counts were unreliable during the initial
   COVID shutdown. The `dq_results.csv` flags a few of these rows.

3. Holidays look like outliers but usually aren't errors. Compare to the
   same holiday in prior years.

## Update cadence

| Field | Refresh frequency | Lag from observation |
|---|---|---|
| All ridership columns | Weekly | 7 to 11 days |
| Bridges & tunnels traffic | Weekly | 5 to 7 days |

The dashboard's "data freshness" indicator computes lag from the latest
`date` value against today.

## Contact for the source data

MTA Data & Analytics, opendata@mta.info. They respond, usually within a
business week.
