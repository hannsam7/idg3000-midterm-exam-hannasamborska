# Midterm Exam (IDG3000) – Sustainability Audit for Akershus municipalities Repro Instructions

## Contents of this ZIP:
- Sustainability-Audit Akershus municipalities_IDG3000.pdf — The submitted paper.
- README.md — Reproduction instructions (full details and commands below).
- Midterm-exam/ — Project folder with scripts and evidence:
  - scripts/
    - node/audit.js — Main collector (runs Lighthouse 3x, greencheck, carbon.txt, CO₂).
    - python/*.py — Aggregation (aggregated.csv/.tex/.md) and charts from summary.csv.
    - municipalities.json — List of 21 municipal homepages (scope).
  - evidence/
    - lighthouse/
      - runs/ — Raw Lighthouse JSONs: <domain>_run-1.json … _run-3.json.
      - <domain>.json — Synthesized median report per site.
    - hosting/
      - *_greencheck.json — Green Web Foundation API responses.
      - *_carbon.txt — carbon.txt files (if found).
    - summary.csv — One row per site (median metrics + hosting fields).
    - aggregated.csv — Mean/Min/Max across all sites.
    - aggregated_table.tex — LaTeX table for the paper.
    - charts/ — PNG figures (performance, LCP vs weight, TBT vs JS, etc.).

## Scope
Audits 21 municipal homepages in Akershus county for:
- Performance (Lighthouse median of 3 cold runs)
- Page weight (transfer bytes, JS bytes)
- Web vitals: FCP, LCP, Speed Index, TBT, CLS
- CO₂ estimates (1byte + SWD models via @tgwf/co2)
- Green hosting status (Green Web Foundation API)
- carbon.txt presence

## Directory Layout
```
Midterm-exam/
  scripts/
    node/        -> audit.js (main script)
    python/      -> visualize.py, spreadsheet_maker.py, aggregate.py
  evidence/
    lighthouse/
      runs/      -> raw Lighthouse run JSONs (<domain>_run-1.json … _run-3.json)
      *.json     -> synthesized median report per site
    hosting/
      *_greencheck.json  -> green hosting API responses
      *_carbon.txt       -> carbon.txt files if found
    summary.csv          -> consolidated per-site medians + hosting fields
    aggregated.csv       -> mean/min/max across sites (generated)
    aggregated_table.tex -> LaTeX aggregated table
    charts/              -> generated figures (performance_scores.png etc.)
```

## Prerequisites
- macOS
- Node.js ≥ 18 (check: `node -v`)
- Python ≥ 3.10 (virtual environment recommended)
- Google Chrome installed (for Lighthouse / headless Chrome)
- jq (optional, for quick JSON inspection)

## Clone
```bash
git clone <repo-url>
cd idg3000-midterm-exam-hannasamborska
```

## Install Node dependencies
```bash
cd Midterm-exam/scripts/node
npm install
cd ../../..   
```

## Python environment (for analysis & charts)
```bash
cd Midterm-exam/scripts/python
python3 -m venv venv
source venv/bin/activate
pip install pandas altair tabulate
cd ../../../..  
```

## Run Audit (data collection)
From repo root:
```bash
node Midterm-exam/scripts/node/audit.js
```
This:
- Performs 3 cold Lighthouse runs per URL (mobile emulation).
- Computes medians for numeric metrics.
- Selects the run whose request count is closest to the median for non-aggregatable data (request list, JS breakdown).
- Estimates CO₂ from median transferBytes.
- Queries Green Web Foundation API.
- Checks for `/carbon.txt`.
- Writes artifacts to evidence/.

## Generate Aggregations, Tables, Charts
From repo root (IMPORTANT activate venv first if not already):
```bash
source Midterm-exam/scripts/python/venv/bin/activate
python Midterm-exam/scripts/python/aggregate.py
python Midterm-exam/scripts/python/visualize.py
python Midterm-exam/scripts/python/spreadsheet_maker.py
```

## Rerun From Scratch
```bash
rm -rf Midterm-exam/evidence
node Midterm-exam/scripts/node/audit.js
source Midterm-exam/scripts/python/venv/bin/activate
python Midterm-exam/scripts/python/aggregate.py
python Midterm-exam/scripts/python/visualize.py
```

## Data Lineage
1. Raw measurements: 3 Lighthouse JSONs per site (no mutation).
2. Median synthesis: one JSON per site + summary.csv row.
3. Aggregation: aggregate.py computes mean/min/max across all sites.
4. Visualization: Python reads summary.csv only (read‑only).
5. Paper tables and figures sourced from summary.csv + aggregated_table.tex.

## Validation Tips
- Check performance score raw (0–1):
  ```bash
  jq '.categories.performance.score' Midterm-exam/evidence/lighthouse/runs/www.lunner.kommune.no_run-1.json
  ```
- Confirm summary conversion (0–100):
  ```bash
  grep www.lunner.kommune.no Midterm-exam/evidence/summary.csv
  ```
- Green hosting counts:
  ```bash
  jq -r '.green' Midterm-exam/evidence/hosting/*_greencheck.json | sort | uniq -c
  ```

## Known Limitations
- Only homepages audited.
- Single network vantage point.
- CO₂ models use global averages.
- No carbon.txt found, all municipalities returned “No” at time of audit.

## Quick Commands Summary
```bash
# Audit
node Midterm-exam/scripts/node/audit.js
# Aggregate + charts
source Midterm-exam/scripts/python/venv/bin/activate
python Midterm-exam/scripts/python/aggregate.py
python Midterm-exam/scripts/python/visualize.py
# Inspect one site
jq '.lighthouseVersion, .categories.performance.score' Midterm-exam/evidence/lighthouse/runs/*asker*_run-1.json
```

## Submission (ZIP)
Create a ZIP with paper and project excluding dev folders:
```bash
zip -r idg3000-midterm-hannasamborska.zip \
  Midterm-exam README.md readme.txt paper.pdf \
  -x "**/node_modules/**" "**/venv/**" "**/.git/**" "**/.DS_Store"
```
Verify:
```bash
unzip -l idg3000-midterm-hannasamborska.zip
```

