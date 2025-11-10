import os
import csv
import math
import pandas as pd
import matplotlib.pyplot as plt

base_dir = os.path.dirname(__file__)
evidence_dir = os.path.join(base_dir, '..', 'evidence')
results_csv = os.path.join(evidence_dir, 'results.csv')
charts_dir = os.path.join(evidence_dir, 'charts')
os.makedirs(charts_dir, exist_ok=True)

# Load CSV
df = pd.read_csv(results_csv)

# Clean numeric columns (Lighthouse gives ms)
for col in ['PerfScore', 'FCP', 'LCP', 'SpeedIndex', 'PageWeightBytes', 'Requests', 'JSBytes', 'CO2_SWD_g', 'CO2_OneByte_g']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 1. Bar chart: Municipality vs PerfScore
plt.figure(figsize=(10, 6))
sorted_df = df.sort_values('PerfScore', ascending=False)
plt.bar(sorted_df['Municipality'], sorted_df['PerfScore'], color='#4b8bbe')
plt.xticks(rotation=90, fontsize=8)
plt.ylabel('Performance Score (%)')
plt.title('Municipality Performance Scores')
plt.tight_layout()
bar_path = os.path.join(charts_dir, 'performance_scores.png')
plt.savefig(bar_path, dpi=150)
plt.close()

# 2. Averages table (save as CSV and print)
averages = {
    'Avg_FCP_ms': round(df['FCP'].mean(), 2),
    'Avg_LCP_ms': round(df['LCP'].mean(), 2),
    'Avg_SpeedIndex_ms': round(df['SpeedIndex'].mean(), 2),
    'Avg_PerfScore_pct': round(df['PerfScore'].mean(), 2)
}
avg_csv = os.path.join(evidence_dir, 'averages_summary.csv')
with open(avg_csv, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Metric', 'Value'])
    for k, v in averages.items():
        w.writerow([k, v])

# 3. GreenHosting distribution (pie + bar)
green_counts = df['GreenHosting'].value_counts()
# Pie
plt.figure(figsize=(5,5))
plt.pie(green_counts.values, labels=green_counts.index, autopct='%1.1f%%', colors=['#2e7d32','#c62828','#9e9e9e'])
plt.title('Green Hosting Distribution')
pie_path = os.path.join(charts_dir, 'green_hosting_pie.png')
plt.savefig(pie_path, dpi=150)
plt.close()

# Bar
plt.figure(figsize=(6,4))
plt.bar(green_counts.index, green_counts.values, color=['#2e7d32','#c62828','#9e9e9e'])
plt.ylabel('Count')
plt.title('Green Hosting Count')
bar2_path = os.path.join(charts_dir, 'green_hosting_bar.png')
plt.savefig(bar2_path, dpi=150)
plt.close()

# JSBytes vs CO2 (SWD) scatter
plt.figure(figsize=(6,4))
plt.scatter(df['JSBytes'] / 1024.0, df['CO2_SWD_g'], c='#6a4fbf', s=35, alpha=0.85)
plt.xlabel('JS Transfer (KB)')
plt.ylabel('CO2 (SWD grams)')
plt.title('JS Bytes vs CO2 (SWD Model)')
plt.tight_layout()
js_co2_path = os.path.join(charts_dir, 'jsbytes_vs_co2.png')
plt.savefig(js_co2_path, dpi=150)
plt.close()



print('Generated:')
print(f'- {bar_path}')
print(f'- {pie_path}')
print(f'- {bar2_path}')
print(f'- {avg_csv}')
print(f'- {js_co2_path}')