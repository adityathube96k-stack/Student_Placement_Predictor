CREATE DATABASE IF NOT EXISTS placement_predictor;

USE placement_predictor;


-- =====================================================
-- USERS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS users (

    id INT AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(150) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    role ENUM('student', 'admin', 'tpo')
        NOT NULL DEFAULT 'student',

    is_active BOOLEAN
        NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP

);


-- =====================================================
-- STUDENTS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS students (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL UNIQUE,

    enrollment_no VARCHAR(50) UNIQUE,

    phone VARCHAR(20),

    department VARCHAR(100),

    course VARCHAR(100),

    year VARCHAR(20),

    semester VARCHAR(20),

    cgpa DECIMAL(4,2),

    attendance DECIMAL(5,2),

    aptitude_score DECIMAL(5,2),

    coding_score DECIMAL(5,2),

    communication_score DECIMAL(5,2),

    technical_score DECIMAL(5,2),

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_student_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);


-- =====================================================
-- SYSTEM CHECK
-- =====================================================

CREATE TABLE IF NOT EXISTS system_check (

    id INT AUTO_INCREMENT PRIMARY KEY,

    message VARCHAR(255) NOT NULL,

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP

);