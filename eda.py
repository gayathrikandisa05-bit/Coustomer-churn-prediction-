"""Generate concise, reproducible EDA figures and observed-rate summaries."""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.config import FIGURES_DIR, PROCESSED_DATA_PATH, REPORTS_DIR, ensure_directories


def _churn_rate(frame: pd.DataFrame, column: str) -> pd.Series:
    return frame.assign(churn_binary=frame["Churn"].eq("Yes")).groupby(column, observed=False)["churn_binary"].mean().sort_values(ascending=False)


def run_eda() -> None:
    """Create business-relevant charts from cleaned data; no causal claims are made."""
    ensure_directories()
    data = pd.read_csv(PROCESSED_DATA_PATH)
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    sns.countplot(data=data, x="Churn", hue="Churn", legend=False, ax=axes[0, 0]); axes[0, 0].set_title("Customer Churn Distribution")
    for column, axis, title in [("Contract", axes[0, 1], "Churn Rate by Contract"), ("PaymentMethod", axes[1, 0], "Churn Rate by Payment Method")]:
        rates = _churn_rate(data, column).mul(100)
        rates.plot.bar(ax=axis, color="#4C78A8"); axis.set(title=title, ylabel="Churn rate (%)", xlabel="")
        axis.tick_params(axis="x", rotation=25)
    sns.boxplot(data=data, x="Churn", y="MonthlyCharges", hue="Churn", legend=False, ax=axes[1, 1]); axes[1, 1].set_title("Monthly Charges by Churn")
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "eda_overview.png", dpi=160); plt.close(fig)
    summary_columns = ["Contract", "InternetService", "PaymentMethod", "TechSupport", "OnlineSecurity", "PaperlessBilling"]
    lines = ["# Business Insights", "", "The following are observed churn associations, not causal effects.", ""]
    for column in summary_columns:
        rates = _churn_rate(data, column).mul(100).round(1)
        lines += [f"## Churn Rate by {column}", ""]
        lines.extend(f"- {category}: {rate:.1f}%" for category, rate in rates.items())
        lines.append("")
    (REPORTS_DIR / "business_insights.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run_eda()
