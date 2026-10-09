"""Leakage-aware statistical diagnostics and baseline classification."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, confusion_matrix, precision_recall_curve, precision_score, recall_score, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split

from data_loader import TARGET
from preprocessing import model_predictor_columns, predictor_columns

RANDOM_STATE = 42


def benjamini_hochberg(p_values: pd.Series) -> np.ndarray:
    """Return Benjamini-Hochberg adjusted p-values for exploratory comparisons."""
    values = p_values.to_numpy(dtype=float)
    order = np.argsort(values)
    ranked = values[order]
    adjusted_ranked = np.minimum.accumulate((ranked * len(values) / np.arange(1, len(values) + 1))[::-1])[::-1]
    adjusted = np.empty_like(adjusted_ranked)
    adjusted[order] = np.minimum(adjusted_ranked, 1.0)
    return adjusted


def spearman_correlations(frame: pd.DataFrame) -> pd.DataFrame:
    numeric = [c for c in predictor_columns() if c != "Type"] + [TARGET]
    return frame[numeric].corr(method="spearman")


def group_comparison(frame: pd.DataFrame, feature: str) -> dict[str, float | str]:
    failed, healthy = frame.loc[frame[TARGET] == 1, feature], frame.loc[frame[TARGET] == 0, feature]
    statistic, p_value = stats.ttest_ind(failed, healthy, equal_var=False)
    # Sample-size-weighted pooled SD for Cohen's d (not the unweighted mean of variances).
    pooled_variance = (
        ((len(failed) - 1) * failed.var(ddof=1) + (len(healthy) - 1) * healthy.var(ddof=1))
        / (len(failed) + len(healthy) - 2)
    )
    pooled_sd = np.sqrt(pooled_variance)
    d = (failed.mean() - healthy.mean()) / pooled_sd if pooled_sd else np.nan
    return {"feature": feature, "failed_mean": failed.mean(), "nonfailed_mean": healthy.mean(), "cohens_d": d, "welch_t": statistic, "p_value": p_value}


def fit_baseline_model(frame: pd.DataFrame) -> tuple[dict[str, object], np.ndarray, np.ndarray]:
    features = model_predictor_columns()
    x, y = frame[features], frame[TARGET]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y)
    numeric = [c for c in features if c != "Type"]
    transformer = ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
        ("type", OneHotEncoder(handle_unknown="ignore"), ["Type"]),
    ])
    model = Pipeline([("transform", transformer), ("classifier", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE))])
    model.fit(x_train, y_train)
    scores = model.predict_proba(x_test)[:, 1]
    predictions = (scores >= 0.5).astype(int)
    metrics = {
        "test_records": int(len(y_test)), "test_failures": int(y_test.sum()),
        "precision": precision_score(y_test, predictions, zero_division=0), "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0), "average_precision": average_precision_score(y_test, scores),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
        "warning": "Synthetic random split only; this does not demonstrate performance on real equipment or future time periods. The fixed 0.50 classification threshold is exploratory and was not optimized on a validation set.",
    }
    return metrics, y_test.to_numpy(), scores


def precision_recall_data(y_true: np.ndarray, scores: np.ndarray) -> pd.DataFrame:
    precision, recall, thresholds = precision_recall_curve(y_true, scores)
    return pd.DataFrame({"precision": precision[:-1], "recall": recall[:-1], "threshold": thresholds})
