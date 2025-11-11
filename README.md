# Sustainability Audit of Municipal Websites (Midterm Exam – IDG3000)

## 1. Overview
This repository contains scripts and evidence for an audit of all municipal websites in the Norwegian county (fylke): **Akershus**.  
Focus: performance, page weight, JavaScript footprint, estimated transfer CO₂ (SWD & OneByte), green hosting status, and transparency (carbon.txt).

## 2. Repository Structure
```
scripts/
  audit.js                 # Multi-run Lighthouse + carbon.txt + Green Web API
  compute_co2.js           # CO₂ estimates from total-byte-weight
  export_to_csv.py         # Aggregates metrics into results.csv
  visualize.py             # Generates charts (performance, hosting, JS vs CO2)
  spreadsheet_maker.py     # Creates spreadsheets + Excel workbook
  extract_screenshots.js   # Saves final page screenshots from Lighthouse JSON
  municipalities.json      # List of municipal root URLs audited
evidence/
  lighthouse/              # Synthesized median Lighthouse JSON per site
    runs/                  # Raw per-run JSONs (3 runs per site)
  hosting/                 # *_greenweb.json and *_carbon.txt (+ *_co2.json after compute_co2.js)
  charts/                  # PNG charts
  spreadsheets/            # results.csv, averages.csv, green_hosting_summary.csv, audit_results.xlsx
  averages_summary.csv     # Quick averages (created by visualize.py)
```

## 3. Tools & Versions
- Node.js: `v23.11.0` (Note: Node 18+ ships with global fetch; no node-fetch needed)
- Lighthouse CLI: `13.0.1`
- Python: `Python 3.13.3`
- pandas / matplotlib / openpyxl: see `scripts/requirements.txt`
- @tgwf/co2: `@tgwf/co2@0.16.9`

## 4. Methodology
1. Collected all municipality URLs (municipalities.json).
2. For each URL ran 3 cold Lighthouse CLI tests (headless Chrome).
3. Computed per-metric medians (Performance score, FCP, LCP, Speed Index, total-byte-weight, request count).
4. Selected the run closest in request count to median to preserve realistic network-requests for JS byte calculation.
5. Synthesized a consolidated JSON per site containing median values plus real request list.
6. Checked:
   - carbon.txt (HTTP GET /carbon.txt)
   - Green hosting (Green Web Foundation API).
7. Estimated CO₂ using @tgwf/co2 (SWD & 1byte models) from total-byte-weight.
8. Exported aggregated metrics to CSV, built charts, spreadsheets, and Excel workbook.
9. Generated final screenshots from Lighthouse JSONs for evidence.

## 5. Metrics Collected
| Column | Description |
| ------ | ----------- |
| PerfScore | Lighthouse Performance score (0–100) median |
| FCP / LCP / SpeedIndex | Median timings (ms) |
| PageWeightBytes | Median total-byte-weight |
| Requests | Median request count (approx) |
| JSBytes | Sum of transferSize for Script resources (from chosen run) |
| CO2_SWD_g / CO2_OneByte_g | Estimated grams CO₂e per page load (transfer only) |
| GreenHosting | Yes/No from Green Web API (`green` boolean) |
| CarbonTxt | Presence of carbon.txt file |
| URL / Municipality | Identification fields |

## 6. Reproduction Steps

### Setup
```sh
git clone <repo-url>
cd Midterm-exam/scripts

# Install Node deps
npm install @tgwf/co2 node-fetch

# Python venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Audit
```sh
# Node (audit + CO2)
cd Midterm-exam/scripts/node
npm install
npm run audit
npm run co2

# Python (CSV + charts + spreadsheets)
cd ../python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 export_to_csv.py
python3 visualize.py
python3 spreadsheet_maker.py
```

### Outputs Verification
```sh
ls ../evidence/lighthouse/*.json | wc -l    # Count synthesized reports
head ../evidence/results.csv
ls ../evidence/charts
ls ../evidence/spreadsheets
```

To clean and re-run (keeping raw audit evidence only):
```sh
rm -f ../evidence/results.csv ../evidence/averages_summary.csv
find ../evidence/charts -type f -delete
rm -rf ../evidence/spreadsheets
find ../evidence/hosting -name '*_co2.json' -delete
# Re-run pipeline thereafter
```

## 7. Script Descriptions
- audit.js: Orchestrates multi-run Lighthouse, median synthesis, carbon.txt probe, green hosting API.
- compute_co2.js: Reads Lighthouse JSON total-byte-weight, calculates SWD + 1byte CO₂, writes *_co2.json.
- export_to_csv.py: Aggregates all metrics from evidence folders into results.csv (includes JSBytes).
- visualize.py: Converts CSV into charts (performance distribution, green hosting pie/bar, JSBytes vs CO2).
- spreadsheet_maker.py: Creates Excel workbook (Results, Averages, GreenHostingSummary) plus CSV summaries.
- extract_screenshots.js: Decodes final-screenshot data URIs to image files for evidence.

## 8. Median Logic
Median reduces variance from single-run outliers. Using real request list from the closest run preserves accurate JS resource enumeration (vs synthetic placeholder).

## 9. Limitations
- Emissions reflect transfer only (no rendering or server-side energy).
- Single-page (homepage) snapshot — deeper navigation not included.
- carbon.txt absent for all sites (indicates transparency gap).
- Green hosting relies on external API accuracy at audit time.

## 10. How to Extend
- Add more metrics (e.g., TBT, CLS) similarly in audit median aggregation.
- Include historical runs (timestamped folders).
- Implement unit tests for parsing (pytest) if needed.

## 11. References (to cite in paper)
- Lighthouse (Google, Web Performance auditing tool).
- Green Web Foundation API: https://www.thegreenwebfoundation.org
- CO₂ Models (@tgwf/co2): SWD & 1byte.
- Web Sustainability Guidelines (W3C WSG).
- Król, K. (2025). Sustainability audit methodology (inspiration).

## 12. Paper Mapping
| Section | Repository Evidence |
|---------|---------------------|
| Abstract | Summaries from results & averages |
| Method | README steps + audit.js code |
| Results | results.csv, charts, Excel |
| Discussion | Interpret performance vs CO₂ vs hosting |
| Conclusion | Recommendations grounded in metrics |
| Reproducibility | This README + scripts |

## 13. Quick Data Quality Check
```sh
python3 - <<'PY'
import pandas as pd
df = pd.read_csv('../evidence/results.csv')
print('Rows:', len(df))
print('Missing PerfScore:', df['PerfScore'].isna().sum())
print('Missing CO2:', df['CO2_SWD_g'].isna().sum(), df['CO2_OneByte_g'].isna().sum())
print('Avg Page Weight MB:', round(df['PageWeightBytes'].mean()/1024/1024,3))
print('Avg JS KB:', round(df['JSBytes'].mean()/1024,2))
PY
```

## 14. License / Academic Integrity
Data collected for academic assessment only. Do not redistribute raw site content.
---
