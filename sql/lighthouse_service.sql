CREATE TABLE IF NOT EXISTS lighthouse_instances (
    id SERIAL PRIMARY KEY,
    account_name VARCHAR(255),
    instance_id VARCHAR(255) NOT NULL,
    instance_name VARCHAR(255),
    zone VARCHAR(255),
    expired_time TIMESTAMP,
    differ_days INT,
    batch_number VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 