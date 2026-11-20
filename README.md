# Molten-salt reactor corrosion and transport model

This project is a small computational study of two topics in molten-salt reactor research: chromium release from an alloy into molten salt, and the movement of two simplified fission-product tracers between model compartments.

The project combines a Python model, a set of exploratory parameter runs, and a conceptual Blender model. It is meant to show how a reduced-order model can be built, tested, and explored. It is not a prediction of how a real reactor will operate.

## What is in the repository

- `src/msr_model/` contains the Python equations and simulation code, including the original lumped model and the Version 0.4 spatial transport extension.
- `data/parameters.json` contains the baseline settings.
- `tests/` contains checks for the main model behavior.
- `results/` contains the baseline output, Monte Carlo data, spatial transport output, summaries, and figures.
- `blender/` contains the script used to build and animate the conceptual reactor.
- `images/reactor_model.png` shows the Blender model.
- `paper/` contains the research paper.
- `docs/` has notes about uncertainty, assumptions, and running the project.

## Running the Python model

You will need Python 3.10 or newer.

On macOS or Linux, open Terminal in this folder and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run the baseline case:

```bash
python -m msr_model.model --params data/parameters.json --output results/baseline_illustrative.csv
```

Run the Version 0.4 spatial transport extension (12-cell illustrative loop):

```bash
python -m msr_model.spatial --output results/spatial_transport.csv
```

Run the 2,000-case scenario analysis:

```bash
python -m msr_model.monte_carlo --n 2000 --seed 20261119 --output-dir results
```

Rebuild the figures:

```bash
python -m msr_model.plot_results
```

Run the tests:

```bash
pytest
```

## What the model does

The chromium part uses an effective surface-release rate. Temperature changes the rate through an Arrhenius multiplier, and a dimensionless redox index changes it through a simple scenario factor. The model tracks the remaining chromium inventory in the alloy and the amount released into the salt.

The two tracer examples in the original lumped model use first-order transfer between a salt compartment and a receiving compartment. Version 0.4 adds an idealized one-dimensional periodic loop divided into equal-volume cells, with advection, axial dispersion, chromium release localized at one cell, and local first-order tracer transfer to cumulative receiver states. See `docs/SPATIAL_TRANSPORT_METHOD.md` for equations, assumptions, and limitations.

The baseline case uses 700 °C and 500 hours. With the current illustrative settings, it gives about 0.050% chromium inventory loss and about 12.50 mg/L dissolved chromium at the end of the run.

## What the model does not do

The parameter values are illustrative placeholders, not values fitted to a specific experiment. The redox index is not a measured electrochemical potential. The CsF-like and CsI-like tracers are simplified bookkeeping examples, not full chemical-speciation models.

The spatial extension is not computational fluid dynamics (CFD): it uses a prescribed constant circulation rate and a simple one-dimensional advection-dispersion equation. The code does not model fission generation, isotope decay, neutron transport, criticality, detailed electrochemistry, geometry-resolved fluid dynamics, spatial temperature or redox gradients, stress, cracking, or reactor safety. The Blender model is a visual explanation of the system and does not calculate real fluid flow.

The tests check whether the code follows selected mathematical properties. Passing them does not mean the model has been validated against experimental reactor data.

## Reproducing the scenario analysis

The Monte Carlo script samples six inputs independently from the ranges listed in `docs/UNCERTAINTY_METHOD.md`. These ranges were selected to explore how the equations behave. They are not measured probability distributions.

The 5th, 50th, and 95th percentiles in the results are percentiles of these selected scenarios. They are not confidence intervals or probabilities about a real reactor. The Spearman values describe associations within this particular set of sampled ranges; they do not show cause and effect.

## Citation

The `CITATION.cff` file contains the project citation information. See `paper/research_paper.docx` for the written study.

## License

This project is shared under the MIT License. See `LICENSE`.
