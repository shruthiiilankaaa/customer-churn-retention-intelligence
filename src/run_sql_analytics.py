"""
SQL Analytics Runner & Export Engine for Telco Customer Churn.

Executes all analytical SQL files sequentially against SQLite database,
displays formatted query outputs, and exports key business datasets to reports/sql_results/.
"""

import sys
import re
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database_utils import (
    get_connection,
    DEFAULT_DB_PATH,
    SQL_DIR,
    REPORTS_SQL_DIR,
)
from src.database_loader import load_database


def split_sql_statements(sql_text: str) -> List[str]:
    """
    Split SQL script by semicolons, filtering out comments and whitespace.
    """
    statements = []
    # Remove single line comments
    clean_lines = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        clean_lines.append(line)
    
    clean_text = "\n".join(clean_lines)
    raw_statements = clean_text.split(";")
    for stmt in raw_statements:
        trimmed = stmt.strip()
        if trimmed:
            statements.append(trimmed)
    return statements


def run_sql_file(conn, file_path: Path, verbose: bool = True) -> List[pd.DataFrame]:
    """Execute all queries in an SQL file and return resulting DataFrames."""
    if not file_path.is_file():
        raise FileNotFoundError(f"SQL file not found: {file_path.resolve()}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    statements = split_sql_statements(content)
    dfs = []

    if verbose:
        print("\n" + "=" * 80)
        print(f"  EXECUTING: {file_path.name} ({len(statements)} queries)")
        print("=" * 80)

    for i, stmt in enumerate(statements, 1):
        try:
            df = pd.read_sql_query(stmt, conn)
            dfs.append(df)
            if verbose:
                # Extract first comment or title if present
                print(f"\n--- Query {i}/{len(statements)} Result Preview ({len(df)} rows) ---")
                print(df.to_string(index=False))
        except Exception as exc:
            print(f"[ERROR] Statement {i} failed in {file_path.name}:\n{stmt}\nError: {exc}")
            raise exc

    return dfs


def run_all_analytics(
    db_path: Optional[Union[str, Path]] = None,
    export_dir: Optional[Union[str, Path]] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Orchestrate full SQL analytics execution and export deliverables.
    """
    target_db = Path(db_path) if db_path else DEFAULT_DB_PATH
    target_export = Path(export_dir) if export_dir else REPORTS_SQL_DIR
    target_export.mkdir(parents=True, exist_ok=True)

    if not target_db.is_file():
        print(f"[INFO] Database not found at {target_db}. Triggering loader...")
        success, _, _ = load_database(db_path=target_db)
        if not success:
            raise RuntimeError("Database loader failed.")

    conn = get_connection(target_db)
    results: Dict[str, Any] = {}

    try:
        # 1. Data Quality Checks
        dq_dfs = run_sql_file(conn, SQL_DIR / "01_data_quality.sql", verbose=verbose)
        results["data_quality"] = dq_dfs

        # 2. Business KPIs
        kpi_dfs = run_sql_file(conn, SQL_DIR / "02_business_kpis.sql", verbose=verbose)
        results["business_kpis"] = kpi_dfs
        # Export Business KPIs scorecard
        kpi_df = kpi_dfs[0]
        kpi_export_path = target_export / "business_kpis.csv"
        kpi_df.to_csv(kpi_export_path, index=False)
        print(f"\n[EXPORT] Saved {kpi_export_path.name}")

        # 3. Churn Analysis
        churn_dfs = run_sql_file(conn, SQL_DIR / "03_churn_analysis.sql", verbose=verbose)
        results["churn_analysis"] = churn_dfs
        # Export: churn_by_contract (query 1), churn_by_internet_service (query 2), churn_by_payment_method (query 3)
        contract_export_path = target_export / "churn_by_contract.csv"
        churn_dfs[0].to_csv(contract_export_path, index=False)
        print(f"[EXPORT] Saved {contract_export_path.name}")

        internet_export_path = target_export / "churn_by_internet_service.csv"
        churn_dfs[1].to_csv(internet_export_path, index=False)
        print(f"[EXPORT] Saved {internet_export_path.name}")

        payment_export_path = target_export / "churn_by_payment_method.csv"
        churn_dfs[2].to_csv(payment_export_path, index=False)
        print(f"[EXPORT] Saved {payment_export_path.name}")

        # 4. Customer Segmentation
        seg_dfs = run_sql_file(conn, SQL_DIR / "04_customer_segmentation.sql", verbose=verbose)
        results["segmentation"] = seg_dfs
        # Export: tenure_spend_segmentation (query 1) and advanced_segment_ranking (query 2)
        seg_export_path = target_export / "tenure_spend_segmentation.csv"
        seg_dfs[0].to_csv(seg_export_path, index=False)
        print(f"[EXPORT] Saved {seg_export_path.name}")

        seg_rank_export_path = target_export / "advanced_segment_ranking.csv"
        seg_dfs[1].to_csv(seg_rank_export_path, index=False)
        print(f"[EXPORT] Saved {seg_rank_export_path.name}")

        # 5. Advanced Analytics
        adv_dfs = run_sql_file(conn, SQL_DIR / "05_advanced_analytics.sql", verbose=verbose)
        results["advanced_analytics"] = adv_dfs

        print("\n" + "=" * 80)
        print(f"  SQL ANALYTICS EXECUTION & EXPORT COMPLETE")
        print(f"  Export directory: {target_export.resolve()}")
        print("=" * 80)

        return results

    finally:
        conn.close()


if __name__ == "__main__":
    run_all_analytics()
