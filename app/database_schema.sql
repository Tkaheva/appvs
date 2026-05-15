-- database_schema.sql
CREATE DATABASE IF NOT EXISTS autosalon_analytics
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE autosalon_analytics;

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('admin', 'manager', 'analyst') DEFAULT 'analyst',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS uploaded_files (
    id INT PRIMARY KEY AUTO_INCREMENT,
    file_id VARCHAR(36) UNIQUE NOT NULL,
    user_id INT,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    file_format VARCHAR(10) NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(500),
    status ENUM('uploaded', 'processing', 'completed', 'failed') DEFAULT 'uploaded'
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    file_id VARCHAR(36) UNIQUE NOT NULL,
    analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_score INT,
    grade VARCHAR(50),
    grade_class VARCHAR(50),
    word_count INT DEFAULT 0,
    admin_word_count INT DEFAULT 0,
    client_word_count INT DEFAULT 0,
    avg_confidence FLOAT,
    FOREIGN KEY (file_id) REFERENCES uploaded_files(file_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS criteria_scores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    analysis_id INT NOT NULL,
    criterion_id VARCHAR(50) NOT NULL,
    score INT,
    keyword_count INT DEFAULT 0,
    keywords_found TEXT,
    FOREIGN KEY (analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dialogue_segments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    analysis_id INT NOT NULL,
    segment_index INT NOT NULL,
    speaker ENUM('admin', 'client') NOT NULL,
    text TEXT NOT NULL,
    timestamp VARCHAR(20),
    confidence FLOAT,
    FOREIGN KEY (analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE
);

INSERT IGNORE INTO users (username, email, password_hash, full_name, role) 
VALUES ('admin', 'admin@autosalon.local', 'admin123', 'Администратор', 'admin');
