"""Reusable churn prediction interface backed by the persisted pipeline."""
from __future__ import annotations

from pathlib import Path
from typing import Mapping

import joblib
import pandas as pd

from src.config import MODELS_DIR
from src.features.engineering import engineer_features


def predict_customer(customer: Mapping[str, object], model_path: Path | None = None) -> dict[str, object]:
    """Return a churn probability, label, and business-oriented risk category."""
    artifact = joblib.load(model_path or MODELS_DIR / "churn_model.joblib")
    customer_frame = engineer_features(pd.DataFrame([customer]))
    feature_frame = customer_frame[artifact["feature_columns"]]
    probability = float(artifact["pipeline"].predict_proba(feature_frame)[0, 1])
    threshold = float(artifact["threshold"])
    risk = "High Risk" if probability >= 0.65 else "Medium Risk" if probability >= 0.35 else "Low Risk"
    return {"churn_probability": probability, "predicted_churn": "Yes" if probability >= threshold else "No", "risk_category": risk, "threshold": threshold}
