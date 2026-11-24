# Phase 4 — Excel Business Analysis & Interactive Dashboard

**Deliverable Workbook**: [`reports/excel/customer_churn_analysis.xlsx`](file:///C:/Users/Sruthi/Documents/telco-churn-app/reports/excel/customer_churn_analysis.xlsx)  
**Generator Script**: [`src/build_excel_analysis.py`](file:///C:/Users/Sruthi/Documents/telco-churn-app/src/build_excel_analysis.py)  
**Validation Suite**: [`src/validate_excel_results.py`](file:///C:/Users/Sruthi/Documents/telco-churn-app/src/validate_excel_results.py) | [`reports/excel/excel_validation.md`](file:///C:/Users/Sruthi/Documents/telco-churn-app/reports/excel/excel_validation.md)  
**Automated Tests**: [`tests/test_excel_deliverables.py`](file:///C:/Users/Sruthi/Documents/telco-churn-app/tests/test_excel_deliverables.py)  
**Source Dataset**: [`data/processed/telco_churn_cleaned.csv`](file:///C:/Users/Sruthi/Documents/telco-churn-app/data/processed/telco_churn_cleaned.csv) (7,043 customers $\times$ 21 columns)

---

## 1. Executive Workbook Overview

The Phase 4 Excel workbook delivers a commercial-grade, multi-sheet analytical financial and customer retention model built entirely on the cleaned IBM Telco Customer Churn dataset. It demonstrates professional spreadsheet modeling standards: strict separation of data and presentation, named Excel Tables, defensive dynamic formulas, multi-dimensional cross-tabulations, native charting, and an executive KPI dashboard.

---

## 2. Worksheet Architecture

The workbook contains five dedicated worksheets designed for both analytical auditability and executive presentation:

```
reports/excel/customer_churn_analysis.xlsx
│
├── 1. Raw_Data            (Source database formatted as Excel Table 'CustomerData')
├── 2. Data_Quality        (Schema constraints, primary key uniqueness & zero-tenure audit)
├── 3. Formula_Analysis    (Dynamic Excel formulas: COUNTIFS, SUMIFS, AVERAGEIFS, XLOOKUP)
├── 4. Pivot_Analysis      (Multi-dimensional cross-tabs & 3x3 Tenure × Spend risk matrix)
└── 5. Dashboard           (Executive scorecards, native charts & retention playbooks)
```

### Sheet 1: `Raw_Data`
- **Purpose**: Serves as the immutable single source of truth for the entire workbook.
- **Specifications**:
  - Contains all **7,043 customer records** and **21 columns** from the cleaned dataset.
  - Formatted as an official Excel Table named **`CustomerData`** (range `A1:U7044`) using modern corporate table styling (`TableStyleMedium9`).
  - Column headers styled in deep navy (`#1F4E79`) with white bold text and centered alignment.
  - Header row frozen (`A2` freeze pane) so column titles remain visible during scrolling.
  - Standardized number formatting applied across columns: integer formatting for `tenure` (`#,##0`), currency formatting for `MonthlyCharges` and `TotalCharges` (`$#,##0.00`), and centered flags for categorical indicators.

### Sheet 2: `Data_Quality`
- **Purpose**: Transparent audit trail verifying dataset hygiene, integrity, and data preparation logic.
- **Components**:
  1. **Core Dataset Health Grid**: 9 automated validation checks covering total record counts (`COUNTA`), primary key uniqueness, blank cell audits (`COUNTBLANK`), target classification validity (`COUNTIFS`), negative boundary audits on charges and tenure, and senior citizen domain compliance. All 9 checks report **PASS**.
  2. **Zero-Tenure Account Audit**: Detailed methodology callout documenting the **11 accounts with tenure = 0**. Explains why these accounts contained blank `TotalCharges` in the raw data (new customer enrollees who joined during the current billing cycle and have not yet completed their first monthly billing cycle) and justifies the clean imputation of `$0.00` rather than dropping valuable accounts. Includes a complete verification table displaying all 11 customer records.

### Sheet 3: `Formula_Analysis`
- **Purpose**: Showcase dynamic, production-grade Excel formulas that calculate customer counts, churn rates, recurring monthly revenue (MRR), revenue exposure, and average revenue per user (ARPU) across 6 core operational dimensions:
  1. **Contract Commitment**: Month-to-month, One year, Two year.
  2. **Payment Rail**: Electronic check, Mailed check, Bank transfer (auto), Credit card (auto).
  3. **Internet Infrastructure**: Fiber optic, DSL, No internet.
  4. **Value-Added Technical Support**: TechSupport (`Yes`, `No`, `No internet service`).
  5. **Account Security Support**: OnlineSecurity (`Yes`, `No`, `No internet service`).
  6. **Customer Tenure Lifecycle Horizons**: New (0–12m), Developing (13–36m), Mature (37–72m).
  7. **Interactive Single Customer Lookup**: An interactive tool powered by `XLOOKUP` and `IFERROR`. Analysts can enter any Customer ID into cell `B49` (e.g., `7590-VHVEG`) to instantly retrieve demographics, contract, tenure, billing metrics, churn status, and an automated **Retention Action Tier** classification (`IF/AND`).

### Sheet 4: `Pivot_Analysis`
- **Purpose**: Multi-tier cross-tabulations analyzing feature interactions and high-risk customer intersections:
  1. **Contract Commitment $\times$ Payment Method** (12 combinations): Demonstrates that `Month-to-month` combined with `Electronic check` represents **55.57% of all companywide lost MRR** (\$77,315.60/month across 1,850 accounts with a 53.73% churn rate).
  2. **Internet Service $\times$ TechSupport** (5 combinations): Highlights the protective gap of support subscriptions, showing that Fiber optic users without TechSupport churn at 49.37% (\$94,900.80 lost MRR), compared to 22.63% for those with TechSupport (-26.74% lower churn).
  3. **3x3 Customer Risk Segmentation Matrix** (9 segments): Cross-classifies Tenure Tiers (`New`, `Developing`, `Mature`) against Monthly Spend Tiers (`Low <= $35`, `Medium $35-$70`, `High > $70`), ranked by lost MRR exposure. The top vulnerability segment—`New (0-12m) | High Spend (>$70)`—is styled with alert highlighting.

### Sheet 5: `Dashboard`
- **Purpose**: High-impact executive dashboard structured for C-level presentation.
- **Components**:
  1. **Executive KPI Cards** (6 styled scorecards):
     - **Total Customers**: 7,043
     - **Churned Customers**: 1,869
     - **Overall Churn Rate**: 26.54%
     - **Baseline Monthly MRR**: \$456,116.60
     - **Churned Monthly Revenue Exposure**: \$139,130.85
     - **MRR Exposure Rate**: 30.50%
  2. **Summary Data Tables**: Clean feeder tables supplying native Excel chart objects.
  3. **4 Native Excel Visualizations**:
     - *Chart 1*: Observed Churn Rate by Contract Commitment (Column chart).
     - *Chart 2*: Observed Churn Rate by Payment Rail (Horizontal bar chart).
     - *Chart 3*: Observed Churn Rate by Internet Service Tier (Column chart).
     - *Chart 4*: Monthly Revenue Exposure (Lost MRR) by Customer Risk Segment (Column chart).
  4. **Executive Business Interpretations & Retention Playbook**: Structured analytical narratives covering month-to-month exposure, payment friction, fiber optic infrastructure vulnerabilities, early-tenure high-spend priorities, and support add-on protective associations.

---

## 3. Formula Inventory & Technical Specifications

| Excel Function | Usage Example in Workbook | Target Analysis |
| :--- | :--- | :--- |
| **COUNTIF** | `=COUNTIF(Raw_Data!$P$2:$P$7044, A6)` | Total customer count per contract tier |
| **COUNTIFS** | `=COUNTIFS(Raw_Data!$P$2:$P$7044, A6, Raw_Data!$U$2:$U$7044, "Yes")` | Churned customer count per contract tier |
| **SUMIF** | `=SUMIF(Raw_Data!$P$2:$P$7044, A6, Raw_Data!$S$2:$S$7044)` | Total recurring MRR per contract tier |
| **SUMIFS** | `=SUMIFS(Raw_Data!$S$2:$S$7044, Raw_Data!$P$2:$P$7044, A6, Raw_Data!$U$2:$U$7044, "Yes")` | Churned MRR exposure per segment |
| **AVERAGEIFS**| `=AVERAGEIFS(Raw_Data!$S$2:$S$7044, Raw_Data!$P$2:$P$7044, A6, Raw_Data!$U$2:$U$7044, "Yes")` | ARPU for churned customers |
| **IFERROR** | `=IFERROR(D6/B6, 0)` | Safe churn rate calculation |
| **XLOOKUP** | `=IFERROR(XLOOKUP($B$49, Raw_Data!$A$2:$A$7044, Raw_Data!$S$2:$S$7044), 0)` | Dynamic customer lookup tool |
| **IF / AND** | `=IF(B58="Yes", "RETAIN LOSS / WIN-BACK", IF(AND(B52<=12, B56>70), "PRIORITY RETENTION RISK", "STANDARD"))` | Account retention priority classification |

---

## 4. Technical Disclosures & Tooling Nuances

### A. PivotTables vs. Pivot-Ready Summary Tables
- **openpyxl Technical Limitation**: The Python `openpyxl` library (version 3.1.5) does not support creating native Excel PivotCache definitions or PivotTable XML parts without causing file repair warnings or corruption upon opening in Microsoft Excel.
- **Implemented Architecture**: In accordance with best practices, the workbook delivers **Pivot-Ready Multi-Dimensional Summary Tables** authored with dynamic Excel formulas on the `Pivot_Analysis` worksheet.
- **Native PivotTable Conversion**: Any user opening the workbook in Microsoft Excel can instantly convert the underlying `CustomerData` table into a native interactive PivotTable:
  1. Navigate to the `Raw_Data` sheet.
  2. Click anywhere inside the `CustomerData` table.
  3. Select **Insert > PivotTable**.
  4. Drag `Contract` to Rows, `PaymentMethod` to Columns, `customerID` to Values (`Count`), and `MonthlyCharges` to Values (`Sum`).

### B. Interactive Slicers
- **openpyxl Technical Limitation**: Native Excel Slicers require `slicerCache` and `slicer` XML relationships that are unsupported in programmatic generation by `openpyxl`.
- **User Interactive Alternative**:
  - Interactive filtering is fully functional on `Raw_Data` via the built-in dropdown filter controls of the `CustomerData` Excel Table.
  - Interactive account lookup is provided dynamically on `Formula_Analysis` via cell `B49`.
  - In desktop Microsoft Excel, users can add visual slicers in two clicks via **Table Design > Insert Slicer** (selecting `Contract`, `InternetService`, and `PaymentMethod`).

### C. Automatic Formula Calculation
- **openpyxl Formula Caching**: When `openpyxl` writes a formula string (e.g., `=COUNTIF(...)`), it does not pre-evaluate and cache the resulting display value inside the XML payload.
- **Resolution**: The workbook generation script explicitly sets:
  ```python
  wb.calculation.fullCalcOnLoad = True
  ```
  This instructs Microsoft Excel to force a full calculation of all formula cells upon opening the file, guaranteeing that all numbers, rates, and lookup values evaluate immediately.

---

## 5. Methodological Terminology & Governance Disclosures

To ensure rigorous data analyst standards, the following disclosures are documented across all sheets and executive summaries:

1. **Churned Monthly Revenue Exposure (\$139,130.85)**: This figure represents a **snapshot revenue proxy** calculated as the sum of monthly charges for customers designated as churned in this observation window.
2. **Annualized Revenue Exposure (\$1,669,570.20)**: This figure is a simple **12$\times$ extrapolation** (\$139,130.85 $\times$ 12) intended to illustrate the annualized magnitude of current revenue drag. It does **not** represent verified historical realized loss over a 12-month trailing period.
3. **Tenure Lifecycle Groups**: The tenure segments (`New 0–12m`, `Developing 13–36m`, `Mature 37–72m`) are **cross-sectional customer classifications** observed at a single point in time. They do not constitute historical cohort survival tracking.
4. **Correlation vs. Causation**: Strong statistical associations (such as higher churn among month-to-month contracts or lower churn among TechSupport subscribers) indicate behavioral correlation, not proven causal impact. Mandating long-term contracts or bundling services without addressing customer value may adversely impact acquisition.

---

## 6. How to Reproduce & Validate

### 1. Rebuild the Excel Workbook
```powershell
python src/build_excel_analysis.py
```

### 2. Run Dedicated Excel Validation Suite
```powershell
python src/validate_excel_results.py
```
*Expected Output: `55/55 CHECKS PASSED` (including 14 category-level reconciliation checks).*

### 3. Run Complete Project Test Suite
```powershell
pytest tests/ -v
```
*Expected Output: `19 passed` (covering Phase 1 Data Foundation, Phase 3 SQL Analytics, and Phase 4 Excel Deliverables).*
