"""Feature preparation and leakage controls."""
from __future__ import annotations

import numpy as np
import pandas as pd

from data_loader import FAILURE_MODES, IDENTIFIERS, OPERATING_FEATURES, TARGET

NUMERIC_FEATURES = ["Air temperature [K]", "Process temperature [K]", "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]"]


def validate_ranges(frame: pd.DataFrame) -> pd.DataFrame:
    """Flag impossible physical values; this does not delete observations."""
    rules = {
        "Air temperature [K]": lambda s: s > 0,
        "Process temperature [K]": lambda s: s > 0,
        "Rotational speed [rpm]": lambda s: s >= 0,
        "Torque [Nm]": lambda s: s >= 0,
        "Tool wear [min]": lambda s: s >= 0,
    }
    return pd.DataFrame([
        {"feature": feature, "invalid_values": int((~rule(frame[feature])).sum())}
        for feature, rule in rules.items()
    ])


def prepare_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add traceable engineering features; do not impute or remove outliers."""
    prepared = frame.copy()
    prepared["Temperature delta [K]"] = prepared["Process temperature [K]"] - prepared["Air temperature [K]"]
    prepared["Power proxy [W]"] = 2 * np.pi * prepared["Rotational speed [rpm]"] * prepared["Torque [Nm]"] / 60
    return prepared


def predictor_columns() -> list[str]:
    """Return permitted EDA variables. IDs and failure-mode labels are excluded."""
    return OPERATING_FEATURES + ["Temperature delta [K]", "Power proxy [W]"]


def model_predictor_columns() -> list[str]:
    """Return raw operating inputs for the baseline model.

    Derived power is deliberately omitted because it is deterministic from torque and
    rotational speed; retaining all three would create unnecessary multicollinearity.
    """
    return OPERATING_FEATURES.copy()


def leakage_audit(columns: list[str]) -> pd.DataFrame:
    forbidden = set(IDENTIFIERS + FAILURE_MODES + [TARGET])
    return pd.DataFrame({"column": columns, "allowed_as_predictor": [column not in forbidden for column in columns]})
