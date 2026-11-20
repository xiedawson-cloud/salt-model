import numpy as np
from msr_model.model import DEFAULTS, simulate
from msr_model.monte_carlo import sample_parameters, evaluate_ensemble


def test_sampling_is_reproducible_and_within_ranges():
    a = sample_parameters(25, seed=7)
    b = sample_parameters(25, seed=7)
    assert a.equals(b)
    assert np.all((a.temperature_C >= 650) & (a.temperature_C <= 750))


def test_analytic_ensemble_matches_ode_for_baseline_parameters():
    p = DEFAULTS.copy()
    one = {
        "temperature_C": p["temperature_C"],
        "cr_flux_ref_mg_m2_h": p["cr_flux_ref_mg_m2_h"],
        "activation_energy_kJ_mol": p["activation_energy_kJ_mol"],
        "redox_index": p["redox_index"],
        "csf_transfer_rate_h": p["csf_transfer_rate_h"],
        "csi_transfer_rate_h": p["csi_transfer_rate_h"],
    }
    from pandas import DataFrame
    mc = evaluate_ensemble(DataFrame([one])).iloc[0]
    ode = simulate(p).iloc[-1]
    assert abs(mc.dissolved_cr_mg_L - ode.dissolved_cr_mg_L) < 1e-6
    assert abs(mc.csf_receiver_fraction - ode.csf_receiver_fraction) < 1e-6
    assert abs(mc.csi_receiver_fraction - ode.csi_receiver_fraction) < 1e-6


def test_tracer_fractions_are_bounded_and_conserved():
    r = evaluate_ensemble(sample_parameters(100, seed=11))
    for salt, receiver in [("csf_salt_fraction", "csf_receiver_fraction"),
                           ("csi_salt_fraction", "csi_receiver_fraction")]:
        assert np.all((r[salt] >= 0) & (r[salt] <= 1))
        assert np.all((r[receiver] >= 0) & (r[receiver] <= 1))
        assert np.allclose(r[salt] + r[receiver], 1.0)
