-- Load cleaned_telco_churn.csv into a table named telco_churn before running.
-- These queries describe associations in the observed data; they do not imply causation.

-- Overall class balance
SELECT churn,
       COUNT(*) AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS customer_percent
FROM telco_churn
GROUP BY churn;

-- Churn rate by contract type
SELECT contract,
       COUNT(*) AS customers,
       ROUND(100.0 * AVG(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_percent
FROM telco_churn
GROUP BY contract
ORDER BY churn_rate_percent DESC;

-- Churn rate by payment method
SELECT paymentmethod,
       COUNT(*) AS customers,
       ROUND(100.0 * AVG(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_percent
FROM telco_churn
GROUP BY paymentmethod
ORDER BY churn_rate_percent DESC;

-- Tenure-band profile
SELECT CASE
           WHEN tenure <= 12 THEN '0-12'
           WHEN tenure <= 24 THEN '13-24'
           WHEN tenure <= 48 THEN '25-48'
           ELSE '49+'
       END AS tenure_group,
       COUNT(*) AS customers,
       ROUND(100.0 * AVG(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_percent
FROM telco_churn
GROUP BY tenure_group
ORDER BY tenure_group;
