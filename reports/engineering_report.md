# Engineering Report: Equipment Fault Diagnosis & Reliability Analysis

## 1. Executive Summary

This reproducible engineering analysis uses the UCI AI4I 2020 synthetic predictive-maintenance dataset. It profiles observed failure patterns, runs leakage-aware statistical diagnostics, and turns results into verification-oriented RCA/FMEA prompts. It does not represent semiconductor tools or prove physical root causes.

## 2. Engineering Problem Statement

The task is to prioritize observable operating conditions for investigation when machine-failure labels are rare. The goal is engineering hypothesis generation and verification planning, not a production decision system.

## 3. Dataset and Limitations

The source contains synthetic observations, no explicit timestamps, downtime records, maintenance histories, or wafer/process measurements. UCI classifies it as time-series, but UDI is an identifier rather than a verified operational timestamp; this project does not create chronological controls or claim temporal deployment performance. Random train/test performance cannot establish future or real-equipment performance. Failure-indicator flags may overlap and are excluded from predictors to prevent leakage.

## 4. Data Quality Assessment

| column | dtype | missing_values | unique_values |
| --- | --- | --- | --- |
| UDI | int64 | 0 | 10000 |
| Product ID | str | 0 | 10000 |
| Type | str | 0 | 3 |
| Air temperature [K] | float64 | 0 | 93 |
| Process temperature [K] | float64 | 0 | 82 |
| Rotational speed [rpm] | int64 | 0 | 941 |
| Torque [Nm] | float64 | 0 | 577 |
| Tool wear [min] | int64 | 0 | 246 |
| Machine failure | int64 | 0 | 2 |
| TWF | int64 | 0 | 2 |
| HDF | int64 | 0 | 2 |
| PWF | int64 | 0 | 2 |

Range-check exceptions: 0. Duplicate rows: 0.

## 5. Exploratory Data Analysis

| records | machine_failure_records | observed_per_record_failure_proportion | ci95_low | ci95_high |
| --- | --- | --- | --- | --- |
| 10000 | 339 | 0.0339 | 0.0305 | 0.0376 |

Figures: `reports/figures/operating_conditions.png` and `reports/figures/failure_modes_and_correlations.png`.

Condition-band failure rates are saved in `data/processed/failure_rates_by_parameter_bands.csv`. Failure-category condition means are saved in `data/processed/failure_category_conditions.csv`; category flags may overlap.

## 6. Failure Pattern Investigation

| failure_indicator | flagged_records | flag_rate | cooccurring_machine_failures | indicator_without_machine_failure | target_alignment_rate | records_with_multiple_mode_flags |
| --- | --- | --- | --- | --- | --- | --- |
| HDF | 115 | 0.0115 | 115 | 0 | 1.0000 | 24 |
| OSF | 98 | 0.0098 | 98 | 0 | 1.0000 | 24 |
| PWF | 95 | 0.0095 | 95 | 0 | 1.0000 | 24 |
| TWF | 46 | 0.0046 | 46 | 0 | 1.0000 | 24 |
| RNF | 19 | 0.0019 | 1 | 18 | 0.0526 | 24 |

Failure-indicator flags are not mutually exclusive: 24 records carry more than one indicator. Importantly, the current official CSV has a documented integrity discrepancy: RNF flags do not reliably co-occur with the machine-failure target, and 9 target-positive records have no indicator. The mode table exposes this explicitly; RNF is excluded from FMEA prioritization.

## 7. Statistical Diagnostics

Welch group comparisons below quantify differences between failure and non-failure observations. Effect size is sample-size-weighted pooled Cohen's d; p-values are descriptive statistics rather than causal evidence. `p_value_bh` applies Benjamini-Hochberg adjustment across these exploratory comparisons.

| feature | failed_mean | nonfailed_mean | cohens_d | welch_t | p_value | p_value_bh |
| --- | --- | --- | --- | --- | --- | --- |
| Air temperature [K] | 300.8864 | 299.9740 | 0.4577 | 7.9817 | 1.95e-14 | 2.73e-14 |
| Process temperature [K] | 310.2903 | 309.9956 | 0.1987 | 3.8984 | 0.0001 | 0.0001 |
| Rotational speed [rpm] | 1496.4867 | 1540.2600 | -0.2444 | -2.0868 | 0.0376 | 0.0376 |
| Torque [Nm] | 50.1681 | 39.6297 | 1.0770 | 11.7808 | 3.64e-27 | 2.55e-26 |
| Tool wear [min] | 143.7817 | 106.6937 | 0.5859 | 9.2643 | 1.91e-18 | 3.34e-18 |
| Temperature delta [K] | 9.4038 | 10.0216 | -0.6209 | -9.6463 | 1.04e-19 | 2.42e-19 |
| Power proxy [W] | 7282.8195 | 6244.5475 | 0.9881 | 10.2733 | 8.87e-22 | 3.10e-21 |

Baseline logistic-regression test metrics: precision=0.139, recall=0.800, F1=0.237, average precision=0.383. Accuracy is intentionally not used as the primary metric because failures are rare. The model uses raw operating inputs and does not include derived power proxy, to avoid redundant deterministic inputs. Synthetic random split only; this does not demonstrate performance on real equipment or future time periods. The fixed 0.50 classification threshold is exploratory and was not optimized on a validation set.

Confusion matrix at the exploratory 0.50 threshold:

| Actual class | Predicted non-failure | Predicted failure |
| --- | --- | --- |
| Non-failure | TN=1995 | FP=420 |
| Failure | FN=17 | TP=68 |

## 8. RCA and FMEA

See `reports/rca_fmea.md`. Candidate explanations must be tested against subsystem inspection, calibration checks, maintenance context, and controlled trials. The FMEA scores are illustrative placeholders, not measured plant risk scores.

## 9. Engineering Recommendations

1. Prioritize instrumentation review for operating signals with the largest observed failure/non-failure separation; confirm measurement quality first.
2. Use the failure-mode register to scope physical inspections, not to diagnose a root cause from a label alone.
3. Establish configuration and maintenance-history capture before attempting real-equipment thresholding or predictive deployment.
4. Validate any parameter-monitoring proposal with a controlled protocol, pre-defined acceptance criteria, and post-change monitoring.

## 10. Limitations and Future Work

Future work should use temporally ordered, asset-specific data with verified failure mechanisms, downtime definitions, maintenance actions, and suitable subgroup assumptions before SPC or reliability claims are made.

## 11. Conclusion

The project demonstrates transparent data validation, interpretable failure analysis, leakage-aware baseline modelling, and disciplined RCA/FMEA framing. It is transferable as an engineering-analysis workflow, not as evidence about semiconductor equipment performance.
