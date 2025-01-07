CREATE TABLE IF NOT EXISTS domains (
    id SERIAL PRIMARY KEY,
    domain_id VARCHAR(255) NOT NULL,
    domain_name VARCHAR(255),
    expired_time DATE,
    differ_days INT,
    status VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 