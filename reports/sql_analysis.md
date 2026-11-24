# Telco Customer Churn & Retention Intelligence: SQL Analytics & Business Query Engineering Report

**Project:** Telco Customer Churn & Retention Intelligence  
**Phase:** Phase 3 — SQL Analytics & Business Query Engineering  
**Database Engine:** SQLite 3 (`database/telco_churn.db`)  
**Underlying Table:** `customers` ($7,043$ rows $\times$ $21$ columns)  
**Status:** Ingestion, query suite, exports, and automated verification **100% Passed**.

---

## 1. Executive Summary

Phase 3 establishes an enterprise-grade, reproducible SQL analytics layer for the Telco Customer Churn & Retention Intelligence platform. Using Python's native `sqlite3` engine and ANSI-compliant SQL, we ingested the standardized dataset into a relational schema, audited data quality, engineered an executive KPI calculation suite, investigated multi-dimensional churn drivers, reproduced a $3 \times 3$ customer risk segmentation model, and demonstrated advanced SQL engineering techniques (CTEs, Window Functions, and Conditional Aggregations).

Every metric was independently reconciled against Pandas in [src/validate_sql_results.py](file:///c:/Users/Sruthi/Documents/telco-churn-app/src/validate_sql_results.py), confirming **$37 / 37$ tests passing with zero discrepancy**.

---

## 2. Relational Database Design & Architecture

### A. Rationale for SQLite
1. **Zero External Configuration:** Embedded relational engine requiring no server daemon, network socket configuration, or credentials, making the project seamlessly reproducible across any developer environment.
2. **ACID Compliance & Transactional Integrity:** Full transactional semantics ensure atomic data loading without partial state corruption.
3. **ANSI SQL & Window Function Support:** Modern SQLite engines ($3.25+$) support Common Table Expressions (CTEs), window ranking (`RANK()`, `DENSE_RANK()`, `ROW_NUMBER()`), and aggregate framing (`SUM() OVER (...)`, `AVG() OVER (...)`).

### B. Table Definition (`customers`)
Defined in [sql/schema.sql](file:///c:/Users/Sruthi/Documents/telco-churn-app/sql/schema.sql):

```sql
CREATE TABLE customers (
    customerID          TEXT PRIMARY KEY NOT NULL,
    gender              TEXT NOT NULL,
    SeniorCitizen       INTEGER NOT NULL,
    Partner             TEXT NOT NULL,
    Dependents          TEXT NOT NULL,
    tenure              INTEGER NOT NULL,
    PhoneService        TEXT NOT NULL,
    MultipleLines       TEXT NOT NULL,
    InternetService     TEXT NOT NULL,
    OnlineSecurity      TEXT NOT NULL,
    OnlineBackup        TEXT NOT NULL,
    DeviceProtection    TEXT NOT NULL,
    TechSupport         TEXT NOT NULL,
    StreamingTV         TEXT NOT NULL,
    StreamingMovies     TEXT NOT NULL,
    Contract            TEXT NOT NULL,
    PaperlessBilling    TEXT NOT NULL,
    PaymentMethod       TEXT NOT NULL,
    MonthlyCharges      REAL NOT NULL,
    TotalCharges        REAL NOT NULL,
    Churn               TEXT NOT NULL
);
```

Six dedicated single-column B-Tree indexes (`idx_customers_churn`, `idx_customers_contract`, etc.) were created to accelerate aggregation and window partitioning.

---

## 3. Data Loading & Data Quality Audit

### Ingestion Methodology ([src/database_loader.py](file:///c:/Users/Sruthi/Documents/telco-churn-app/src/database_loader.py))
The ingestion pipeline reads `data/processed/telco_churn_cleaned.csv`, executes the DDL schema idempotently (`DROP TABLE IF EXISTS`), loads rows via parameterized batch insertion (`cursor.executemany`), and verifies row counts and primary-key constraints before committing.

### Data Hygiene & Validation Findings ([sql/01_data_quality.sql](file:///c:/Users/Sruthi/Documents/telco-churn-app/sql/01_data_quality.sql))
* **Total Records:** Exactly **7,043 rows** inserted and verified.
* **Primary Key Constraint:** **7,043 distinct `customerID` values**, 0 duplicates, 0 nulls.
* **Missing Values:** Zero NULL or unhandled values across all 21 columns.
* **Legitimate Zero Tenure Accounts:** Exactly 11 accounts have `tenure = 0` with `TotalCharges = 0.0`. These accounts represent brand-new signups onboarded in the current cycle who have not yet received their first bill. They are properly preserved rather than dropped or misclassified as missing data.
* **Domain Validity:** 0 invalid categorical entries; all numerical variables conform to physical non-negative boundaries.

---

## 4. Executive Business Intelligence KPIs

Executed via [sql/02_business_kpis.sql](file:///c:/Users/Sruthi/Documents/telco-churn-app/sql/02_business_kpis.sql) and exported to [reports/sql_results/business_kpis.csv](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/sql_results/business_kpis.csv):

```
┌────────────────────────────────────────────────────────────────────────┐
│               EXECUTIVE CHURN & FINANCIAL REVENUE SCORECARD            │
├───────────────────────────────────┬────────────────────┬───────────────┤
│ Metric Name                       │ SQL Output         │ Interpretation│
├───────────────────────────────────┼────────────────────┼───────────────┤
│ Total Customers                   │ 7,043 accounts     │ Baseline base │
│ Active Customers                  │ 5,174 accounts     │ 73.46%        │
│ Churned Customers                 │ 1,869 accounts     │ 26.54%        │
│ Overall Customer Churn Rate       │ 26.54%             │ Account churn │
│ Total Baseline Monthly MRR        │ $456,116.60        │ Recurring top │
│ Active Customer Monthly MRR       │ $316,985.75        │ 69.50% of MRR │
│ Churned Monthly MRR Exposure      │ $139,130.85        │ 30.50% of MRR │
│ MRR Churn Rate (%)                │ 30.50%             │ Revenue drag  │
│ Average Monthly Bill (Active)     │ $61.27 / month     │ Retained ARPU │
│ Average Monthly Bill (Churned)    │ $74.44 / month     │ Lost ARPU     │
│ Average Monthly Bill (Overall)    │ $64.76 / month     │ Portfolio ARPU│
│ Simple Annualized MRR Exposure    │ $1,669,570.20      │ Extrapolation │
└───────────────────────────────────┴────────────────────┴───────────────┘
```

### Critical Financial Finding: Disproportionate Revenue Drag
The SQL queries establish that while churned accounts represent **26.54%** of customer volume, they account for **30.50% of Monthly Recurring Revenue ($139,130.85)**. Churned customers pay **$13.17 more per month (+21.5%)** than retained customers ($74.44 vs. $61.27).

> [!IMPORTANT]
> **Methodological Note on Terminology:**  
> The metric `churned_customer_mrr_exposure` ($139,130.85) represents a **snapshot revenue exposure proxy**—the sum of monthly charges associated with accounts flagged as churned in this observation window. The annualized figure ($1,669,570.20) is a **simple 12-month mathematical extrapolation**, not a realized, historical, or audited annual revenue loss.

---

## 5. Churn Driver & Segment Analysis

Executed via [sql/03_churn_analysis.sql](file:///c:/Users/Sruthi/Documents/telco-churn-app/sql/03_churn_analysis.sql):

### A. Contract Commitment Type ([reports/sql_results/churn_by_contract.csv](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/sql_results/churn_by_contract.csv))
* **Month-to-month:** 3,875 accounts | 1,655 churned | **42.71% churn rate** | $122,981.35 churned MRR (88.4% of all lost MRR).
* **One year:** 1,473 accounts | 166 churned | **11.27% churn rate** | $11,940.60 churned MRR.
* **Two year:** 1,695 accounts | 48 churned | **2.83% churn rate** | $4,208.90 churned MRR.
* *Finding:* Month-to-month customers exhibit **15.1x higher churn propensity** than two-year contract holders.

### B. Internet Service Infrastructure ([reports/sql_results/churn_by_internet_service.csv](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/sql_results/churn_by_internet_service.csv))
* **Fiber optic:** 3,096 accounts | 1,297 churned | **41.89% churn rate** | $114,319.40 churned MRR (82.2% of all lost MRR).
* **DSL:** 2,421 accounts | 459 churned | **18.96% churn rate** | $22,467.25 churned MRR.
* **No internet service:** 1,526 accounts | 113 churned | **7.40% churn rate** | $2,344.20 churned MRR.

### C. Payment Rail Friction ([reports/sql_results/churn_by_payment_method.csv](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/sql_results/churn_by_payment_method.csv))
* **Electronic check:** 2,365 accounts | 1,071 churned | **45.29% churn rate** | $84,957.90 churned MRR (61.1% of all lost MRR).
* **Mailed check:** 1,612 accounts | 308 churned | **19.11% churn rate** | $16,778.60 churned MRR.
* **Bank transfer (automatic):** 1,544 accounts | 258 churned | **16.71% churn rate** | $19,655.70 churned MRR.
* **Credit card (automatic):** 1,522 accounts | 232 churned | **15.24% churn rate** | $17,738.65 churned MRR.

### D. Value-Added Service Shields
* **TechSupport:** Accounts without tech support churn at **41.64%** ($105,741.05 churned MRR) vs. **15.17%** ($23,733.95 churned MRR) for accounts with tech support.
* **OnlineSecurity:** Accounts without online security churn at **41.77%** ($106,606.35 churned MRR) vs. **14.61%** ($22,868.65 churned MRR) with security.

---

## 6. Two-Dimensional Tenure $\times$ Spend Segmentation Matrix

Recreated in SQL via [sql/04_customer_segmentation.sql](file:///c:/Users/Sruthi/Documents/telco-churn-app/sql/04_customer_segmentation.sql) and exported to [reports/sql_results/tenure_spend_segmentation.csv](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/sql_results/tenure_spend_segmentation.csv) and [reports/sql_results/advanced_segment_ranking.csv](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/sql_results/advanced_segment_ranking.csv):

| Rank | Tenure Tier | Spend Tier | Accounts | Churned | Churn % | Total MRR | Lost MRR | Share of Lost MRR | Cumulative % |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **New (0-12m)** | **High (>$70)** | **875** | **594** | **67.89%** | **$72,693.55** | **$49,871.30** | **35.84%** | **35.84%** |
| **2** | **Developing (13-36m)** | **High (>$70)** | **918** | **372** | **40.52%** | **$81,072.10** | **$33,376.55** | **23.99%** | **59.83%** |
| **3** | Mature (37-72m) | High (>$70) | 1,790 | 301 | 16.82% | $169,536.65 | $29,243.15 | 21.02% | 80.85% |
| **4** | New (0-12m) | Medium ($35-$70) | 670 | 291 | 43.43% | $35,868.85 | $15,562.20 | 11.19% | 92.04% |
| **5** | Developing (13-36m) | Medium ($35-$70) | 477 | 78 | 16.35% | $26,251.45 | $4,273.10 | 3.07% | 95.11% |
| **6** | New (0-12m) | Low (<=$35) | 641 | 152 | 23.71% | $14,067.35 | $3,520.75 | 2.53% | 97.64% |
| **7** | Mature (37-72m) | Medium ($35-$70) | 578 | 44 | 7.61% | $32,476.85 | $2,346.50 | 1.69% | 99.33% |
| **8** | Developing (13-36m) | Low (<=$35) | 461 | 24 | 5.21% | $10,065.10 | $599.95 | 0.43% | 99.76% |
| **9** | Mature (37-72m) | Low (<=$35) | 633 | 13 | 2.05% | $14,084.70 | $337.35 | 0.24% | 100.00% |

### Key Strategic Findings:
1. **Pareto Concentration:** The top 2 segments (`New / High Spend` and `Developing / High Spend`) account for **59.83% of all churned revenue** ($83,247.85/month) despite comprising only 25.5% of total subscribers.
2. **Inflection Cliff:** High-spend new customers churn at an unsustainable **67.89%**. Retention interventions must prioritize this group in the first 90 days.

---

## 7. Advanced SQL Concepts Demonstrated

Implemented in [sql/05_advanced_analytics.sql](file:///c:/Users/Sruthi/Documents/telco-churn-app/sql/05_advanced_analytics.sql):

1. **Common Table Expressions (CTEs):** Structured, readable modular query building across multi-stage aggregations.
2. **`DENSE_RANK()` Window Ranking:** Ranking contract types by churn risk and customer segments by revenue exposure without gaps.
3. **Cumulative Window Frames (`SUM() OVER (...)`):** Running total of revenue exposure (`ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`) to construct cumulative Pareto curves in SQL.
4. **Baseline Deviation Modeling:** Evaluating cohort churn rates against the companywide average ($26.54\%$) using an unbounded window ratio (`100.0 * SUM(cohort_churned) OVER () / SUM(cohort_customers) OVER ()`).
5. **Window Partitioning (`PARTITION BY`):** Calculating average charges within contract types (`AVG(MonthlyCharges) OVER (PARTITION BY Contract)`) and categorizing individual customers by price variance from their contract mean.
6. **Top-N Customer Ranking (`ROW_NUMBER()`):** Isolating the top 10 highest-spend churned customer accounts for executive audit and win-back campaigns.

---

## 8. Independent Validation Results (SQL vs. Pandas)

Executed via [src/validate_sql_results.py](file:///c:/Users/Sruthi/Documents/telco-churn-app/src/validate_sql_results.py):

* **Validation Strategy:** All 10 high-level KPIs and 27 segment metrics (count, churn %, churned MRR across 9 segments) were computed independently in Python using pure Pandas vector operations from `data/processed/telco_churn_cleaned.csv` and compared against direct SQL query outputs from `database/telco_churn.db`.
* **Tolerance:** $\pm 0.05$ (for rounding precision).
* **Summary Results:**
  * Total Metrics Audited: **37**
  * Total Metrics Passing: **37**
  * Maximum Observed Discrepancy: **0.0000**
  * **Result: 100% RECONCILIATION SUCCESS.**

---

## 9. Limitations of Cross-Sectional Snapshot Data

1. **Cross-Sectional vs. Longitudinal:** The dataset captures accounts at a single evaluation point. Churned customers represent historical exits recorded in the snapshot; active accounts represent survivors. We cannot calculate calendar retention cohorts (e.g., January 2024 cohort retained through December 2024) without transaction log timestamps.
2. **Survivorship Bias:** Long-tenure accounts (37–72 months) have already survived the high-hazard onboarding cliff. Their lower churn rate reflects survival selection rather than immunity.
3. **Unobserved Causal Drivers:** Technical support tickets, speed test throughput, and customer satisfaction (CSAT) are omitted from the schema.
