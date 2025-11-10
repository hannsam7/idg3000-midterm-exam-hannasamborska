import os, shutil, pandas as pd

base_dir = os.path.dirname(__file__)
evidence_dir = os.path.join(base_dir, '..', 'evidence')
results = os.path.join(evidence_dir, 'results.csv')
out_dir = os.path.join(evidence_dir, 'spreadsheets')
os.makedirs(out_dir, exist_ok=True)

# Copy raw CSV
shutil.copyfile(results, os.path.join(out_dir, 'results.csv'))

df = pd.read_csv(results)
num_cols = ['PerfScore','FCP','LCP','SpeedIndex','TBT','CLS','PageWeightBytes','Requests','JSBytes','CO2_SWD_g','CO2_OneByte_g']
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce')

avg = {
    'Avg_PerfScore_pct': round(df['PerfScore'].mean(),2),
    'Avg_FCP_ms': round(df['FCP'].mean(),2),
    'Avg_LCP_ms': round(df['LCP'].mean(),2),
    'Avg_SpeedIndex_ms': round(df['SpeedIndex'].mean(),2),
    'Avg_TBT_ms': round(df['TBT'].mean(),2) if 'TBT' in df else None,
    'Avg_CLS': round(df['CLS'].mean(),3) if 'CLS' in df else None,
    'Avg_Requests': round(df['Requests'].mean(),2),
    'Avg_JSBytes': round(df['JSBytes'].mean(),2) if 'JSBytes' in df else None,
    'Avg_PageWeight_MB': round((df['PageWeightBytes'].mean() / (1024*1024)),3),
    'Avg_CO2_SWD_g': round(df['CO2_SWD_g'].mean(),4),
    'Avg_CO2_OneByte_g': round(df['CO2_OneByte_g'].mean(),4)
}
avg_df = pd.DataFrame(list(avg.items()), columns=['Metric','Value'])
green_df = df['GreenHosting'].value_counts(dropna=False).rename_axis('GreenHosting').reset_index(name='Count')

avg_df.to_csv(os.path.join(out_dir,'averages.csv'), index=False)
green_df.to_csv(os.path.join(out_dir,'green_hosting_summary.csv'), index=False)

xlsx = os.path.join(out_dir,'audit_results.xlsx')
with pd.ExcelWriter(xlsx, engine='openpyxl') as w:
    df.to_excel(w, sheet_name='Results', index=False)
    avg_df.to_excel(w, sheet_name='Averages', index=False)
    green_df.to_excel(w, sheet_name='GreenHostingSummary', index=False)

print('Wrote spreadsheets to', out_dir)