"""Reduced-order molten-salt reactor model.

State vector:
  0: alloy chromium inventory remaining (fraction of initial modeled inventory)
  1: dissolved chromium in salt (mg/L)
  2: CsF-like inventory in salt (arbitrary normalized molar inventory)
  3: CsF-like inventory in receiving compartment
  4: CsI-like inventory in salt
  5: CsI-like inventory in receiving compartment

The corrosion law is a lumped, empirical surface-flux model. Fission-product
transfer is first-order compartment exchange. All default kinetic parameters
are illustrative and must be calibrated before quantitative use.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

R_GAS = 8.314462618  # J mol-1 K-1

DEFAULTS = {
    "temperature_C": 700.0,
    "duration_h": 500.0,
    "time_points": 501,
    "salt_volume_L": 10.0,
    "alloy_wetted_area_m2": 0.25,
    "alloy_initial_cr_inventory_mg": 250000.0,
    "cr_flux_ref_mg_m2_h": 1.0,
    "activation_energy_kJ_mol": 80.0,
    "reference_temperature_C": 700.0,
    "redox_index": 0.0,
    "redox_sensitivity": 1.0,
    "csf_transfer_rate_h": 0.001,
    "csi_transfer_rate_h": 0.0003,
    "initial_csf_inventory": 1.0,
    "initial_csi_inventory": 1.0
}

def arrhenius_multiplier(temp_C: float, ref_C: float, ea_kJ_mol: float) -> float:
    """Arrhenius temperature multiplier normalized to 1 at ref_C."""
    t = temp_C + 273.15
    tr = ref_C + 273.15
    if t <= 0 or tr <= 0:
        raise ValueError("Temperature must be above absolute zero.")
    ea = ea_kJ_mol * 1000.0
    return float(np.exp(-ea / R_GAS * (1.0/t - 1.0/tr)))

def rhs(_t: float, y: np.ndarray, p: dict) -> list[float]:
    alloy_frac, cr_mg_L, csf_salt, csf_recv, csi_salt, csi_recv = y
    # This redox_index is a dimensionless scenario control, NOT volts or a
    # measured electrochemical potential. A calibrated electrochemical model
    # would need species activities, equilibrium potentials and sensor data.
    redox_factor = np.exp(p["redox_sensitivity"] * p["redox_index"])
    temp_factor = arrhenius_multiplier(
        p["temperature_C"], p["reference_temperature_C"],
        p["activation_energy_kJ_mol"]
    )
    cr_flux = p["cr_flux_ref_mg_m2_h"] * temp_factor * redox_factor
    cr_release_mg_h = cr_flux * p["alloy_wetted_area_m2"] * max(alloy_frac, 0.0)
    d_alloy = -cr_release_mg_h / p["alloy_initial_cr_inventory_mg"]
    d_cr_salt = cr_release_mg_h / p["salt_volume_L"]

    # Lumped first-order transfer. Transfer is conservative between the two
    # modeled compartments; it is not a detailed thermodynamic speciation law.
    csf_rate = p["csf_transfer_rate_h"] * max(csf_salt, 0.0)
    csi_rate = p["csi_transfer_rate_h"] * max(csi_salt, 0.0)
    return [
        d_alloy, d_cr_salt,
        -csf_rate, csf_rate,
        -csi_rate, csi_rate
    ]

def simulate(params: dict | None = None) -> pd.DataFrame:
    p = DEFAULTS.copy()
    if params:
        p.update(params)
    if p["duration_h"] <= 0 or p["time_points"] < 2:
        raise ValueError("duration_h must be positive and time_points >= 2.")
    if p["salt_volume_L"] <= 0 or p["alloy_initial_cr_inventory_mg"] <= 0:
        raise ValueError("Salt volume and initial chromium inventory must be positive.")
    if p["cr_flux_ref_mg_m2_h"] < 0:
        raise ValueError("Reference chromium flux cannot be negative.")
    y0 = [
        1.0, 0.0,
        p["initial_csf_inventory"], 0.0,
        p["initial_csi_inventory"], 0.0
    ]
    times = np.linspace(0, p["duration_h"], int(p["time_points"]))
    sol = solve_ivp(
        lambda t, y: rhs(t, y, p),
        (0.0, p["duration_h"]), y0, t_eval=times,
        method="BDF", rtol=1e-8, atol=1e-10
    )
    if not sol.success:
        raise RuntimeError(sol.message)
    out = pd.DataFrame({
        "time_h": sol.t,
        "alloy_cr_inventory_fraction": sol.y[0],
        "dissolved_cr_mg_L": sol.y[1],
        "csf_salt_fraction": sol.y[2],
        "csf_receiver_fraction": sol.y[3],
        "csi_salt_fraction": sol.y[4],
        "csi_receiver_fraction": sol.y[5]
    })
    out["chromium_inventory_loss_percent"] = 100.0 * (1.0 - out["alloy_cr_inventory_fraction"])
    return out

def load_params(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())

def main():
    parser = argparse.ArgumentParser(description="Run a reduced-order molten-salt reactor case.")
    parser.add_argument("--params", default="data/parameters.json")
    parser.add_argument("--output", default="results/baseline.csv")
    args = parser.parse_args()
    p = load_params(args.params) if Path(args.params).exists() else DEFAULTS
    result = simulate(p)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(result.tail(1).to_string(index=False))

if __name__ == "__main__":
    main()
