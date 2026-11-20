"""Monte Carlo scenario analysis for the reduced-order MSR model.

The ranges below are exploratory scenario ranges, not fitted distributions,
measured parameter uncertainties, or probability statements about a reactor.
The constant-parameter ODEs have closed-form solutions; this module evaluates
those exact solutions efficiently for many independent parameter draws.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from .model import DEFAULTS, arrhenius_multiplier

# Explicitly illustrative ranges chosen to explore model behavior.
# Uniform distributions are design choices for scenario sampling, not evidence
# that the parameters are physically uniformly distributed.
SCENARIO_RANGES = {
    "temperature_C": (650.0, 750.0),
    "cr_flux_ref_mg_m2_h": (0.5, 1.5),
    "activation_energy_kJ_mol": (60.0, 100.0),
    "redox_index": (-0.5, 0.5),
    "csf_transfer_rate_h": (0.0005, 0.0015),
    "csi_transfer_rate_h": (0.00015, 0.00045),
}


def sample_parameters(n: int = 2000, seed: int = 20261119) -> pd.DataFrame:
    """Draw independent uniform scenarios over SCENARIO_RANGES."""
    if n < 1:
        raise ValueError("n must be at least 1")
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        key: rng.uniform(low, high, n)
        for key, (low, high) in SCENARIO_RANGES.items()
    })


def evaluate_ensemble(samples: pd.DataFrame, base: dict | None = None) -> pd.DataFrame:
    """Evaluate final-time model outputs using exact constant-input solutions."""
    p = DEFAULTS.copy()
    if base:
        p.update(base)
    s = samples.copy()
    temp_factor = np.exp(
        -s["activation_energy_kJ_mol"].to_numpy() * 1000.0 / 8.314462618
        * (1.0 / (s["temperature_C"].to_numpy() + 273.15)
           - 1.0 / (p["reference_temperature_C"] + 273.15))
    )
    redox_factor = np.exp(p["redox_sensitivity"] * s["redox_index"].to_numpy())
    flux = s["cr_flux_ref_mg_m2_h"].to_numpy() * temp_factor * redox_factor
    rate = flux * p["alloy_wetted_area_m2"] / p["alloy_initial_cr_inventory_mg"]
    t = p["duration_h"]
    alloy_fraction = np.exp(-rate * t)
    s["chromium_inventory_loss_percent"] = 100.0 * (1.0 - alloy_fraction)
    s["dissolved_cr_mg_L"] = (
        p["alloy_initial_cr_inventory_mg"] * (1.0 - alloy_fraction)
        / p["salt_volume_L"]
    )
    s["csf_receiver_fraction"] = 1.0 - np.exp(-s["csf_transfer_rate_h"] * t)
    s["csf_salt_fraction"] = 1.0 - s["csf_receiver_fraction"]
    s["csi_receiver_fraction"] = 1.0 - np.exp(-s["csi_transfer_rate_h"] * t)
    s["csi_salt_fraction"] = 1.0 - s["csi_receiver_fraction"]
    return s


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    """Return median and 5th/95th scenario percentiles for output columns."""
    outputs = [
        "chromium_inventory_loss_percent", "dissolved_cr_mg_L",
        "csf_receiver_fraction", "csi_receiver_fraction"
    ]
    return results[outputs].quantile([0.05, 0.50, 0.95]).rename(
        index={0.05: "5th_percentile", 0.50: "median", 0.95: "95th_percentile"}
    )


def rank_associations(results: pd.DataFrame) -> pd.DataFrame:
    """Spearman rank associations; descriptive, not causal or inferential."""
    inputs = list(SCENARIO_RANGES)
    outputs = ["chromium_inventory_loss_percent", "dissolved_cr_mg_L",
               "csf_receiver_fraction", "csi_receiver_fraction"]
    rows = []
    for output in outputs:
        for parameter in inputs:
            rho, _ = spearmanr(results[parameter], results[output])
            rows.append({"output": output, "parameter": parameter,
                         "spearman_rho": float(rho)})
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Monte Carlo scenario analysis")
    parser.add_argument("--n", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261119)
    parser.add_argument("--output-dir", default="results")
    args = parser.parse_args()
    out = Path(args.output_dir)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    samples = sample_parameters(args.n, args.seed)
    results = evaluate_ensemble(samples)
    samples.to_csv(out / "monte_carlo_inputs.csv", index=False)
    results.to_csv(out / "monte_carlo_outputs.csv", index=False)
    summarize(results).to_csv(out / "monte_carlo_summary.csv")
    rank_associations(results).to_csv(out / "rank_associations.csv", index=False)
    print("Scenario ensemble summary (not confidence intervals):")
    print(summarize(results).to_string())
    print(f"\nSaved {len(results)} scenarios to {out.resolve()}")

if __name__ == "__main__":
    main()
