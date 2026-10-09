import pandas as pd
import pytest
from failure_analysis import overall_failure_rate, failure_mode_summary, wilson_interval
from statistical_analysis import group_comparison


def frame():
    return pd.DataFrame({"Machine failure": [0, 1, 0, 1], "TWF": [0, 1, 0, 0], "HDF": [0, 1, 0, 1], "PWF": [0, 0, 0, 0], "OSF": [0, 0, 0, 0], "RNF": [0, 0, 0, 0]})


def test_failure_rate_and_confidence_interval():
    report = overall_failure_rate(frame()).iloc[0]
    assert report["observed_per_record_failure_proportion"] == .5
    assert report["ci95_low"] < .5 < report["ci95_high"]


def test_failure_mode_overlap_is_reported():
    summary = failure_mode_summary(frame())
    assert summary["records_with_multiple_mode_flags"].iloc[0] == 1
    twf = summary.loc[summary["failure_indicator"] == "TWF"].iloc[0]
    assert twf["target_alignment_rate"] == 1


def test_wilson_interval_empty_denominator():
    assert str(wilson_interval(0, 0)[0]) == "nan"


def test_group_comparison_uses_sample_size_weighted_cohens_d():
    values = pd.DataFrame({"Machine failure": [1, 1, 0, 0, 0], "signal": [4.0, 8.0, 1.0, 2.0, 3.0]})
    result = group_comparison(values, "signal")
    expected = 4.0 / ((10.0 / 3.0) ** 0.5)
    assert result["cohens_d"] == pytest.approx(expected)
