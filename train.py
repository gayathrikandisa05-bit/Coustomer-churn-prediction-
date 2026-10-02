"""Train, validate, tune, and persist churn-classification pipelines."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, average_precision_score,
                             confusion_matrix, f1_score, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from src.config import FIGURES_DIR, MODELS_DIR, PROCESSED_DATA_PATH, RANDOM_STATE, REPORTS_DIR, ensure_directories
from src.features.engineering import engineer_features

TARGET = "Churn"
ID_COLUMN = "customerID"


def build_preprocessor(features: pd.DataFrame) -> ColumnTransformer:
    """Build a transformer fitted only within downstream training pipelines."""
    numeric = features.select_dtypes(include=["number"]).columns.tolist()
    categorical = [column for column in features.columns if column not in numeric]
    numeric_pipe = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("numeric", numeric_pipe, numeric),
        ("categorical", categorical_pipe, categorical),
    ])


def candidate_models() -> dict[str, object]:
    """Return a compact set of interpretable and non-linear classifiers."""
    return {
        "Dummy": DummyClassifier(strategy="prior"),
        "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, min_samples_leaf=20, class_weight="balanced", random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(n_estimators=300, min_samples_leaf=5, class_weight="balanced", n_jobs=-1, random_state=RANDOM_STATE),
        "Gradient Boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
        "HistGradient Boosting": HistGradientBoostingClassifier(random_state=RANDOM_STATE),
    }


def _metrics(y_true, probabilities, threshold: float) -> dict[str, float]:
    predictions = (np.asarray(probabilities) >= threshold).astype(int)
    return {
        "accuracy": accuracy_score(y_true, predictions), "precision": precision_score(y_true, predictions, zero_division=0),
        "recall": recall_score(y_true, predictions, zero_division=0), "f1": f1_score(y_true, predictions, zero_division=0),
        "roc_auc": roc_auc_score(y_true, probabilities), "pr_auc": average_precision_score(y_true, probabilities),
    }


def _save_evaluation_figures(y_test, probabilities, threshold: float) -> None:
    predictions = (probabilities >= threshold).astype(int)
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.5))
    ConfusionMatrixDisplay(confusion_matrix(y_test, predictions), display_labels=["No", "Yes"]).plot(ax=axes[0], colorbar=False)
    axes[0].set_title(f"Confusion Matrix (threshold={threshold:.2f})")
    fpr, tpr, _ = roc_curve(y_test, probabilities)
    axes[1].plot(fpr, tpr, label=f"ROC-AUC = {roc_auc_score(y_test, probabilities):.3f}")
    axes[1].plot([0, 1], [0, 1], "--", color="grey"); axes[1].set(xlabel="False positive rate", ylabel="True positive rate", title="ROC Curve")
    axes[1].legend()
    precision, recall, _ = precision_recall_curve(y_test, probabilities)
    axes[2].plot(recall, precision, label=f"PR-AUC = {average_precision_score(y_test, probabilities):.3f}")
    axes[2].set(xlabel="Recall", ylabel="Precision", title="Precision-Recall Curve"); axes[2].legend()
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "model_evaluation_curves.png", dpi=160); plt.close(fig)


def train_model() -> dict:
    """Perform a leak-free split, CV model selection, threshold choice, and final evaluation."""
    ensure_directories()
    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError("Run `python -m src.data.cleaning` before training.")
    data = engineer_features(pd.read_csv(PROCESSED_DATA_PATH))
    features = data.drop(columns=[TARGET, ID_COLUMN])
    target = data[TARGET].map({"No": 0, "Yes": 1})
    x_train, x_test, y_train, y_test = train_test_split(features, target, test_size=0.2, stratify=target, random_state=RANDOM_STATE)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    comparisons = []
    for name, estimator in candidate_models().items():
        pipeline = Pipeline([("preprocessor", build_preprocessor(features)), ("model", estimator)])
        scores = cross_val_score(pipeline, x_train, y_train, cv=cv, scoring="roc_auc", n_jobs=-1)
        comparisons.append({"model": name, "cv_roc_auc_mean": scores.mean(), "cv_roc_auc_std": scores.std()})
    comparison = pd.DataFrame(comparisons).sort_values("cv_roc_auc_mean", ascending=False)
    comparison.to_csv(REPORTS_DIR / "model_comparison.csv", index=False)

    # Tune the strongest observed CV candidate (Gradient Boosting) on training folds.
    # The intentionally compact grid keeps this project reproducible on a laptop.
    base_pipeline = Pipeline([("preprocessor", build_preprocessor(features)), ("model", GradientBoostingClassifier(random_state=RANDOM_STATE))])
    search = GridSearchCV(base_pipeline, {"model__n_estimators": [100, 150], "model__max_depth": [2], "model__learning_rate": [0.05, 0.1]}, scoring="roc_auc", cv=cv, n_jobs=-1, refit=True)
    search.fit(x_train, y_train)
    best_pipeline = search.best_estimator_

    # OOF probabilities decide the operating threshold without touching the test set.
    oof_probabilities = cross_val_predict(best_pipeline, x_train, y_train, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
    thresholds = np.arange(0.20, 0.71, 0.01)
    selected_threshold = float(max(thresholds, key=lambda value: f1_score(y_train, oof_probabilities >= value)))
    best_pipeline.fit(x_train, y_train)
    test_probabilities = best_pipeline.predict_proba(x_test)[:, 1]
    test_metrics = _metrics(y_test, test_probabilities, selected_threshold)
    _save_evaluation_figures(y_test, test_probabilities, selected_threshold)
    _save_feature_importance(best_pipeline)

    artifact = {"pipeline": best_pipeline, "threshold": selected_threshold, "feature_columns": features.columns.tolist(), "metrics": test_metrics}
    joblib.dump(artifact, MODELS_DIR / "churn_model.joblib")
    results = {"best_parameters": search.best_params_, "best_cv_roc_auc": search.best_score_, "threshold": selected_threshold, "test_metrics": test_metrics, "comparison": comparison.to_dict(orient="records")}
    (REPORTS_DIR / "training_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    _write_evaluation_report(results)
    return results


def _save_feature_importance(pipeline: Pipeline) -> None:
    """Persist global tree importance; it indicates association, not causation."""
    names = pipeline.named_steps["preprocessor"].get_feature_names_out()
    importance = pd.DataFrame({"feature": names, "importance": pipeline.named_steps["model"].feature_importances_}).sort_values("importance", ascending=False)
    importance.to_csv(REPORTS_DIR / "feature_importance.csv", index=False)
    top = importance.head(15).sort_values("importance")
    fig, axis = plt.subplots(figsize=(9, 6))
    axis.barh(top["feature"], top["importance"], color="#4C78A8")
    axis.set(title="Global Feature Importance (Gradient Boosting)", xlabel="Relative importance")
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "feature_importance.png", dpi=160); plt.close(fig)


def _write_evaluation_report(results: dict) -> None:
    metrics = results["test_metrics"]
    lines = ["# Model Evaluation", "", "## Method", "", "Models were compared with 5-fold stratified cross-validation on the training set using ROC-AUC. The held-out 20% test set was evaluated once after selection and tuning.", "", "## Final Model", "", f"- Tuned Gradient Boosting parameters: `{results['best_parameters']}`", f"- Cross-validation ROC-AUC: {results['best_cv_roc_auc']:.3f}", f"- Operating threshold selected from training out-of-fold predictions: {results['threshold']:.2f}", "", "## Held-out Test Metrics", ""]
    lines.extend(f"- {name.replace('_', ' ').title()}: {value:.3f}" for name, value in metrics.items())
    lines += ["", "False negatives are customers likely to churn who are missed by a retention campaign; false positives receive an unnecessary retention intervention. Threshold selection emphasizes F1 to balance these outcomes."]
    (REPORTS_DIR / "model_evaluation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    result = train_model()
    print(json.dumps(result["test_metrics"], indent=2))
