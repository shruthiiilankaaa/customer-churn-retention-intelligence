"""
Automated Pytest Suite for SQL Analytics Layer.

Tests:
1. Row count integrity (exactly 7,043 rows).
2. Customer ID uniqueness & primary key constraints.
3. Churn categorical domain integrity.
4. Internal consistency of business KPI aggregates.
5. 3x3 segmentation exhaustive coverage (exactly 9 segments).
6. Segment accounts sum to total customer population.
7. Segment churned MRR sums to company churned MRR.
8. Independent Pandas vs. SQL numerical validation reconciliation.
"""

import sys
from pathlib import Path
import pytest
import sqlite3

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database_utils import get_connection, DEFAULT_DB_PATH
from src.database_loader import load_database
from src.validate_sql_results import validate_results


@pytest.fixture(scope="module")
def db_conn():
    """Ensure database is loaded and yield SQLite connection."""
    if not DEFAULT_DB_PATH.is_file():
        success, _, _ = load_database()
        assert success, "Failed to initialize database fixture."
    conn = get_connection(DEFAULT_DB_PATH)
    yield conn
    conn.close()


def test_database_row_count(db_conn):
    """1. Test that customers table contains exactly 7,043 rows."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM customers;")
    total_count = cursor.fetchone()[0]
    assert total_count == 7043, f"Expected 7,043 customers, found {total_count}"


def test_customer_id_uniqueness(db_conn):
    """2. Test that customerID is strictly unique with 0 duplicates and 0 nulls."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT customerID), COUNT(*) FROM customers;")
    distinct_ids, total_rows = cursor.fetchone()
    assert distinct_ids == total_rows == 7043

    cursor.execute("SELECT COUNT(*) FROM customers WHERE customerID IS NULL OR customerID = '';")
    null_ids = cursor.fetchone()[0]
    assert null_ids == 0


def test_churn_categories_valid(db_conn):
    """3. Test that Churn values are strictly in ('Yes', 'No')."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT DISTINCT Churn FROM customers;")
    categories = {row[0] for row in cursor.fetchall()}
    assert categories == {"Yes", "No"}, f"Unexpected churn categories: {categories}"


def test_kpi_internal_consistency(db_conn):
    """4. Test that business KPI calculations are internally mathematically consistent."""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_cust,
            SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) AS active_cust,
            SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_cust,
            ROUND(SUM(MonthlyCharges), 2) AS total_mrr,
            ROUND(SUM(CASE WHEN Churn = 'No' THEN MonthlyCharges ELSE 0.0 END), 2) AS active_mrr,
            ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
        FROM customers;
    """)
    row = cursor.fetchone()
    
    # Customer counts add up
    assert row["active_cust"] + row["churned_cust"] == row["total_cust"] == 7043
    
    # Financial MRR adds up within rounding tolerance
    reconstructed_mrr = round(row["active_mrr"] + row["churned_mrr"], 2)
    assert abs(reconstructed_mrr - row["total_mrr"]) <= 0.01


def test_segmentation_exactly_nine_combinations(db_conn):
    """5. Test that segmentation produces exactly 9 mutually exclusive segments."""
    cursor = db_conn.cursor()
    cursor.execute("""
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
            COUNT(*) AS cnt
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
    """)
    rows = cursor.fetchall()
    assert len(rows) == 9, f"Expected 9 segment combinations, got {len(rows)}"
    for r in rows:
        assert r["cnt"] > 0, f"Empty segment detected: {r['tenure_tier']} | {r['spend_tier']}"


def test_segment_customer_counts_sum_to_total(db_conn):
    """6. Test that segment account counts sum to exactly 7,043 customers."""
    cursor = db_conn.cursor()
    cursor.execute("""
        WITH seg AS (
            SELECT 
                COUNT(*) AS cnt
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
                END
        )
        SELECT SUM(cnt) FROM seg;
    """)
    summed_cust = cursor.fetchone()[0]
    assert summed_cust == 7043


def test_segment_churned_mrr_sums_to_total(db_conn):
    """7. Test that segment churned MRR sums to total company churned MRR."""
    cursor = db_conn.cursor()
    cursor.execute("""
        WITH seg AS (
            SELECT 
                SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END) AS seg_mrr
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
                END
        )
        SELECT ROUND(SUM(seg_mrr), 2) FROM seg;
    """)
    summed_seg_mrr = cursor.fetchone()[0]
    
    cursor.execute("SELECT ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) FROM customers;")
    total_churned_mrr = cursor.fetchone()[0]
    
    assert abs(summed_seg_mrr - total_churned_mrr) <= 0.01
    assert total_churned_mrr == 139130.85


def test_independent_sql_pandas_validation():
    """8. Test that independent SQL vs. Pandas validation passes with zero defects."""
    passed, audit_df = validate_results()
    assert passed is True
    failed_rows = audit_df[audit_df["Status"] == "FAIL"]
    assert len(failed_rows) == 0, f"Validation failures detected:\n{failed_rows}"


if __name__ == "__main__":
    pytest.main(["-v", str(__file__)])
