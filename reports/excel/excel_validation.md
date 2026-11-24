# Excel Analytics Validation & Benchmark Reconciliation Report

**Project**: Customer Churn & Retention Intelligence  
**Phase**: Phase 4 — Excel Business Analysis & Interactive Dashboard  
**Artifact**: [`reports/excel/customer_churn_analysis.xlsx`](file:///C:/Users/Sruthi/Documents/telco-churn-app/reports/excel/customer_churn_analysis.xlsx)  
**Source Dataset**: [`data/processed/telco_churn_cleaned.csv`](file:///C:/Users/Sruthi/Documents/telco-churn-app/data/processed/telco_churn_cleaned.csv) (7,043 rows $\times$ 21 columns)  
**Audit Date**: November 2026 (Updated & Category-Level Reconciled)  
**Status**: **PASS (55/55 Automated Checks Passed | 19/19 Pytest Suite Passed)**

---

## 1. Executive Summary & Root Cause Analysis

This report documents the exhaustive reconciliation of the Phase 4 Excel workbook [`reports/excel/customer_churn_analysis.xlsx`](file:///C:/Users/Sruthi/Documents/telco-churn-app/reports/excel/customer_churn_analysis.xlsx) against the established Phase 3 SQLite database and Pandas ground truth.

### Discrepancy Investigation & Root Cause
During quality assurance review, an audit identified that while overall churned MRR exposure was correctly calculated as **$139,130.85**, several category-level values displayed on the Dashboard feeder tables did not match Phase 3 SQL results.

- **Root Cause**: The workbook generator script [`src/build_excel_analysis.py`](file:///C:/Users/Sruthi/Documents/telco-churn-app/src/build_excel_analysis.py) previously contained static Python tuples hardcoded into `build_dashboard_sheet()` using unverified draft approximations (e.g., $122,981.35 for Month-to-month instead of $120,847.10, and $84,957.90 for Electronic check instead of $84,288.75).
- **Remediation**: The workbook generator was re-engineered so that all summary tables, cross-tabulations, and KPI scorecards are **dynamically computed directly from the source dataset** using Pandas. Zero figures are hardcoded.
- **Verification**: The automated test harness [`src/validate_excel_results.py`](file:///C:/Users/Sruthi/Documents/telco-churn-app/src/validate_excel_results.py) was expanded with **14 category-level reconciliation checks**, confirming exact agreement across every single category.

---

## 2. Core Portfolio Benchmark Reconciliation

| Metric Description | Python / SQL Benchmark | Excel Workbook Value | Cell / Location | Absolute Difference | Tolerance Threshold | Validation Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Total Customers** | 7,043 | 7,043 | `Dashboard!A5` | 0 | Exact Match ($\Delta = 0$) | **PASS** |
| **Active Customers** | 5,174 | 5,174 | `Formula_Analysis!C9` | 0 | Exact Match ($\Delta = 0$) | **PASS** |
| **Churned Customers** | 1,869 | 1,869 | `Dashboard!C5` | 0 | Exact Match ($\Delta = 0$) | **PASS** |
| **Overall Churn Rate** | 26.54% | 26.54% | `Dashboard!E5` | 0.0000% | $\pm 0.05\%$ | **PASS** |
| **Total Baseline MRR** | \$456,116.60 | \$456,116.60 | `Dashboard!G5` | \$0.00 | $\pm \$0.05$ | **PASS** |
| **Active Customer MRR** | \$316,985.75 | \$316,985.75 | `Formula_Analysis!Total` | \$0.00 | $\pm \$0.05$ | **PASS** |
| **Churned MRR Exposure** | \$139,130.85 | \$139,130.85 | `Dashboard!I5` | \$0.00 | $\pm \$0.05$ | **PASS** |
| **MRR Exposure Rate** | 30.50% | 30.50% | `Dashboard!K5` | 0.0000% | $\pm 0.05\%$ | **PASS** |
| **Active Customer ARPU** | \$61.27/mo | \$61.27/mo | `Formula_Analysis!J9` | \$0.00 | $\pm \$0.05$ | **PASS** |
| **Churned Customer ARPU** | \$74.44/mo | \$74.44/mo | `Formula_Analysis!I9` | \$0.00 | $\pm \$0.05$ | **PASS** |
| **Annualized MRR Exposure** | \$1,669,570.20 | \$1,669,570.20 | Disclosures & Insights | \$0.00 | $\pm \$0.05$ | **PASS** |

---

## 3. Category-Level Churned MonthlyCharges Reconciliation

### A. Contract Commitment Terms

| Contract Type | Customer Count | Churned Count | Churn Rate | Total MRR ($) | Churned MRR ($) (SQL Benchmark) | Excel Dashboard (`Dashboard!C9:C11`) | Delta | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Month-to-month** | 3,875 | 1,655 | 42.71% | \$257,294.15 | **\$120,847.10** | **\$120,847.10** | \$0.00 | **PASS** |
| **One year** | 1,473 | 166 | 11.27% | \$95,816.60 | **\$14,118.45** | **\$14,118.45** | \$0.00 | **PASS** |
| **Two year** | 1,695 | 48 | 2.83% | \$103,005.85 | **\$4,165.30** | **\$4,165.30** | \$0.00 | **PASS** |
| **Contract Total** | **7,043** | **1,869** | **26.54%** | **\$456,116.60** | **\$139,130.85** | **\$139,130.85** | **\$0.00** | **PASS** |

*Key Insight*: Month-to-month contracts generate **86.86%** of companywide lost MRR ($120,847.10 / $139,130.85).

### B. Payment Rails

| Payment Rail | Customer Count | Churned Count | Churn Rate | Total MRR ($) | Churned MRR ($) (SQL Benchmark) | Excel Dashboard (`Dashboard!G9:G12`) | Delta | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Electronic check** | 2,365 | 1,071 | 45.29% | \$180,345.00 | **\$84,288.75** | **\$84,288.75** | \$0.00 | **PASS** |
| **Mailed check** | 1,612 | 308 | 19.11% | \$70,794.30 | **\$16,803.60** | **\$16,803.60** | \$0.00 | **PASS** |
| **Bank transfer (automatic)** | 1,544 | 258 | 16.71% | \$103,745.45 | **\$20,091.90** | **\$20,091.90** | \$0.00 | **PASS** |
| **Credit card (automatic)** | 1,522 | 232 | 15.24% | \$101,231.85 | **\$17,946.60** | **\$17,946.60** | \$0.00 | **PASS** |
| **Payment Method Total** | **7,043** | **1,869** | **26.54%** | **\$456,116.60** | **\$139,130.85** | **\$139,130.85** | **\$0.00** | **PASS** |

*Key Insight*: Electronic check accounts for **60.58%** of companywide lost MRR ($84,288.75 / $139,130.85).

### C. Internet Infrastructure

| Internet Service Tier | Customer Count | Churned Count | Churn Rate | Total MRR ($) | Churned MRR ($) (SQL Benchmark) | Excel Dashboard (`Dashboard!K9:K11`) | Delta | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fiber optic** | 3,096 | 1,297 | 41.89% | \$283,284.40 | **\$114,300.05** | **\$114,300.05** | \$0.00 | **PASS** |
| **DSL** | 2,421 | 459 | 18.96% | \$140,665.35 | **\$22,529.20** | **\$22,529.20** | \$0.00 | **PASS** |
| **No internet service** | 1,526 | 113 | 7.40% | \$32,166.85 | **\$2,301.60** | **\$2,301.60** | \$0.00 | **PASS** |
| **Internet Service Total** | **7,043** | **1,869** | **26.54%** | **\$456,116.60** | **\$139,130.85** | **\$139,130.85** | **\$0.00** | **PASS** |

*Key Insight*: Fiber optic broadband represents **82.15%** of companywide lost MRR ($114,300.05 / $139,130.85).

---

## 4. Priority Risk Segment Reconciliation (3x3 Matrix)

| Risk Segment Dimension | Benchmark Value | Excel Workbook Value | Excel Location | Delta | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Total Segment Accounts** | 875 | 875 | `Pivot_Analysis!C33` | 0 | **PASS** |
| **Churned Segment Accounts** | 594 | 594 | `Pivot_Analysis!D33` | 0 | **PASS** |
| **Segment Churn Rate** | 67.89% | 67.89% | `Pivot_Analysis!E33` | 0.00% | **PASS** |
| **Total Segment MRR** | \$72,693.55 | \$72,693.55 | `Pivot_Analysis!F33` | \$0.00 | **PASS** |
| **Segment Churned MRR** | \$49,871.30 | \$49,871.30 | `Pivot_Analysis!G33` | \$0.00 | **PASS** |
| **Share of Total Lost MRR** | 35.84% | 35.84% | `Pivot_Analysis!H33` | 0.00% | **PASS** |
| **Priority Vulnerability Rank**| Rank 1 of 9 | Rank 1 of 9 | `Pivot_Analysis!I33` | 0 | **PASS** |

---

## 5. Chart Readability & UX Improvements

1. **Native Data Labels Enabled**: All four charts on the `Dashboard` worksheet now feature direct data labels (`DataLabelList(showVal=True)`), rendering exact percentages and dollar amounts directly on columns and bars.
2. **Horizontal Bar Optimization**: Chart 2 (Payment Rail) leverages a horizontal orientation with explicit category and x-axis titles, ensuring long payment method names remain readable.
3. **Gridline & Axis Scaling**: Vertical gridlines and standardized percentage number formatting (`0%`) ensure executive clarity without clutter.

---

## 6. Automated Testing Results

- **Validation Runner** ([`src/validate_excel_results.py`](file:///C:/Users/Sruthi/Documents/telco-churn-app/src/validate_excel_results.py)): **55 / 55 CHECKS PASSED** (100.0%).
- **Pytest Suite** ([`tests/test_excel_deliverables.py`](file:///C:/Users/Sruthi/Documents/telco-churn-app/tests/test_excel_deliverables.py)): **19 / 19 TESTS PASSED** (including dedicated category reconciliation test).
