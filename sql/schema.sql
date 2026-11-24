-- Schema Definition for Telco Customer Churn & Retention Intelligence
-- Database: SQLite (database/telco_churn.db)
-- Table: customers

DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customerID          TEXT PRIMARY KEY NOT NULL,
    gender              TEXT NOT NULL,
    SeniorCitizen       INTEGER NOT NULL,
    Partner             TEXT NOT NULL,
    Dependents          TEXT NOT NULL,
    tenure              INTEGER NOT NULL,
    PhoneService        TEXT NOT NULL,
    MultipleLines       TEXT NOT NULL,
    InternetService     TEXT NOT NULL,
    OnlineSecurity      TEXT NOT NULL,
    OnlineBackup        TEXT NOT NULL,
    DeviceProtection    TEXT NOT NULL,
    TechSupport         TEXT NOT NULL,
    StreamingTV         TEXT NOT NULL,
    StreamingMovies     TEXT NOT NULL,
    Contract            TEXT NOT NULL,
    PaperlessBilling    TEXT NOT NULL,
    PaymentMethod       TEXT NOT NULL,
    MonthlyCharges      REAL NOT NULL,
    TotalCharges        REAL NOT NULL,
    Churn               TEXT NOT NULL
);

-- Analytical indexes to support fast aggregation, filtering, and window functions
CREATE INDEX IF NOT EXISTS idx_customers_churn ON customers(Churn);
CREATE INDEX IF NOT EXISTS idx_customers_contract ON customers(Contract);
CREATE INDEX IF NOT EXISTS idx_customers_internetservice ON customers(InternetService);
CREATE INDEX IF NOT EXISTS idx_customers_paymentmethod ON customers(PaymentMethod);
CREATE INDEX IF NOT EXISTS idx_customers_tenure ON customers(tenure);
CREATE INDEX IF NOT EXISTS idx_customers_monthlycharges ON customers(MonthlyCharges);
