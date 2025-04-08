-- Enable the necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Version tracking tables
CREATE TABLE IF NOT EXISTS schema_versions (
    version_id SERIAL PRIMARY KEY,
    version_number INTEGER NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE(version_number)
);

CREATE TABLE IF NOT EXISTS migration_history (
    migration_id SERIAL PRIMARY KEY,
    version_id INTEGER REFERENCES schema_versions(version_id),
    migration_name TEXT NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    error_message TEXT,
    rollback_sql TEXT,
    checksum TEXT,
    UNIQUE(migration_name, version_id)
);

CREATE TABLE IF NOT EXISTS rollback_history (
    rollback_id SERIAL PRIMARY KEY,
    from_version INTEGER NOT NULL,
    to_version INTEGER NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    error_message TEXT,
    initiated_by TEXT NOT NULL,
    FOREIGN KEY (from_version) REFERENCES schema_versions(version_number),
    FOREIGN KEY (to_version) REFERENCES schema_versions(version_number)
);

-- Monitoring and logging tables
CREATE TABLE IF NOT EXISTS migration_metrics (
    metric_id SERIAL PRIMARY KEY,
    migration_id INTEGER REFERENCES migration_history(migration_id),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    duration_ms INTEGER,
    rows_affected INTEGER,
    memory_usage_mb INTEGER,
    cpu_usage_percent FLOAT,
    lock_wait_time_ms INTEGER,
    error_count INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS database_health (
    health_id SERIAL PRIMARY KEY,
    check_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active_connections INTEGER,
    transaction_count INTEGER,
    dead_tuples INTEGER,
    bloat_ratio FLOAT,
    index_usage_ratio FLOAT,
    cache_hit_ratio FLOAT,
    replication_lag INTEGER,
    health_status TEXT NOT NULL,
    details JSONB
);

CREATE TABLE IF NOT EXISTS migration_logs (
    log_id SERIAL PRIMARY KEY,
    migration_id INTEGER REFERENCES migration_history(migration_id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    log_level TEXT NOT NULL,
    message TEXT NOT NULL,
    context JSONB,
    pod_name TEXT,
    pod_namespace TEXT
);

-- nessary tables for file download and upload
CREATE TABLE IF NOT EXISTS files (
    file_id UUID PRIMARY KEY NOT NULL,
    apikey_id UUID NOT NULL,
    extension VARCHAR(255) NOT NULL,
    data BYTEA DEFAULT ''::bytea,
    complete BOOLEAN NOT NULL DEFAULT FALSE,
    time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial version
INSERT INTO schema_versions (version_number, description) 
VALUES (1, 'Initial schema version')
ON CONFLICT (version_number) DO NOTHING;

-- Create indexes for monitoring tables
CREATE INDEX IF NOT EXISTS idx_migration_metrics_migration_id ON migration_metrics(migration_id);
CREATE INDEX IF NOT EXISTS idx_migration_logs_migration_id ON migration_logs(migration_id);
CREATE INDEX IF NOT EXISTS idx_migration_logs_timestamp ON migration_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_database_health_check_time ON database_health(check_time);
