"""Turn observed aggregate patterns into targeted, non-causal recommendations."""
from __future__ import annotations

import pandas as pd

from src.config import PROCESSED_DATA_PATH, REPORTS_DIR


def create_recommendations() -> None:
    """Write recommendations tied to the highest observed churn-rate groups."""
    data = pd.read_csv(PROCESSED_DATA_PATH)
    data["churn_rate"] = data["Churn"].eq("Yes")
    contract = data.groupby("Contract")["churn_rate"].mean().sort_values(ascending=False)
    payment = data.groupby("PaymentMethod")["churn_rate"].mean().sort_values(ascending=False)
    support = data.groupby("TechSupport")["churn_rate"].mean().sort_values(ascending=False)
    lines = [
        "# Business Recommendations", "",
        "Recommendations below are based on observed churn-rate differences in this dataset. They are prioritization hypotheses to test, not causal conclusions.", "",
        "## Observed Priorities", "",
        f"- Highest observed contract churn rate: **{contract.index[0]}** ({contract.iloc[0]:.1%}).",
        f"- Highest observed payment-method churn rate: **{payment.index[0]}** ({payment.iloc[0]:.1%}).",
        f"- Highest observed technical-support churn rate: **{support.index[0]}** ({support.iloc[0]:.1%}).", "",
        "## Recommended Actions", "",
        f"1. Test a retention journey for **{contract.index[0]}** customers, such as a clear annual-contract incentive or early value check-in.",
        f"2. Review friction in the **{payment.index[0]}** journey and A/B test a low-friction switch to automatic payment where appropriate.",
        f"3. Offer proactive onboarding or support outreach to **{support.index[0]}** customers, measuring incremental retention against a control group.",
        "4. Use the churn model as a ranked outreach list, with the selected threshold reflecting the cost trade-off between missed churners and unnecessary offers.",
        "5. Evaluate every intervention with randomized or quasi-experimental measurement before scaling.",
    ]
    (REPORTS_DIR / "business_recommendations.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    create_recommendations()
