-- ===================================================================
-- MySQL Database Initialization Script
-- Purpose: Create database and user for Trading Dashboard
-- ===================================================================

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS trading_dashboard
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Create user 'trading' with password 'trading123'
-- Note: Change the password in production environment
CREATE USER IF NOT EXISTS 'trading'@'localhost' IDENTIFIED BY 'trading123';
CREATE USER IF NOT EXISTS 'trading'@'%' IDENTIFIED BY 'trading123';

-- Grant all privileges on trading_dashboard database
GRANT ALL PRIVILEGES ON trading_dashboard.* TO 'trading'@'localhost';
GRANT ALL PRIVILEGES ON trading_dashboard.* TO 'trading'@'%';

-- Apply changes
FLUSH PRIVILEGES;

-- Show created database
SHOW DATABASES LIKE 'trading_dashboard';

-- Show user privileges
SHOW GRANTS FOR 'trading'@'localhost';
