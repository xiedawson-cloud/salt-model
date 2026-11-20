import argparse
import pandas as pd
from pathlib import Path

p = argparse.ArgumentParser(description="Summarize verified corrosion-depth measurements.")
p.add_argument("--input", required=True, help="CSV completed from the mapping template")
args = p.parse_args()
df = pd.read_csv(args.input)
required = ["alloy", "maximum_corrosion_depth_um"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise SystemExit(f"Missing required columns: {missing}")
df["maximum_corrosion_depth_um"] = pd.to_numeric(df["maximum_corrosion_depth_um"], errors="coerce")
valid = df.dropna(subset=["alloy", "maximum_corrosion_depth_um"])
if valid.empty:
    raise SystemExit("No verified numeric corrosion-depth rows found.")
summary = valid.groupby("alloy")["maximum_corrosion_depth_um"].agg(
    n="count", mean_um="mean", sd_um="std", min_um="min", max_um="max"
).reset_index()
out = Path(args.input).with_name("corrosion_depth_summary.csv")
summary.to_csv(out, index=False)
print(summary.to_string(index=False))
print(f"\\nWrote {out}")
print("\\nInterpretation: descriptive summary only. Do not compare directly with mg/L chromium outputs.")
