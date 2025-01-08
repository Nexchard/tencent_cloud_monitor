CREATE TABLE IF NOT EXISTS ssl_certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_name VARCHAR(255),
    certificate_id VARCHAR(255),
    domain VARCHAR(255),
    product_name VARCHAR(255),
    project_name VARCHAR(255),
    expired_time DATETIME,
    differ_days INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
); 