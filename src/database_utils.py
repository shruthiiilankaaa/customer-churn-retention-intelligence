"""
Database Utilities Module for Telco Customer Churn & Retention Intelligence.

Provides reusable SQLite connection handling, script execution, query execution,
and DataFrame conversion utilities.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Union, Any, List, Tuple
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_DIR = PROJECT_ROOT / "database"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "telco_churn.db"
DEFAULT_PROCESSED_CSV = PROJECT_ROOT / "data" / "processed" / "telco_churn_cleaned.csv"
SQL_DIR = PROJECT_ROOT / "sql"
REPORTS_SQL_DIR = PROJECT_ROOT / "reports" / "sql_results"


def get_connection(db_path: Optional[Union[str, Path]] = None) -> sqlite3.Connection:
    """
    Establish and return a connection to the SQLite database.
    Ensures directory exists and enables foreign keys and row access by name.
    """
    target_path = Path(db_path) if db_path else DEFAULT_DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def execute_script(conn: sqlite3.Connection, sql_text: str) -> None:
    """Execute multi-statement SQL script."""
    cursor = conn.cursor()
    cursor.executescript(sql_text)
    conn.commit()


def execute_query(
    conn: sqlite3.Connection,
    query: str,
    params: Optional[Union[Tuple, List, dict]] = None
) -> List[sqlite3.Row]:
    """Execute a parameterized query and return fetched rows."""
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    return cursor.fetchall()


def query_to_dataframe(
    conn: sqlite3.Connection,
    query: str,
    params: Optional[Union[Tuple, List, dict]] = None
) -> pd.DataFrame:
    """Execute query and return results as a Pandas DataFrame."""
    return pd.read_sql_query(query, conn, params=params)
