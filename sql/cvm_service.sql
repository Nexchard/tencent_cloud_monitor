CREATE TABLE IF NOT EXISTS cvm_instances (
    id SERIAL PRIMARY KEY,
    account_name VARCHAR(255),
    instance_id VARCHAR(255) NOT NULL,
    instance_name VARCHAR(255),
    zone VARCHAR(255),
    project_name VARCHAR(255),
    expired_time TIMESTAMP,
    differ_days INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 