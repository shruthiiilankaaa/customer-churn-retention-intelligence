-- ==============================================================================
-- 05_ADVANCED_ANALYTICS.SQL: Window Functions, CTEs & Advanced BI Modeling
-- Project: Telco Customer Churn & Retention Intelligence
-- Database: SQLite (database/telco_churn.db)
-- Table: customers
--
-- Methodological Note:
-- This analysis uses cross-sectional snapshot data. Window functions evaluate 
-- multi-level aggregations, rankings, partitions, and baseline deviations within 
-- this snapshot without simulating unobserved historical cohort migrations.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Rank Contract Types by Churn Rate (DENSE_RANK with CTE)
-- Demonstrates: CTE, aggregation, window ranking.
-- Purpose: Identifies the contractual arrangements carrying highest relative risk.
-- ------------------------------------------------------------------------------
WITH contract_stats AS (
    SELECT 
        Contract,
        COUNT(*) AS total_accounts,
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_accounts,
        ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
        ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
    FROM customers
    GROUP BY Contract
)
SELECT 
    DENSE_RANK() OVER (ORDER BY churn_rate_pct DESC) AS risk_rank,
    Contract,
    total_accounts,
    churned_accounts,
    churn_rate_pct,
    churned_mrr
FROM contract_stats
ORDER BY risk_rank ASC;


-- ------------------------------------------------------------------------------
-- 2. Rank Customer Segments by Revenue Exposure (DENSE_RANK & Window Running Total)
-- Demonstrates: Multi-dimensional CTE, DENSE_RANK(), cumulative SUM() OVER().
-- Purpose: Quantifies revenue concentration across Tenure × Spend segments.
-- ------------------------------------------------------------------------------
WITH segment_revenue AS (
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
        COUNT(*) AS total_accounts,
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_accounts,
        ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
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
    DENSE_RANK() OVER (ORDER BY churned_mrr DESC) AS revenue_exposure_rank,
    tenure_tier,
    spend_tier,
    total_accounts,
    churned_accounts,
    churned_mrr,
    ROUND(
        100.0 * churned_mrr / SUM(churned_mrr) OVER (), 
        2
    ) AS pct_of_total_churned_mrr,
    ROUND(
        100.0 * SUM(churned_mrr) OVER (
            ORDER BY churned_mrr DESC 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) / SUM(churned_mrr) OVER (), 
        2
    ) AS cumulative_mrr_risk_share_pct
FROM segment_revenue
ORDER BY revenue_exposure_rank ASC;


-- ------------------------------------------------------------------------------
-- 3. Compare Tenure Cohort Churn Rates Against Company Baseline
-- Demonstrates: CTE, overall window aggregation (SUM() OVER()), baseline delta.
-- Purpose: Pinpoints exact customer lifecycle stages deviating from the 26.54% norm.
-- ------------------------------------------------------------------------------
WITH cohort_rates AS (
    SELECT 
        CASE 
            WHEN tenure <= 6 THEN '01. 0-6 Months'
            WHEN tenure <= 12 THEN '02. 7-12 Months'
            WHEN tenure <= 24 THEN '03. 13-24 Months'
            WHEN tenure <= 36 THEN '04. 25-36 Months'
            WHEN tenure <= 48 THEN '05. 37-48 Months'
            WHEN tenure <= 60 THEN '06. 49-60 Months'
            ELSE '07. 61-72 Months'
        END AS tenure_cohort,
        COUNT(*) AS cohort_customers,
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS cohort_churned,
        ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS cohort_churn_rate_pct
    FROM customers
    GROUP BY 
        CASE 
            WHEN tenure <= 6 THEN '01. 0-6 Months'
            WHEN tenure <= 12 THEN '02. 7-12 Months'
            WHEN tenure <= 24 THEN '03. 13-24 Months'
            WHEN tenure <= 36 THEN '04. 25-36 Months'
            WHEN tenure <= 48 THEN '05. 37-48 Months'
            WHEN tenure <= 60 THEN '06. 49-60 Months'
            ELSE '07. 61-72 Months'
        END
)
SELECT 
    tenure_cohort,
    cohort_customers,
    cohort_churned,
    cohort_churn_rate_pct,
    ROUND(
        100.0 * SUM(cohort_churned) OVER () / SUM(cohort_customers) OVER (), 
        2
    ) AS company_baseline_churn_rate_pct,
    ROUND(
        cohort_churn_rate_pct - (100.0 * SUM(cohort_churned) OVER () / SUM(cohort_customers) OVER ()), 
        2
    ) AS deviation_from_baseline_pct
FROM cohort_rates
ORDER BY tenure_cohort ASC;


-- ------------------------------------------------------------------------------
-- 4. Calculate Segment Percentage Contribution to Churned MRR via SUM() OVER()
-- Demonstrates: Unbounded window SUM() OVER() without self-joins.
-- Purpose: Accurately isolates share of revenue drag contributed by each tier.
-- ------------------------------------------------------------------------------
WITH payment_contract_churn AS (
    SELECT 
        Contract,
        PaymentMethod,
        COUNT(*) AS accounts,
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_accounts,
        ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
    FROM customers
    GROUP BY Contract, PaymentMethod
)
SELECT 
    Contract,
    PaymentMethod,
    accounts,
    churned_accounts,
    churned_mrr,
    ROUND(
        100.0 * churned_mrr / SUM(churned_mrr) OVER (), 
        2
    ) AS contribution_to_total_churned_mrr_pct,
    DENSE_RANK() OVER (ORDER BY churned_mrr DESC) AS severity_rank
FROM payment_contract_churn
ORDER BY severity_rank ASC;


-- ------------------------------------------------------------------------------
-- 5. Rank High-Risk Operational Profiles (Contract × Internet × Support)
-- Demonstrates: Multi-feature grouping, conditional filtering, DENSE_RANK().
-- Purpose: Identifies the exact operational service bundles exhibiting highest churn.
-- ------------------------------------------------------------------------------
WITH profile_stats AS (
    SELECT 
        Contract,
        InternetService,
        TechSupport,
        COUNT(*) AS customer_count,
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_count,
        ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
        ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0.0 END), 2) AS churned_mrr
    FROM customers
    GROUP BY Contract, InternetService, TechSupport
    HAVING COUNT(*) >= 50 -- Filter out tiny noise clusters
)
SELECT 
    DENSE_RANK() OVER (ORDER BY churn_rate_pct DESC) AS risk_rank,
    Contract,
    InternetService,
    TechSupport,
    customer_count,
    churned_count,
    churn_rate_pct,
    churned_mrr
FROM profile_stats
ORDER BY risk_rank ASC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- 6. Top High-Monthly-Charge Churned Customers (ROW_NUMBER & DENSE_RANK)
-- Demonstrates: Window ROW_NUMBER() and DENSE_RANK() filtered by status.
-- Purpose: Generates an executive intervention/audit list of highest-value lost accounts.
-- ------------------------------------------------------------------------------
WITH churned_ranked AS (
    SELECT 
        customerID,
        tenure,
        Contract,
        InternetService,
        PaymentMethod,
        MonthlyCharges,
        TotalCharges,
        ROW_NUMBER() OVER (ORDER BY MonthlyCharges DESC, TotalCharges DESC) AS value_row_num,
        DENSE_RANK() OVER (ORDER BY MonthlyCharges DESC) AS charge_rank
    FROM customers
    WHERE Churn = 'Yes'
)
SELECT 
    value_row_num,
    charge_rank,
    customerID,
    tenure,
    Contract,
    InternetService,
    PaymentMethod,
    MonthlyCharges,
    TotalCharges
FROM churned_ranked
WHERE value_row_num <= 10
ORDER BY value_row_num ASC;


-- ------------------------------------------------------------------------------
-- 7. Compare Customer Charges Against Contract Average (AVG() OVER PARTITION BY)
-- Demonstrates: PARTITION BY window aggregation and individual variance calculation.
-- Purpose: Discovers if customers paying above their contractual average churn more.
-- ------------------------------------------------------------------------------
WITH customer_charge_variance AS (
    SELECT 
        customerID,
        Contract,
        tenure,
        MonthlyCharges,
        Churn,
        ROUND(AVG(MonthlyCharges) OVER (PARTITION BY Contract), 2) AS avg_contract_mrr,
        ROUND(MonthlyCharges - AVG(MonthlyCharges) OVER (PARTITION BY Contract), 2) AS charge_diff_from_contract_avg
    FROM customers
)
SELECT 
    Contract,
    CASE 
        WHEN charge_diff_from_contract_avg > 15.0 THEN 'Significantly Above Avg (+$15)'
        WHEN charge_diff_from_contract_avg >= -15.0 THEN 'Around Average (-$15 to +$15)'
        ELSE 'Significantly Below Avg (-$15)'
    END AS price_premium_tier,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2) AS group_avg_mrr
FROM customer_charge_variance
GROUP BY 
    Contract,
    CASE 
        WHEN charge_diff_from_contract_avg > 15.0 THEN 'Significantly Above Avg (+$15)'
        WHEN charge_diff_from_contract_avg >= -15.0 THEN 'Around Average (-$15 to +$15)'
        ELSE 'Significantly Below Avg (-$15)'
    END
ORDER BY Contract ASC, churn_rate_pct DESC;
