"""
Data Cleaning & Preprocessing Pipeline for Telco Customer Churn.

This module cleans raw IBM Telco Customer Churn data into a standardized,
business-ready analytical table:
- Strips trailing/leading string whitespace
- Resolves whitespace values in TotalCharges (converts tenure=0 to 0.0)
- Enforces strict data types (TotalCharges float, tenure int, MonthlyCharges float)
- Preserves the original customerID untouched
- Exports the cleaned dataset to data/processed/
"""

from pathlib import Path
from typing import Optional, Union, Tuple, Dict, Any
import numpy as np
import pandas as pd

DEFAULT_PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
DEFAULT_CLEANED_FILENAME = "telco_churn_cleaned.csv"


def clean_telco_data(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Clean the raw Telco DataFrame in a reproducible, non-destructive manner.

    Parameters:
        raw_df: The raw input DataFrame loaded from the CSV.

    Returns:
        Tuple of (cleaned_df, cleaning_audit_log)
    """
    # 1. Create deep copy to strictly preserve raw data
    df = raw_df.copy(deep=True)
    audit: Dict[str, Any] = {
        "raw_record_count": len(df),
        "raw_column_count": len(df.columns),
        "actions_taken": [],
    }

    # 2. Strip whitespace from string/object columns (preserving customerID)
    str_cols = df.select_dtypes(include=["object"]).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
    audit["actions_taken"].append(f"Trimmed whitespace across {len(str_cols)} string columns.")

    # 3. Clean TotalCharges:
    # In raw IBM Telco, TotalCharges is stored as object/string with 11 blank spaces ' '
    # representing customers with tenure == 0 (new signups with no completed bill yet).
    if "TotalCharges" in df.columns:
        # Identify whitespace/empty cells
        blank_mask = df["TotalCharges"].isin(["", " ", "nan", "NaN", "None"])
        blank_count = int(blank_mask.sum())

        if blank_count > 0:
            # Check how many have tenure == 0
            tenure_zero_count = int((blank_mask & (df["tenure"] == 0)).sum()) if "tenure" in df.columns else 0
            
            # Replace empty string with NaN temporarily, then impute 0.0 for tenure == 0
            df.loc[blank_mask, "TotalCharges"] = np.nan
            df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
            
            # Impute 0.0 for new customers (tenure == 0)
            df.loc[df["TotalCharges"].isna() & (df["tenure"] == 0), "TotalCharges"] = 0.0
            
            audit["total_charges_cleaned"] = {
                "blank_count": blank_count,
                "tenure_zero_imputed_as_zero": tenure_zero_count,
                "remaining_nans": int(df["TotalCharges"].isna().sum()),
            }
            audit["actions_taken"].append(
                f"Resolved {blank_count} whitespace values in TotalCharges (imputed 0.0 for tenure=0 new signups)."
            )
        else:
            df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
            audit["actions_taken"].append("Converted TotalCharges to numeric float64.")

    # 4. Enforce canonical data types
    if "tenure" in df.columns:
        df["tenure"] = pd.to_numeric(df["tenure"], errors="raise").astype("int64")

    if "MonthlyCharges" in df.columns:
        df["MonthlyCharges"] = pd.to_numeric(df["MonthlyCharges"], errors="raise").astype("float64")

    if "SeniorCitizen" in df.columns:
        df["SeniorCitizen"] = pd.to_numeric(df["SeniorCitizen"], errors="raise").astype("int64")

    if "TotalCharges" in df.columns:
        df["TotalCharges"] = df["TotalCharges"].astype("float64")

    audit["actions_taken"].append("Enforced explicit data types (tenure: int64, charges: float64).")

    # 5. Verify customerID integrity
    if "customerID" in df.columns:
        audit["customer_id_unique"] = bool(df["customerID"].nunique() == len(df))
        audit["customer_id_count"] = len(df["customerID"])

    # 6. Final verification of missing values
    post_null_counts = df.isna().sum().to_dict()
    unresolved_nulls = {k: int(v) for k, v in post_null_counts.items() if v > 0}
    audit["unresolved_nulls"] = unresolved_nulls
    audit["cleaned_record_count"] = len(df)
    audit["cleaned_column_count"] = len(df.columns)

    return df, audit


def save_cleaned_data(
    df: pd.DataFrame,
    output_dir: Optional[Union[str, Path]] = None,
    filename: str = DEFAULT_CLEANED_FILENAME,
) -> Path:
    """
    Save the cleaned DataFrame to the processed directory.

    Parameters:
        df: The cleaned DataFrame.
        output_dir: Directory where the CSV should be saved. Defaults to data/processed/.
        filename: Destination filename.

    Returns:
        Path of the saved CSV.
    """
    target_dir = Path(output_dir) if output_dir else DEFAULT_PROCESSED_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    out_path = target_dir / filename

    df.to_csv(out_path, index=False)
    print(f"[INFO] Cleaned dataset saved to: {out_path.resolve()}")
    return out_path


def run_cleaning_pipeline(
    raw_df: pd.DataFrame,
    output_dir: Optional[Union[str, Path]] = None,
) -> Tuple[pd.DataFrame, Path, Dict[str, Any]]:
    """
    Execute end-to-end cleaning and persistence.

    Parameters:
        raw_df: Raw input DataFrame.
        output_dir: Destination folder.

    Returns:
        Tuple of (cleaned_df, destination_path, audit_log)
    """
    cleaned_df, audit = clean_telco_data(raw_df)
    dest_path = save_cleaned_data(cleaned_df, output_dir=output_dir)
    return cleaned_df, dest_path, audit
