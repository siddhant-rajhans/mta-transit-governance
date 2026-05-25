"""
Pull MTA ridership datasets from data.ny.gov.

Run this first. It downloads the three CSVs we use into data/raw/.
If a file already exists it gets skipped, so you can re-run safely.
"""

import os
import sys
from urllib.request import urlretrieve

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

DATASETS = {
    "daily_ridership_2020_2025.csv":
        "https://data.ny.gov/api/views/vxuj-8kew/rows.csv?accessType=DOWNLOAD",
    "subway_hourly_2025.csv":
        "https://data.ny.gov/api/views/wujg-7c2s/rows.csv?accessType=DOWNLOAD",
    "bus_hourly_2025.csv":
        "https://data.ny.gov/api/views/kv7t-r4xa/rows.csv?accessType=DOWNLOAD",
}


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    for name, url in DATASETS.items():
        path = os.path.join(RAW_DIR, name)
        if os.path.exists(path):
            print(f"skip  {name} (already downloaded)")
            continue
        print(f"fetch {name} ...")
        urlretrieve(url, path)
        size_mb = os.path.getsize(path) / 1_000_000
        print(f"      done. {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
