"""
Data Loader Module for Telco Customer Churn & Retention Intelligence.

This module provides reproducible functions to locate and load the raw IBM Telco
Customer Churn dataset from the data/raw/ directory. If the file is not found,
it raises a descriptive DatasetNotFoundError with actionable download instructions.
"""

import os
from pathlib import Path
from typing import Optional, Union
import pandas as pd


class DatasetNotFoundError(FileNotFoundError):
    """Custom exception raised when the raw dataset cannot be found on disk."""
    pass


# Default locations and accepted filenames for the raw dataset
DEFAULT_RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
ACCEPTED_RAW_FILENAMES = [
    "WA_Fn-UseC_-Telco-Customer-Churn.csv",
    "telco_customer_churn.csv",
    "Telco-Customer-Churn.csv"
]


def find_raw_dataset_path(raw_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Search the raw data directory for recognized Telco Churn CSV filenames.

    Parameters:
        raw_dir: Path to directory containing raw data. Defaults to data/raw/.

    Returns:
        Path to the raw CSV file.

    Raises:
        DatasetNotFoundError: If no recognized raw dataset CSV is found.
    """
    search_dir = Path(raw_dir) if raw_dir else DEFAULT_RAW_DIR

    if not search_dir.exists():
        search_dir.mkdir(parents=True, exist_ok=True)

    for filename in ACCEPTED_RAW_FILENAMES:
        candidate = search_dir / filename
        if candidate.is_file():
            return candidate

    # Also check if any CSV file exists in raw_dir
    csv_files = list(search_dir.glob("*.csv"))
    if csv_files:
        return csv_files[0]

    # If missing, provide explicit instructions
    expected_paths = "\n  - ".join([str(search_dir / fn) for fn in ACCEPTED_RAW_FILENAMES])
    raise DatasetNotFoundError(
        f"\n[ERROR] Raw IBM Telco Customer Churn dataset not found!\n"
        f"Expected one of the following file paths:\n  - {expected_paths}\n\n"
        f"ACTION REQUIRED:\n"
        f"1. Download the IBM Telco Customer Churn dataset from Kaggle or IBM Community:\n"
        f"   - Kaggle: https://www.kaggle.com/datasets/blastchar/telco-customer-churn\n"
        f"2. Place the CSV file into:\n"
        f"   {search_dir.resolve()}\n"
        f"3. Name the file 'WA_Fn-UseC_-Telco-Customer-Churn.csv' or 'telco_customer_churn.csv'.\n"
        f"4. Re-run the data ingestion/cleaning pipeline."
    )


def load_raw_data(file_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """
    Load the raw Telco Customer Churn dataset into a Pandas DataFrame.

    Parameters:
        file_path: Optional explicit path to the CSV file. If None, searches data/raw/.

    Returns:
        pd.DataFrame containing the raw dataset.
    """
    path = Path(file_path) if file_path else find_raw_dataset_path()
    if not path.is_file():
        raise DatasetNotFoundError(f"Specified raw file does not exist: {path}")

    print(f"[INFO] Loading raw dataset from: {path.resolve()}")
    df = pd.read_csv(path, dtype={"customerID": str})
    print(f"[INFO] Successfully loaded raw dataset. Shape: {df.shape[0]} rows, {df.shape[1]} columns.")
    return df


if __name__ == "__main__":
    try:
        data = load_raw_data()
        print(f"[SUCCESS] Dataset loaded successfully with {len(data)} rows.")
    except DatasetNotFoundError as err:
        print(err)
