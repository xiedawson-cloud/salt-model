import numpy as np
import pytest

from msr_model.model import arrhenius_multiplier, simulate


def test_arrhenius_multiplier_is_one_at_reference_temperature():
    assert arrhenius_multiplier(700.0, 700.0, 80.0) == pytest.approx(1.0)


def test_higher_temperature_increases_arrhenius_multiplier():
    low = arrhenius_multiplier(650.0, 700.0, 80.0)
    high = arrhenius_multiplier(750.0, 700.0, 80.0)
    assert high > low


def test_chromium_inventory_does_not_increase():
    result = simulate()
    inventory = result["alloy_cr_inventory_fraction"].to_numpy()
    assert np.all(np.diff(inventory) <= 1e-10)
    assert np.all(inventory >= 0.0)


def test_baseline_outputs_are_finite_and_nonnegative():
    result = simulate()
    final = result.iloc[-1]
    values = final[[
        "dissolved_cr_mg_L",
        "csf_salt_fraction",
        "csf_receiver_fraction",
        "csi_salt_fraction",
        "csi_receiver_fraction",
    ]].to_numpy(dtype=float)
    assert np.all(np.isfinite(values))
    assert np.all(values >= 0.0)
