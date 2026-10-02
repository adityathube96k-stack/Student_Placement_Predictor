-- =====================================================
-- PLACEMENT READINESS HISTORY
-- =====================================================

CREATE TABLE IF NOT EXISTS readiness_history (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    cgpa DECIMAL(4,2),

    attendance DECIMAL(5,2),

    aptitude_score DECIMAL(5,2),

    coding_score DECIMAL(5,2),

    communication_score DECIMAL(5,2),

    technical_score DECIMAL(5,2),

    readiness_score DECIMAL(5,2),

    readiness_level VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_readiness_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);