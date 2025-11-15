import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

repo = Path(__file__).resolve().parents[2]  
evidence = repo / "evidence"
charts_dir = evidence / "charts"
charts_dir.mkdir(parents=True, exist_ok=True)

csv_path = evidence / "summary.csv"
df = pd.read_csv(csv_path)

# Coerce numeric columns
num_cols = ["performanceScore","transferBytes","requests","jsBytes",
            "co2_onebyte_grams","co2_swd_grams","fcp_ms","lcp_ms",
            "speed_index_ms","tbt_ms","cls"]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Short domain label
df["label"] = df.get("domain", df.get("url", "")).astype(str).str.replace(r"^https?://", "", regex=True)

sns.set_theme(style="whitegrid")

# 1) Top 15 by transfer size
if "transferBytes" in df.columns:
    top = df.sort_values("transferBytes", ascending=False).head(15)
    plt.figure(figsize=(12,7))
    sns.barplot(data=top, x="transferBytes", y="label", palette="viridis")
    plt.xlabel("Transfer size (bytes)"); plt.ylabel("")
    plt.title("Top 15 pages by transfer size")
    plt.tight_layout()
    plt.savefig(charts_dir / "top15_transfer_bytes.png", dpi=200)
    plt.close()

# 2) Performance vs Transfer size
if "performanceScore" in df.columns and "transferBytes" in df.columns:
    plt.figure(figsize=(10,7))
    sns.scatterplot(data=df, x="transferBytes", y="performanceScore",
                    size="jsBytes" if "jsBytes" in df.columns else None,
                    hue="co2_swd_grams" if "co2_swd_grams" in df.columns else None,
                    palette="mako", sizes=(20,200), alpha=0.8)
    plt.xlabel("Transfer size (bytes)")
    plt.ylabel("Performance score (0–100)")
    plt.title("Performance vs Transfer size")
    plt.tight_layout()
    plt.savefig(charts_dir / "perf_vs_transfer.png", dpi=200)
    plt.close()

# 3) CO2 model comparison
if "co2_onebyte_grams" in df.columns and "co2_swd_grams" in df.columns:
    plt.figure(figsize=(10,7))
    sns.scatterplot(data=df, x="co2_onebyte_grams", y="co2_swd_grams")
    plt.xlabel("CO₂ (grams) – OneByte model")
    plt.ylabel("CO₂ (grams) – SWD model")
    plt.title("CO₂ estimates comparison")
    plt.tight_layout()
    plt.savefig(charts_dir / "co2_models_comparison.png", dpi=200)
    plt.close()

# 4) JS bytes share vs total bytes
if "jsBytes" in df.columns and "transferBytes" in df.columns:
    share = df[df["transferBytes"] > 0].copy()
    share["js_share_pct"] = (share["jsBytes"].fillna(0) / share["transferBytes"]) * 100
    plt.figure(figsize=(12,7))
    sns.barplot(data=share.sort_values("js_share_pct", ascending=False).head(15),
                x="js_share_pct", y="label", palette="rocket")
    plt.xlabel("JS share of transfer (%)"); plt.ylabel("")
    plt.title("Top 15 pages by JS share (%)")
    plt.tight_layout()
    plt.savefig(charts_dir / "top15_js_share.png", dpi=200)
    plt.close()

print(f"Charts written to: {charts_dir}")