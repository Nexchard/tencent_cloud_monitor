CREATE TABLE IF NOT EXISTS billing_info (
    id SERIAL PRIMARY KEY,
    account_name VARCHAR(255),
    balance FLOAT,
    project_name VARCHAR(255),
    service_name VARCHAR(255),
    real_total_cost FLOAT,
    total_cost FLOAT,
    cash_pay_amount FLOAT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 