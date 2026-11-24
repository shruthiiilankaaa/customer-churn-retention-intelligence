-- ==============================================================================
-- 02_BUSINESS_KPIS.SQL: Executive Business Intelligence & Financial KPIs
-- Project: Telco Customer Churn & Retention Intelligence
-- Database: SQLite (database/telco_churn.db)
-- Table: customers
-- ==============================================================================

-- 1. Executive Churn & Revenue Exposure Scorecard
-- Calculates 12 core business and financial metrics in a single consolidated row.
-- Uses safe division (NULLIF) and 1.0 multiplier to guarantee floating-point precision.
-- Note on terminology: 'churned_mrr_exposure' represents snapshot monthly recurring
-- revenue associated with churned accounts in this observation window; 
-- 'simple_annualized_mrr_exposure' is an annualized extrapolation (snapshot MRR * 12),
-- not realized or historical revenue loss.

SELECT 
    -- Customer Population Metrics
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) AS active_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    
    -- Account Churn Rate
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1.0 ELSE 0.0 END) / 
        NULLIF(COUNT(*), 0), 
        2
    ) AS overall_churn_rate_pct,

    -- Monthly Recurring Revenue (MRR) Totals
    ROUND(SUM(MonthlyCharges), 2) AS total_baseline_mrr,
    ROUND(SUM(CASE WHEN Churn = 'No' THEN MonthlyCharges ELSE 0.0 END), 2) AS active_customer_mrr,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_customer_mrr_exposure,

    -- Financial Revenue Churn Rate
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END) / 
        NULLIF(SUM(MonthlyCharges), 0), 
        2
    ) AS mrr_churn_rate_pct,

    -- Average Monthly Charges (ARPU Proxy) by Churn Status
    ROUND(
        AVG(CASE WHEN Churn = 'No' THEN MonthlyCharges ELSE NULL END), 
        2
    ) AS avg_monthly_charges_active,
    ROUND(
        AVG(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE NULL END), 
        2
    ) AS avg_monthly_charges_churned,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges_overall,

    -- Simple Annualized Revenue Exposure (Extrapolation: Snapshot Churned MRR * 12)
    ROUND(
        SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END) * 12.0, 
        2
    ) AS simple_annualized_mrr_exposure
FROM customers;

-- 2. Comparative Revenue & Volume Profile by Churn Status
-- Evaluates side-by-side volume, revenue share, and charge profiles.
SELECT 
    Churn AS churn_status,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 2) AS customer_share_pct,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_charges,
    ROUND(100.0 * SUM(MonthlyCharges) / (SELECT SUM(MonthlyCharges) FROM customers), 2) AS revenue_share_pct,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charge,
    ROUND(MIN(MonthlyCharges), 2) AS min_monthly_charge,
    ROUND(MAX(MonthlyCharges), 2) AS max_monthly_charge,
    ROUND(AVG(TotalCharges), 2) AS avg_cumulative_total_charges
FROM customers
GROUP BY Churn;

-- 3. Revenue Disparity & Sensitivity Multipliers
-- Quantifies the financial premium of churned customers relative to retained accounts.
SELECT 
    ROUND(AVG(CASE WHEN Churn = 'Yes' THEN MonthlyCharges END), 2) AS churned_arpu,
    ROUND(AVG(CASE WHEN Churn = 'No' THEN MonthlyCharges END), 2) AS active_arpu,
    ROUND(
        (AVG(CASE WHEN Churn = 'Yes' THEN MonthlyCharges END) - 
         AVG(CASE WHEN Churn = 'No' THEN MonthlyCharges END)), 
        2
    ) AS arpu_difference,
    ROUND(
        (AVG(CASE WHEN Churn = 'Yes' THEN MonthlyCharges END) / 
         NULLIF(AVG(CASE WHEN Churn = 'No' THEN MonthlyCharges END), 0) - 1.0) * 100.0, 
        2
    ) AS churned_premium_percentage
FROM customers;
