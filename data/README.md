# Telco Customer Churn & Retention Analytics: Data Documentation

## 1. Dataset Overview

This project analyzes the **IBM Telco Customer Churn** dataset, a benchmark telecommunications industry dataset tracking 7,043 customer accounts in California. It contains comprehensive customer profiles covering demographic attributes, account tenure, subscribed phone and internet services, contract arrangements, payment mechanisms, billing charges, and churn flags.

---

## 2. Dataset Acquisition Preparation

> [!IMPORTANT]
> The raw IBM Telco Customer Churn dataset is required to power the Analytics, SQL modeling, and BI reporting layers. 

### Expected Filename & Directory
Place the downloaded CSV into the raw data directory:
* **Path**: `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv` (or `data/raw/telco_customer_churn.csv`)

### Official Sources to Obtain the Dataset
1. **Kaggle**: [Kaggle Telco Customer Churn by BlastChar](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
2. **IBM Business Analytics Community**: [IBM Sample Datasets - Telco Customer Churn](https://community.ibm.com/community/user/businessanalytics/blogs/steven-macko/2019/07/11/telco-customer-churn)

---

## 3. Data Dictionary Template

The dataset contains **21 original columns** representing distinct customer dimensions:

| # | Column Name | Raw Data Type | Cleaned Data Type | Description & Permissible Values | Business Dimension |
|---|---|---|---|---|---|
| 1 | `customerID` | String | String | Unique customer identifier (e.g., `7590-VHVEG`) | Identity |
| 2 | `gender` | String | String | Customer gender (`Male`, `Female`) | Demographics |
| 3 | `SeniorCitizen` | Integer | Integer | Senior citizen indicator (`1`: Yes, `0`: No) | Demographics |
| 4 | `Partner` | String | String | Has a partner/spouse (`Yes`, `No`) | Demographics |
| 5 | `Dependents` | String | String | Has dependents/children (`Yes`, `No`) | Demographics |
| 6 | `tenure` | Integer | Integer | Months customer has stayed with company (`0` to `72`) | Account Tenure |
| 7 | `PhoneService` | String | String | Has phone service (`Yes`, `No`) | Telephony |
| 8 | `MultipleLines` | String | String | Multiple phone lines (`Yes`, `No`, `No phone service`) | Telephony |
| 9 | `InternetService` | String | String | Internet provider type (`DSL`, `Fiber optic`, `No`) | Internet |
| 10 | `OnlineSecurity` | String | String | Online security add-on (`Yes`, `No`, `No internet service`) | Value-Added Services |
| 11 | `OnlineBackup` | String | String | Cloud backup add-on (`Yes`, `No`, `No internet service`) | Value-Added Services |
| 12 | `DeviceProtection` | String | String | Tech warranty add-on (`Yes`, `No`, `No internet service`) | Value-Added Services |
| 13 | `TechSupport` | String | String | Premium technical support (`Yes`, `No`, `No internet service`) | Value-Added Services |
| 14 | `StreamingTV` | String | String | IPTV streaming (`Yes`, `No`, `No internet service`) | Media & Entertainment |
| 15 | `StreamingMovies` | String | String | Film streaming (`Yes`, `No`, `No internet service`) | Media & Entertainment |
| 16 | `Contract` | String | String | Contractual commitment (`Month-to-month`, `One year`, `Two year`) | Contract & Billing |
| 17 | `PaperlessBilling` | String | String | Paperless digital billing (`Yes`, `No`) | Contract & Billing |
| 18 | `PaymentMethod` | String | String | Payment channel (`Electronic check`, `Mailed check`, `Bank transfer (automatic)`, `Credit card (automatic)`) | Contract & Billing |
| 19 | `MonthlyCharges` | Float | Float | Recurring monthly bill amount (USD) | Revenue / Financials |
| 20 | `TotalCharges` | Object (String) | Float | Lifetime cumulative bill amount (USD). Note: contains 11 blank spaces in raw data | Revenue / Financials |
| 21 | `Churn` | String | String | Primary target variable: customer churned in last month (`Yes`, `No`) | Outcome / Target |

---

## 4. Data Cleaning Methodology

### 1. `TotalCharges` Whitespace Handling
* **Observation**: In the raw dataset, `TotalCharges` is stored as an `object`/string column containing **11 rows with blank whitespace (`" "`)**.
* **Root Cause Analysis**: All 11 records have `tenure = 0`. These represent newly onboarded customers who joined in the current month and have not yet completed their first billing cycle.
* **Resolution**: Rather than dropping these rows (which would introduce bias against new signups), the pipeline assigns `TotalCharges = 0.0` for records where `tenure == 0`, and casts the column to `float64`.

### 2. String Hygiene & Whitespace Trimming
* All text-based categorical columns are trimmed of leading/trailing spaces to prevent subtle encoding mismatches (e.g. `' Month-to-month'` vs `'Month-to-month'`).

### 3. Customer Identifier Preservation
* The primary key `customerID` is strictly preserved unaltered in both raw and processed datasets to enable cross-table relational joins, cohort tracking, and customer-level lookups in SQL and BI tools.

### 4. Non-Destructive Raw Data Governance
* The raw dataset in `data/raw/` is treated as immutable read-only storage.
* Cleaned and standardized data is saved separately to:
  `data/processed/telco_churn_cleaned.csv`

---

## 5. Execution Instructions

1. **Verify Raw Dataset Status**:
   ```bash
   python src/data_loader.py
   ```
   *If the CSV is absent, it prints explicit download and location instructions.*

2. **Execute Ingestion, Validation & Cleaning**:
   ```bash
   python src/pipeline.py
   ```
