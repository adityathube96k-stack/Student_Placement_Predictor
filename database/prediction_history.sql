-- =====================================================
-- PLACEMENT PREDICTION HISTORY
-- =====================================================

CREATE TABLE IF NOT EXISTS prediction_history (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    cgpa DECIMAL(4,2),

    attendance DECIMAL(5,2),

    aptitude_score DECIMAL(5,2),

    coding_score DECIMAL(5,2),

    communication_score DECIMAL(5,2),

    technical_score DECIMAL(5,2),

    prediction VARCHAR(50),

    placement_probability DECIMAL(5,2),

    not_placed_probability DECIMAL(5,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_prediction_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);