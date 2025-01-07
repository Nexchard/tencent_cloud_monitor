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