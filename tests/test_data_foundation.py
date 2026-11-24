"""
Unit Tests for Data Foundation: Loader, Validation, and Cleaning Modules.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import find_raw_dataset_path, load_raw_data, DatasetNotFoundError
from src.data_validation import (
    validate_required_columns,
    validate_customer_ids,
    validate_total_charges_blanks,
    validate_categorical_values,
    validate_target_consistency,
    run_full_validation,
    EXPECTED_COLUMNS,
)
from src.data_cleaning import clean_telco_data


def test_missing_dataset_raises_error(tmp_path):
    """Verify that find_raw_dataset_path raises DatasetNotFoundError with instructions when file missing."""
    with pytest.raises(DatasetNotFoundError) as exc_info:
        find_raw_dataset_path(raw_dir=tmp_path)
    assert "Raw IBM Telco Customer Churn dataset not found" in str(exc_info.value)
    assert "Kaggle" in str(exc_info.value)


def test_schema_validation_catches_missing_columns():
    """Verify required column validation detects missing columns."""
    incomplete_df = pd.DataFrame({"customerID": ["C1"], "gender": ["Male"]})
    result = validate_required_columns(incomplete_df)
    assert result["is_valid"] is False
    assert len(result["missing_columns"]) > 0
    assert "Churn" in result["missing_columns"]


def test_customer_id_validation_catches_duplicates():
    """Verify customerID validation detects duplicates and nulls."""
    duplicate_df = pd.DataFrame({"customerID": ["C1", "C1", None]})
    result = validate_customer_ids(duplicate_df)
    assert result["is_valid"] is False
    assert result["duplicate_id_count"] == 1
    assert result["null_id_count"] == 1


def test_total_charges_blank_detection_and_cleaning():
    """Verify TotalCharges whitespace detection and cleaning logic (tenure=0 => 0.0)."""
    sample_data = {col: ["No"] * 3 for col in EXPECTED_COLUMNS}
    sample_data["customerID"] = ["C1", "C2", "C3"]
    sample_data["gender"] = ["Male", "Female", "Male"]
    sample_data["SeniorCitizen"] = [0, 1, 0]
    sample_data["tenure"] = [0, 12, 24]
    sample_data["MonthlyCharges"] = [25.0, 70.0, 95.0]
    sample_data["TotalCharges"] = [" ", "840.0", "2280.0"]
    sample_data["Contract"] = ["Month-to-month", "One year", "Two year"]
    sample_data["PaymentMethod"] = [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
    ]
    sample_data["Churn"] = ["No", "Yes", "No"]

    df = pd.DataFrame(sample_data)

    # 1. Validation catches the blank
    val_result = validate_total_charges_blanks(df)
    assert val_result["is_valid"] is False
    assert val_result["blank_or_whitespace_count"] == 1
    assert val_result["tenure_zero_correlation_count"] == 1

    # 2. Cleaning fixes the blank, preserves original df unchanged
    cleaned_df, audit = clean_telco_data(df)

    # Raw df should still have string and ' '
    assert df["TotalCharges"].iloc[0] == " "
    assert isinstance(df["TotalCharges"].iloc[0], str)

    # Cleaned df should have numeric 0.0
    assert cleaned_df["TotalCharges"].iloc[0] == 0.0
    assert pd.api.types.is_float_dtype(cleaned_df["TotalCharges"])
    assert cleaned_df["tenure"].dtype == np.int64
    assert audit["total_charges_cleaned"]["tenure_zero_imputed_as_zero"] == 1
    assert len(audit["unresolved_nulls"]) == 0


if __name__ == "__main__":
    pytest.main(["-v", str(__file__)])
