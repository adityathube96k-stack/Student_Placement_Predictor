-- =====================================================
-- SKILL GAP ANALYSIS HISTORY
-- =====================================================

CREATE TABLE IF NOT EXISTS skill_gap_history (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    aptitude_score DECIMAL(5,2),

    coding_score DECIMAL(5,2),

    communication_score DECIMAL(5,2),

    technical_score DECIMAL(5,2),

    total_gap DECIMAL(6,2),

    overall_status VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_skill_gap_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);