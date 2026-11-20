import numpy as np
import pytest

from msr_model.spatial import simulate_spatial


def test_spatial_model_returns_one_row_per_requested_time_point():
    result = simulate_spatial({"n_cells": 8, "time_points": 21, "duration_h": 10.0})
    assert len(result) == 21
    assert "chromium_cell_00_mg_L" in result
    assert "csf_cell_07_fraction" in result


def test_periodic_transport_conserves_tracer_mass_with_receiver_transfer():
    result = simulate_spatial({"n_cells": 8, "time_points": 31, "duration_h": 50.0})
    assert np.allclose(result["csf_total_fraction"], 1.0, atol=2e-7)
    assert np.allclose(result["csi_total_fraction"], 1.0, atol=2e-7)


def test_chromium_inventory_loss_matches_integrated_chromium_release():
    p = {"n_cells": 8, "time_points": 31, "duration_h": 20.0}
    result = simulate_spatial(p)
    final = result.iloc[-1]
    released_from_alloy = (1.0 - final["alloy_cr_inventory_fraction"]) * 250000.0
    chromium_in_salt = final["chromium_total_mg"]
    assert chromium_in_salt == pytest.approx(released_from_alloy, rel=2e-6, abs=1e-7)


def test_zero_flow_and_zero_dispersion_preserve_localized_tracer_cell():
    result = simulate_spatial({
        "n_cells": 6, "time_points": 11, "duration_h": 10.0,
        "flow_rate_L_h": 0.0, "axial_dispersion_m2_h": 0.0,
        "csf_transfer_rate_h": 0.0, "csi_transfer_rate_h": 0.0,
    })
    assert result["csf_cell_00_fraction"].iloc[-1] == pytest.approx(1.0)
    assert result[[f"csf_cell_{i:02d}_fraction" for i in range(1, 6)]].iloc[-1].sum() == pytest.approx(0.0)


def test_invalid_cell_count_is_rejected():
    with pytest.raises(ValueError):
        simulate_spatial({"n_cells": 2})
