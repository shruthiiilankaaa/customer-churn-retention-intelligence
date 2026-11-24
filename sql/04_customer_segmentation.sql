-- ==============================================================================
-- 04_CUSTOMER_SEGMENTATION.SQL: Two-Dimensional Tenure × Spend Risk Matrix
-- Project: Telco Customer Churn & Retention Intelligence
-- Database: SQLite (database/telco_churn.db)
-- Table: customers
-- ==============================================================================

-- 1. 3x3 Tenure × Monthly Spend Customer Segmentation Matrix
-- Categorizes all accounts across mutually exclusive and exhaustive boundaries:
--   Tenure: New (0-12m), Developing (13-36m), Mature (37-72m)
--   Spend : Low (<= $35), Medium ($35 - $70), High (> $70)

WITH segmented_customers AS (
    SELECT 
        customerID,
        MonthlyCharges,
        Churn,
        CASE 
            WHEN tenure <= 12 THEN 'New (0-12m)'
            WHEN tenure <= 36 THEN 'Developing (13-36m)'
            ELSE 'Mature (37-72m)'
        END AS tenure_tier,
        CASE 
            WHEN MonthlyCharges <= 35.0 THEN 'Low (<=$35)'
            WHEN MonthlyCharges <= 70.0 THEN 'Medium ($35-$70)'
            ELSE 'High (>$70)'
        END AS spend_tier,
        CASE 
            WHEN tenure <= 12 THEN 1
            WHEN tenure <= 36 THEN 2
            ELSE 3
        END AS tenure_sort,
        CASE 
            WHEN MonthlyCharges <= 35.0 THEN 1
            WHEN MonthlyCharges <= 70.0 THEN 2
            ELSE 3
        END AS spend_sort
    FROM customers
)
SELECT 
    tenure_tier,
    spend_tier,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 
        2
    ) AS churn_rate_pct,
    ROUND(SUM(MonthlyCharges), 2) AS total_segment_mrr,
    ROUND(
        SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 
        2
    ) AS churned_mrr,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END) / 
        (SELECT SUM(MonthlyCharges) FROM customers WHERE Churn = 'Yes'), 
        2
    ) AS share_of_total_churned_mrr_pct
FROM segmented_customers
GROUP BY tenure_tier, spend_tier, tenure_sort, spend_sort
ORDER BY tenure_sort ASC, spend_sort ASC;


-- 2. Segment Revenue Exposure Ranking using DENSE_RANK()
-- Ranks customer segments by magnitude of monthly revenue exposure (lost MRR).
WITH segment_metrics AS (
    SELECT 
        CASE 
            WHEN tenure <= 12 THEN 'New (0-12m)'
            WHEN tenure <= 36 THEN 'Developing (13-36m)'
            ELSE 'Mature (37-72m)'
        END AS tenure_tier,
        CASE 
            WHEN MonthlyCharges <= 35.0 THEN 'Low (<=$35)'
            WHEN MonthlyCharges <= 70.0 THEN 'Medium ($35-$70)'
            ELSE 'High (>$70)'
        END AS spend_tier,
        COUNT(*) AS total_customers,
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
        ROUND(
            100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 
            2
        ) AS churn_rate_pct,
        ROUND(SUM(MonthlyCharges), 2) AS total_segment_mrr,
        ROUND(
            SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 
            2
        ) AS churned_mrr
    FROM customers
    GROUP BY 
        CASE 
            WHEN tenure <= 12 THEN 'New (0-12m)'
            WHEN tenure <= 36 THEN 'Developing (13-36m)'
            ELSE 'Mature (37-72m)'
        END,
        CASE 
            WHEN MonthlyCharges <= 35.0 THEN 'Low (<=$35)'
            WHEN MonthlyCharges <= 70.0 THEN 'Medium ($35-$70)'
            ELSE 'High (>$70)'
        END
)
SELECT 
    DENSE_RANK() OVER (ORDER BY churned_mrr DESC) AS mrr_risk_rank,
    tenure_tier,
    spend_tier,
    total_customers,
    churned_customers,
    churn_rate_pct,
    total_segment_mrr,
    churned_mrr,
    ROUND(
        100.0 * churned_mrr / (SELECT SUM(MonthlyCharges) FROM customers WHERE Churn = 'Yes'), 
        2
    ) AS pct_of_total_churned_mrr,
    ROUND(
        100.0 * SUM(churned_mrr) OVER (ORDER BY churned_mrr DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / 
        (SELECT SUM(MonthlyCharges) FROM customers WHERE Churn = 'Yes'),
        2
    ) AS cumulative_pct_of_churned_mrr
FROM segment_metrics
ORDER BY mrr_risk_rank ASC;
