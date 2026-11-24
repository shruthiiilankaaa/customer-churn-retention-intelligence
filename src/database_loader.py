"""
Database Ingestion & Loader for Telco Customer Churn & Retention Intelligence.

Loads the cleaned dataset (data/processed/telco_churn_cleaned.csv) into SQLite
database (database/telco_churn.db), executes DDL schema, verifies primary-key uniqueness,
and audits record counts. Repeatable and idempotent.
"""

import sys
from pathlib import Path
from typing import Optional, Union, Tuple
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database_utils import (
    get_connection,
    execute_script,
    DEFAULT_DB_PATH,
    DEFAULT_PROCESSED_CSV,
    SQL_DIR,
)

SCHEMA_FILE = SQL_DIR / "schema.sql"


def load_database(
    csv_path: Optional[Union[str, Path]] = None,
    db_path: Optional[Union[str, Path]] = None,
    schema_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, int, str]:
    """
    Ingest cleaned CSV into SQLite table 'customers'.

    Parameters:
        csv_path: Path to cleaned CSV.
        db_path: Destination SQLite DB file.
        schema_path: DDL schema file.

    Returns:
        Tuple of (success_flag, inserted_row_count, summary_message)
    """
    target_csv = Path(csv_path) if csv_path else DEFAULT_PROCESSED_CSV
    target_db = Path(db_path) if db_path else DEFAULT_DB_PATH
    target_schema = Path(schema_path) if schema_path else SCHEMA_FILE

    print("=" * 70)
    print("  TELCO DATABASE LOADER: SQLITE INGESTION PIPELINE")
    print("=" * 70)

    # 1. Verify existence of cleaned CSV
    if not target_csv.is_file():
        err_msg = (
            f"[ERROR] Cleaned dataset not found at: {target_csv.resolve()}\n"
            "Please run the data foundation pipeline first: python src/pipeline.py"
        )
        print(err_msg)
        return False, 0, err_msg

    print(f"[INFO] Reading processed dataset from: {target_csv.resolve()}")
    df = pd.read_csv(target_csv)
    raw_len = len(df)
    print(f"[INFO] Loaded {raw_len:,} rows with {len(df.columns)} columns.")

    # 2. Connect to SQLite & execute schema
    print(f"[INFO] Connecting to SQLite database at: {target_db.resolve()}")
    conn = get_connection(target_db)

    try:
        with open(target_schema, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        print(f"[INFO] Applying DDL schema from: {target_schema.name}")
        execute_script(conn, schema_sql)

        # 3. Insert records using parameterized executemany for high performance & safety
        cols = list(df.columns)
        placeholders = ", ".join(["?"] * len(cols))
        col_names = ", ".join(cols)
        insert_sql = f"INSERT INTO customers ({col_names}) VALUES ({placeholders});"

        records = [tuple(row) for row in df.itertuples(index=False, name=None)]
        cursor = conn.cursor()
        cursor.executemany(insert_sql, records)
        conn.commit()

        # 4. Verify row count and primary-key uniqueness
        cursor.execute("SELECT COUNT(*), COUNT(DISTINCT customerID) FROM customers;")
        total_rows, distinct_ids = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) FROM customers WHERE customerID IS NULL;")
        null_ids = cursor.fetchone()[0]

        print("-" * 70)
        print("  DATABASE INGESTION AUDIT")
        print("-" * 70)
        print(f"Total CSV Rows Read      : {raw_len:,}")
        print(f"Total Rows in 'customers': {total_rows:,}")
        print(f"Unique 'customerID' Count: {distinct_ids:,}")
        print(f"Null 'customerID' Count  : {null_ids}")

        assert total_rows == raw_len, f"Mismatch: expected {raw_len} rows, got {total_rows}"
        assert total_rows == distinct_ids, f"Duplicate IDs detected: {total_rows - distinct_ids}"
        assert null_ids == 0, f"Null customer IDs found: {null_ids}"

        summary = (
            f"Successfully loaded and verified {total_rows:,} records into "
            f"table 'customers' in {target_db.name}."
        )
        print(f"[SUCCESS] {summary}")
        print("=" * 70)
        return True, total_rows, summary

    except Exception as exc:
        conn.rollback()
        err = f"Failed to load database: {exc}"
        print(f"[FAILURE] {err}")
        return False, 0, err
    finally:
        conn.close()


if __name__ == "__main__":
    success, count, msg = load_database()
    if not success:
        sys.exit(1)
