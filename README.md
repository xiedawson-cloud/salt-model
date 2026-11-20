Experimental data acquisition and benchmarking

Dataset selected

McAlpine, S., & Short, M. P. (2020). *Corrosion of commercial alloys in FLiNaK molten salt containing EuF3 and simulant fission product additives*. Journal of Nuclear Materials. https://doi.org/10.1016/j.jnucmat.2020.151994

Open data repository: https://github.com/shortlab/2020-Molten-Salt-Corrosion-FPs  
Dataset DOI: https://doi.org/10.5281/zenodo.3671744  
Workbook: `Molten-Salt-Corrosion-Data.xlsx` (10.5 KB; repository description says it contains maximum corrosion-depth data).

The public repository README identifies four tested alloys: Hastelloy N, 316L stainless steel, Ni-201, and Incoloy 800H. It also identifies SEM images, EDX line scans, and EMPA data. The workbook is described as containing the maximum corrosion depth values reported in the paper.

Acquisition status

The source and workbook metadata were verified against the public GitHub repository and Zenodo record. The workbook's binary contents could not be downloaded into this execution environment, so **no experimental numeric rows have been transcribed or analyzed here**. Do not represent the current package as containing the raw measurements or a completed numerical benchmark.

Download the workbook from the GitHub repository link above and place it beside this README as:

`Molten-Salt-Corrosion-Data.xlsx`

The Zenodo record provides a versioned archival deposit and DOI.

Compatibility and limits

The workbook reports maximum corrosion depth. The current model predicts dissolved chromium concentration and normalized tracer transport. These are different observables.

A valid quantitative comparison requires a physically justified conversion from depth loss to mass loss and then to chromium release. That conversion needs, at minimum, alloy density, chromium mass fraction, exposed area, test duration, specimen geometry, and the correct test-specific depth definition. Even then, alloy corrosion depth is not necessarily uniform recession and may include selective dealloying.

Therefore:
- Do not directly compare corrosion depth (typically a length) with chromium concentration (mg/L).
- Do not fit the model's chromium surface-flux parameter from corrosion-depth values without the conversion and assumptions above.
- The published experiment can support material/condition-specific corrosion-depth benchmarking once the workbook and matching test metadata are extracted.
- The dataset does not measure the spatial concentration profile around a circulating loop; it cannot validate the model's predicted 12-cell gradients.

Reproducible workflow

1. Download the workbook and place it in this directory.
2. Run `python inspect_dataset.py` to list workbook sheets and export each sheet to CSV.
3. Review the paper and source images to map each row to alloy, salt composition, temperature, exposure duration, and replicate.
4. Fill `measurement_mapping_template.csv` with verified metadata. Leave unknown fields blank.
5. Run `python benchmark_depth.py --input <verified_csv>` only after the mapping has been reviewed.

The benchmark script reports descriptive summaries and does not claim model validation unless a compatible model observable and unit conversion are supplied.
