# Customer Churn Prediction

An end-to-end, reproducible machine-learning project that predicts Telco customer churn and profiles customer segments for retention planning.

## Problem and Objective

Customer churn reduces recurring revenue. This project identifies customers with an elevated churn probability, profiles customer segments, and produces evidence-based retention hypotheses. It is decision support: observed associations and feature importance do not establish causation.

## Dataset

The project uses the supplied IBM Telco Customer Churn dataset at `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv`. The raw file is never modified. The source contains 7,043 customer records and 21 columns.

## What the Project Includes

- Reusable loading, schema validation, and data cleaning.
- Safe conversion of `TotalCharges`; 11 blank values belonging to zero-tenure customers are set to zero because no charges have accrued.
- Data-quality report, EDA figures, and observed churn-rate analysis.
- Feature engineering: tenure group, service count, support/security flag, and average monthly spend.
- Leak-free stratified train/test split, `ColumnTransformer`, and scikit-learn pipelines.
- Baseline, Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, and HistGradient Boosting comparison.
- Cross-validation, constrained Gradient Boosting tuning, operating-threshold selection using training out-of-fold predictions, and test evaluation.
- Global feature importance, K-Means segmentation, business recommendations, a saved prediction model, and Streamlit UI.

## Results

The tuned Gradient Boosting model was selected with 5-fold training cross-validation. Its held-out test metrics are:

| Metric | Score |
| --- | ---: |
| Accuracy | 0.778 |
| Precision | 0.563 |
| Recall | 0.725 |
| F1 | 0.634 |
| ROC-AUC | 0.845 |
| PR-AUC | 0.665 |

The selected operating threshold is 0.34. It is selected from training out-of-fold probabilities, not the held-out test data. Detailed outputs are in `reports/model_evaluation.md` and `reports/training_results.json`.

K-Means selected two customer segments from silhouette-score comparison. Segment profiles are in `reports/segment_profiles.csv`.

## Architecture

```text
data/raw/                   Raw source data
data/processed/             Cleaned data and customer segments
src/data/cleaning.py        Cleaning and validation
src/features/engineering.py Feature engineering
src/models/train.py         Train, tune, evaluate, and persist the model
src/models/predict.py       Reusable prediction interface
src/evaluation/             EDA and recommendations
src/segmentation/segment.py K-Means segmentation
app/app.py                  Streamlit dashboard
reports/                    Reports, metrics, and figures
tests/                      Regression tests
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Reproduce the Pipeline

Run from the repository root:

```bash
python -m src.data.cleaning
MPLBACKEND=Agg python -m src.evaluation.eda
MPLBACKEND=Agg python -m src.models.train
MPLBACKEND=Agg python -m src.segmentation.segment
python -m src.evaluation.recommendations
python -m unittest discover -s tests -v
```

The commands create `data/processed/cleaned_telco_churn.csv`, model artifacts under `models/`, and reports/figures under `reports/`.

## Launch the Dashboard

```bash
streamlit run app/app.py
```

## Example Programmatic Prediction

```python
from src.models.predict import predict_customer

prediction = predict_customer(customer_dictionary)
# {'churn_probability': ..., 'predicted_churn': 'Yes' or 'No',
#  'risk_category': 'Low Risk'/'Medium Risk'/'High Risk', 'threshold': ...}
```

The `customer_dictionary` must include the source customer fields except `customerID` and `Churn`.

## Limitations and Next Steps

- This observational dataset cannot establish why customers churn.
- Intervention effectiveness should be tested experimentally before rollout.
- Add temporal validation and retention-cost labels when those data become available.
- Integrate production monitoring for input drift, prediction quality, and intervention outcomes.
