-- IPLM Database Setup Script
-- Run this script in MySQL to create the database and user
-- Command line:
-- mysql -u root < setup_database.sql

-- Cleanup existing database and user
DROP DATABASE IF EXISTS iplm_db;
DROP USER IF EXISTS 'iplm_user'@'localhost';

-- Create database
CREATE DATABASE IF NOT EXISTS iplm_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (change password as needed)
CREATE USER IF NOT EXISTS 'iplm_user'@'localhost' IDENTIFIED BY 'IPLM_password_123';

-- Grant privileges
GRANT ALL PRIVILEGES ON iplm_db.* TO 'iplm_user'@'localhost';

-- Flush privileges
FLUSH PRIVILEGES;

-- Use the database
USE iplm_db;

-- Create tables in dependency order to satisfy foreign keys

-- 1) types (root table for classification tree)
CREATE TABLE IF NOT EXISTS `types` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL,
  `parent_id` INT NULL,
  `path` VARCHAR(500) NOT NULL,
  `level` INT NOT NULL DEFAULT 0,
  `description` TEXT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_path` (`path`(255)),
  INDEX `idx_parent_id` (`parent_id`),
  CONSTRAINT `fk_types_parent` FOREIGN KEY (`parent_id`) REFERENCES `types`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2) processes
CREATE TABLE IF NOT EXISTS `processes` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL UNIQUE,
  `node` VARCHAR(255) NOT NULL,
  `fab` VARCHAR(100) NOT NULL,
  `description` TEXT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3) ips (references types and processes)
CREATE TABLE IF NOT EXISTS `ips` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL UNIQUE,
  `type_id` INT NOT NULL,
  `process_id` INT NOT NULL,
  `parent_ip_id` INT NULL,
  `revision` VARCHAR(50) NOT NULL,
  `status` ENUM('alpha','beta','production','obsolete') NOT NULL,
  `provider` VARCHAR(255) NOT NULL,
  `description` TEXT,
  `documentation` TEXT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `fk_ips_type` FOREIGN KEY (`type_id`) REFERENCES `types`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ips_process` FOREIGN KEY (`process_id`) REFERENCES `processes`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ips_parent` FOREIGN KEY (`parent_ip_id`) REFERENCES `ips`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Show success message
SELECT 'Database and tables created successfully!' AS message;
