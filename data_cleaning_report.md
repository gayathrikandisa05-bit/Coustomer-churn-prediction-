# Data Cleaning Report

## Summary

- Input rows: 7043
- Output rows: 7043
- Input columns: 21
- Input memory usage: 1,954,553 bytes
- Exact duplicate rows before cleaning: 0
- Exact duplicate rows removed: 0
- Blank `TotalCharges` set to `0` for zero-tenure customers: 11

## Decisions

- Whitespace was stripped from text fields; empty text became missing.
- `TotalCharges`, `MonthlyCharges`, and `tenure` were converted to numeric.
- `SeniorCitizen` was validated as a binary integer.
- Blank `TotalCharges` is zero only for customers with zero tenure; no other missing numeric values were silently imputed.
- Exact duplicate records are removed; customer IDs are otherwise preserved.
- No numerical values were removed or capped. Extreme tenure and charge values are plausible customer observations and are handled downstream by model preprocessing.

## Validation

- Invalid numeric values: {'tenure': 0, 'MonthlyCharges': 0, 'TotalCharges': 0}
- Invalid `SeniorCitizen` values: 0
- Unexpected categories: {}
- Missing values after cleaning: {'customerID': 0, 'gender': 0, 'SeniorCitizen': 0, 'Partner': 0, 'Dependents': 0, 'tenure': 0, 'PhoneService': 0, 'MultipleLines': 0, 'InternetService': 0, 'OnlineSecurity': 0, 'OnlineBackup': 0, 'DeviceProtection': 0, 'TechSupport': 0, 'StreamingTV': 0, 'StreamingMovies': 0, 'Contract': 0, 'PaperlessBilling': 0, 'PaymentMethod': 0, 'MonthlyCharges': 0, 'TotalCharges': 0, 'Churn': 0}

## Target Distribution

- No: 5174
- Yes: 1869
- Churn percentage: 26.5%
- Non-churn percentage: 73.5%
- Non-churn to churn imbalance ratio: 2.77:1

## Raw Data Profile

### Data Types

- `customerID`: str
- `gender`: str
- `SeniorCitizen`: int64
- `Partner`: str
- `Dependents`: str
- `tenure`: int64
- `PhoneService`: str
- `MultipleLines`: str
- `InternetService`: str
- `OnlineSecurity`: str
- `OnlineBackup`: str
- `DeviceProtection`: str
- `TechSupport`: str
- `StreamingTV`: str
- `StreamingMovies`: str
- `Contract`: str
- `PaperlessBilling`: str
- `PaymentMethod`: str
- `MonthlyCharges`: float64
- `TotalCharges`: str
- `Churn`: str

### Missing Values Before Cleaning

- `customerID`: 0
- `gender`: 0
- `SeniorCitizen`: 0
- `Partner`: 0
- `Dependents`: 0
- `tenure`: 0
- `PhoneService`: 0
- `MultipleLines`: 0
- `InternetService`: 0
- `OnlineSecurity`: 0
- `OnlineBackup`: 0
- `DeviceProtection`: 0
- `TechSupport`: 0
- `StreamingTV`: 0
- `StreamingMovies`: 0
- `Contract`: 0
- `PaperlessBilling`: 0
- `PaymentMethod`: 0
- `MonthlyCharges`: 0
- `TotalCharges`: 0
- `Churn`: 0

### Unique Values

- `customerID`: 7043
- `gender`: 2
- `SeniorCitizen`: 2
- `Partner`: 2
- `Dependents`: 2
- `tenure`: 73
- `PhoneService`: 2
- `MultipleLines`: 3
- `InternetService`: 3
- `OnlineSecurity`: 3
- `OnlineBackup`: 3
- `DeviceProtection`: 3
- `TechSupport`: 3
- `StreamingTV`: 3
- `StreamingMovies`: 3
- `Contract`: 3
- `PaperlessBilling`: 2
- `PaymentMethod`: 4
- `MonthlyCharges`: 1585
- `TotalCharges`: 6531
- `Churn`: 2
