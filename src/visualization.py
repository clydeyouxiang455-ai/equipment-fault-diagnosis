"""Publication-ready, interpretable visualisations."""
from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from data_loader import TARGET


def save_figures(frame: pd.DataFrame, mode_summary: pd.DataFrame, correlations: pd.DataFrame, pr_data: pd.DataFrame, output_dir: str | Path = "reports/figures") -> None:
    output = Path(output_dir); output.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for outcome, group in frame.groupby(TARGET):
        axes[0].hist(group["Process temperature [K]"], bins=25, alpha=.65, label=f"Machine failure={outcome}")
    axes[0].set(xlabel="Process temperature [K]", ylabel="Records", title="Process temperature distribution"); axes[0].legend()
    axes[1].scatter(frame["Rotational speed [rpm]"], frame["Torque [Nm]"], c=frame[TARGET], cmap="coolwarm", alpha=.35, s=10)
    axes[1].set(xlabel="Rotational speed [rpm]", ylabel="Torque [Nm]", title="Torque-speed observations")
    frame.boxplot(column="Tool wear [min]", by=TARGET, ax=axes[2])
    axes[2].set(xlabel="Machine failure (0=no, 1=yes)", ylabel="Tool wear [min]", title="Tool wear by failure outcome")
    fig.suptitle("")
    fig.tight_layout(); fig.savefig(output / "operating_conditions.png", dpi=180); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].bar(mode_summary["failure_indicator"], mode_summary["flagged_records"], color="#4472C4")
    axes[0].set(xlabel="Failure-indicator label", ylabel="Flagged records", title="Observed failure-indicator flags")
    image = axes[1].imshow(correlations, vmin=-1, vmax=1, cmap="coolwarm")
    axes[1].set_xticks(range(len(correlations.columns)), correlations.columns, rotation=70, ha="right", fontsize=7)
    axes[1].set_yticks(range(len(correlations.index)), correlations.index, fontsize=7); axes[1].set_title("Spearman correlations")
    fig.colorbar(image, ax=axes[1], label="rho"); fig.tight_layout(); fig.savefig(output / "failure_modes_and_correlations.png", dpi=180); plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 4)); ax.plot(pr_data["recall"], pr_data["precision"], color="#4472C4")
    ax.set(xlabel="Recall", ylabel="Precision", title="Baseline logistic regression: precision-recall curve", xlim=(0, 1), ylim=(0, 1)); fig.tight_layout(); fig.savefig(output / "precision_recall_curve.png", dpi=180); plt.close(fig)
