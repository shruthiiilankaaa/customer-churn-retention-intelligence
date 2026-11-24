# Exploratory Data Analysis & Customer Behavior Notebooks

This directory contains executable, fully verified Jupyter notebooks covering the Phase 2 exploratory data analysis and customer behavior investigation for the Telco Customer Churn & Retention Intelligence project.

Each notebook has been executed against `data/processed/telco_churn_cleaned.csv` with zero errors. All cell outputs, statistical summaries, and visual plots are saved within the notebooks and referenced in [reports/eda_findings.md](../reports/eda_findings.md).

---

## Notebook Inventory

### 1. [01_data_understanding.ipynb](01_data_understanding.ipynb)
- **Objective:** Dataset profiling, schema architecture, and data hygiene audit.
- **Key Analyses:**
  - 21-feature schema breakdown across identity, demographics, services, billing, and financials.
  - Primary key uniqueness constraint verification on `customerID` (7,043 unique, 0 duplicates).
  - Target variable analysis (`Churn`: 73.46% active vs. 26.54% churned).
  - Statistical profiling of numerical distributions (`tenure`, `MonthlyCharges`, `TotalCharges`).
  - Categorical cardinalities and value distributions.
- **Figures Generated:** `01_churn_distribution.png`, `01_numerical_distributions.png`.

### 2. [02_exploratory_data_analysis.ipynb](02_exploratory_data_analysis.ipynb)
- **Objective:** Deep-dive investigation into behavioral, service, and contract drivers of customer churn.
- **Key Analyses:**
  - Contractual commitment: Month-to-month (42.71% churn) vs. One-year (11.27%) vs. Two-year (2.83%).
  - Tenure hazard curve: Inflection analysis showing a 53.0% churn rate in months 0–6.
  - Internet infrastructure: Fiber optic churn rate (41.89%) vs. DSL (18.96%) vs. No internet (7.40%).
  - Payment channel friction: Electronic check (45.29% churn) vs. Automated credit card/bank transfer (~15–16%).
  - Value-added retention anchors: TechSupport and OnlineSecurity reducing churn from ~41.7% to ~14.6%–15.2%.
  - Demographic breakdowns: Seniors (41.68%), Partners (19.66%), Dependents (15.45%), and Gender neutrality.
- **Figures Generated:** `02_churn_by_contract_and_internet.png`, `02_tenure_and_cohort_churn.png`, `02_charges_boxplots.png`, `02_churn_by_payment_channel.png`, `02_services_churn_comparison.png`.

### 3. [03_revenue_and_customer_analysis.ipynb](03_revenue_and_customer_analysis.ipynb)
- **Objective:** Top-line financial accounting, revenue-at-risk exposure, and 2D customer risk segmentation.
- **Key Analyses:**
  - Monthly Recurring Revenue (MRR) breakdown: $456,116.60 total baseline MRR.
  - Revenue at risk: $139,130.85/month lost to churn (30.50% of MRR; $1.67M annualized ARR).
  - Disproportionate revenue drag: 26.54% churned accounts drive 30.50% of revenue loss ($74.44 avg bill for churned vs. $61.27 for retained).
  - Two-dimensional customer segmentation matrix: Tenure Tiers (`New: 0-12m`, `Developing: 13-36m`, `Mature: 37-72m`) × Spend Tiers (`Low: <=$35`, `Medium: $35-$70`, `High: >$70`).
  - Critical vulnerability segment: `New / High Spend` (67.89% churn rate, $49,871.30 monthly revenue lost).
- **Figures Generated:** `03_revenue_exposure_comparison.png`, `03_segmentation_heatmaps.png`.

### 4. [04_statistical_analysis.ipynb](04_statistical_analysis.ipynb)
- **Objective:** Inferential statistical testing, non-parametric comparisons, and standardized effect sizes.
- **Key Analyses:**
  - Chi-Square ($\chi^2$) tests of independence & Cramér's V across all 16 categorical predictors.
  - Ranking association strength: `Contract` (V = 0.4101), `OnlineSecurity` (V = 0.3474), `TechSupport` (V = 0.3429).
  - Identification of non-significant predictors: `gender` ($p = 0.487$) and `PhoneService` ($p = 0.339$).
  - Distributional normality diagnostics (D'Agostino-Pearson $K^2$ rejecting Gaussian normality for tenure, charges).
  - Non-parametric Mann-Whitney U tests and Welch's t-tests.
  - Standardized effect sizes: Cohen's d for tenure ($d = -0.852$, large) and monthly charges ($d = +0.446$, medium).
  - Methodological critique: Correlation vs. causation, statistical vs. business significance, and cross-sectional snapshot limitations.
- **Figures Generated:** `04_cramers_v_ranking.png`.
