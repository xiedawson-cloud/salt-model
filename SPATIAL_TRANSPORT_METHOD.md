# Version 0.4: idealized spatial transport extension

## Purpose

Version 0.4 extends the earlier well-mixed compartment model by dividing a circulating salt loop into `N` equal-volume cells. It is a deliberately small, one-dimensional transport prototype intended to test how advection, axial dispersion, localized chromium release, and local tracer transfer can be represented and verified in code.

## Governing equations

For any transported cell inventory or concentration `x_i`, the periodic advection-dispersion operator is

\[
\frac{dx_i}{dt}=a(x_{i-1}-x_i)+d(x_{i+1}-2x_i+x_{i-1}),
\]

where indices wrap around the loop, `a = Q N / V` is the cell-scale advective rate, and `d = D / (\Delta x)^2` is the cell-scale dispersion rate. Here `Q` is volumetric flow rate, `V` is total salt volume, `D` is an effective axial dispersion coefficient, and `\Delta x = L/N` is cell length.

Chromium is released at cell 0 using the same effective Arrhenius/redox scenario law as the lumped model. The source is added to the chromium concentration in that cell, while the alloy inventory decreases by the corresponding released mass. Chromium is transported around the periodic loop but has no additional chemical sink in this version.

For each normalized tracer, local first-order transfer removes `k x_i` from each salt cell and adds the sum of those local rates to a cumulative receiver state. This construction conserves salt-plus-receiver tracer inventory, subject to numerical integration tolerance.

## Illustrative default scenario

- 12 equal-volume cells
- 6 m loop length
- 10 L total salt volume
- 120 L/h circulation rate
- 0.015 m²/h effective axial dispersion coefficient
- Chromium source localized at cell 0
- Initial CsF-like and CsI-like tracer inventory localized in cell 0
- 700 °C and 500 h, retaining the earlier illustrative chemistry parameters

These are analyst-selected placeholders. They are not measured values, a specific reactor geometry, or calibrated transport coefficients.

## Example output

For the default illustrative run, the final mean dissolved chromium concentration is approximately 12.4969 mg/L, with cell values from approximately 12.4959 to 12.4978 mg/L. The final receiver fractions are approximately 0.3935 for the CsF-like tracer and 0.1393 for the CsI-like tracer. The total normalized salt-plus-receiver inventory remains approximately 1.0 for each tracer.

The small final chromium gradient is a consequence of the selected high circulation rate and low source strength in this scenario; it should not be interpreted as evidence that real reactor loops are well mixed.

## Assumptions and limitations

- One-dimensional periodic loop with equal-volume cells.
- Constant flow rate, salt volume, temperature, and dispersion coefficient.
- First-order upwind advection and central-difference axial dispersion.
- No branches, pump transients, geometry-dependent velocity field, buoyancy, turbulence closure, or CFD.
- No spatial temperature or redox variation.
- Chromium source is localized at one cell and has no precipitation, deposition, or chemical reaction sink.
- CsF-like and CsI-like tracers remain bookkeeping tracers; this is not chemical speciation, volatility, or salt/gas partition modelling.
- Parameters remain illustrative and have not been calibrated or independently validated against experiments.

## Verification

The test suite checks that the solver returns the requested time points, tracer salt-plus-receiver totals are conserved, chromium released from the alloy matches chromium accumulated in the salt, zero flow and zero dispersion preserve a localized tracer distribution, and invalid cell counts are rejected. Passing these software tests verifies selected numerical/accounting properties only; it does not validate physical accuracy.

## Run it

```bash
python -m msr_model.spatial --output results/spatial_transport.csv
pytest
```
