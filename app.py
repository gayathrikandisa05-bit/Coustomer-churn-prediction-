"""A simple Streamlit interface for the trained churn pipeline."""
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import MODELS_DIR, PROCESSED_DATA_PATH
from src.models.predict import predict_customer

st.set_page_config(page_title="Customer Churn Prediction", page_icon="📉", layout="wide")
st.title("Customer Churn Prediction")
st.caption("Predictions are decision support, not evidence of why a customer will churn.")

if not (MODELS_DIR / "churn_model.joblib").exists():
    st.error("Model artifact is missing. Run `python -m src.models.train` first.")
    st.stop()
reference = pd.read_csv(PROCESSED_DATA_PATH)
with st.form("customer_form"):
    left, right = st.columns(2)
    customer = {}
    categorical = [
        column for column in reference.select_dtypes(include=["object", "string"]).columns
        if column not in ["customerID", "Churn"]
    ]
    with left:
        customer["tenure"] = st.number_input("Tenure (months)", min_value=0, max_value=100, value=12)
        customer["MonthlyCharges"] = st.number_input("Monthly charges", min_value=0.0, value=70.0)
        customer["TotalCharges"] = st.number_input("Total charges", min_value=0.0, value=840.0)
        customer["SeniorCitizen"] = st.selectbox("Senior citizen", [0, 1])
    with right:
        for column in categorical:
            customer[column] = st.selectbox(column, sorted(reference[column].dropna().unique()))
    submitted = st.form_submit_button("Predict churn")
if submitted:
    result = predict_customer(customer)
    st.metric("Churn probability", f"{result['churn_probability']:.1%}")
    st.write(f"**Prediction:** {result['predicted_churn']}  |  **Risk:** {result['risk_category']}")
    st.caption(f"Operating threshold: {result['threshold']:.2f}")
