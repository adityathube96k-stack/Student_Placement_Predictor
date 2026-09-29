CREATE DATABASE IF NOT EXISTS placement_predictor;

USE placement_predictor;

CREATE TABLE IF NOT EXISTS system_check (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO system_check (message)
SELECT 'Day 1 database setup completed'
WHERE NOT EXISTS (
    SELECT 1 FROM system_check
);