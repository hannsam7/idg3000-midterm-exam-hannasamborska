from pathlib import Path
import pandas as pd
import numpy as np

# Locate evidence folder
evidence_dir = Path(__file__).resolve().parents[2] / "evidence"
csv_path = evidence_dir / "summary.csv"
if not csv_path.exists():
    csv_path = evidence_dir / "results.csv"
if not csv_path.exists():
    raise SystemExit(f"No summary.csv or results.csv found in {evidence_dir}")

df = pd.read_csv(csv_path)

# Normalize dtypes
num_cols = [
    "performanceScore", "transferBytes", "requests", "jsBytes",
    "co2_onebyte_grams", "co2_swd_grams",
    "fcp_ms", "lcp_ms", "speed_index_ms", "tbt_ms", "cls"
]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Derive MB columns for readability
if "transferBytes" in df.columns:
    df["transferMB"] = df["transferBytes"] / 1e6
if "jsBytes" in df.columns:
    df["jsMB"] = df["jsBytes"] / 1e6

metrics_to_aggregate = [
    ("performanceScore", "score (0–100)"),
    ("fcp_ms", "ms"),
    ("lcp_ms", "ms"),
    ("speed_index_ms", "ms"),
    ("tbt_ms", "ms"),
    ("cls", "unitless"),
    ("requests", "count"),
    ("transferMB", "MB"),
    ("jsMB", "MB"),
    ("co2_onebyte_grams", "grams"),
    ("co2_swd_grams", "grams"),
]

rows = []
for col, unit in metrics_to_aggregate:
    if col in df.columns:
        s = df[col].dropna()
        if len(s) == 0:
            continue
        rows.append({
            "metric": col,
            "unit": unit,
            "sites": int(s.count()),
            "mean": float(s.mean()),
            "min": float(s.min()),
            "max": float(s.max()),
        })

agg = pd.DataFrame(rows).sort_values("metric")

# Round for presentation 
def round_col(series, unit):
    if unit in ("MB",):
        return series.round(2)
    if unit in ("ms", "grams"):
        return series.round(1)
    if unit in ("unitless",):
        return series.round(4)
    if unit in ("score (0–100)", "count"):
        return series.round(0)
    return series

for i, row in agg.iterrows():
    unit = row["unit"]
    for k in ("mean", "min", "max"):
        agg.at[i, k] = round_col(pd.Series([row[k]]), unit).iloc[0]

# Green hosting counts
green_counts = {}
if "greenHosting" in df.columns:
    # normalize to strings: true/false/unknown
    gh = df["greenHosting"].astype(str).str.lower().map(
        {"true": "green", "false": "not_green"}
    ).fillna("unknown")
    green_counts = gh.value_counts().to_dict()

# Write outputs
out_csv = evidence_dir / "aggregated.csv"
out_tex = evidence_dir / "aggregated_table.tex"
out_md = evidence_dir / "aggregated.md"

agg.to_csv(out_csv, index=False)

# LaTeX (booktabs) table for the paper
with open(out_tex, "w", encoding="utf-8") as f:
    f.write("\\begin{table}[h]\n\\centering\n")
    f.write("\\caption{Aggregated results across all municipalities}\n\\label{tab:aggregated}\n")
    f.write("\\begin{tabular}{lrrrr}\n\\toprule\n")
    f.write("Metric & Sites & Mean & Min & Max \\\\\n\\midrule\n")
    for _, r in agg.iterrows():
        name = r['metric']
        unit = r['unit']
        f.write(f"{name} ({unit}) & {int(r['sites'])} & {r['mean']} & {r['min']} & {r['max']} \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")

# Markdown summary 
lines = ["# Aggregated metrics", "", agg.to_markdown(index=False)]
if green_counts:
    lines += ["", "## Green hosting counts", ""]
    for k in ("green", "not_green", "unknown"):
        if k in green_counts:
            lines.append(f"- {k.replace('_',' ').title()}: {green_counts[k]}")
with open(out_md, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Saved: {out_csv}")
print(f"Saved: {out_tex}")
print(f"Saved: {out_md}")
if green_counts:
    print("Green hosting counts:", green_counts)