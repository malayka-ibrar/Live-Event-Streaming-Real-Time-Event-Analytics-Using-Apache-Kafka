-- Create database for event streaming
CREATE DATABASE IF NOT EXISTS event_streaming;
USE event_streaming;

-- Create events table
CREATE TABLE IF NOT EXISTS events (
    event_id VARCHAR(255) PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id INT NOT NULL,
    device VARCHAR(20),
    event_timestamp DATETIME NOT NULL,
    session_id VARCHAR(255),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for faster queries
    INDEX idx_event_type (event_type),
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (event_timestamp),
    INDEX idx_device (device)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create aggregated statistics table
CREATE TABLE IF NOT EXISTS aggregated_stats (
    stat_date DATE PRIMARY KEY,
    total_events INT DEFAULT 0,
    unique_users INT DEFAULT 0,
    events_by_type JSON,
    top_countries JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create hourly stats table
CREATE TABLE IF NOT EXISTS hourly_stats (
    hour_timestamp DATETIME PRIMARY KEY,
    event_type VARCHAR(50),
    event_count INT,
    unique_users INT,
    INDEX idx_hour (hour_timestamp),
    INDEX idx_type (event_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create view for recent events
CREATE OR REPLACE VIEW recent_events_view AS
SELECT 
    event_id,
    event_type,
    user_id,
    device,
    event_timestamp,
    JSON_UNQUOTE(JSON_EXTRACT(metadata, '$.country')) as country,
    JSON_UNQUOTE(JSON_EXTRACT(metadata, '$.city')) as city
FROM events
ORDER BY event_timestamp DESC
LIMIT 100;

-- Sample queries for testing
SELECT 'Database setup complete!' as status;