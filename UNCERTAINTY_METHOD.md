# Monte Carlo scenario analysis

## Purpose

The ensemble explores how outputs of the current reduced-order model change when selected inputs vary over stated ranges. It is a sensitivity/scenario exercise, not a statistical characterization of real reactor uncertainty.

## Sampled inputs

| Input | Lower | Upper | Sampling |
|---|---:|---:|---|
| Temperature (°C) | 650 | 750 | Independent uniform |
| Reference Cr flux (mg m⁻² h⁻¹) | 0.5 | 1.5 | Independent uniform |
| Effective activation energy (kJ mol⁻¹) | 60 | 100 | Independent uniform |
| Dimensionless redox scenario index | -0.5 | 0.5 | Independent uniform |
| CsF-like transfer rate (h⁻¹) | 0.0005 | 0.0015 | Independent uniform |
| CsI-like transfer rate (h⁻¹) | 0.00015 | 0.00045 | Independent uniform |

These bounds are analyst-selected illustrative ranges. They are not inferred from a dataset, and independent sampling ignores possible parameter correlations.

## Outputs

- Chromium inventory loss (%),
- Dissolved chromium concentration (mg/L),
- CsF-like receiver fraction,
- CsI-like receiver fraction.

The code reports the 5th, 50th, and 95th percentiles of the sampled ensemble. These should be called **scenario percentiles**, not confidence intervals.

## Mathematical implementation

For constant inputs, the corrosion state obeys `df/dt = -lambda*f`, with `lambda = J_ref * Arrhenius * exp(alpha*xi) * A / M0`. Thus `f(t) = exp(-lambda*t)` and dissolved chromium is `M0*(1-f)/V`.

For each tracer, `dN_salt/dt = -k*N_salt` and `dN_receiver/dt = k*N_salt`, giving `N_receiver(t) = N0*(1-exp(-k*t))` and `N_salt(t)=N0*exp(-k*t)`. The ensemble uses these exact solutions to evaluate many scenarios efficiently. A unit test compares the baseline analytic outputs with the SciPy ODE solution.

## Interpretation limits

The analysis does not establish probabilities for actual reactor outcomes. It only shows the consequences of the selected ranges under the current model structure. A future evidence-based uncertainty study should derive parameter distributions and correlations from matched experimental data and measurement uncertainties.
