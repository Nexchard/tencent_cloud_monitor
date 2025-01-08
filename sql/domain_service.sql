CREATE TABLE IF NOT EXISTS domains (
    id SERIAL PRIMARY KEY,
    account_name VARCHAR(255),
    domain_id VARCHAR(255) NOT NULL,
    domain_name VARCHAR(255),
    expired_time DATE,
    differ_days INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 