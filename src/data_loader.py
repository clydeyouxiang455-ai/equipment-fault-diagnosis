"""Reproducible acquisition and schema checks for the UCI AI4I 2020 dataset."""
from __future__ import annotations

from pathlib import Path
import hashlib
from urllib.request import urlretrieve

import pandas as pd

DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00601/ai4i2020.csv"
EXPECTED_ROWS = 10_000
EXPECTED_SHA256 = "dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e"
TARGET = "Machine failure"
FAILURE_MODES = ["TWF", "HDF", "PWF", "OSF", "RNF"]
IDENTIFIERS = ["UDI", "Product ID"]
OPERATING_FEATURES = ["Type", "Air temperature [K]", "Process temperature [K]", "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]"]
REQUIRED_COLUMNS = set(IDENTIFIERS + OPERATING_FEATURES + [TARGET] + FAILURE_MODES)


def source_checksum(path: str | Path) -> str:
    """Return the SHA-256 checksum of a downloaded raw file."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def download_data(destination: str | Path = "data/raw/ai4i2020.csv", verify_checksum: bool = True) -> Path:
    """Download the unmodified source CSV from UCI."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(DATA_URL, destination)
    load_data(destination)
    if verify_checksum and source_checksum(destination) != EXPECTED_SHA256:
        raise ValueError("Downloaded CSV checksum differs from the documented UCI release; review the source before analysis.")
    return destination


def load_data(path: str | Path = "data/raw/ai4i2020.csv") -> pd.DataFrame:
    """Load and validate the required schema without modifying the raw data."""
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if not set(frame[TARGET].dropna().unique()).issubset({0, 1}):
        raise ValueError("Machine failure must be binary (0/1).")
    for mode in FAILURE_MODES:
        if not set(frame[mode].dropna().unique()).issubset({0, 1}):
            raise ValueError(f"{mode} must be binary (0/1).")
    if len(frame) != EXPECTED_ROWS:
        raise ValueError(f"Expected {EXPECTED_ROWS} rows from the official release, found {len(frame)}.")
    return frame


def data_quality_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Return transparent data-quality checks for report generation."""
    return pd.DataFrame({
        "column": frame.columns,
        "dtype": [str(frame[c].dtype) for c in frame.columns],
        "missing_values": [int(frame[c].isna().sum()) for c in frame.columns],
        "unique_values": [int(frame[c].nunique(dropna=True)) for c in frame.columns],
    })
