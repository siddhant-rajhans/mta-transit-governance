# Data Lineage

How data moves from a turnstile to a chart on the dashboard.

```
   Subway turnstile          OMNY readers          AFC bus farebox
       at station                                     on the bus
            \                    |                       /
             \                   |                      /
              \                  v                     /
               +------> MTA internal collection <-----+
                          (proprietary, daily ETL)
                                  |
                                  v
                       MTA estimation methodology
                  (combines counts, fills gaps, smooths)
                                  |
                                  v
                       Published to data.ny.gov
                       (CSV, weekly refresh, ~7-11 day lag)
                                  |
                                  v
              scripts/fetch_ridership.py downloads
                       to data/raw/*.csv
                                  |
                                  v
                  scripts/clean_ridership.py
              (column normalization, date parsing,
               dedup, sort, write data/clean/)
                                  |
                                  v
              scripts/data_quality_checks.py
              (runs 5 rules, writes dq_results.csv)
                                  |
                                  v
            dashboard/MTA_Transit_Dashboard.pbix
                   (Power BI, refreshed manually)
```

## Trust boundaries

There are three places where I am trusting somebody else's work:

1. **Turnstile and OMNY counts.** Hardware-level; I take these at face
   value. Failure mode: a turnstile breaks and undercounts. MTA accounts
   for some of this but not all.

2. **MTA's estimation methodology.** I'm using the published estimates as
   given. Their methodology document explains the rough approach. I have
   not independently validated it, and I don't think a one-person project
   could.

3. **The data.ny.gov publication.** Occasionally rows get reposted with
   different values, presumably after a correction. DQ-005 catches the
   duplicate-date case. There's no clean way to detect silent updates to
   existing rows; if I were running this in production I'd snapshot the
   raw file daily and diff.

## What I own

Everything from `scripts/` onward. The cleaning is deterministic; given
the same raw input you get the same clean output. The quality checks are
the ones in `data_quality_rules.md`.

## Refresh model

This is currently a manual refresh. Run `fetch_ridership.py` weekly,
then `clean_ridership.py`, then open the .pbix and click Refresh.

If this were a production dashboard, the right move would be to schedule
the Python steps via Airflow (or cron, if you're being honest about the
volume), publish to a SQL warehouse, and let Power BI Service refresh
from there.
