"""
Validation script for Phase 4 Excel deliverables.

Verifies:
1. Workbook file existence and structural integrity.
2. Presence and structure of all 5 required worksheets:
   - Raw_Data (Table 'CustomerData', freeze pane, 7,043 rows)
   - Data_Quality (Integrity tests, 11 zero-tenure records documented)
   - Formula_Analysis (COUNTIF, COUNTIFS, SUMIF, SUMIFS, AVERAGEIFS, XLOOKUP formulas)
   - Pivot_Analysis (Multi-dimensional cross-tabulations and 3x3 matrix)
   - Dashboard (6 KPI cards, 4 native Excel charts with data labels, executive insights)
3. Quantitative reconciliation against Python and SQL ground truth:
   - Overall Portfolio KPIs (tolerance +/- $0.05 and +/- 0.05%).
   - Category-level Churned MonthlyCharges (Contract, Payment Method, Internet Service).
   - Category-level Churn Rates.
   - Priority Risk Segment (New/High Spend).
4. Workbook calculation properties (fullCalcOnLoad = True).
"""

import sys
from pathlib import Path
import pandas as pd
import openpyxl

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

WORKBOOK_PATH = PROJECT_ROOT / "reports" / "excel" / "customer_churn_analysis.xlsx"
CLEANED_CSV = PROJECT_ROOT / "data" / "processed" / "telco_churn_cleaned.csv"


def validate_excel_workbook() -> bool:
    print("=" * 75)
    print("  CUSTOMER CHURN & RETENTION INTELLIGENCE — EXCEL VALIDATION SUITE")
    print("=" * 75)

    checks_passed = 0
    checks_total = 0

    def record_check(description: str, passed: bool, detail: str = ""):
        nonlocal checks_passed, checks_total
        checks_total += 1
        if passed:
            checks_passed += 1
            print(f"  [PASS] {description} {detail}")
        else:
            print(f"  [FAIL] {description} - {detail}")

    # -------------------------------------------------------------
    # 1. File Presence
    # -------------------------------------------------------------
    record_check("Workbook file exists", WORKBOOK_PATH.is_file(), f"({WORKBOOK_PATH.name})")
    if not WORKBOOK_PATH.is_file():
        print("[ERROR] Cannot continue without workbook file.")
        return False

    wb = openpyxl.load_workbook(WORKBOOK_PATH, data_only=False)

    # -------------------------------------------------------------
    # 2. Worksheet Inventory
    # -------------------------------------------------------------
    expected_sheets = ["Raw_Data", "Data_Quality", "Formula_Analysis", "Pivot_Analysis", "Dashboard"]
    record_check("Required sheets exist", set(expected_sheets).issubset(set(wb.sheetnames)),
                 f"Found: {wb.sheetnames}")

    # Calculation property
    record_check("fullCalcOnLoad enabled", wb.calculation.fullCalcOnLoad is True,
                 f"(fullCalcOnLoad = {wb.calculation.fullCalcOnLoad})")

    # -------------------------------------------------------------
    # 3. Sheet 1: Raw_Data
    # -------------------------------------------------------------
    ws_raw = wb["Raw_Data"]
    record_check("Raw_Data row count matches 7,044", ws_raw.max_row == 7044, f"(Rows: {ws_raw.max_row})")
    record_check("Raw_Data column count matches 21", ws_raw.max_column == 21, f"(Cols: {ws_raw.max_column})")
    record_check("Raw_Data contains CustomerData table", "CustomerData" in ws_raw.tables,
                 f"(Tables: {list(ws_raw.tables.keys())})")
    if "CustomerData" in ws_raw.tables:
        tab = ws_raw.tables["CustomerData"]
        record_check("CustomerData table range is A1:U7044", tab.ref == "A1:U7044", f"(Ref: {tab.ref})")
    record_check("Raw_Data freeze pane set to A2", ws_raw.freeze_panes == "A2", f"(Freeze: {ws_raw.freeze_panes})")

    # -------------------------------------------------------------
    # 4. Sheet 2: Data_Quality
    # -------------------------------------------------------------
    ws_dq = wb["Data_Quality"]
    record_check("Data_Quality has content", ws_dq.max_row >= 25, f"(Rows: {ws_dq.max_row})")
    dq_text = " ".join(str(cell.value) for row in ws_dq.iter_rows(max_row=35, max_col=7) for cell in row if cell.value)
    record_check("Data_Quality documents 11 zero-tenure records", "11 accounts" in dq_text or "4472-LVYGI" in dq_text,
                 "Zero-tenure audit table and methodology present")

    # -------------------------------------------------------------
    # 5. Sheet 3: Formula_Analysis
    # -------------------------------------------------------------
    ws_fa = wb["Formula_Analysis"]
    fa_formulas = [str(cell.value) for row in ws_fa.iter_rows() for cell in row if str(cell.value).startswith("=")]
    fa_text = " ".join(fa_formulas)

    record_check("Formula_Analysis contains COUNTIF / COUNTIFS", "COUNTIF" in fa_text, "Found dynamic count formulas")
    record_check("Formula_Analysis contains SUMIF / SUMIFS", "SUMIF" in fa_text, "Found dynamic sum formulas")
    record_check("Formula_Analysis contains AVERAGEIF / AVERAGEIFS", "AVERAGEIF" in fa_text, "Found dynamic average formulas")
    record_check("Formula_Analysis contains XLOOKUP", "XLOOKUP" in fa_text, "Found dynamic lookup tool")
    record_check("Formula_Analysis contains IFERROR", "IFERROR" in fa_text, "Found error-handling wrappers")

    # Verify sections present in Formula_Analysis
    fa_all_text = " ".join(str(cell.value) for row in ws_fa.iter_rows() for cell in row if cell.value)
    record_check("Formula_Analysis covers Contract Type", "Contract Commitment" in fa_all_text, "Section 1")
    record_check("Formula_Analysis covers Payment Rail", "Payment Rail" in fa_all_text, "Section 2")
    record_check("Formula_Analysis covers Internet Infrastructure", "Internet Infrastructure" in fa_all_text, "Section 3")
    record_check("Formula_Analysis covers TechSupport", "TechSupport Subscription" in fa_all_text, "Section 4")
    record_check("Formula_Analysis covers OnlineSecurity", "OnlineSecurity Subscription" in fa_all_text, "Section 5")
    record_check("Formula_Analysis covers Tenure Horizon", "Tenure Horizon" in fa_all_text, "Section 6")

    # -------------------------------------------------------------
    # 6. Sheet 4: Pivot_Analysis
    # -------------------------------------------------------------
    ws_pa = wb["Pivot_Analysis"]
    pa_text = " ".join(str(cell.value) for row in ws_pa.iter_rows() for cell in row if cell.value)
    record_check("Pivot_Analysis has disclosure banner", "TECHNICAL & MODELING DISCLOSURE" in pa_text,
                 "Openpyxl / native PivotTable distinction disclosed")
    record_check("Pivot_Analysis has Contract x Payment cross-tab", "Contract Commitment × Payment Method" in pa_text, "Section 1")
    record_check("Pivot_Analysis has Internet x TechSupport cross-tab", "Internet Service Tier × TechSupport" in pa_text, "Section 2")
    record_check("Pivot_Analysis has 3x3 Risk Matrix", "3x3 Customer Risk Segmentation Matrix" in pa_text, "Section 3")

    # -------------------------------------------------------------
    # 7. Sheet 5: Dashboard Structure & Elements
    # -------------------------------------------------------------
    ws_db = wb["Dashboard"]
    record_check("Dashboard contains charts", len(ws_db._charts) >= 4, f"(Chart count: {len(ws_db._charts)})")

    # Verify chart data labels enabled
    all_charts_have_labels = all(getattr(c, "dataLabels", None) is not None for c in ws_db._charts)
    record_check("Dashboard charts have data labels enabled", all_charts_have_labels, "Data labels visible on series")

    # Verify overall KPI card values
    df = pd.read_csv(CLEANED_CSV)
    gt_total = len(df)
    gt_churn = (df["Churn"] == "Yes").sum()
    gt_rate = gt_churn / gt_total
    gt_mrr = df["MonthlyCharges"].sum()
    gt_lost_mrr = df.loc[df["Churn"] == "Yes", "MonthlyCharges"].sum()
    gt_mrr_rate = gt_lost_mrr / gt_mrr

    kpi_targets = {
        "Total Customers": (ws_db["A5"].value, gt_total, 0),
        "Churned Customers": (ws_db["C5"].value, gt_churn, 0),
        "Overall Churn Rate": (ws_db["E5"].value, gt_rate, 0.0005),
        "Baseline MRR": (ws_db["G5"].value, gt_mrr, 0.05),
        "Churned MRR Exposure": (ws_db["I5"].value, gt_lost_mrr, 0.05),
        "MRR Exposure Rate": (ws_db["K5"].value, gt_mrr_rate, 0.0005),
    }

    for kpi_name, (val, target, tol) in kpi_targets.items():
        if val is None:
            record_check(f"Dashboard KPI '{kpi_name}'", False, "Value is None")
        else:
            diff = abs(val - target)
            record_check(f"Dashboard KPI '{kpi_name}'", diff <= tol, f"(Val: {val}, Expected: {target}, Diff: {diff:.4f})")

    # -------------------------------------------------------------
    # 8. Category-Level Reconciliation Checks (Phase 3 SQL Ground Truth)
    # -------------------------------------------------------------
    print("-" * 75)
    print("  CATEGORY-LEVEL CHURNED MRR RECONCILIATION CHECKS (PHASE 3 SQL)")
    print("-" * 75)

    # 8A. Contract Category Churned MRR
    # Expected Phase 3 SQL: Month-to-month: $120,847.10 | One year: $14,118.45 | Two year: $4,165.30
    gt_contract_lost = df[df["Churn"] == "Yes"].groupby("Contract")["MonthlyCharges"].sum().to_dict()
    db_contract_lost = {
        ws_db.cell(row=r, column=1).value: ws_db.cell(row=r, column=3).value
        for r in range(9, 12)
    }

    for c_name, expected_val in [("Month-to-month", 120847.10), ("One year", 14118.45), ("Two year", 4165.30)]:
        actual_val = db_contract_lost.get(c_name)
        gt_val = gt_contract_lost.get(c_name, 0.0)
        record_check(f"Contract Lost MRR: '{c_name}' matches SQL/Pandas",
                     actual_val is not None and abs(actual_val - expected_val) <= 0.05 and abs(actual_val - gt_val) <= 0.05,
                     f"(Excel: ${actual_val:,.2f}, Expected: ${expected_val:,.2f}, GT: ${gt_val:,.2f})")

    contract_sum = sum(db_contract_lost.values())
    record_check("Contract Lost MRR categories sum to $139,130.85", abs(contract_sum - gt_lost_mrr) <= 0.05,
                 f"(Sum: ${contract_sum:,.2f})")

    # 8B. Payment Method Category Churned MRR
    # Expected Phase 3 SQL: Electronic check: $84,288.75 | Mailed check: $16,803.60 | Bank transfer: $20,091.90 | Credit card: $17,946.60
    gt_payment_lost = df[df["Churn"] == "Yes"].groupby("PaymentMethod")["MonthlyCharges"].sum().to_dict()
    db_payment_lost = {
        ws_db.cell(row=r, column=5).value: ws_db.cell(row=r, column=7).value
        for r in range(9, 13)
    }

    expected_payments = [
        ("Electronic check", 84288.75),
        ("Mailed check", 16803.60),
        ("Bank transfer (automatic)", 20091.90),
        ("Credit card (automatic)", 17946.60),
    ]
    for p_name, expected_val in expected_payments:
        actual_val = db_payment_lost.get(p_name)
        gt_val = gt_payment_lost.get(p_name, 0.0)
        record_check(f"Payment Method Lost MRR: '{p_name}' matches SQL/Pandas",
                     actual_val is not None and abs(actual_val - expected_val) <= 0.05 and abs(actual_val - gt_val) <= 0.05,
                     f"(Excel: ${actual_val:,.2f}, Expected: ${expected_val:,.2f}, GT: ${gt_val:,.2f})")

    payment_sum = sum(db_payment_lost.values())
    record_check("Payment Method Lost MRR categories sum to $139,130.85", abs(payment_sum - gt_lost_mrr) <= 0.05,
                 f"(Sum: ${payment_sum:,.2f})")

    # 8C. Internet Service Category Churned MRR
    # Expected Phase 3 SQL: Fiber optic: $114,300.05 | DSL: $22,529.20 | No internet service: $2,301.60
    gt_internet_lost = df[df["Churn"] == "Yes"].groupby("InternetService")["MonthlyCharges"].sum().to_dict()
    db_internet_lost = {
        ws_db.cell(row=r, column=9).value: ws_db.cell(row=r, column=11).value
        for r in range(9, 12)
    }

    expected_internets = [
        ("Fiber optic", "Fiber optic", 114300.05),
        ("DSL", "DSL", 22529.20),
        ("No internet service", "No", 2301.60),
    ]
    for label, code, expected_val in expected_internets:
        actual_val = db_internet_lost.get(label)
        gt_val = gt_internet_lost.get(code, 0.0)
        record_check(f"Internet Service Lost MRR: '{label}' matches SQL/Pandas",
                     actual_val is not None and abs(actual_val - expected_val) <= 0.05 and abs(actual_val - gt_val) <= 0.05,
                     f"(Excel: ${actual_val:,.2f}, Expected: ${expected_val:,.2f}, GT: ${gt_val:,.2f})")

    internet_sum = sum(db_internet_lost.values())
    record_check("Internet Service Lost MRR categories sum to $139,130.85", abs(internet_sum - gt_lost_mrr) <= 0.05,
                 f"(Sum: ${internet_sum:,.2f})")

    # -------------------------------------------------------------
    # 9. Priority Risk Segment Reconciliation
    # -------------------------------------------------------------
    seg_mask = (df["tenure"] <= 12) & (df["MonthlyCharges"] > 70)
    gt_seg_tot = seg_mask.sum()
    gt_seg_churn = (seg_mask & (df["Churn"] == "Yes")).sum()
    gt_seg_rate = gt_seg_churn / gt_seg_tot
    gt_seg_lost_mrr = df.loc[seg_mask & (df["Churn"] == "Yes"), "MonthlyCharges"].sum()
    gt_seg_mrr_share = gt_seg_lost_mrr / gt_lost_mrr

    record_check("Top Risk Segment Total Accounts match exactly (875)", ws_pa["C33"].value == gt_seg_tot)
    record_check("Top Risk Segment Churned Accounts match exactly (594)", ws_pa["D33"].value == gt_seg_churn)
    record_check("Top Risk Segment Churn Rate within 0.05% (67.89%)", abs(ws_pa["E33"].value - gt_seg_rate) <= 0.0005)
    record_check("Top Risk Segment Lost MRR within $0.05 ($49,871.30)", abs(ws_pa["G33"].value - gt_seg_lost_mrr) <= 0.05)
    record_check("Top Risk Segment Lost MRR Share within 0.05% (35.84%)", abs(ws_pa["H33"].value - gt_seg_mrr_share) <= 0.0005)

    # -------------------------------------------------------------
    # 10. Dashboard Insights and Disclosures
    # -------------------------------------------------------------
    db_text = " ".join(str(cell.value) for row in ws_db.iter_rows() for cell in row if cell.value)
    record_check("Dashboard contains executive business insights", "Executive Business Interpretations" in db_text, "Present")
    record_check("Dashboard executive text contains reconciled figures", "$120,847.10" in db_text and "$84,288.75" in db_text and "$114,300.05" in db_text,
                 "Narratives reflect exact SQL ground truth")
    record_check("Dashboard contains methodological terminology notes", "Methodological Terminology" in db_text, "Present")
    record_check("Dashboard contains slicer technical disclosure", "Slicer Disclosures" in db_text or "slicers" in db_text.lower(), "Present")

    print("=" * 75)
    print(f"  EXCEL VALIDATION RESULT: {checks_passed}/{checks_total} CHECKS PASSED")
    print("=" * 75)
    return checks_passed == checks_total


if __name__ == "__main__":
    success = validate_excel_workbook()
    sys.exit(0 if success else 1)
