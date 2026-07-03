#!/usr/bin/env python3
"""Remove duplicate rows (by url) from ab_combined.csv, in place. Keeps first occurrence."""
import csv
from pathlib import Path

ROOT = Path(__file__).parent
CSV_PATH = ROOT / "ab_combined.csv"


def main():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    seen = set()
    deduped = []
    for row in rows:
        url = (row.get("url") or "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        deduped.append(row)

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduped)

    print(f"Rows before: {len(rows)}")
    print(f"Rows after:  {len(deduped)}")
    print(f"Removed:     {len(rows) - len(deduped)}")


if __name__ == "__main__":
    main()
