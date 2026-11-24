# Telco Customer Churn & Retention Intelligence: Comprehensive EDA & Behavioral Findings Report

**Project:** Telco Customer Churn & Retention Intelligence  
**Phase:** Phase 2 — Exploratory Data Analysis & Customer Behavior Analysis  
**Data Source:** `data/processed/telco_churn_cleaned.csv` (7,043 customer accounts, 21 variables)  
**Status:** All 4 analytical notebooks built, executed, and statistically verified.

---

## 1. Executive Summary

This exploratory data analysis establishes a data-driven foundation for customer retention at Telco. By evaluating customer demographics, account tenure, subscribed telephony and internet services, contractual terms, payment channels, and financial metrics across 7,043 subscriber records, we uncover critical business vulnerabilities.

Key findings indicate that **churn is heavily concentrated in specific customer segments and lifecycle phases**:
* **Baseline Churn Volume:** 1,869 customers churned, representing an overall churn rate of **26.54%**.
* **Disproportionate Financial Drag:** Churned customers account for 26.54% of accounts but **30.50% of total Monthly Recurring Revenue (MRR)** ($139,130.85/month, or **$1,669,570.20 annualized ARR at risk**). This occurs because churners pay an average monthly bill of **$74.44**, compared to **$61.27** for retained customers.
* **The High-Spend Onboarding Hazard:** New customers (tenure $\le 12$ months) paying high monthly charges ($> \$70/\text{month}$) experience an alarming **67.89% churn rate**, generating **$49,871.30/month in lost revenue** (35.8% of all churned dollars).
* **Primary Structural Levers:** Contractual terms (Month-to-month: 42.7% churn vs. Two-year: 2.8%), Internet service (Fiber optic: 41.9% vs. DSL: 19.0%), Payment rails (Electronic check: 45.3% vs. Automated credit card/bank transfer: ~15.2%–16.7%), and Tech support / Online security bundles (41.6% churn without support vs. 15.2% with support).
* **Non-Factors:** Customer gender ($p = 0.487$) and standalone landline phone service ($p = 0.339$) show **no statistically significant relationship** with churn and should not be used for retention targeting.

---

## 2. Verified Analytical Findings by Domain

### A. Dataset Dimensions & Baseline Hygiene ([01_data_understanding.ipynb](file:///c:/Users/Sruthi/Documents/telco-churn-app/notebooks/01_data_understanding.ipynb))
* **Population:** Exactly **7,043 unique accounts**, with primary key uniqueness verified ($0$ duplicates, $0$ null identifiers).
* **Completeness:** 100% complete dataset post-cleaning. All 11 missing `TotalCharges` records in raw data were confirmed to be new signups (`tenure = 0`) and imputed to $0.0$.
* **Class Balance:**
  * Active / Retained: 5,174 accounts (73.46%)
  * Churned: 1,869 accounts (26.54%)
* **Tenure Distribution:** Bimodal distribution peaking at month 1 (new onboarding) and month 72 (long-term loyalists). Mean tenure is 32.37 months; median is 29.0 months.
* **Charge Metrics:**
  * `MonthlyCharges`: Mean \$64.76, Median \$70.35, Min \$18.25, Max \$118.75.
  * `TotalCharges`: Right-skewed (+0.96 skewness), Mean \$2,279.73, Median \$1,394.55, Max \$8,684.80.

### B. Churn Driver Investigation ([02_exploratory_data_analysis.ipynb](file:///c:/Users/Sruthi/Documents/telco-churn-app/notebooks/02_exploratory_data_analysis.ipynb))

```
┌────────────────────────────────────────────────────────────────────────┐
│               CHURN RATE BY CONTRACT TYPE AND TENURE                   │
├───────────────────────┬──────────────┬───────────────┬─────────────────┤
│ Contract Type         │ Total Accts  │ Churned Accts │ Churn Rate (%)  │
├───────────────────────┼──────────────┼───────────────┼─────────────────┤
│ Month-to-month        │ 3,875        │ 1,655         │ 42.71%          │
│ One year              │ 1,473        │ 166           │ 11.27%          │
│ Two year              │ 1,695        │ 48            │ 2.83%           │
└───────────────────────┴──────────────┴───────────────┴─────────────────┘
```

1. **Contractual Structure:**
   * Month-to-month contracts represent 55.0% of the customer base but generate **88.6% of all churn events** (1,655 out of 1,869 churned accounts).
   * Two-year contract holders have an attrition rate of only 2.83%.

2. **Tenure Hazard Curve:**
   * **0–6 Months:** Churn rate is **53.0%** (critical onboarding hazard).
   * **7–12 Months:** Churn rate is **34.7%**.
   * **13–24 Months:** Churn rate drops to **28.6%**.
   * **25–48 Months:** Churn rate stabilizes at **17.8%**.
   * **49–72 Months:** Churn rate declines to **9.5%**.

3. **Internet Infrastructure:**
   * **Fiber Optic:** 3,096 subscribers; **41.89% churn rate** (1,297 churned).
   * **DSL:** 2,421 subscribers; **18.96% churn rate** (459 churned).
   * **No Internet Service:** 1,526 subscribers; **7.40% churn rate** (113 churned).
   * *Diagnostic:* Fiber optic carries the highest monthly fees (~$80–$118) but experiences extreme churn when delivered without technical support or premium reliability.

4. **Payment Channels & Friction:**
   * **Electronic Check:** 2,365 subscribers; **45.29% churn rate** (1,071 churned).
   * **Mailed Check:** 1,612 subscribers; **19.11% churn rate** (308 churned).
   * **Bank Transfer (Automatic):** 1,544 subscribers; **16.71% churn rate** (258 churned).
   * **Credit Card (Automatic):** 1,522 subscribers; **15.24% churn rate** (232 churned).
   * *Mechanism:* Automatic payment channels provide billing inertia, while manual/electronic checks force conscious monthly evaluation.

5. **Value-Added Support & Security:**
   * **Tech Support:** Customers without TechSupport churn at **41.64%** vs. **15.17%** for those with it.
   * **Online Security:** Customers without OnlineSecurity churn at **41.77%** vs. **14.61%** for those with it.
   * **Device Protection & Cloud Backup:** Reduce churn from ~39% to ~21–22%.
   * Add-on technical services act as vital retention anchors.

6. **Demographic Patterns:**
   * **Senior Citizens:** Experience **41.68% churn** (vs. 23.61% for non-seniors).
   * **Partners & Dependents:** Protective factors. Customers with partners churn at 19.66% (vs. 32.96% single); customers with dependents churn at 15.45% (vs. 31.28% without dependents).
   * **Gender:** Male (26.16%) vs. Female (26.92%) — statistically indistinguishable.

---

### C. Revenue Exposure & Risk Segmentation ([03_revenue_and_customer_analysis.ipynb](file:///c:/Users/Sruthi/Documents/telco-churn-app/notebooks/03_revenue_and_customer_analysis.ipynb))

```
┌────────────────────────────────────────────────────────────────────────┐
│                  TOP-LINE FINANCIAL CHURN AUDIT                        │
├───────────────────────────────────┬────────────────────┬───────────────┤
│ Financial Metric                  │ Value (USD)        │ Share (%)     │
├───────────────────────────────────┼────────────────────┼───────────────┤
│ Total Baseline MRR                │ $456,116.60        │ 100.00%       │
│ Active / Retained Customer MRR    │ $316,985.75        │ 69.50%        │
│ Churned MRR (Revenue at Risk)     │ $139,130.85        │ 30.50%        │
│ Annualized ARR at Risk            │ $1,669,570.20      │ —             │
│ Average Monthly Bill (Retained)   │ $61.27 / month     │ —             │
│ Average Monthly Bill (Churned)    │ $74.44 / month     │ (+21.5%)      │
└───────────────────────────────────┴────────────────────┴───────────────┘
```

#### Two-Dimensional Segmentation Matrix (Tenure Tiers × Spend Tiers)

Customers are categorized across Tenure (`New: 0-12m`, `Developing: 13-36m`, `Mature: 37-72m`) and Spend (`Low: <= $35`, `Medium: $35-$70`, `High: > $70`):

| Tenure Tier | Spend Tier | Accounts | Churned | Churn % | Total MRR | Lost MRR | % of Lost MRR |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **New (0-12m)** | **High (>$70)** | **875** | **594** | **67.89%** | **$72,693.55** | **$49,871.30** | **35.84%** |
| Developing (13-36m) | High (>$70) | 918 | 372 | 40.52% | $81,072.10 | $33,376.55 | 23.99% |
| Mature (37-72m) | High (>$70) | 1,790 | 301 | 16.82% | $169,536.65 | $29,243.15 | 21.02% |
| New (0-12m) | Medium ($35-$70) | 670 | 291 | 43.43% | $35,868.85 | $15,562.20 | 11.19% |
| Developing (13-36m) | Medium ($35-$70) | 477 | 78 | 16.35% | $26,251.45 | $4,273.10 | 3.07% |
| New (0-12m) | Low (<=$35) | 641 | 152 | 23.71% | $14,067.35 | $3,520.75 | 2.53% |
| Mature (37-72m) | Medium ($35-$70) | 578 | 44 | 7.61% | $32,476.85 | $2,346.50 | 1.69% |
| Developing (13-36m) | Low (<=$35) | 461 | 24 | 5.21% | $10,065.10 | $599.95 | 0.43% |
| Mature (37-72m) | Low (<=$35) | 633 | 13 | 2.05% | $14,084.70 | $337.35 | 0.24% |

**Key Takeaway:** The top two vulnerability segments (`New / High Spend` and `Developing / High Spend`) account for **$83,247.85/month (59.8% of all lost revenue)** despite representing only 25.5% of total subscribers.

---

### D. Inferential Statistics & Hypothesis Testing ([04_statistical_analysis.ipynb](file:///c:/Users/Sruthi/Documents/telco-churn-app/notebooks/04_statistical_analysis.ipynb))

#### 1. Categorical Features: Chi-Square ($\chi^2$) & Cramér's V Ranking

| Feature | $\chi^2$ Statistic | d.o.f. | p-value | Cramér's V | Association Strength |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`Contract`** | **1,184.60** | **2** | **< 1e-10** | **0.4101** | **Strong (Top Predictor)** |
| **`OnlineSecurity`** | **850.00** | **2** | **< 1e-10** | **0.3474** | **Strong** |
| **`TechSupport`** | **828.20** | **2** | **< 1e-10** | **0.3429** | **Strong** |
| **`InternetService`** | **732.31** | **2** | **< 1e-10** | **0.3225** | **Strong** |
| **`PaymentMethod`** | **648.14** | **3** | **< 1e-10** | **0.3034** | **Strong** |
| `OnlineBackup` | 601.81 | 2 | < 1e-10 | 0.2923 | Moderate |
| `DeviceProtection` | 558.42 | 2 | < 1e-10 | 0.2816 | Moderate |
| `StreamingMovies` | 375.66 | 2 | < 1e-10 | 0.2310 | Moderate |
| `StreamingTV` | 374.20 | 2 | < 1e-10 | 0.2305 | Moderate |
| `PaperlessBilling` | 258.28 | 1 | < 1e-10 | 0.1915 | Moderate |
| `Dependents` | 189.13 | 1 | < 1e-10 | 0.1639 | Moderate |
| `SeniorCitizen` | 159.43 | 1 | < 1e-10 | 0.1505 | Moderate |
| `Partner` | 158.73 | 1 | < 1e-10 | 0.1501 | Moderate |
| `MultipleLines` | 11.33 | 2 | 0.0035 | 0.0401 | Trivial ($V < 0.05$) |
| `PhoneService` | 0.92 | 1 | 0.3388 | 0.0114 | **Not Significant ($p \ge 0.05$)** |
| `gender` | 0.48 | 1 | 0.4865 | 0.0083 | **Not Significant ($p \ge 0.05$)** |

#### 2. Numerical Features: Normality & Two-Sample Comparisons

Normality tests (D'Agostino-Pearson $K^2$) demonstrated that `tenure` ($p < 1\text{e-}10$), `MonthlyCharges` ($p < 1\text{e-}10$), and `TotalCharges` ($p < 1\text{e-}10$) violate Gaussian normality. We report non-parametric Mann-Whitney U along with Welch's t-test and Cohen's d:

| Feature | Retained Mean | Churned Mean | Mann-Whitney U | U p-value | Welch t-stat | Cohen's d | Magnitude |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`tenure`** | 37.57 mos | 17.98 mos | 2,515,538 | < 1e-10 | -34.82 | **-0.852** | **Large** |
| **`MonthlyCharges`** | $61.27 | $74.44 | 6,003,126 | < 1e-10 | 18.41 | **+0.446** | **Medium** |
| **`TotalCharges`** | $2,549.76 | $1,531.80 | 3,381,224 | < 1e-10 | -18.71 | **-0.458** | **Medium** |

---

## 3. Methodological Rigor & Critical Analytical Evaluation

1. **Correlation $\neq$ Causation:**
   * **Month-to-month contracts ($V = 0.4101$):** Customers do not churn *because* they signed a month-to-month contract. Rather, customers who lack certainty, are testing service quality, or anticipate moving intentionally choose month-to-month terms. Simply mandating long contracts without addressing onboarding friction will likely impair customer acquisition.
   * **Electronic Check Payments ($V = 0.3034$):** Paying by electronic check requires active monthly intervention and generates payment friction (e.g., failed bank clearing, forgotten manual logins). Conversely, credit cards provide automated billing inertia.

2. **Statistical Significance vs. Business Importance:**
   * Because $N = 7,043$, features like `MultipleLines` achieve $p = 0.0035$ despite a negligible Cramér's V ($0.0401$). In executive reporting, we distinguish statistical confidence from operational materiality.

3. **Analytical Limitations:**
   * **Cross-Sectional Snapshot:** The dataset captures accounts at a single snapshot in time. We observe who has churned recently, but cannot construct true longitudinal retention cohort curves across calendar sign-up cohorts.
   * **Survivorship Bias:** Long-tenure subscribers (48–72 months) represent surviving accounts who have already navigated the high-attrition onboarding cliff.
   * **Missing Operational Signals:** Operational metrics such as network ticket volume, speed test throughput, and customer satisfaction scores (CSAT/NPS) are absent from this public schema.

---

## 4. Business Questions Answered

| # | Business Question | Data-Backed Answer |
|---|---|---|
| 1 | **What is the overall churn rate of our subscriber base?** | **26.54%** (1,869 churned customers out of 7,043 total accounts). |
| 2 | **What is the recurring monthly revenue lost to churn?** | **$139,130.85 per month** (30.50% of total Monthly Recurring Revenue; $1.67M annualized). |
| 3 | **Are churned customers lower-value or higher-value subscribers?** | **Higher-value.** Churned customers pay an average of **$74.44/month**, which is **21.5% higher** than retained customers ($61.27/month). |
| 4 | **When during the customer lifecycle is churn risk highest?** | **In the first 6 months.** Churn reaches **53.0%** in months 0–6 and drops to 9.5% after month 48. |
| 5 | **Which product line exhibits the highest attrition?** | **Fiber Optic Internet.** Churn is **41.89%** (vs. 18.96% for DSL), driven by high costs without bundled tech support. |
| 6 | **Which payment channel poses the greatest collection and retention risk?** | **Electronic Check.** Accounts paying via electronic check churn at **45.29%**, compared to 15.2% on automated credit card billing. |
| 7 | **Do value-added services protect customer accounts?** | **Yes, dramatically.** Subscribing to `TechSupport` or `OnlineSecurity` reduces churn from ~41.7% down to **~14.6%–15.2%** (a 64% relative reduction). |
| 8 | **Does gender influence churn propensity?** | **No.** Gender differences are statistically non-significant ($\chi^2 = 0.48, p = 0.487$). Retention programs should not segment by gender. |

---

## 5. Potential KPIs for Upcoming SQL & Power BI Phases

The findings from Phase 2 establish the core metric catalog for the upcoming dimensional modeling (SQL) and executive reporting (Power BI) phases:

### A. Executive & Financial KPIs
* **Overall Customer Churn Rate (%):** $\frac{\text{Churned Customers}}{\text{Total Customers}} \times 100$
* **Monthly Recurring Revenue (MRR) at Risk ($):** $\sum \text{MonthlyCharges of Churned Customers}$
* **MRR Churn Rate (%):** $\frac{\text{Churned MRR}}{\text{Total Baseline MRR}} \times 100$
* **Annualized Revenue Exposure (ARR Lost) ($):** $\text{Churned MRR} \times 12$
* **Revenue Disparity Ratio:** $\frac{\text{Average Monthly Charge (Churned)}}{\text{Average Monthly Charge (Retained)}}$

### B. Segment & Lifecycle KPIs
* **Early-Tenure Churn Rate (0–6 Months) (%):** Churn rate for customers with $\text{tenure} \le 6$.
* **Contract Risk Ratio:** $\frac{\text{Month-to-Month Churn Rate}}{\text{Two-Year Churn Rate}}$ (Baseline: 15.1x)
* **High-Value New Customer Vulnerability (%):** Churn rate for $\text{tenure} \le 12 \text{ months} \cap \text{MonthlyCharges} > \$70$.
* **Support Attachment Rate (%):** Percentage of broadband subscribers with active `TechSupport` or `OnlineSecurity`.
* **Automated Payment Penetration Rate (%):** Percentage of customers using automated Credit Card or Bank Transfer payment rails.

---

## 6. Catalog of Generated Visualizations

All high-resolution figures have been verified and saved to `reports/figures/`:

| Figure Filename | Notebook Source | Content Description |
| :--- | :--- | :--- |
| [01_churn_distribution.png](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/figures/01_churn_distribution.png) | Notebook 1 | Snapshot customer churn volume bar chart and class proportion donut chart. |
| [01_numerical_distributions.png](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/figures/01_numerical_distributions.png) | Notebook 1 | Histograms and KDE curves with mean/median markers for tenure, monthly, and total charges. |
| [02_churn_by_contract_and_internet.png](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/figures/02_churn_by_contract_and_internet.png) | Notebook 2 | Grouped comparison of churn rate across contract types and internet service types. |
| [02_tenure_and_cohort_churn.png](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/figures/02_tenure_and_cohort_churn.png) | Notebook 2 | Bivariate tenure density curves and cohort-level churn rate progression. |
| [02_charges_boxplots.png](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/figures/02_charges_boxplots.png) | Notebook 2 | Boxplot comparisons for monthly charges and cumulative total charges by churn status. |
| [02_churn_by_payment_channel.png](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/figures/02_churn_by_payment_channel.png) | Notebook 2 | Horizontal bar chart of customer churn rate by payment mechanism. |
| [02_services_churn_comparison.png](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/figures/02_services_churn_comparison.png) | Notebook 2 | Bar chart detailing churn reduction associated with tech support, security, and backup. |
| [03_revenue_exposure_comparison.png](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/figures/03_revenue_exposure_comparison.png) | Notebook 3 | Customer headcount share vs. MRR share comparison and average bill comparison. |
| [03_segmentation_heatmaps.png](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/figures/03_segmentation_heatmaps.png) | Notebook 3 | Dual heatmaps visualizing churn rate (%) and lost MRR ($) across the 3x3 Tenure × Spend matrix. |
| [04_cramers_v_ranking.png](file:///c:/Users/Sruthi/Documents/telco-churn-app/reports/figures/04_cramers_v_ranking.png) | Notebook 4 | Horizontal bar chart ranking all 16 categorical predictors by Cramér's V effect size. |
