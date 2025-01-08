-- 创建 CVM 实例表
CREATE TABLE IF NOT EXISTS cvm_instances (
    id SERIAL PRIMARY KEY,
    instance_id VARCHAR(255) NOT NULL,
    instance_name VARCHAR(255),
    zone VARCHAR(255),
    project_name VARCHAR(255),
    expired_time TIMESTAMP,
    differ_days INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建 CBS 云硬盘表
CREATE TABLE IF NOT EXISTS cbs_disks (
    id SERIAL PRIMARY KEY,
    disk_id VARCHAR(255) NOT NULL,
    disk_name VARCHAR(255),
    project_id VARCHAR(255),
    project_name VARCHAR(255),
    zone VARCHAR(255),
    expired_time TIMESTAMP,
    differ_days INT,
    status VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建轻量应用服务器表
CREATE TABLE IF NOT EXISTS lighthouse_instances (
    id SERIAL PRIMARY KEY,
    instance_id VARCHAR(255) NOT NULL,
    instance_name VARCHAR(255),
    zone VARCHAR(255),
    expired_time TIMESTAMP,
    differ_days INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建域名表
CREATE TABLE IF NOT EXISTS domains (
    id SERIAL PRIMARY KEY,
    domain_id VARCHAR(255) NOT NULL,
    domain_name VARCHAR(255),
    expired_time DATE,
    differ_days INT,
    status VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建 SSL 证书表
CREATE TABLE IF NOT EXISTS ssl_certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    domain VARCHAR(255),
    product_name VARCHAR(255),
    project_name VARCHAR(255),
    expired_time DATETIME,
    differ_days INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建账单信息表
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