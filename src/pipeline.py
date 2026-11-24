"""
Data Foundation Pipeline Runner for Telco Churn & Retention Analytics.

Executes the complete data ingestion, schema validation, cleaning, and persistence workflow.
If the raw dataset is missing, provides clear step-by-step acquisition guidance.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_raw_data, DatasetNotFoundError
from src.data_validation import run_full_validation, format_validation_report
from src.data_cleaning import run_cleaning_pipeline


def execute_pipeline():
    """Execute the full data foundation workflow."""
    print("=" * 70)
    print("  CUSTOMER CHURN & RETENTION INTELLIGENCE: DATA FOUNDATION PIPELINE")
    print("=" * 70)

    # 1. Dataset Ingestion Check
    try:
        raw_df = load_raw_data()
    except DatasetNotFoundError as err:
        print("\n" + str(err))
        print("\n[RESULT] Pipeline halted safely. No files or state were corrupted.")
        sys.exit(1)

    # 2. Raw Data Validation Audit
    print("\n[STEP 1/3] Running Raw Data Schema & Hygiene Validation...")
    raw_validation = run_full_validation(raw_df)
    print(format_validation_report(raw_validation))

    # 3. Data Cleaning Pipeline
    print("\n[STEP 2/3] Executing Cleaning & Type Enforcement Pipeline...")
    cleaned_df, dest_path, audit = run_cleaning_pipeline(raw_df)
    for action in audit["actions_taken"]:
        print(f"  -> {action}")

    # 4. Post-Cleaning Validation
    print("\n[STEP 3/3] Validating Cleaned Dataset...")
    cleaned_validation = run_full_validation(cleaned_df)
    print(format_validation_report(cleaned_validation))

    print("\n" + "=" * 70)
    print(f"  DATA FOUNDATION PIPELINE COMPLETE")
    print(f"  Cleaned dataset saved at: {dest_path}")
    print(f"  Total records: {len(cleaned_df)} | Total features: {len(cleaned_df.columns)}")
    print("=" * 70)


if __name__ == "__main__":
    execute_pipeline()
