CREATE TABLE IF NOT EXISTS billing_info (
    id SERIAL PRIMARY KEY,
    account_name VARCHAR(255),
    project_name VARCHAR(255),
    service_name VARCHAR(255),
    balance FLOAT,
    real_total_cost FLOAT,
    total_cost FLOAT,
    cash_pay_amount FLOAT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    billing_date DATE GENERATED ALWAYS AS (DATE(updated_at)) STORED,
    UNIQUE KEY unique_billing_record (account_name, project_name, service_name, billing_date)
); 