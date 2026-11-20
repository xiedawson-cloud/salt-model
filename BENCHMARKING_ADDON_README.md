# Experimental benchmarking and research presentation add-on

This add-on is designed to be merged into the existing `salt-model` repository.

Contents:
- `research/experimental_benchmark/README.md`: data provenance, access status, compatibility rules.
- `research/experimental_benchmark/inspect_dataset.py`: inspects the source workbook after the user downloads it.
- `research/experimental_benchmark/benchmark_depth.py`: descriptive summary of verified corrosion-depth rows.
- `research/experimental_benchmark/measurement_mapping_template.csv`: metadata capture template.
- `research/experimental_benchmark/reproducibility_manifest.json`: machine-readable provenance/status.
- `research/experimental_benchmark/figures/`: workflow and model-output figures.
- `results/figures/spatial_chromium_heatmap.png`: standalone model visualization.

Important: the public workbook metadata was verified, but its binary data could not be retrieved in this environment. Therefore this add-on does not claim a numerical experimental benchmark or model validation. Download `Molten-Salt-Corrosion-Data.xlsx` from the source repository and follow the README before analysis.
