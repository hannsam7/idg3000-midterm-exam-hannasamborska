import os, shutil, pandas as pd
from pathlib import Path

base_dir = Path(__file__).resolve().parent              
evidence_dir = base_dir.parent.parent / "evidence"      
results = evidence_dir / "results.csv"
summary = evidence_dir / "summary.csv"
out_dir = evidence_dir / "spreadsheets"
out_dir.mkdir(parents=True, exist_ok=True)

source_csv = results if results.exists() else summary
if not source_csv.exists():
    raise SystemExit(f"No results.csv or summary.csv found in {evidence_dir}")

shutil.copyfile(source_csv, out_dir / source_csv.name)

df = pd.read_csv(source_csv)

df = df.rename(columns={
    "performanceScore": "PerfScore",
    "fcp_ms": "FCP",
    "lcp_ms": "LCP",
    "speed_index_ms": "SpeedIndex",
    "tbt_ms": "TBT",
    "cls": "CLS",
    "transferBytes": "PageWeightBytes",
    "jsBytes": "JSBytes",
    "co2_swd_grams": "CO2_SWD_g",
    "co2_onebyte_grams": "CO2_OneByte_g",
    "requests": "Requests",
    "domain": "Municipality"
})

num_cols = ['PerfScore','FCP','LCP','SpeedIndex','TBT','CLS','PageWeightBytes','Requests','JSBytes','CO2_SWD_g','CO2_OneByte_g']
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce')

if "GreenHosting" not in df.columns:
    df["GreenHosting"] = "unknown"

avg = {
    'Avg_PerfScore_pct': round(df['PerfScore'].mean(),2),
    'Avg_FCP_ms': round(df['FCP'].mean(),2),
    'Avg_LCP_ms': round(df['LCP'].mean(),2),
    'Avg_SpeedIndex_ms': round(df['SpeedIndex'].mean(),2),
    'Avg_TBT_ms': round(df['TBT'].mean(),2),
    'Avg_CLS': round(df['CLS'].mean(),3),
    'Avg_Requests': round(df['Requests'].mean(),2),
    'Avg_JSBytes': round(df['JSBytes'].mean(),2),
    'Avg_PageWeight_MB': round((df['PageWeightBytes'].mean() / (1024*1024)),3),
    'Avg_CO2_SWD_g': round(df['CO2_SWD_g'].mean(),4),
    'Avg_CO2_OneByte_g': round(df['CO2_OneByte_g'].mean(),4)
}
avg_df = pd.DataFrame(list(avg.items()), columns=['Metric','Value'])
green_df = df['GreenHosting'].value_counts(dropna=False).rename_axis('GreenHosting').reset_index(name='Count')

avg_df.to_csv(out_dir / 'averages.csv', index=False)
green_df.to_csv(out_dir / 'green_hosting_summary.csv', index=False)

xlsx = out_dir / 'audit_results.xlsx'
try:
    import openpyxl
    with pd.ExcelWriter(xlsx, engine='openpyxl') as w:
        df.to_excel(w, sheet_name='Results', index=False)
        avg_df.to_excel(w, sheet_name='Averages', index=False)
        green_df.to_excel(w, sheet_name='GreenHostingSummary', index=False)
except Exception as e:
    print("Excel export skipped:", e)

print('Wrote spreadsheets to', out_dir)