# 📡 Telco Customer Churn & Retention Intelligence

An enterprise-grade, end-to-end Customer Churn Analytics, Retention Intelligence, and Machine Learning Platform. 

This repository bridges **Production Machine Learning** (Streamlit + SHAP Explainability) with **Advanced Business Analytics** (Reproducible Data Foundation, Schema Validation, Cohort Analytics, and Executive Business Intelligence).

---

## 🏛️ System Architecture

The project is structured into two decoupled, high-performance layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│            TELCO CHURN & RETENTION INTELLIGENCE PLATFORM               │
├────────────────────────────────────┬───────────────────────────────────┤
│  Layer 1: Business Analytics &     │  Layer 2: Production ML &         │
│  Data Foundation (Analytics Layer) │  Inference (Application Layer)    │
├────────────────────────────────────┼───────────────────────────────────┤
│ • Raw Data Governance & Audit      │ • Pre-trained Random Forest Model │
│ • Automated Schema Validation      │ • Scikit-Learn Pipelines          │
│ • Reproducible Data Cleaning       │ • SHAP Explainability Waterfall   │
│ • SQL Modeling & Cohort Analytics  │ • Interactive Streamlit UI        │
│ • Executive BI & Retention Metrics │ • Single & Batch CSV Inference    │
└────────────────────────────────────┴───────────────────────────────────┘
```

---

## 📂 Repository Structure

```text
telco-churn-app/
├── data/
│   ├── raw/                           # Immutable raw storage (WA_Fn-UseC_-Telco-Customer-Churn.csv)
│   ├── processed/                     # Standardized analytical datasets (telco_churn_cleaned.csv)
│   └── README.md                      # Data documentation, dictionary, and acquisition instructions
├── database/
│   └── telco_churn.db                 # Embedded SQLite relational database (7,043 customer records)
├── models/
│   └── README.md                      # Model architecture documentation & artifact inventory
├── notebooks/
│   ├── 01_data_understanding.ipynb    # Data profiling & schema architecture
│   ├── 02_exploratory_data_analysis.ipynb # Churn drivers & behavioral analysis
│   ├── 03_revenue_and_customer_analysis.ipynb # Revenue exposure & 2D segmentation
│   ├── 04_statistical_analysis.ipynb  # Chi-square, Cramér's V, Mann-Whitney U, Cohen's d
│   └── README.md                      # Notebook inventory & execution guide
├── powerbi/
│   └── README.md                      # Power BI data models, DAX measures, and dashboard layouts
├── reports/
│   ├── excel/                         # Phase 4 Excel workbook, validation & documentation
│   │   ├── customer_churn_analysis.xlsx # Production 5-sheet financial & retention Excel model
│   │   ├── excel_validation.md        # Comprehensive benchmark reconciliation audit (41/41 PASS)
│   │   └── README.md                  # Excel workbook architecture, formula catalog & disclosures
│   ├── figures/                       # Publication-ready visualizations (10 figures)
│   ├── sql_results/                   # Exported analytical CSV deliverables (6 datasets)
│   ├── eda_findings.md                # Comprehensive Phase 2 EDA & behavioral findings report
│   ├── sql_analysis.md                # Comprehensive Phase 3 SQL analytics & KPI report
│   └── README.md                      # Reports and deliverables catalog
├── sql/
│   ├── schema.sql                     # DDL table creation and performance indexing
│   ├── 01_data_quality.sql            # Data hygiene, primary key uniqueness & domain checks
│   ├── 02_business_kpis.sql           # Executive KPI scorecard & ARPU revenue metrics
│   ├── 03_churn_analysis.sql          # Multi-dimensional churn driver query suite
│   ├── 04_customer_segmentation.sql   # 3x3 Tenure × Spend matrix & DENSE_RANK revenue ranking
│   ├── 05_advanced_analytics.sql      # CTEs, window running sums, PARTITION BY contract variance
│   └── README.md                      # SQL execution instructions & query guide
├── src/
│   ├── __init__.py                    # Package exports
│   ├── data_loader.py                 # Safe ingestion & missing dataset handling
│   ├── data_validation.py             # Schema, type, range, and categorical validation suite
│   ├── data_cleaning.py               # Reproducible cleaning & TotalCharges whitespace resolution
│   ├── database_utils.py              # SQLite connection, script & query utilities
│   ├── database_loader.py             # SQLite ingestion pipeline & primary-key audit
│   ├── run_sql_analytics.py           # SQL runner & result CSV export engine
│   ├── validate_sql_results.py        # Independent SQL vs. Pandas metric reconciliation
│   ├── build_excel_analysis.py        # Phase 4 Excel workbook generation engine
│   ├── validate_excel_results.py      # Independent Excel vs. Pandas metric reconciliation
│   └── pipeline.py                    # End-to-end data foundation execution runner
├── tests/
│   ├── test_data_foundation.py        # Automated test suite for data validation and cleaning
│   ├── test_sql_analytics.py          # Automated test suite for SQL database, KPIs & validation
│   └── test_excel_deliverables.py     # Automated test suite for Phase 4 Excel workbook & KPIs
├── model_metadata.joblib              # Serialized feature lists & target definitions (production)
├── preprocessor.joblib                # Fitted Scikit-Learn preprocessing pipeline (production)
├── telco_final_model.joblib           # Trained Random Forest classifier (production)
├── streamlit_app.py                   # Streamlit web application & SHAP interface
├── requirements.txt                   # Environment dependencies
└── README.md                          # Project documentation
```

---

## 📊 Dataset Foundation & Acquisition

The analytics layer is built upon the **IBM Telco Customer Churn** dataset (7,043 customer accounts, 21 variables).

### Acquiring the Dataset
1. Download `WA_Fn-UseC_-Telco-Customer-Churn.csv` from [Kaggle Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) or [IBM Business Analytics](https://community.ibm.com/community/user/businessanalytics/blogs/steven-macko/2019/07/11/telco-customer-churn).
2. Save the CSV into `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv`.
3. Read the complete data dictionary and specifications in [data/README.md](data/README.md).

### Data Cleaning Methodology
- **`TotalCharges` Whitespace Handling**: In the raw dataset, 11 records have blank whitespace `" "` for `TotalCharges`. All 11 records correspond to `tenure = 0` (brand new customers who have not yet received their first invoice). Rather than discarding these records, the pipeline assigns `TotalCharges = 0.0` and casts the column to `float64`.
- **String Sanitation**: All text features are stripped of whitespace padding.
- **Identity Preservation**: The primary key `customerID` is strictly preserved unaltered across all raw and processed tables.
- **Data Types Enforced**: `tenure` (`int64`), `MonthlyCharges` (`float64`), `TotalCharges` (`float64`), `SeniorCitizen` (`int64`).

---

## 🚀 Execution Instructions

### 1. Run Data Foundation Pipeline (Ingestion, Validation, Cleaning)
```bash
python src/pipeline.py
```

### 2. Ingest SQLite Database & Execute SQL Analytics
```bash
# Ingest cleaned data into SQLite database
python src/database_loader.py

# Execute full SQL analytical query suite and export result CSVs
python src/run_sql_analytics.py

# Verify independent SQL vs. Pandas metric reconciliation
python src/validate_sql_results.py
```

### 3. Generate & Validate Phase 4 Excel Business Model
```bash
# Build the production 5-sheet Excel workbook with tables, formulas, and charts
python src/build_excel_analysis.py

# Run independent Excel reconciliation audit (41 automated checks)
python src/validate_excel_results.py
```

### 4. Run Automated Pytest Suite (Data Foundation, SQL Analytics & Excel Deliverables)
```bash
pytest tests/ -v
```

### 5. Launch Streamlit Prediction & SHAP Application
```bash
streamlit run streamlit_app.py
```

---

## 🧠 Machine Learning & Inference Layer

The application layer features an end-to-end ML prediction engine trained on balanced customer data.

### Model Benchmarks

| Model | F1 Score | ROC-AUC | Status |
| :--- | :---: | :---: | :--- |
| **Logistic Regression** | ~0.61 | ~0.84 | Baseline evaluated |
| **XGBoost** | ~0.58 | ~0.81 | Baseline evaluated |
| **Random Forest (Final)** | ~0.53 | ~0.82 | Selected & Deployed (`telco_final_model.joblib`) |

### Streamlit Features
- **Single Customer Prediction**: Dynamic calculation of `SpendingRate`, `TenureGroup`, and `ContractMonths` with instant churn probability output.
- **SHAP Waterfall Plots**: Transparent, local feature importance powered by `shap.TreeExplainer`.
- **Batch CSV Scoring**: Upload customer lists, score churn probabilities, and download enriched CSVs.

---

## 🛠️ Technology Stack

- **Analytics & ETL**: Python 3.11, Pandas, NumPy
- **Testing & Quality Assurance**: Pytest
- **Machine Learning**: Scikit-Learn, Joblib
- **Model Interpretability**: SHAP (SHapley Additive exPlanations)
- **Visualization & UI**: Streamlit, Matplotlib, Seaborn
