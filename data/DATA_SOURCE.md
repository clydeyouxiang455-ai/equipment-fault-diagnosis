# Data source and provenance

## Authoritative source

- Dataset: AI4I 2020 Predictive Maintenance Dataset
- Publisher: UCI Machine Learning Repository
- Landing page: https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset
- Official CSV endpoint: https://archive.ics.uci.edu/ml/machine-learning-databases/00601/ai4i2020.csv
- DOI: https://doi.org/10.24432/C5HS5C
- License: CC BY 4.0
- Retrieved: 2026-10-09

The raw CSV is intentionally Git-ignored. It is obtained only through `data_loader.download_data()` and remains unmodified under `data/raw/`. The downloader validates the expected row count, schema, binary label fields, and (by default) the recorded SHA-256 checksum before analysis.

## Reproducibility receipt

The CSV used to generate the committed reports contained 10,000 rows and 14 columns. Its SHA-256 checksum was:

`dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e`

## Documentation discrepancy

The UCI narrative describes some individual failure-mode frequencies that do not match the current official CSV's observed sums. This repository therefore computes and reports all counts directly from the downloaded CSV rather than copying narrative counts:

- UCI narrative: TWF=51 and RNF=5; current official CSV: TWF=46 and RNF=19.
- UCI narrative and CSV agree for HDF=115, PWF=95 and OSF=98.
- 18 of the 19 RNF flags occur where `Machine failure=0`; 9 target-positive records carry no indicator flag.
- UCI narrative describes Type shares as L/M/H = 50%/30%/20%; the official CSV contains L=6,000, M=2,997 and H=1,003. `Type` is treated only as a dataset category, not as a real production-mix or quality claim.

This is a source-documentation/data-integrity discrepancy, not an inferred equipment finding. RNF is shown in the data-quality output but excluded from FMEA prioritization.

## Scope

UCI describes the data as synthetic and designed to reflect industrial predictive-maintenance data, and categorizes it as multivariate/time-series. The CSV has no explicit timestamp; its `UDI` header is treated as an identifier rather than a verified deployment-time field (the UCI variable table calls this `UID`). UCI reports six primary input features; the CSV has 14 columns: two identifiers, six primary inputs, and six target/label fields. It is not semiconductor-fabrication, ATE, handler, wafer-sort, or field-equipment data. The project makes no such claim.
