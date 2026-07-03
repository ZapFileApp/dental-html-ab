#!/usr/bin/env python3
"""Merge all per-city CSVs in Canada_cities/ into one combined CSV."""
import csv
from pathlib import Path

ROOT = Path(__file__).parent
SRC_DIR = ROOT / "Canada_cities"
OUT_PATH = ROOT / "ab_combined.csv"

FIELDNAMES = ["url", "name", "address", "city", "state", "phone"]


def main():
    files = sorted(SRC_DIR.glob("*.csv"))
    rows_written = 0

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
        writer.writeheader()

        for csv_path in files:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    writer.writerow({k: row.get(k, "") for k in FIELDNAMES})
                    rows_written += 1

    print(f"Files merged:  {len(files)}")
    print(f"Rows written:  {rows_written}")
    print(f"Output:        {OUT_PATH}")


if __name__ == "__main__":
    main()
