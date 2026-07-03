#!/usr/bin/env python3
"""Strip query params from every url in ab_combined.csv, then re-dedupe
(stripping params, e.g. UTM tags, commonly collapses previously-distinct rows
into the same url)."""
import csv
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).parent
CSV_PATH = ROOT / "ab_combined.csv"


def strip_query(url):
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def main():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    seen = set()
    deduped = []
    stripped_count = 0
    for row in rows:
        url = (row.get("url") or "").strip()
        if not url:
            continue
        new_url = strip_query(url)
        if new_url != url:
            stripped_count += 1
        row["url"] = new_url
        if new_url in seen:
            continue
        seen.add(new_url)
        deduped.append(row)

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduped)

    print(f"Rows before:            {len(rows)}")
    print(f"URLs with query params: {stripped_count}")
    print(f"Rows after (deduped):   {len(deduped)}")
    print(f"New duplicates removed: {len(rows) - len(deduped)}")


if __name__ == "__main__":
    main()
