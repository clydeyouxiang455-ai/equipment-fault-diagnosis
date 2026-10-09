import pandas as pd
import pytest
from preprocessing import model_predictor_columns, prepare_features, predictor_columns, validate_ranges


def sample():
    return pd.DataFrame({"Type": ["L", "M"], "Air temperature [K]": [300., 301.], "Process temperature [K]": [310., 311.], "Rotational speed [rpm]": [1200, 1500], "Torque [Nm]": [40., 30.], "Tool wear [min]": [5, 10], "Machine failure": [0, 1], "TWF": [0, 1], "HDF": [0, 0], "PWF": [0, 0], "OSF": [0, 0], "RNF": [0, 0]})


def test_engineering_features_are_calculated():
    result = prepare_features(sample())
    assert result.loc[0, "Temperature delta [K]"] == 10
    assert round(result.loc[0, "Power proxy [W]"], 2) == 5026.55


def test_failure_mode_labels_are_not_predictors():
    assert not set(["TWF", "HDF", "PWF", "OSF", "RNF", "Machine failure"]).intersection(predictor_columns())
    assert "Power proxy [W]" not in model_predictor_columns()


def test_range_checks_do_not_remove_records():
    result = validate_ranges(sample())
    assert result["invalid_values"].sum() == 0


def test_loader_rejects_non_binary_failure_mode(monkeypatch):
    from data_loader import load_data
    bad = sample()
    bad.insert(0, "UDI", [1, 2]); bad.insert(1, "Product ID", ["M1", "M2"])
    # Add 9,998 valid records so only the mode validation is under test.
    valid = pd.concat([bad.iloc[[0]]] * 5000 + [bad.iloc[[1]]] * 5000, ignore_index=True)
    valid.loc[0, "TWF"] = 2
    monkeypatch.setattr("data_loader.pd.read_csv", lambda _path: valid)
    with pytest.raises(ValueError, match="TWF must be binary"):
        load_data("not-used.csv")


def test_source_checksum_is_stable_for_known_bytes(monkeypatch):
    from data_loader import source_checksum
    monkeypatch.setattr("data_loader.Path.read_bytes", lambda _path: b"ai4i")
    assert source_checksum("sample.txt") == "4f8c0784878f7d017f4f64a8ca56243cdfd0a9b6130a882fe8ad3470e02ddc3c"
