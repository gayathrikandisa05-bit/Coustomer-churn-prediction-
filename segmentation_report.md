# Customer Segmentation

K-Means was fitted on standardized tenure, monthly charges, total charges, and service count. Cluster count was chosen by the highest silhouette score from k=2 through k=6.

- Selected clusters: 2
- Silhouette scores: {2: 0.46697748732774425, 3: 0.41195764623265974, 4: 0.41869686158784414, 5: 0.3872372221707717, 6: 0.37376064632662637}

## Segment Profiles

- Segment 0: {'customers': 2501.0, 'average_tenure': 54.493, 'average_monthly_charges': 90.248, 'average_total_charges': 4898.573, 'churn_rate': 0.177, 'average_service_count': 5.518}
- Segment 1: {'customers': 4542.0, 'average_tenure': 20.19, 'average_monthly_charges': 50.728, 'average_total_charges': 837.701, 'churn_rate': 0.314, 'average_service_count': 2.176}
