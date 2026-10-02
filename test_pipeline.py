"""Focused regression tests for essential project behavior."""
import unittest

import pandas as pd

from src.data.cleaning import clean_telco_data, load_raw_data
from src.features.engineering import engineer_features
from src.models.predict import predict_customer


class TestDataPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load_raw_data()
        cls.cleaned = clean_telco_data(cls.raw).data

    def test_raw_data_loads(self):
        self.assertGreater(len(self.raw), 0)
        self.assertIn("Churn", self.raw.columns)

    def test_total_charges_is_numeric_and_complete(self):
        self.assertTrue(pd.api.types.is_numeric_dtype(self.cleaned["TotalCharges"]))
        self.assertEqual(int(self.cleaned.isna().sum().sum()), 0)

    def test_cleaning_preserves_valid_target(self):
        self.assertEqual(set(self.cleaned["Churn"].unique()), {"Yes", "No"})

    def test_feature_engineering_adds_expected_columns(self):
        features = engineer_features(self.cleaned)
        self.assertTrue({"TenureGroup", "ServiceCount", "HasSupportOrSecurity", "AverageMonthlySpend"}.issubset(features.columns))

    def test_prediction_output_format_when_model_exists(self):
        customer = self.cleaned.drop(columns=["customerID", "Churn"]).iloc[0].to_dict()
        result = predict_customer(customer)
        self.assertEqual(set(result), {"churn_probability", "predicted_churn", "risk_category", "threshold"})
        self.assertGreaterEqual(result["churn_probability"], 0.0)
        self.assertLessEqual(result["churn_probability"], 1.0)


if __name__ == "__main__":
    unittest.main()
