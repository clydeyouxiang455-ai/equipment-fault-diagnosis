"""Run the complete engineering analysis from raw CSV to reports."""
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))
from data_loader import data_quality_summary, load_data
from preprocessing import prepare_features, validate_ranges, predictor_columns
from failure_analysis import overall_failure_rate, failure_mode_summary, failure_rate_by_band, failure_category_conditions
from statistical_analysis import benjamini_hochberg, spearman_correlations, group_comparison, fit_baseline_model, precision_recall_data
from visualization import save_figures


def table_md(frame):
    headers = [str(x) for x in frame.columns]
    rows = [[f"{x:.2e}" if isinstance(x, float) and x != 0 and abs(x) < 0.0001 else (f"{x:.4f}" if isinstance(x, float) else str(x).replace("|", "\\|")) for x in row] for row in frame.itertuples(index=False, name=None)]
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"] + ["| " + " | ".join(row) + " |" for row in rows])


def write_reports(tables: dict, metrics: dict) -> None:
    report_dir = Path("reports"); report_dir.mkdir(exist_ok=True)
    rca = tables["comparisons"].sort_values("p_value").head(4)
    confusion = metrics["confusion_matrix"]
    # RNF is excluded from FMEA ranking because its indicator does not consistently
    # align with Machine failure in the current official CSV.
    fmea = tables["modes"].query("failure_indicator != 'RNF'").copy()
    context = {
        "HDF": ("Dataset flag tied to low temperature difference and lower rotational speed", "Review temperature sensors, thermal path and operating state; test a controlled operating envelope"),
        "OSF": ("Dataset flag tied to tool-wear and torque product with Type-specific thresholds", "Inspect tool condition/load path; verify torque calibration and configuration threshold"),
        "PWF": ("Dataset flag tied to calculated rotational power outside documented bounds", "Verify speed/torque instrumentation and load condition; repeat under controlled load"),
        "TWF": ("Dataset-generated tool-wear failure flag", "Inspect tool wear measurement and replacement criteria; compare with controlled wear samples"),
        "RNF": ("Dataset-generated random-failure flag", "Review event logging and unmeasured factors; no parameter-only causal claim is justified"),
    }
    fmea["potential_effect"] = "Unexpected equipment fault indication; impact requires asset context"
    fmea["possible_cause"] = fmea["failure_indicator"].map(lambda x: context[x][0])
    fmea["existing_evidence"] = "Observed synthetic-dataset flag frequency"
    fmea["alternative_explanations"] = "Sensor error, configuration differences, or unmeasured maintenance/operating context"
    fmea["additional_measurements"] = "Calibration status, configuration ID, maintenance history, subsystem inspection results"
    fmea["recommended_verification"] = fmea["failure_indicator"].map(lambda x: context[x][1])
    fmea["severity"] = 7
    fmea["occurrence"] = fmea["flag_rate"].apply(lambda x: 2 if x < .01 else 3)
    fmea["detection"] = 5
    fmea["rpn"] = fmea["severity"] * fmea["occurrence"] * fmea["detection"]
    (report_dir / "rca_fmea.md").write_text(
        "# RCA and Preliminary FMEA\n\n"
        "This is an investigation aid. Severity=7 and Detection=5 are illustrative engineering judgments; Occurrence=2 or 3 is assigned only from synthetic-data indicator frequency. RPN=S x O x D is illustrative only, not a measured plant risk score or action priority.\n\n"
        "## 5 Why prompt\n\n"
        "1. Why was a failure label observed? It may reflect a documented synthetic-data rule or random flag; first reconcile the target with the indicator columns because the official CSV contains mismatches.\n"
        "2. Why was that operating condition present? Examine operating state, load, tool condition and configuration.\n"
        "3. Why might that condition persist? Inspect control logic, setup, thermal path, wear-management and measurement quality.\n"
        "4. Why was it not detected earlier? Review monitoring coverage, calibration status and inspection triggers.\n"
        "5. What is the verified root cause? Do not answer until physical inspection and a controlled validation provide evidence.\n\n"
        "## Fishbone / Ishikawa prompt\n\n"
        "Investigate **Machine** (mechanisms/interfaces), **Method** (setup/control logic), **Measurement** (calibration/sampling), **Material or Tooling** (wear/load), **Environment** (thermal conditions), and **People/Management** (maintenance/standard work). These are hypothesis categories, not dataset-derived causes.\n\n"
        + table_md(fmea), encoding="utf-8"
    )
    report = f"""# Engineering Report: Equipment Fault Diagnosis & Reliability Analysis

## 1. Executive Summary

This reproducible engineering analysis uses the UCI AI4I 2020 synthetic predictive-maintenance dataset. It profiles observed failure patterns, runs leakage-aware statistical diagnostics, and turns results into verification-oriented RCA/FMEA prompts. It does not represent semiconductor tools or prove physical root causes.

## 2. Engineering Problem Statement

The task is to prioritize observable operating conditions for investigation when machine-failure labels are rare. The goal is engineering hypothesis generation and verification planning, not a production decision system.

## 3. Dataset and Limitations

The source contains synthetic observations, no explicit timestamps, downtime records, maintenance histories, or wafer/process measurements. UCI classifies it as time-series, but UDI is an identifier rather than a verified operational timestamp; this project does not create chronological controls or claim temporal deployment performance. Random train/test performance cannot establish future or real-equipment performance. Failure-indicator flags may overlap and are excluded from predictors to prevent leakage.

## 4. Data Quality Assessment

{table_md(tables['quality'].head(12))}

Range-check exceptions: {int(tables['ranges']['invalid_values'].sum())}. Duplicate rows: {tables['duplicates']}.

## 5. Exploratory Data Analysis

{table_md(tables['overall'])}

Figures: `reports/figures/operating_conditions.png` and `reports/figures/failure_modes_and_correlations.png`.

Condition-band failure rates are saved in `data/processed/failure_rates_by_parameter_bands.csv`. Failure-category condition means are saved in `data/processed/failure_category_conditions.csv`; category flags may overlap.

## 6. Failure Pattern Investigation

{table_md(tables['modes'])}

Failure-indicator flags are not mutually exclusive: {tables['multi_mode']} records carry more than one indicator. Importantly, the current official CSV has a documented integrity discrepancy: RNF flags do not reliably co-occur with the machine-failure target, and {tables['unlabelled_target_failures']} target-positive records have no indicator. The mode table exposes this explicitly; RNF is excluded from FMEA prioritization.

## 7. Statistical Diagnostics

Welch group comparisons below quantify differences between failure and non-failure observations. Effect size is sample-size-weighted pooled Cohen's d; p-values are descriptive statistics rather than causal evidence. `p_value_bh` applies Benjamini-Hochberg adjustment across these exploratory comparisons.

{table_md(tables['comparisons'])}

Baseline logistic-regression test metrics: precision={metrics['precision']:.3f}, recall={metrics['recall']:.3f}, F1={metrics['f1']:.3f}, average precision={metrics['average_precision']:.3f}. Accuracy is intentionally not used as the primary metric because failures are rare. The model uses raw operating inputs and does not include derived power proxy, to avoid redundant deterministic inputs. {metrics['warning']}

Confusion matrix at the exploratory 0.50 threshold:

| Actual class | Predicted non-failure | Predicted failure |
| --- | --- | --- |
| Non-failure | TN={confusion[0][0]} | FP={confusion[0][1]} |
| Failure | FN={confusion[1][0]} | TP={confusion[1][1]} |

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
"""
    (report_dir / "engineering_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    raw = load_data()
    frame = prepare_features(raw)
    mode_summary = failure_mode_summary(frame)
    unlabelled_target_failures = int(((raw["Machine failure"] == 1) & (raw[["TWF", "HDF", "PWF", "OSF", "RNF"]].sum(axis=1) == 0)).sum())
    comparisons = __import__('pandas').DataFrame([group_comparison(frame, f) for f in predictor_columns() if f != 'Type'])
    comparisons["p_value_bh"] = benjamini_hochberg(comparisons["p_value"])
    tables = {
        "quality": data_quality_summary(raw), "ranges": validate_ranges(raw),
        "overall": overall_failure_rate(frame), "modes": mode_summary,
        "comparisons": comparisons,
        "failure_category_conditions": failure_category_conditions(frame),
        "duplicates": int(raw.duplicated().sum()), "multi_mode": int((raw[["TWF", "HDF", "PWF", "OSF", "RNF"]].sum(axis=1) > 1).sum()), "unlabelled_target_failures": unlabelled_target_failures,
    }
    correlations = spearman_correlations(frame)
    continuous = [feature for feature in predictor_columns() if feature != "Type"]
    bands = __import__('pandas').concat([failure_rate_by_band(frame, feature).assign(feature=feature) for feature in continuous], ignore_index=True)
    metrics, y_true, scores = fit_baseline_model(frame)
    pr_data = precision_recall_data(y_true, scores)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    for name, table in [("data_quality", tables["quality"]), ("range_checks", tables["ranges"]), ("overall_failure_rate", tables["overall"]), ("failure_modes", tables["modes"]), ("failure_category_conditions", tables["failure_category_conditions"]), ("failure_rates_by_parameter_bands", bands), ("group_comparisons", tables["comparisons"]), ("correlations", correlations), ("precision_recall", pr_data)]:
        table.to_csv(Path("data/processed") / f"{name}.csv", index=True if name == "correlations" else False)
    Path("reports/model_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    save_figures(frame, tables["modes"], correlations, pr_data)
    write_reports(tables, metrics)
    print("Analysis complete. Outputs written to data/processed and reports.")


if __name__ == "__main__":
    main()
