"""Interpretable descriptive analysis for observed machine failures."""
from __future__ import annotations

import pandas as pd

from data_loader import FAILURE_MODES, TARGET


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return (float("nan"), float("nan"))
    p = successes / total
    denom = 1 + z**2 / total
    centre = (p + z**2 / (2 * total)) / denom
    half = z * ((p * (1 - p) / total + z**2 / (4 * total**2)) ** 0.5) / denom
    return centre - half, centre + half


def overall_failure_rate(frame: pd.DataFrame) -> pd.DataFrame:
    failures, total = int(frame[TARGET].sum()), len(frame)
    low, high = wilson_interval(failures, total)
    return pd.DataFrame([{
        "records": total,
        "machine_failure_records": failures,
        "observed_per_record_failure_proportion": failures / total,
        "ci95_low": low,
        "ci95_high": high,
    }])


def failure_mode_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mode in FAILURE_MODES:
        flagged = int(frame[mode].sum())
        cooccurring = int(((frame[mode] == 1) & (frame[TARGET] == 1)).sum())
        rows.append({
            "failure_indicator": mode,
            "flagged_records": flagged,
            "flag_rate": frame[mode].mean(),
            "cooccurring_machine_failures": cooccurring,
            "indicator_without_machine_failure": flagged - cooccurring,
            "target_alignment_rate": cooccurring / flagged if flagged else float("nan"),
        })
    overlaps = (frame[FAILURE_MODES].sum(axis=1) > 1).sum()
    result = pd.DataFrame(rows).sort_values("flagged_records", ascending=False)
    result["records_with_multiple_mode_flags"] = int(overlaps)
    return result.reset_index(drop=True)


def failure_rate_by_band(frame: pd.DataFrame, feature: str, bands: int = 4) -> pd.DataFrame:
    grouped = pd.qcut(frame[feature], q=bands, duplicates="drop")
    result = frame.assign(condition_band=grouped).groupby("condition_band", observed=True)[TARGET].agg(records="size", machine_failure_records="sum", observed_per_record_failure_proportion="mean").reset_index()
    result["condition_band"] = result["condition_band"].astype(str)
    return result


def failure_category_conditions(frame: pd.DataFrame) -> pd.DataFrame:
    """Means by target/indicator flag; indicators can overlap and are not exclusive categories."""
    signals = ["Air temperature [K]", "Process temperature [K]", "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]", "Temperature delta [K]", "Power proxy [W]"]
    records = []
    for label in [TARGET] + FAILURE_MODES:
        means = frame.groupby(label)[signals].mean(numeric_only=True)
        if 1 in means.index:
            row = means.loc[1].to_dict()
            row.update({"failure_label": label, "flagged_records": int(frame[label].sum())})
            records.append(row)
    return pd.DataFrame(records)
