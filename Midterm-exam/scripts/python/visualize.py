import os, csv, pandas as pd, matplotlib.pyplot as plt
from pathlib import Path

base_dir = Path(__file__).resolve().parent
# evidence folder is at Midterm-exam/evidence (two levels up from scripts/python)
evidence_dir = base_dir.parent.parent / "evidence"
results_csv = evidence_dir / "results.csv"
if not results_csv.exists():
    alt = evidence_dir / "summary.csv"
    if alt.exists():
        results_csv = alt
charts_dir = evidence_dir / "charts"
charts_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(results_csv)

df = df.rename(columns={
    "domain": "Municipality",
    "performanceScore": "PerfScore",
    "fcp_ms": "FCP",
    "lcp_ms": "LCP",
    "speed_index_ms": "SpeedIndex",
    "transferBytes": "PageWeightBytes",
    "jsBytes": "JSBytes",
    "co2_swd_grams": "CO2_SWD_g",
    "co2_onebyte_grams": "CO2_OneByte_g"
})

if "GreenHosting" not in df.columns:
    df["GreenHosting"] = "unknown"

for col in ["PerfScore","FCP","LCP","SpeedIndex","PageWeightBytes","Requests","JSBytes","CO2_SWD_g","CO2_OneByte_g"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# 1. Performance scores
plt.figure(figsize=(10,6))
sorted_df = df.sort_values('PerfScore', ascending=False)
plt.bar(sorted_df['Municipality'], sorted_df['PerfScore'], color='#4b8bbe')
plt.xticks(rotation=90, fontsize=8)
plt.ylabel('Performance Score (0–100)')
plt.title('Municipality Performance Scores')
plt.tight_layout()
perf_path = charts_dir / 'performance_scores.png'
plt.savefig(perf_path, dpi=150); plt.close()

# 2. JS Bytes vs CO2 (SWD)
plt.figure(figsize=(7,5))
plt.scatter(df['JSBytes']/1024.0, df['CO2_SWD_g'], c='#6a4fbf', s=35, alpha=0.85)
plt.xlabel('JS Transfer (KB)')
plt.ylabel('CO₂ (SWD grams)')
plt.title('JS Bytes vs CO₂')
plt.tight_layout()
js_co2_path = charts_dir / 'jsbytes_vs_co2.png'
plt.savefig(js_co2_path, dpi=150); plt.close()

# 3. Transfer size vs Performance
if 'PageWeightBytes' in df.columns:
    plt.figure(figsize=(7,5))
    js_share = (df['JSBytes']/df['PageWeightBytes'].replace(0, pd.NA))*100
    plt.scatter(df['PageWeightBytes']/1024.0, df['PerfScore'],
                s=(js_share.fillna(0))*2+20,
                c=df['CO2_SWD_g'], cmap='viridis', alpha=0.85)
    plt.colorbar(label='CO₂ SWD (g)')
    plt.xlabel('Transfer Size (KB)')
    plt.ylabel('Performance Score')
    plt.title('Performance vs Transfer Size (bubble=JS share %, color=CO₂)')
    plt.tight_layout()
    perf_transfer_path = charts_dir / 'perf_vs_transfer.png'
    plt.savefig(perf_transfer_path, dpi=150); plt.close()
else:
    perf_transfer_path = None

# 4. Top 10 by transfer size
top10 = df.sort_values('PageWeightBytes', ascending=False).head(10)
plt.figure(figsize=(10,6))
plt.bar(top10['Municipality'], top10['PageWeightBytes']/1024.0, color='#ff7043')
plt.xticks(rotation=90, fontsize=8)
plt.ylabel('Transfer Size (KB)')
plt.title('Top 10 Heaviest Pages')
plt.tight_layout()
top_heavy_path = charts_dir / 'top10_transfer.png'
plt.savefig(top_heavy_path, dpi=150); plt.close()

# 5. CO2 model comparison
plt.figure(figsize=(6,5))
plt.scatter(df['CO2_OneByte_g'], df['CO2_SWD_g'], c='#00897b', s=40, alpha=0.8)
plt.xlabel('CO₂ OneByte (g)')
plt.ylabel('CO₂ SWD (g)')
plt.title('CO₂ Model Comparison')
plt.tight_layout()
co2_compare_path = charts_dir / 'co2_models.png'
plt.savefig(co2_compare_path, dpi=150); plt.close()

avg = {
    "Avg_PerfScore": round(df['PerfScore'].mean(),2),
    "Avg_LCP_ms": round(df['LCP'].mean(),2),
    "Avg_FCP_ms": round(df['FCP'].mean(),2),
    "Avg_Transfer_KB": round((df['PageWeightBytes']/1024.0).mean(),2),
    "Avg_CO2_SWD_g": round(df['CO2_SWD_g'].mean(),4)
}
avg_csv = evidence_dir / 'averages_summary.csv'
with open(avg_csv, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['Metric','Value'])
    for k,v in avg.items(): w.writerow([k,v])

print("Charts generated:")
for p in [perf_path, js_co2_path, perf_transfer_path, top_heavy_path, co2_compare_path, avg_csv]:
    if p: print("-", p)