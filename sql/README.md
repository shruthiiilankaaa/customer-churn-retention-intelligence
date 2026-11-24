# SQL Modeling, Analytics & Business Query Engineering

This directory contains the production DDL schemas and analytical SQL query suite for the Telco Customer Churn & Retention Intelligence platform. All scripts are written in standard ANSI SQL and executed against the embedded SQLite database (`database/telco_churn.db`).

---

## Directory Inventory

| File | Purpose & Description |
| :--- | :--- |
| [schema.sql](schema.sql) | DDL script defining table `customers` (21 columns, primary key `customerID`, data types, and performance indexes). |
| [01_data_quality.sql](01_data_quality.sql) | 9 data hygiene, primary key uniqueness, null audit, zero-tenure consistency, and domain range validation queries. |
| [02_business_kpis.sql](02_business_kpis.sql) | Executive scorecard calculating 12 business and financial metrics (Total accounts, churn rate, baseline MRR, churned MRR exposure, ARPU by status, and simple annualized MRR extrapolation). |
| [03_churn_analysis.sql](03_churn_analysis.sql) | 10 multi-dimensional queries evaluating churn rates across contract types, internet services, payment rails, value-added services, tenure bands, and spend tiers. |
| [04_customer_segmentation.sql](04_customer_segmentation.sql) | Recreates the 3x3 Tenure × Spend risk matrix and ranks segments by lost MRR exposure using `DENSE_RANK()`. |
| [05_advanced_analytics.sql](05_advanced_analytics.sql) | 7 advanced analytical queries utilizing CTEs, window rankings, unbounded cumulative sums, baseline deviations, and `PARTITION BY` contract variance. |

---

## Execution Instructions

### 1. Ingest Dataset into SQLite Database
```bash
python src/database_loader.py
```
*Creates `database/telco_churn.db`, runs `schema.sql`, inserts all 7,043 rows, verifies row counts and primary key uniqueness, and prints an audit summary.*

### 2. Execute SQL Analytics & Export Deliverables
```bash
python src/run_sql_analytics.py
```
*Executes all 5 SQL files sequentially, displays readable query outputs in the terminal, and exports analytical CSVs to `reports/sql_results/`.*

### 3. Run Independent SQL vs. Pandas Reconciliation
```bash
python src/validate_sql_results.py
```
*Independently calculates all 37 core metrics in Pandas and compares them against SQLite database query outputs.*

### 4. Run Automated Test Suite
```bash
pytest tests/ -v
```
*Runs all 12 automated unit and integration tests across Phase 1 (Data Foundation) and Phase 3 (SQL Analytics).*

---

## Exported Result Deliverables (`reports/sql_results/`)

Running `python src/run_sql_analytics.py` generates:
* `business_kpis.csv`: Executive scorecard with 12 financial and volume metrics.
* `churn_by_contract.csv`: Retention breakdown by contract commitment.
* `churn_by_internet_service.csv`: Retention breakdown by internet infrastructure.
* `churn_by_payment_method.csv`: Retention breakdown by payment channel.
* `tenure_spend_segmentation.csv`: 3x3 Tenure × Spend segmentation matrix.
* `advanced_segment_ranking.csv`: DENSE_RANK() revenue exposure ranking.
