# Model Evaluation

## Method

Models were compared with 5-fold stratified cross-validation on the training set using ROC-AUC. The held-out 20% test set was evaluated once after selection and tuning.

## Final Model

- Tuned Gradient Boosting parameters: `{'model__learning_rate': 0.05, 'model__max_depth': 2, 'model__n_estimators': 150}`
- Cross-validation ROC-AUC: 0.850
- Operating threshold selected from training out-of-fold predictions: 0.34

## Held-out Test Metrics

- Accuracy: 0.778
- Precision: 0.563
- Recall: 0.725
- F1: 0.634
- Roc Auc: 0.845
- Pr Auc: 0.665

False negatives are customers likely to churn who are missed by a retention campaign; false positives receive an unnecessary retention intervention. Threshold selection emphasizes F1 to balance these outcomes.
