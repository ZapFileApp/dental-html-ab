#!/usr/bin/env python3
"""Generate urls.js (a windowed batch of URLs, split into batches of BATCH_SIZE)
and the matching .github/workflows/scrape.yml matrix, sourced from ab_combined.csv.
Mirrors the pattern used for province city-batching (see ../next_batch.py)."""
import csv
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

BATCH_SIZE = 50
OFFSET = 0
WINDOW = 800

WORKFLOW_TEMPLATE = """name: Crawl Dentist Websites

on:
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        batch: [{batch_list}]
      fail-fast: false
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{{{ secrets.GH_PAT }}}}

      - uses: actions/setup-node@v4
        with:
          node-version: '24'

      - name: Install dependencies
        run: npm install

      - name: Install Playwright Chromium
        run: npx playwright install chromium --with-deps

      - name: Run crawler
        run: node scrape.js
        env:
          BATCH_NUM: ${{{{ matrix.batch }}}}

      - name: Commit, push, and merge results
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git checkout -b results/batch-${{{{ matrix.batch }}}}
          git add scrapedDentists/ failures/
          if git diff --cached --quiet; then
            echo "Nothing to commit, skipping PR"
            exit 0
          fi
          git commit -m "results: batch ${{{{ matrix.batch }}}}"
          git push origin results/batch-${{{{ matrix.batch }}}} --force
          gh pr create \\
            --title "results: batch ${{{{ matrix.batch }}}}" \\
            --body "Auto-generated crawl results for batch ${{{{ matrix.batch }}}}" \\
            --base main \\
            --head results/batch-${{{{ matrix.batch }}}} || true
          gh pr merge results/batch-${{{{ matrix.batch }}}} --merge --delete-branch
        env:
          GH_TOKEN: ${{{{ secrets.GH_PAT }}}}
"""


def load_urls():
    path = os.path.join(ROOT, "ab_combined.csv")
    urls = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            url = (row.get("url") or "").strip()
            if url:
                urls.append(url)
    return urls


def main():
    all_urls = load_urls()
    window = all_urls[OFFSET:OFFSET + WINDOW]
    if not window:
        print(f"Nothing to do: no urls beyond offset {OFFSET} ({len(all_urls)} total)")
        return

    js_lines = ["const urls = ["]
    for i in range(0, len(window), 5):
        chunk = window[i:i + 5]
        js_lines.append("  " + ", ".join(f'"{u}"' for u in chunk) + ",")
    js_lines.append("];")
    js_lines.append("")
    js_lines.append(f"const BATCH_SIZE = {BATCH_SIZE};")
    js_lines.append("")
    js_lines.append("const batches = {};")
    js_lines.append("for (let i = 0; i < urls.length; i++) {")
    js_lines.append("  const batchNum = Math.floor(i / BATCH_SIZE) + 1;")
    js_lines.append("  if (!batches[batchNum]) batches[batchNum] = [];")
    js_lines.append("  batches[batchNum].push(urls[i]);")
    js_lines.append("}")
    js_lines.append("")
    js_lines.append("module.exports = { batches };")
    js_lines.append("")

    with open(os.path.join(ROOT, "urls.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(js_lines))

    num_batches = (len(window) + BATCH_SIZE - 1) // BATCH_SIZE
    batch_list = ", ".join(str(i) for i in range(1, num_batches + 1))
    gh_workflows_dir = os.path.join(ROOT, ".github", "workflows")
    os.makedirs(gh_workflows_dir, exist_ok=True)
    with open(os.path.join(gh_workflows_dir, "scrape.yml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(WORKFLOW_TEMPLATE.format(batch_list=batch_list))

    end = OFFSET + len(window)
    print(f"OK: urls {OFFSET+1}-{end} of {len(all_urls)} ({len(window)} urls), {num_batches} batches")
    print(f"Remaining after this batch: {len(all_urls) - end}")


if __name__ == "__main__":
    main()
