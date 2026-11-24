-- ==============================================================================
-- 01_DATA_QUALITY.SQL: Data Hygiene, Schema Conformance & Integrity Audits
-- Project: Telco Customer Churn & Retention Intelligence
-- Database: SQLite (database/telco_churn.db)
-- Table: customers
-- ==============================================================================

-- 1. Total records in database
-- Checks baseline row volume against source dataset
SELECT 
    COUNT(*) AS total_records
FROM customers;

-- 2. Distinct customer ID count
-- Confirms whether all rows represent distinct customer identifiers
SELECT 
    COUNT(DISTINCT customerID) AS distinct_customer_ids
FROM customers;

-- 3. Duplicate customer ID check
-- Checks for duplicate primary keys (expected: 0 rows returned)
SELECT 
    customerID,
    COUNT(*) AS occurrence_count
FROM customers
GROUP BY customerID
HAVING COUNT(*) > 1;

-- 4. NULL / Missing value counts across all critical attributes
-- Ensures zero missing or unhandled values across all dimensions
SELECT 
    SUM(CASE WHEN customerID IS NULL THEN 1 ELSE 0 END) AS null_customer_id,
    SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) AS null_gender,
    SUM(CASE WHEN SeniorCitizen IS NULL THEN 1 ELSE 0 END) AS null_senior_citizen,
    SUM(CASE WHEN tenure IS NULL THEN 1 ELSE 0 END) AS null_tenure,
    SUM(CASE WHEN Contract IS NULL THEN 1 ELSE 0 END) AS null_contract,
    SUM(CASE WHEN InternetService IS NULL THEN 1 ELSE 0 END) AS null_internet_service,
    SUM(CASE WHEN PaymentMethod IS NULL THEN 1 ELSE 0 END) AS null_payment_method,
    SUM(CASE WHEN MonthlyCharges IS NULL THEN 1 ELSE 0 END) AS null_monthly_charges,
    SUM(CASE WHEN TotalCharges IS NULL THEN 1 ELSE 0 END) AS null_total_charges,
    SUM(CASE WHEN Churn IS NULL THEN 1 ELSE 0 END) AS null_churn
FROM customers;

-- 5. Target variable (Churn) distribution & integrity
-- Confirms valid binary classes ('Yes', 'No') and baseline proportion
SELECT 
    Churn,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 2) AS percentage
FROM customers
GROUP BY Churn;

-- 6. Categorical domain validity checks
-- Flags any unexpected categorical entries across key business attributes
SELECT 
    'Invalid Contract' AS check_name,
    COUNT(*) AS invalid_count
FROM customers
WHERE Contract NOT IN ('Month-to-month', 'One year', 'Two year')

UNION ALL

SELECT 
    'Invalid InternetService' AS check_name,
    COUNT(*) AS invalid_count
FROM customers
WHERE InternetService NOT IN ('DSL', 'Fiber optic', 'No')

UNION ALL

SELECT 
    'Invalid PaymentMethod' AS check_name,
    COUNT(*) AS invalid_count
FROM customers
WHERE PaymentMethod NOT IN (
    'Electronic check', 
    'Mailed check', 
    'Bank transfer (automatic)', 
    'Credit card (automatic)'
)

UNION ALL

SELECT 
    'Invalid Churn' AS check_name,
    COUNT(*) AS invalid_count
FROM customers
WHERE Churn NOT IN ('Yes', 'No');

-- 7. Numerical domain & range constraints
-- Validates non-negativity and boundary logic (tenure 0-72, senior citizen in {0,1})
SELECT 
    SUM(CASE WHEN tenure < 0 THEN 1 ELSE 0 END) AS negative_tenure_count,
    SUM(CASE WHEN tenure > 100 THEN 1 ELSE 0 END) AS excessive_tenure_count,
    SUM(CASE WHEN MonthlyCharges < 0 THEN 1 ELSE 0 END) AS negative_monthly_charges_count,
    SUM(CASE WHEN TotalCharges < 0 THEN 1 ELSE 0 END) AS negative_total_charges_count,
    SUM(CASE WHEN SeniorCitizen NOT IN (0, 1) THEN 1 ELSE 0 END) AS invalid_senior_citizen_count
FROM customers;

-- 8. Zero tenure audit
-- Verifies new customers with tenure = 0 and confirms TotalCharges = 0.0 imputation
SELECT 
    customerID,
    tenure,
    MonthlyCharges,
    TotalCharges,
    Contract,
    PaymentMethod,
    Churn
FROM customers
WHERE tenure = 0;

-- 9. TotalCharges and tenure relationship consistency check
-- Audits relationship: customers with tenure >= 1 should have positive TotalCharges
-- and for tenure = 0, TotalCharges must be 0.0 (not treated as missing data)
SELECT 
    SUM(CASE WHEN tenure = 0 AND TotalCharges != 0 THEN 1 ELSE 0 END) AS tenure_zero_nonzero_total_charges,
    SUM(CASE WHEN tenure > 0 AND TotalCharges = 0 THEN 1 ELSE 0 END) AS tenure_pos_zero_total_charges,
    SUM(CASE WHEN tenure >= 1 AND TotalCharges < (MonthlyCharges * 0.5) THEN 1 ELSE 0 END) AS total_charges_under_half_monthly
FROM customers;
