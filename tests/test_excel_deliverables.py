"""
Automated Pytest Suite for Phase 4 Excel Deliverables.

Validates:
- File existence of reports/excel/customer_churn_analysis.xlsx
- Worksheet structure and naming conventions
- Excel Table 'CustomerData' definition and bounds
- Dynamic formula presence in 'Formula_Analysis'
- Multi-dimensional summary tables in 'Pivot_Analysis'
- KPI card values and charts on 'Dashboard'
- Strict reconciliation against data/processed/telco_churn_cleaned.csv
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
import openpyxl

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

WORKBOOK_PATH = PROJECT_ROOT / "reports" / "excel" / "customer_churn_analysis.xlsx"
CLEANED_CSV = PROJECT_ROOT / "data" / "processed" / "telco_churn_cleaned.csv"


@pytest.fixture(scope="module")
def workbook():
    assert WORKBOOK_PATH.is_file(), f"Excel workbook not found at {WORKBOOK_PATH}"
    wb = openpyxl.load_workbook(WORKBOOK_PATH, data_only=False)
    return wb


@pytest.fixture(scope="module")
def cleaned_df():
    assert CLEANED_CSV.is_file(), f"Cleaned CSV not found at {CLEANED_CSV}"
    return pd.read_csv(CLEANED_CSV)


def test_workbook_sheets(workbook):
    expected_sheets = ["Raw_Data", "Data_Quality", "Formula_Analysis", "Pivot_Analysis", "Dashboard"]
    for s in expected_sheets:
        assert s in workbook.sheetnames, f"Missing required sheet: {s}"
    assert workbook.calculation.fullCalcOnLoad is True


def test_raw_data_sheet(workbook, cleaned_df):
    ws = workbook["Raw_Data"]
    assert ws.max_row == len(cleaned_df) + 1  # 7044
    assert ws.max_column == len(cleaned_df.columns)  # 21
    assert "CustomerData" in ws.tables
    tab = ws.tables["CustomerData"]
    assert tab.ref == f"A1:U{len(cleaned_df) + 1}"
    assert ws.freeze_panes == "A2"


def test_data_quality_sheet(workbook):
    ws = workbook["Data_Quality"]
    assert ws.max_row >= 20
    text_content = " ".join(str(cell.value) for row in ws.iter_rows(max_row=35, max_col=7) for cell in row if cell.value)
    assert "7,043" in text_content or "7043" in text_content
    assert "4472-LVYGI" in text_content  # First zero-tenure customer ID
    assert "TotalCharges = 0.00" in text_content or "TotalCharges=0.0" in text_content or "TotalCharges" in text_content


def test_formula_analysis_formulas(workbook):
    ws = workbook["Formula_Analysis"]
    formulas = [str(cell.value) for row in ws.iter_rows() for cell in row if str(cell.value).startswith("=")]
    formula_blob = " ".join(formulas)

    assert "COUNTIF" in formula_blob
    assert "COUNTIFS" in formula_blob
    assert "SUMIF" in formula_blob
    assert "SUMIFS" in formula_blob
    assert "AVERAGEIF" in formula_blob
    assert "AVERAGEIFS" in formula_blob
    assert "XLOOKUP" in formula_blob
    assert "IFERROR" in formula_blob


def test_pivot_analysis_tables(workbook):
    ws = workbook["Pivot_Analysis"]
    text_content = " ".join(str(cell.value) for row in ws.iter_rows() for cell in row if cell.value)
    assert "TECHNICAL & MODELING DISCLOSURE" in text_content
    assert "Month-to-month" in text_content
    assert "Electronic check" in text_content
    assert "Fiber optic" in text_content
    assert "3x3 Customer Risk Segmentation Matrix" in text_content
    assert "New (0-12m)" in text_content


def test_dashboard_kpis_and_charts(workbook, cleaned_df):
    ws = workbook["Dashboard"]
    assert len(ws._charts) >= 4

    tot_cust = ws["A5"].value
    churn_cust = ws["C5"].value
    churn_rate = ws["E5"].value
    mrr_total = ws["G5"].value
    mrr_lost = ws["I5"].value
    mrr_rate = ws["K5"].value

    expected_tot = len(cleaned_df)
    expected_churn = (cleaned_df["Churn"] == "Yes").sum()
    expected_rate = expected_churn / expected_tot
    expected_mrr = cleaned_df["MonthlyCharges"].sum()
    expected_lost_mrr = cleaned_df.loc[cleaned_df["Churn"] == "Yes", "MonthlyCharges"].sum()
    expected_mrr_rate = expected_lost_mrr / expected_mrr

    assert tot_cust == expected_tot
    assert churn_cust == expected_churn
    assert abs(churn_rate - expected_rate) < 0.0005
    assert abs(mrr_total - expected_mrr) < 0.05
    assert abs(mrr_lost - expected_lost_mrr) < 0.05
    assert abs(mrr_rate - expected_mrr_rate) < 0.0005


def test_category_level_churned_mrr_reconciliation(workbook, cleaned_df):
    ws = workbook["Dashboard"]

    # Contract Lost MRR (Rows 9-11, Col 3)
    # Expected Phase 3 SQL: Month-to-month: $120,847.10, One year: $14,118.45, Two year: $4,165.30
    assert ws.cell(row=9, column=1).value == "Month-to-month"
    assert abs(ws.cell(row=9, column=3).value - 120847.10) < 0.05
    assert ws.cell(row=10, column=1).value == "One year"
    assert abs(ws.cell(row=10, column=3).value - 14118.45) < 0.05
    assert ws.cell(row=11, column=1).value == "Two year"
    assert abs(ws.cell(row=11, column=3).value - 4165.30) < 0.05

    # Payment Method Lost MRR (Rows 9-12, Col 7)
    # Expected Phase 3 SQL: Electronic check: $84,288.75, Mailed check: $16,803.60, Bank transfer: $20,091.90, Credit card: $17,946.60
    assert ws.cell(row=9, column=5).value == "Electronic check"
    assert abs(ws.cell(row=9, column=7).value - 84288.75) < 0.05
    assert ws.cell(row=10, column=5).value == "Mailed check"
    assert abs(ws.cell(row=10, column=7).value - 16803.60) < 0.05
    assert ws.cell(row=11, column=5).value == "Bank transfer (automatic)"
    assert abs(ws.cell(row=11, column=7).value - 20091.90) < 0.05
    assert ws.cell(row=12, column=5).value == "Credit card (automatic)"
    assert abs(ws.cell(row=12, column=7).value - 17946.60) < 0.05

    # Internet Service Lost MRR (Rows 9-11, Col 11)
    # Expected Phase 3 SQL: Fiber optic: $114,300.05, DSL: $22,529.20, No internet service: $2,301.60
    assert ws.cell(row=9, column=9).value == "Fiber optic"
    assert abs(ws.cell(row=9, column=11).value - 114300.05) < 0.05
    assert ws.cell(row=10, column=9).value == "DSL"
    assert abs(ws.cell(row=10, column=11).value - 22529.20) < 0.05
    assert ws.cell(row=11, column=9).value == "No internet service"
    assert abs(ws.cell(row=11, column=11).value - 2301.60) < 0.05

