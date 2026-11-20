"""Idealized 1-D loop transport extension for the molten-salt study.

This module represents a circulating salt loop as equal-volume cells with
periodic boundaries. Advection is first-order upwind, axial dispersion is a
central-difference term, chromium is released at cell 0, and the two tracer
inventories transfer locally to a cumulative receiving compartment.

All transport inputs are illustrative scenario parameters, not measured
reactor conditions. This is not CFD or a validated reactor-flow model.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

from .model import DEFAULTS, arrhenius_multiplier

SPATIAL_DEFAULTS = {
    **DEFAULTS,
    "n_cells": 12,
    "loop_length_m": 6.0,
    "flow_rate_L_h": 120.0,
    "axial_dispersion_m2_h": 0.015,
    "initial_tracer_cell": 0,
}


def _transport_derivative(values: np.ndarray, adv_rate: float, disp_rate: float) -> np.ndarray:
    """Conservative periodic advection-dispersion derivative for equal cells."""
    upstream = np.roll(values, 1)
    downstream = np.roll(values, -1)
    return adv_rate * (upstream - values) + disp_rate * (downstream - 2.0 * values + upstream)


def simulate_spatial(params: dict | None = None) -> pd.DataFrame:
    """Run the illustrative 1-D circulating-loop model.

    Chromium concentration is reported in mg/L per cell. Tracer inventories
    are normalized totals distributed among cells; transfer to the receiver
    is accumulated so salt + receiver inventory remains conserved.
    """
    p = SPATIAL_DEFAULTS.copy()
    if params:
        p.update(params)

    n = int(p["n_cells"])
    if n < 3:
        raise ValueError("n_cells must be at least 3 for the periodic stencil.")
    if p["duration_h"] <= 0 or int(p["time_points"]) < 2:
        raise ValueError("duration_h must be positive and time_points >= 2.")
    if p["salt_volume_L"] <= 0 or p["loop_length_m"] <= 0:
        raise ValueError("Salt volume and loop length must be positive.")
    if p["flow_rate_L_h"] < 0 or p["axial_dispersion_m2_h"] < 0:
        raise ValueError("Flow rate and axial dispersion cannot be negative.")
    if p["alloy_initial_cr_inventory_mg"] <= 0 or p["cr_flux_ref_mg_m2_h"] < 0:
        raise ValueError("Initial chromium inventory must be positive and flux nonnegative.")
    initial_cell = int(p["initial_tracer_cell"])
    if not 0 <= initial_cell < n:
        raise ValueError("initial_tracer_cell must identify an existing cell.")

    dx = p["loop_length_m"] / n
    # u/dx = (Q/V)*N for a constant-area loop.
    adv_rate = (p["flow_rate_L_h"] / p["salt_volume_L"]) * n
    disp_rate = p["axial_dispersion_m2_h"] / (dx * dx)
    cell_volume_L = p["salt_volume_L"] / n
    temp_factor = arrhenius_multiplier(
        p["temperature_C"], p["reference_temperature_C"],
        p["activation_energy_kJ_mol"]
    )
    redox_factor = np.exp(p["redox_sensitivity"] * p["redox_index"])
    release_rate_at_full_inventory = (
        p["cr_flux_ref_mg_m2_h"] * temp_factor * redox_factor
        * p["alloy_wetted_area_m2"]
    )

    # State: alloy fraction; N chromium concentrations; N CsF masses;
    # CsF receiver; N CsI masses; CsI receiver.
    y0 = np.zeros(1 + 3 * n + 2, dtype=float)
    y0[0] = 1.0
    csf_start = 1 + n
    csi_start = csf_start + n + 1
    y0[csf_start + initial_cell] = p["initial_csf_inventory"]
    y0[csi_start + initial_cell] = p["initial_csi_inventory"]

    def rhs(_time: float, y: np.ndarray) -> np.ndarray:
        alloy_fraction = max(y[0], 0.0)
        cr = y[1:1 + n]
        csf = y[csf_start:csf_start + n]
        csf_receiver_index = csf_start + n
        csi = y[csi_start:csi_start + n]
        csi_receiver_index = csi_start + n

        release_mg_h = release_rate_at_full_inventory * alloy_fraction
        d_alloy = -release_mg_h / p["alloy_initial_cr_inventory_mg"]
        d_cr = _transport_derivative(cr, adv_rate, disp_rate)
        d_cr[0] += release_mg_h / cell_volume_L

        d_csf = _transport_derivative(csf, adv_rate, disp_rate)
        d_csi = _transport_derivative(csi, adv_rate, disp_rate)
        csf_transfer = p["csf_transfer_rate_h"] * csf
        csi_transfer = p["csi_transfer_rate_h"] * csi
        d_csf -= csf_transfer
        d_csi -= csi_transfer

        dy = np.zeros_like(y)
        dy[0] = d_alloy
        dy[1:1 + n] = d_cr
        dy[csf_start:csf_start + n] = d_csf
        dy[csf_receiver_index] = float(np.sum(csf_transfer))
        dy[csi_start:csi_start + n] = d_csi
        dy[csi_receiver_index] = float(np.sum(csi_transfer))
        return dy

    times = np.linspace(0.0, p["duration_h"], int(p["time_points"]))
    solution = solve_ivp(
        rhs, (0.0, p["duration_h"]), y0, t_eval=times,
        method="BDF", rtol=1e-8, atol=1e-10
    )
    if not solution.success:
        raise RuntimeError(solution.message)

    data: dict[str, np.ndarray] = {"time_h": solution.t}
    cr = solution.y[1:1 + n, :].T
    csf = solution.y[csf_start:csf_start + n, :].T
    csf_receiver = solution.y[csf_start + n, :]
    csi = solution.y[csi_start:csi_start + n, :].T
    csi_receiver = solution.y[csi_start + n, :]
    data["alloy_cr_inventory_fraction"] = solution.y[0]
    data["chromium_total_mg"] = cr.sum(axis=1) * cell_volume_L
    data["chromium_mean_mg_L"] = cr.mean(axis=1)
    data["chromium_max_mg_L"] = cr.max(axis=1)
    data["chromium_min_mg_L"] = cr.min(axis=1)
    data["csf_salt_total_fraction"] = csf.sum(axis=1)
    data["csf_receiver_fraction"] = csf_receiver
    data["csf_total_fraction"] = data["csf_salt_total_fraction"] + csf_receiver
    data["csi_salt_total_fraction"] = csi.sum(axis=1)
    data["csi_receiver_fraction"] = csi_receiver
    data["csi_total_fraction"] = data["csi_salt_total_fraction"] + csi_receiver
    for cell in range(n):
        data[f"chromium_cell_{cell:02d}_mg_L"] = cr[:, cell]
        data[f"csf_cell_{cell:02d}_fraction"] = csf[:, cell]
        data[f"csi_cell_{cell:02d}_fraction"] = csi[:, cell]
    return pd.DataFrame(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the illustrative 1-D molten-salt loop transport model.")
    parser.add_argument("--output", default="results/spatial_transport.csv")
    parser.add_argument("--cells", type=int, default=SPATIAL_DEFAULTS["n_cells"])
    args = parser.parse_args()
    result = simulate_spatial({"n_cells": args.cells})
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    print(result.iloc[-1][[
        "chromium_mean_mg_L", "chromium_max_mg_L", "chromium_min_mg_L",
        "csf_receiver_fraction", "csi_receiver_fraction",
    ]].to_string())


if __name__ == "__main__":
    main()
