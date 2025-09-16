Here’s a **polished README draft** that keeps your voice but organizes everything clearly, adds the four links, and emphasizes the **pipeline + testing** story.

---

# Olist Brazil E-commerce: Data Pipeline for Predictive Analysis

## Project Overview

This project demonstrates a **full data-engineering + machine-learning pipeline** on the public
[Olist Brazilian E-commerce dataset](https://www.kaggle.com/olistbr/brazilian-ecommerce).
The focus is on **production-ready data flows, cloud management, and testing**,
with modeling used primarily to validate the pipeline rather than to chase the highest accuracy.

---

## Key Highlights

* **AWS Cloud Pipeline** – Raw CSVs → **AWS RDS (PostgreSQL)** → locally-run SQL queries → upload to **Amazon S3** → download to local machine for analytics and modeling.
* **SQL Feature Engineering** – Recency/Frequency metrics, pricing features, and logistical variables such as `estimated_days_vs_actual`.
* **Predictive Modeling** –

  * **Delivery Delay**: XGBoost model predicting late deliveries.
  * **Customer Churn**: Logistic Regression and Random Forest.
    *(Models are intentionally simple—goal is pipeline reliability, not SOTA accuracy.)*
* **Data Quality Testing** – Outlier flags, negative-time checks, and unit tests to validate every SQL query before export.

---

## Key Results & Visuals

| Artifact                                                      | Link                                                         |
| ------------------------------------------------------------- | ------------------------------------------------------------ |
| Feature Importance – **Delivery Delay (XGBoost)**             | [delivery\feature_importance.png](results/ML/delivery_prediciton/feature_importance.png) |
| Feature Importance – **Customer Churn (Logistic Regression)** | [churn\lr\feature_importance.png](results/ML/churn_prediction/logistic_regression_V1/coefficients.png)     |
| Feature Importance – **Customer Churn (Random Forest)**       | [churn\rf\feature_importance.png](results/ML/churn_prediction/random_forest_V1/coefficients.png)     |
| **Orders Heatmap** (geographic order density)                 | [orders\heatmap.png](results\heatmap\brazil_heatmap.html)                    |


---

## Testing & Data Quality

Every SQL query was accompanied by **pytest-style checks** to guarantee accuracy before moving data downstream.
Examples:

* **Aggregation tests** – revenue sums across states match overall totals.
* **Consistency tests** – order counts match between joined tables.
* **Outlier detection** – freight ratio > 2 or negative shipping times flagged for review.

---

## Tech Stack

| Layer                      | Tools                  |
| -------------------------- | ---------------------- |
| **Data Storage**           | Amazon S3              |
| **Database / Query Layer** | AWS RDS (PostgreSQL)   |
| **Analytics / Testing**    | Python, pandas, pytest |
| **Modeling**               | scikit-learn, XGBoost  |

---

## Pipeline Flow

```
Raw Olist CSVs
   │
   ├─► Load to AWS RDS (PostgreSQL)
   │
   ├─► Local SQL queries + pytest data-quality tests
   │
   ├─► Export clean feature tables
   │
   ├─► Upload to Amazon S3 bucket
   │
   └─► Download refined CSVs for local modeling
```

---

## Insights

* **Late Delivery** – `distinct_sellers` emerged as the most influential predictor; orders involving multiple sellers have a higher probability of being late.
* **Customer Churn** – Features reflecting **customer spending behavior** (order value, frequency) are strongest predictors of repeat purchasing, which aligns with the fact that **most Olist customers only order once**.

---

## Takeaways

* Building a **tested, cloud-based data pipeline** is just as critical as modeling.
* **SQL feature engineering + automated tests** ensure reliability and reproducibility.
* Even modest models (XGBoost, Random Forest) can surface actionable logistics and customer-behavior insights when the data pipeline is solid.

---

### Contact

👤 **Hayden Holmes**
[LinkedIn](https://www.linkedin.com/in/hayden-holmes-3b6566267/)


