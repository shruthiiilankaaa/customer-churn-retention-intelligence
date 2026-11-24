"""
Data Validation Module for Telco Customer Churn & Retention Intelligence.

Provides reusable, non-destructive validation functions to verify schema integrity,
type conformity, value constraints, and data hygiene on the raw and cleaned datasets.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

# Official IBM Telco Churn Schema
EXPECTED_COLUMNS: List[str] = [
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn",
]

ALLOWED_CATEGORICAL_VALUES: Dict[str, List[str]] = {
    "gender": ["Male", "Female"],
    "Partner": ["Yes", "No"],
    "Dependents": ["Yes", "No"],
    "PhoneService": ["Yes", "No"],
    "MultipleLines": ["Yes", "No", "No phone service"],
    "InternetService": ["DSL", "Fiber optic", "No"],
    "OnlineSecurity": ["Yes", "No", "No internet service"],
    "OnlineBackup": ["Yes", "No", "No internet service"],
    "DeviceProtection": ["Yes", "No", "No internet service"],
    "TechSupport": ["Yes", "No", "No internet service"],
    "StreamingTV": ["Yes", "No", "No internet service"],
    "StreamingMovies": ["Yes", "No", "No internet service"],
    "Contract": ["Month-to-month", "One year", "Two year"],
    "PaperlessBilling": ["Yes", "No"],
    "PaymentMethod": [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ],
}

ALLOWED_TARGET_VALUES: List[str] = ["Yes", "No"]


def validate_required_columns(df: pd.DataFrame) -> Dict[str, Any]:
    """Check that all required schema columns exist."""
    present_cols = set(df.columns)
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in present_cols]
    extra_cols = [col for col in df.columns if col not in EXPECTED_COLUMNS]

    is_valid = len(missing_cols) == 0
    return {
        "check": "required_columns",
        "is_valid": is_valid,
        "missing_columns": missing_cols,
        "extra_columns": extra_cols,
        "message": (
            "All expected columns present."
            if is_valid
            else f"Missing {len(missing_cols)} required columns: {missing_cols}"
        ),
    }


def validate_customer_ids(df: pd.DataFrame, id_col: str = "customerID") -> Dict[str, Any]:
    """Check customerID column for nulls and duplicate entries."""
    if id_col not in df.columns:
        return {
            "check": "customer_id_integrity",
            "is_valid": False,
            "message": f"Column '{id_col}' not found in DataFrame.",
        }

    total_records = len(df)
    null_ids = int(df[id_col].isna().sum())
    duplicate_count = int(df.duplicated(subset=[id_col]).sum())
    unique_ids = int(df[id_col].nunique())

    is_valid = (null_ids == 0) and (duplicate_count == 0)
    return {
        "check": "customer_id_integrity",
        "is_valid": is_valid,
        "total_records": total_records,
        "unique_ids": unique_ids,
        "null_id_count": null_ids,
        "duplicate_id_count": duplicate_count,
        "message": (
            f"Customer IDs are 100% unique ({unique_ids} unique, 0 duplicates, 0 nulls)."
            if is_valid
            else f"ID validation failed: {duplicate_count} duplicates, {null_ids} nulls."
        ),
    }


def validate_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect standard NaN / None missing values across all columns."""
    null_counts = df.isna().sum().to_dict()
    cols_with_nulls = {k: int(v) for k, v in null_counts.items() if v > 0}

    is_valid = len(cols_with_nulls) == 0
    return {
        "check": "missing_values",
        "is_valid": is_valid,
        "columns_with_nulls": cols_with_nulls,
        "total_missing_cells": int(sum(cols_with_nulls.values())),
        "message": (
            "No standard NaN missing values detected."
            if is_valid
            else f"Missing values found in {len(cols_with_nulls)} columns: {cols_with_nulls}"
        ),
    }


def validate_total_charges_blanks(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Detect blank or whitespace-only strings in the TotalCharges column.
    In the raw IBM dataset, TotalCharges contains 11 records with whitespace ' '
    corresponding to new customers with tenure == 0.
    """
    if "TotalCharges" not in df.columns:
        return {
            "check": "total_charges_blanks",
            "is_valid": False,
            "message": "Column 'TotalCharges' not found in DataFrame.",
        }

    series = df["TotalCharges"]
    if pd.api.types.is_numeric_dtype(series):
        # Already converted to numeric
        nan_count = int(series.isna().sum())
        return {
            "check": "total_charges_blanks",
            "is_valid": nan_count == 0,
            "blank_or_whitespace_count": 0,
            "numeric_nan_count": nan_count,
            "message": f"TotalCharges is numeric with {nan_count} NaNs.",
        }

    # If string or object, detect whitespace-only strings
    blank_mask = series.astype(str).str.strip() == ""
    blank_count = int(blank_mask.sum())

    # Check relationship to tenure == 0 if tenure exists
    tenure_zero_blanks = 0
    if "tenure" in df.columns and blank_count > 0:
        tenure_zero_blanks = int((blank_mask & (df["tenure"] == 0)).sum())

    is_valid = blank_count == 0
    return {
        "check": "total_charges_blanks",
        "is_valid": is_valid,
        "blank_or_whitespace_count": blank_count,
        "tenure_zero_correlation_count": tenure_zero_blanks,
        "message": (
            "No blank/whitespace strings detected in TotalCharges."
            if is_valid
            else (
                f"Detected {blank_count} blank/whitespace string values in TotalCharges "
                f"({tenure_zero_blanks} have tenure = 0)."
            )
        ),
    }


def validate_data_types(df: pd.DataFrame) -> Dict[str, Any]:
    """Verify expected fundamental data types for raw or cleaned dataset."""
    type_issues = []

    # Tenure must be numeric
    if "tenure" in df.columns and not pd.api.types.is_numeric_dtype(df["tenure"]):
        type_issues.append("tenure is not numeric")

    # MonthlyCharges must be numeric
    if "MonthlyCharges" in df.columns and not pd.api.types.is_numeric_dtype(df["MonthlyCharges"]):
        type_issues.append("MonthlyCharges is not numeric")

    # SeniorCitizen must be integer or binary
    if "SeniorCitizen" in df.columns and not pd.api.types.is_numeric_dtype(df["SeniorCitizen"]):
        type_issues.append("SeniorCitizen is not numeric")

    is_valid = len(type_issues) == 0
    return {
        "check": "data_types",
        "is_valid": is_valid,
        "type_issues": type_issues,
        "message": "Data types conform to expected types." if is_valid else f"Type issues: {type_issues}",
    }


def validate_numerical_ranges(df: pd.DataFrame) -> Dict[str, Any]:
    """Check that numerical values fall within reasonable, non-negative domains."""
    range_issues = []

    if "tenure" in df.columns and pd.api.types.is_numeric_dtype(df["tenure"]):
        neg_tenure = int((df["tenure"] < 0).sum())
        if neg_tenure > 0:
            range_issues.append(f"{neg_tenure} negative tenure records")

    if "MonthlyCharges" in df.columns and pd.api.types.is_numeric_dtype(df["MonthlyCharges"]):
        neg_monthly = int((df["MonthlyCharges"] < 0).sum())
        if neg_monthly > 0:
            range_issues.append(f"{neg_monthly} negative MonthlyCharges records")

    if "TotalCharges" in df.columns and pd.api.types.is_numeric_dtype(df["TotalCharges"]):
        neg_total = int((df["TotalCharges"] < 0).sum())
        if neg_total > 0:
            range_issues.append(f"{neg_total} negative TotalCharges records")

    if "SeniorCitizen" in df.columns and pd.api.types.is_numeric_dtype(df["SeniorCitizen"]):
        invalid_sc = int((~df["SeniorCitizen"].isin([0, 1])).sum())
        if invalid_sc > 0:
            range_issues.append(f"{invalid_sc} SeniorCitizen records outside [0, 1]")

    is_valid = len(range_issues) == 0
    return {
        "check": "numerical_ranges",
        "is_valid": is_valid,
        "range_issues": range_issues,
        "message": "All numerical ranges are valid (non-negative)." if is_valid else f"Range issues: {range_issues}",
    }


def validate_categorical_values(df: pd.DataFrame) -> Dict[str, Any]:
    """Check categorical columns against authorized enumeration of values."""
    invalid_categories: Dict[str, List[Any]] = {}

    for col, allowed in ALLOWED_CATEGORICAL_VALUES.items():
        if col in df.columns:
            # Drop nulls before checking unique values
            unique_vals = df[col].dropna().unique().tolist()
            unexpected = [val for val in unique_vals if val not in allowed]
            if unexpected:
                invalid_categories[col] = unexpected

    is_valid = len(invalid_categories) == 0
    return {
        "check": "categorical_values",
        "is_valid": is_valid,
        "invalid_categories": invalid_categories,
        "message": (
            "All categorical columns contain authorized domain values."
            if is_valid
            else f"Invalid categorical values detected in: {list(invalid_categories.keys())}"
        ),
    }


def validate_target_consistency(df: pd.DataFrame, target_col: str = "Churn") -> Dict[str, Any]:
    """Verify target variable presence, missing values, and permissible values."""
    if target_col not in df.columns:
        return {
            "check": "target_consistency",
            "is_valid": False,
            "message": f"Target column '{target_col}' not present.",
        }

    null_count = int(df[target_col].isna().sum())
    unique_vals = df[target_col].dropna().unique().tolist()
    unexpected_vals = [v for v in unique_vals if v not in ALLOWED_TARGET_VALUES]

    is_valid = (null_count == 0) and (len(unexpected_vals) == 0)
    distribution = df[target_col].value_counts(normalize=True).to_dict()

    return {
        "check": "target_consistency",
        "is_valid": is_valid,
        "null_count": null_count,
        "unique_values": unique_vals,
        "unexpected_values": unexpected_vals,
        "class_distribution": distribution,
        "message": (
            f"Target '{target_col}' valid. Class breakdown: {distribution}"
            if is_valid
            else f"Target validation failed. Nulls: {null_count}, Unexpected: {unexpected_vals}"
        ),
    }


def run_full_validation(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Run the full battery of validation checks without modifying the input DataFrame.

    Returns:
        Structured dictionary summary of validation results.
    """
    checks = [
        validate_required_columns(df),
        validate_customer_ids(df),
        validate_missing_values(df),
        validate_total_charges_blanks(df),
        validate_data_types(df),
        validate_numerical_ranges(df),
        validate_categorical_values(df),
        validate_target_consistency(df),
    ]

    all_passed = all(c["is_valid"] for c in checks if c["check"] != "total_charges_blanks")
    # Note: total_charges_blanks is expected in raw data (11 rows), will be cleaned in pipeline

    return {
        "summary": {
            "total_records": len(df),
            "total_columns": len(df.columns),
            "all_core_checks_passed": all_passed,
        },
        "detailed_checks": checks,
    }


def format_validation_report(report: Dict[str, Any]) -> str:
    """Format the validation output as a human-readable text report."""
    lines = [
        "=" * 70,
        "  TELCO DATA VALIDATION AUDIT REPORT",
        "=" * 70,
        f"Records: {report['summary']['total_records']} | Columns: {report['summary']['total_columns']}",
        "-" * 70,
    ]
    for check in report["detailed_checks"]:
        status = "PASSED" if check["is_valid"] else "FLAGGED"
        icon = "[OK]" if check["is_valid"] else "[WARN]"
        lines.append(f"{icon} {check['check'].upper():<26}: {status} - {check['message']}")
    lines.append("=" * 70)
    return "\n".join(lines)
