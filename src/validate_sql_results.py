"""
Independent SQL vs. Pandas Validation Engine for Telco Churn Metrics.

Calculates business metrics independently using Pandas directly from the cleaned CSV
and compares them against SQL database query outputs. Employs numerical tolerances
to verify mathematical alignment and guarantee analytical integrity.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database_utils import (
    get_connection,
    DEFAULT_DB_PATH,
    DEFAULT_PROCESSED_CSV,
)


def compute_pandas_metrics(csv_path: Path) -> Dict[str, Any]:
    """
    Independently calculate all business KPIs and 3x3 segment metrics using Pandas.
    """
    df = pd.read_csv(csv_path)

    # 1. High-level KPIs
    total_cust = len(df)
    active_cust = int((df["Churn"] == "No").sum())
    churned_cust = int((df["Churn"] == "Yes").sum())
    churn_rate_pct = round(100.0 * churned_cust / total_cust, 2)

    total_mrr = round(float(df["MonthlyCharges"].sum()), 2)
    active_mrr = round(float(df[df["Churn"] == "No"]["MonthlyCharges"].sum()), 2)
    churned_mrr = round(float(df[df["Churn"] == "Yes"]["MonthlyCharges"].sum()), 2)
    mrr_churn_rate_pct = round(100.0 * churned_mrr / total_mrr, 2)

    avg_mrr_active = round(float(df[df["Churn"] == "No"]["MonthlyCharges"].mean()), 2)
    avg_mrr_churned = round(float(df[df["Churn"] == "Yes"]["MonthlyCharges"].mean()), 2)

    # 2. Tenure x Spend Segmentation (3x3 Matrix)
    df["tenure_tier"] = np.where(
        df["tenure"] <= 12, "New (0-12m)",
        np.where(df["tenure"] <= 36, "Developing (13-36m)", "Mature (37-72m)")
    )
    df["spend_tier"] = np.where(
        df["MonthlyCharges"] <= 35.0, "Low (<=$35)",
        np.where(df["MonthlyCharges"] <= 70.0, "Medium ($35-$70)", "High (>$70)")
    )

    seg_grouped = df.groupby(["tenure_tier", "spend_tier"], observed=False).agg(
        total_customers=("customerID", "count"),
        churned_customers=("Churn", lambda s: (s == "Yes").sum()),
        churn_rate_pct=("Churn", lambda s: round((s == "Yes").mean() * 100.0, 2)),
        churned_mrr=("MonthlyCharges", lambda s: round(float(s[df.loc[s.index, "Churn"] == "Yes"].sum()), 2))
    ).reset_index()

    segment_dict = {}
    for row in seg_grouped.itertuples():
        key = f"{row.tenure_tier} | {row.spend_tier}"
        segment_dict[key] = {
            "total_customers": row.total_customers,
            "churned_customers": row.churned_customers,
            "churn_rate_pct": row.churn_rate_pct,
            "churned_mrr": row.churned_mrr,
        }

    return {
        "total_customers": total_cust,
        "active_customers": active_cust,
        "churned_customers": churned_cust,
        "overall_churn_rate_pct": churn_rate_pct,
        "total_baseline_mrr": total_mrr,
        "active_customer_mrr": active_mrr,
        "churned_customer_mrr_exposure": churned_mrr,
        "mrr_churn_rate_pct": mrr_churn_rate_pct,
        "avg_monthly_charges_active": avg_mrr_active,
        "avg_monthly_charges_churned": avg_mrr_churned,
        "segments": segment_dict,
    }


def fetch_sql_metrics(conn) -> Dict[str, Any]:
    """
    Fetch business KPIs and 3x3 segment metrics directly from SQLite database.
    """
    # 1. Fetch KPIs
    kpi_query = """
    SELECT 
        total_customers,
        active_customers,
        churned_customers,
        overall_churn_rate_pct,
        total_baseline_mrr,
        active_customer_mrr,
        churned_customer_mrr_exposure,
        mrr_churn_rate_pct,
        avg_monthly_charges_active,
        avg_monthly_charges_churned
    FROM (
        SELECT 
            COUNT(*) AS total_customers,
            SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) AS active_customers,
            SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
            ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*), 2) AS overall_churn_rate_pct,
            ROUND(SUM(MonthlyCharges), 2) AS total_baseline_mrr,
            ROUND(SUM(CASE WHEN Churn = 'No' THEN MonthlyCharges ELSE 0.0 END), 2) AS active_customer_mrr,
            ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_customer_mrr_exposure,
            ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END) / SUM(MonthlyCharges), 2) AS mrr_churn_rate_pct,
            ROUND(AVG(CASE WHEN Churn = 'No' THEN MonthlyCharges END), 2) AS avg_monthly_charges_active,
            ROUND(AVG(CASE WHEN Churn = 'Yes' THEN MonthlyCharges END), 2) AS avg_monthly_charges_churned
        FROM customers
    );
    """
    kpi_row = conn.execute(kpi_query).fetchone()

    # 2. Fetch Segmentation
    seg_query = """
    SELECT 
        CASE 
            WHEN tenure <= 12 THEN 'New (0-12m)'
            WHEN tenure <= 36 THEN 'Developing (13-36m)'
            ELSE 'Mature (37-72m)'
        END AS tenure_tier,
        CASE 
            WHEN MonthlyCharges <= 35.0 THEN 'Low (<=$35)'
            WHEN MonthlyCharges <= 70.0 THEN 'Medium ($35-$70)'
            ELSE 'High (>$70)'
        END AS spend_tier,
        COUNT(*) AS total_customers,
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
        ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
        ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
    FROM customers
    GROUP BY 
        CASE 
            WHEN tenure <= 12 THEN 'New (0-12m)'
            WHEN tenure <= 36 THEN 'Developing (13-36m)'
            ELSE 'Mature (37-72m)'
        END,
        CASE 
            WHEN MonthlyCharges <= 35.0 THEN 'Low (<=$35)'
            WHEN MonthlyCharges <= 70.0 THEN 'Medium ($35-$70)'
            ELSE 'High (>$70)'
        END;
    """
    seg_rows = conn.execute(seg_query).fetchall()

    seg_dict = {}
    for r in seg_rows:
        key = f"{r['tenure_tier']} | {r['spend_tier']}"
        seg_dict[key] = {
            "total_customers": r["total_customers"],
            "churned_customers": r["churned_customers"],
            "churn_rate_pct": r["churn_rate_pct"],
            "churned_mrr": r["churned_mrr"],
        }

    return {
        "total_customers": kpi_row["total_customers"],
        "active_customers": kpi_row["active_customers"],
        "churned_customers": kpi_row["churned_customers"],
        "overall_churn_rate_pct": kpi_row["overall_churn_rate_pct"],
        "total_baseline_mrr": kpi_row["total_baseline_mrr"],
        "active_customer_mrr": kpi_row["active_customer_mrr"],
        "churned_customer_mrr_exposure": kpi_row["churned_customer_mrr_exposure"],
        "mrr_churn_rate_pct": kpi_row["mrr_churn_rate_pct"],
        "avg_monthly_charges_active": kpi_row["avg_monthly_charges_active"],
        "avg_monthly_charges_churned": kpi_row["avg_monthly_charges_churned"],
        "segments": seg_dict,
    }


def validate_results(
    csv_path: Optional[Path] = None,
    db_path: Optional[Path] = None,
    tolerance: float = 0.05
) -> Tuple[bool, pd.DataFrame]:
    """
    Run independent validation and generate comparison audit table.
    """
    target_csv = csv_path if csv_path else DEFAULT_PROCESSED_CSV
    target_db = db_path if db_path else DEFAULT_DB_PATH

    print("=" * 85)
    print("  INDEPENDENT SQL VS. PANDAS METRIC RECONCILIATION & VALIDATION")
    print("=" * 85)
    print(f"CSV Source     : {target_csv.resolve()}")
    print(f"Database Source: {target_db.resolve()}")
    print(f"Tolerance      : +/- {tolerance}")
    print("-" * 85)

    py_metrics = compute_pandas_metrics(target_csv)
    conn = get_connection(target_db)
    try:
        sql_metrics = fetch_sql_metrics(conn)
    finally:
        conn.close()

    records = []

    # 1. Compare High-Level KPIs
    kpi_keys = [
        ("total_customers", "Total Customers (Count)"),
        ("active_customers", "Active Customers (Count)"),
        ("churned_customers", "Churned Customers (Count)"),
        ("overall_churn_rate_pct", "Overall Churn Rate (%)"),
        ("total_baseline_mrr", "Total Baseline MRR ($)"),
        ("active_customer_mrr", "Active Customer MRR ($)"),
        ("churned_customer_mrr_exposure", "Churned Customer MRR Exposure ($)"),
        ("mrr_churn_rate_pct", "MRR Churn Rate (%)"),
        ("avg_monthly_charges_active", "Avg Monthly Charges - Active ($)"),
        ("avg_monthly_charges_churned", "Avg Monthly Charges - Churned ($)"),
    ]

    all_passed = True

    for key, label in kpi_keys:
        p_val = py_metrics[key]
        s_val = sql_metrics[key]
        diff = abs(p_val - s_val)
        passed = diff <= tolerance
        if not passed:
            all_passed = False
        records.append({
            "Metric Name": label,
            "Pandas Value": p_val,
            "SQL Value": s_val,
            "Abs Difference": round(diff, 4),
            "Status": "PASS" if passed else "FAIL"
        })

    # 2. Compare 3x3 Segments
    py_segs = py_metrics["segments"]
    sql_segs = sql_metrics["segments"]

    assert len(py_segs) == 9, f"Expected 9 Pandas segments, found {len(py_segs)}"
    assert len(sql_segs) == 9, f"Expected 9 SQL segments, found {len(sql_segs)}"

    for seg_name in sorted(py_segs.keys()):
        p_seg = py_segs[seg_name]
        s_seg = sql_segs.get(seg_name, {})

        # Total accounts
        p_total = p_seg["total_customers"]
        s_total = s_seg.get("total_customers", 0)
        diff_tot = abs(p_total - s_total)
        tot_passed = diff_tot <= tolerance
        if not tot_passed:
            all_passed = False
        records.append({
            "Metric Name": f"Segment Count [{seg_name}]",
            "Pandas Value": p_total,
            "SQL Value": s_total,
            "Abs Difference": diff_tot,
            "Status": "PASS" if tot_passed else "FAIL"
        })

        # Churn rate
        p_rate = p_seg["churn_rate_pct"]
        s_rate = s_seg.get("churn_rate_pct", 0.0)
        diff_rate = abs(p_rate - s_rate)
        rate_passed = diff_rate <= tolerance
        if not rate_passed:
            all_passed = False
        records.append({
            "Metric Name": f"Segment Churn % [{seg_name}]",
            "Pandas Value": p_rate,
            "SQL Value": s_rate,
            "Abs Difference": round(diff_rate, 4),
            "Status": "PASS" if rate_passed else "FAIL"
        })

        # Churned MRR
        p_mrr = p_seg["churned_mrr"]
        s_mrr = s_seg.get("churned_mrr", 0.0)
        diff_mrr = abs(p_mrr - s_mrr)
        mrr_passed = diff_mrr <= tolerance
        if not mrr_passed:
            all_passed = False
        records.append({
            "Metric Name": f"Segment Churned MRR [{seg_name}]",
            "Pandas Value": p_mrr,
            "SQL Value": s_mrr,
            "Abs Difference": round(diff_mrr, 4),
            "Status": "PASS" if mrr_passed else "FAIL"
        })

    audit_df = pd.DataFrame(records)
    print(audit_df.to_string(index=False))
    print("-" * 85)
    
    passed_count = (audit_df["Status"] == "PASS").sum()
    total_checks = len(audit_df)
    
    if all_passed:
        print(f"[VERDICT] VALIDATION PASSED: All {passed_count}/{total_checks} independent checks verified successfully!")
    else:
        print(f"[VERDICT] VALIDATION FAILED: {total_checks - passed_count} checks exceeded tolerance threshold.")

    print("=" * 85)
    return all_passed, audit_df


if __name__ == "__main__":
    success, df_results = validate_results()
    if not success:
        sys.exit(1)
