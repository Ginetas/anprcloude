#!/bin/bash
# Database Initialization Script
# This script is run when PostgreSQL container starts
# It sets up the database with proper permissions and extensions

set -e

echo "Starting database initialization..."

# Enable useful PostgreSQL extensions
echo "Enabling PostgreSQL extensions..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- UUID extension for generating UUIDs
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- JSON/JSONB support (usually enabled by default in modern PostgreSQL)
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";

    -- Full-text search support
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";

    -- For better query optimization
    CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
EOSQL

# Create application-specific schema and roles
echo "Setting up schemas and roles..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create schemas if they don't exist
    CREATE SCHEMA IF NOT EXISTS public;
    CREATE SCHEMA IF NOT EXISTS audit;

    -- Set search path
    ALTER DATABASE "$POSTGRES_DB" SET search_path TO public,audit;
EOSQL

# Create indexes for better performance (optional, can be done via migration)
echo "Setting up audit logging..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Audit table schema
    CREATE TABLE IF NOT EXISTS audit.audit_log (
        id BIGSERIAL PRIMARY KEY,
        table_name TEXT NOT NULL,
        operation VARCHAR(10) NOT NULL,
        record_id UUID,
        old_values JSONB,
        new_values JSONB,
        changed_by VARCHAR(255),
        changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        user_agent TEXT
    );

    -- Create index on audit log
    CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit.audit_log(changed_at DESC);
    CREATE INDEX IF NOT EXISTS idx_audit_log_table ON audit.audit_log(table_name);
    CREATE INDEX IF NOT EXISTS idx_audit_log_operation ON audit.audit_log(operation);
EOSQL

# Set up basic permissions
echo "Setting up database permissions..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Grant permissions on schemas
    GRANT USAGE ON SCHEMA public TO "$POSTGRES_USER";
    GRANT USAGE ON SCHEMA audit TO "$POSTGRES_USER";

    -- Grant permissions on audit tables
    GRANT ALL PRIVILEGES ON audit.audit_log TO "$POSTGRES_USER";
    GRANT USAGE, SELECT ON SEQUENCE audit.audit_log_id_seq TO "$POSTGRES_USER";
EOSQL

echo "Database initialization completed successfully!"
