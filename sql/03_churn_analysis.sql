-- ==============================================================================
-- 03_CHURN_ANALYSIS.SQL: Multi-Dimensional Churn Driver & Segment Analysis
-- Project: Telco Customer Churn & Retention Intelligence
-- Database: SQLite (database/telco_churn.db)
-- Table: customers
-- ==============================================================================

-- 1. Churn Rate by Contract Type
-- Evaluates retention performance across contractual commitment terms.
SELECT 
    Contract,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customer_count,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_charges,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
FROM customers
GROUP BY Contract
ORDER BY churn_rate_pct DESC;

-- 2. Churn Rate by Internet Service
-- Evaluates retention across fiber optic, DSL, and non-internet customer tiers.
SELECT 
    InternetService,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customer_count,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_charges,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
FROM customers
GROUP BY InternetService
ORDER BY churn_rate_pct DESC;

-- 3. Churn Rate by Payment Method
-- Analyzes payment friction: electronic check vs. automated payment rails.
SELECT 
    PaymentMethod,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customer_count,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_charges,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
FROM customers
GROUP BY PaymentMethod
ORDER BY churn_rate_pct DESC;

-- 4. Churn Rate by TechSupport Subscription
-- Evaluates protective retention effect of premium technical support.
SELECT 
    TechSupport,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customer_count,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_charges,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
FROM customers
GROUP BY TechSupport
ORDER BY churn_rate_pct DESC;

-- 5. Churn Rate by OnlineSecurity Subscription
-- Evaluates retention benefit of cybersecurity value-added services.
SELECT 
    OnlineSecurity,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customer_count,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_charges,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
FROM customers
GROUP BY OnlineSecurity
ORDER BY churn_rate_pct DESC;

-- 6. Churn Rate by Gender
-- Verifies independence of churn propensity across gender segments.
SELECT 
    gender,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customer_count,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_charges,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
FROM customers
GROUP BY gender
ORDER BY churn_rate_pct DESC;

-- 7. Churn Rate by Tenure Cohort Bands
-- Highlights early-tenure attrition cliffs vs. mature account stability.
SELECT 
    CASE 
        WHEN tenure <= 6 THEN '0-6 Months'
        WHEN tenure <= 12 THEN '7-12 Months'
        WHEN tenure <= 24 THEN '13-24 Months'
        WHEN tenure <= 36 THEN '25-36 Months'
        WHEN tenure <= 48 THEN '37-48 Months'
        WHEN tenure <= 60 THEN '49-60 Months'
        ELSE '61-72 Months'
    END AS tenure_cohort,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customer_count,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_charges,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
FROM customers
GROUP BY 
    CASE 
        WHEN tenure <= 6 THEN '0-6 Months'
        WHEN tenure <= 12 THEN '7-12 Months'
        WHEN tenure <= 24 THEN '13-24 Months'
        WHEN tenure <= 36 THEN '25-36 Months'
        WHEN tenure <= 48 THEN '37-48 Months'
        WHEN tenure <= 60 THEN '49-60 Months'
        ELSE '61-72 Months'
    END
ORDER BY MIN(tenure) ASC;

-- 8. Churn Rate by Monthly Spend Tiers
-- Analyzes price sensitivity and attrition across spending tiers.
SELECT 
    CASE 
        WHEN MonthlyCharges <= 35.0 THEN 'Low (<= $35)'
        WHEN MonthlyCharges <= 70.0 THEN 'Medium ($35 - $70)'
        ELSE 'High (> $70)'
    END AS spend_tier,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customer_count,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_charges,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
FROM customers
GROUP BY 
    CASE 
        WHEN MonthlyCharges <= 35.0 THEN 'Low (<= $35)'
        WHEN MonthlyCharges <= 70.0 THEN 'Medium ($35 - $70)'
        ELSE 'High (> $70)'
    END
ORDER BY MIN(MonthlyCharges) ASC;

-- 9. Customer Counts and Churn Rates by Tenure Band and Contract Type
-- Evaluates the cross-section of lifecycle maturity and contractual lock-in.
SELECT 
    CASE 
        WHEN tenure <= 12 THEN 'New (0-12m)'
        WHEN tenure <= 36 THEN 'Developing (13-36m)'
        ELSE 'Mature (37-72m)'
    END AS tenure_tier,
    Contract,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customer_count,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
FROM customers
GROUP BY 
    CASE 
        WHEN tenure <= 12 THEN 'New (0-12m)'
        WHEN tenure <= 36 THEN 'Developing (13-36m)'
        ELSE 'Mature (37-72m)'
    END,
    Contract
ORDER BY 
    CASE 
        WHEN tenure <= 12 THEN 1
        WHEN tenure <= 36 THEN 2
        ELSE 3
    END,
    churn_rate_pct DESC;

-- 10. Churned MRR Exposure by Contract Type and Internet Service
-- Quantifies the financial concentration of churned monthly revenue.
SELECT 
    Contract,
    InternetService,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(MonthlyCharges), 2) AS segment_total_mrr,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END) / 
        (SELECT SUM(MonthlyCharges) FROM customers WHERE Churn = 'Yes'), 
        2
    ) AS pct_of_company_churned_mrr
FROM customers
GROUP BY Contract, InternetService
ORDER BY churned_mrr DESC;
