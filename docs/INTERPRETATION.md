# Initial Monte Carlo scenario results

A deterministic ensemble of 2,000 cases was generated with random seed `20261119`. Six model inputs were sampled independently from the illustrative uniform ranges documented in `docs/UNCERTAINTY_METHOD.md`. Baseline duration remained 500 h; the other non-sampled system settings remained at their baseline values.

| Output | 5th scenario percentile | Median | 95th scenario percentile |
|---|---:|---:|---:|
| Chromium inventory loss (%) | 0.01948 | 0.04748 | 0.10592 |
| Dissolved chromium (mg/L) | 4.8689 | 11.8702 | 26.4804 |
| CsF-like receiver fraction | 0.24080 | 0.39241 | 0.51603 |
| CsI-like receiver fraction | 0.07974 | 0.14043 | 0.19583 |

These are **scenario percentiles**, not confidence intervals, prediction intervals, or probabilities for an operating reactor. They depend directly on analyst-selected parameter bounds, independent sampling, and the simplified model equations. The results are useful for checking how the model behaves under the stated assumptions; they are not experimental evidence.

The median dissolved chromium result is close to the separate baseline illustrative case (about 12.50 mg/L), but the ensemble median differs because inputs vary across the chosen ranges.
