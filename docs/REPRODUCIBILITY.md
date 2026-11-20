# Reproducibility checklist

- Python 3.10 or newer
- Install dependencies with `pip install -e ".[dev]"`
- Baseline inputs: `data/parameters.json`
- Monte Carlo default seed: `20261119`
- Default ensemble size: 2,000
- Numerical ODE method: SciPy `solve_ivp`, BDF, `rtol=1e-8`, `atol=1e-10`
- Run tests with `pytest`
- Regenerate ensemble files with `python -m msr_model.monte_carlo --n 2000 --seed 20261119 --output-dir results`

The Monte Carlo output files are deterministic for a fixed seed and software environment. They are generated outputs, not experimental observations.
