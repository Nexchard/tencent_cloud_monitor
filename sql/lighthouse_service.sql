CREATE TABLE IF NOT EXISTS lighthouse_instances (
    id SERIAL PRIMARY KEY,
    instance_id VARCHAR(255) NOT NULL,
    instance_name VARCHAR(255),
    zone VARCHAR(255),
    expired_time TIMESTAMP,
    differ_days INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 