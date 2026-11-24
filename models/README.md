# Machine Learning Model Artifacts

This directory documents the serialized models and artifact assets.

> [!NOTE]
> To preserve 100% backward compatibility with the existing [streamlit_app.py](../streamlit_app.py), the active runtime model artifacts remain hosted at the repository root:
> - `telco_final_model.joblib` (Trained Random Forest Classifier)
> - `preprocessor.joblib` (Fitted Scikit-Learn preprocessing pipeline)
> - `model_metadata.joblib` (Serialized categorical, numerical, and target schema dictionaries)

### Production Model Specification
- **Algorithm**: `RandomForestClassifier` (Scikit-Learn) with hyperparameter tuning & class weight balancing.
- **Preprocessing Pipeline**:
  - Categorical Features: One-Hot Encoding (`OneHotEncoder`)
  - Numerical Features: Standard Scaling (`StandardScaler`)
  - Engineered Features: `ContractMonths`, `SpendingRate`, `TenureGroup`, `TotalServices`
- **Explainability**: Integrated TreeExplainer via SHAP (`shap.TreeExplainer`).
