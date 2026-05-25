# MTA Transit Data Governance Dashboard

A Power BI dashboard built on MTA's public ridership data, with the data
governance documentation that usually doesn't ship with it: a data
dictionary, a set of data quality rules, a lineage map, and a short
policy memo on AI/ML governance for transit.

I built this because I was applying for the MTA's Enterprise Architecture
fellowship and wanted to show the work, not just talk about it.

## What's in here

```
data/         cleaned CSV exports, ready for Power BI
scripts/      Python scripts that pull and clean the raw data
dashboard/    the .pbix file plus screenshots of each page
docs/         data dictionary, quality rules, lineage, AI memo
```

## The dashboard

Three pages.

Page 1 is an executive summary. Daily ridership trend from 2020 to 2025
(the COVID dip is still visible, recovery is uneven), KPI cards for the
current month, and a mode filter so you can isolate subway vs bus vs
commuter rail.

Page 2 looks at system health. Ridership by mode side by side, a
day-of-week x month heatmap that makes the seasonality obvious, and a
data quality indicator showing how many records passed all rules.

Page 3 is the data quality monitor. It runs the rules from
`docs/data_quality_rules.md` against the cleaned dataset and shows
results. Right now most rules pass, but a few weeks in 2020 have
suspiciously round numbers that probably came from manual estimates.

## Data sources

All datasets are public, pulled from `data.ny.gov`:

- MTA Daily Ridership Data (2020-2025) - the agency's most-downloaded
  dataset, with daily totals across subway, bus, LIRR, Metro-North,
  Access-A-Ride, and bridges & tunnels.
- MTA Subway Hourly Ridership (2025+) - hourly by station and fare type.
- MTA Bus Hourly Ridership (2025+) - hourly by route and fare type.

The cleaning script handles a few quirks: inconsistent date formats
between datasets, a couple of duplicate rows in the hourly bus data, and
the fact that "Access-A-Ride" gets spelled three different ways depending
on the export.

## Why governance docs

A dashboard without a data dictionary is just a picture. If you want
someone else to trust the numbers, they need to know where the data came
from, what each column means, what counts as bad data, and what happens
when bad data shows up.

The four docs in `docs/` are the minimum I'd want before signing off on
a dataset for production use.

## The AI memo

`docs/ai_governance_memo.md` is a one-pager on what an AI/ML governance
framework at MTA could look like, given the agency's recent moves into
AI camera analytics and fare evasion detection. It references NIST AI
RMF, NYC Local Law 144, and the EU AI Act's risk tiers. It's not a legal
document. It's the kind of memo I'd write for a manager who needs to
brief leadership.

## How to reproduce

```bash
# 1. pull the raw data
python scripts/fetch_ridership.py

# 2. clean and run quality checks
python scripts/clean_ridership.py
python scripts/data_quality_checks.py

# 3. open dashboard/MTA_Transit_Dashboard.pbix in Power BI Desktop
```

You'll need Python 3.10+, pandas, and Power BI Desktop (free).

## What this is and isn't

It's a portfolio project. The data is real, the dashboard is real, the
governance docs are written the way I'd actually write them at work.

It is not a production system, an MTA-endorsed analysis, or a complete
governance framework. It's what one person can do in a few days to
demonstrate the skills the job asks for.

## License

MIT. Use any of it you want.
