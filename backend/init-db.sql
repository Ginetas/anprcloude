-- Initial Database Setup
-- This script runs when the PostgreSQL container is first created

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search optimization

-- Set timezone
SET timezone = 'UTC';

-- Create database if not exists (handled by Docker)
-- Note: The database is already created by POSTGRES_DB environment variable

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE anpr_db TO anpr;

-- You can add initial data here if needed
-- Example:
-- INSERT INTO cameras (name, rtsp_url, enabled) VALUES ('Default Camera', 'rtsp://example.com', true);
