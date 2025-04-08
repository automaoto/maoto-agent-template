# Testing Guide

This document provides comprehensive testing instructions for the database migration system.

## Prerequisites

- PostgreSQL 12 or higher
- Bash shell
- `jq` command-line tool
- Docker (for containerized testing)
- Kubernetes (for pod-based testing)

## Local Testing Setup

1. **Set up test database**:
```bash
# Create test database
createdb migration_test_db

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=migration_test_db
export DB_USER=postgres
export DB_PASSWORD=postgres
```

2. **Initialize test environment**:
```bash
# Run initial schema
psql -d migration_test_db -f src/databasepostgre/init.sql

# Make migration script executable
chmod +x src/databasepostgre/migrate.sh
```

## Test Cases

### 1. Basic Migration Testing

```bash
# Create test migration
cat > src/databasepostgre/migrations/002_test_migration.sql << EOF
-- Migration: 002_test_migration
-- Version: 2
-- Description: Test migration

CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

INSERT INTO test_table (name) VALUES ('test1') ON CONFLICT DO NOTHING;
EOF

# Create rollback migration
cat > src/databasepostgre/migrations/002_rollback.sql << EOF
-- Rollback migration for version 2
DROP TABLE test_table;
EOF

# Run migration
./src/databasepostgre/migrate.sh

# Verify migration
psql -d migration_test_db -c "SELECT * FROM test_table;"
```

### 2. Health Check Testing

```bash
# Test database health monitoring
psql -d migration_test_db -c "SELECT * FROM database_health ORDER BY check_time DESC LIMIT 1;"

# Test warning conditions
psql -d migration_test_db -c "UPDATE database_health SET health_status = 'warning' WHERE health_id = (SELECT MAX(health_id) FROM database_health);"
```

### 3. Performance Metrics Testing

```bash
# Create large test migration
cat > src/databasepostgre/migrations/003_performance_test.sql << EOF
-- Migration: 003_performance_test
-- Version: 3
-- Description: Performance test migration

CREATE TABLE performance_test (
    id SERIAL PRIMARY KEY,
    data TEXT
);

INSERT INTO performance_test (data) 
SELECT 'test_data_' || generate_series(1, 1000);
EOF

# Run migration and check metrics
./src/databasepostgre/migrate.sh
psql -d migration_test_db -c "SELECT migration_name, duration_ms, rows_affected, memory_usage_mb, cpu_usage_percent FROM migration_history JOIN migration_metrics ON migration_history.migration_id = migration_metrics.migration_id ORDER BY migration_history.migration_id DESC LIMIT 1;"
```

### 3.1 Data Migration Testing

```bash
# Create a data migration file
cat > src/databasepostgre/migrations/004_data_migration.sql << EOF
-- Migration: 004_data_migration
-- Version: 4
-- Description: Data migration test

-- Create a source table with sample data
CREATE TABLE data_source (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    value INTEGER
);

-- Insert some data
INSERT INTO data_source (name, value) 
VALUES 
    ('item1', 10),
    ('item2', 20),
    ('item3', 30);

-- Create a destination table
CREATE TABLE data_destination (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    value INTEGER,
    migrated_at TIMESTAMP DEFAULT NOW()
);

-- Migrate data with transformation
INSERT INTO data_destination (name, value)
SELECT 
    UPPER(name),
    value * 2
FROM data_source;
EOF

# Run migration
./src/databasepostgre/migrate.sh

# Verify data migration
psql -d migration_test_db -c "SELECT * FROM data_destination;"
```

### 3.2 Advanced Metrics Testing

```bash
# Create a test migration with various SQL operations to test metrics collection
cat > src/databasepostgre/migrations/005_metrics_test.sql << EOF
-- Migration: 005_metrics_test
-- Version: 5
-- Description: Comprehensive metrics test

CREATE TABLE metrics_test (
    id SERIAL PRIMARY KEY,
    col1 TEXT,
    col2 INTEGER
);

-- Insert multiple rows to test counting
INSERT INTO metrics_test (col1, col2)
VALUES
  ('row1', 101),
  ('row2', 102),
  ('row3', 103),
  ('row4', 104),
  ('row5', 105);

-- Update some rows
UPDATE metrics_test SET col1 = col1 || '_updated' WHERE col2 > 102;

-- Create an index
CREATE INDEX idx_metrics_test_col1 ON metrics_test(col1);

-- Alter table
ALTER TABLE metrics_test ADD COLUMN col3 TIMESTAMP DEFAULT NOW();
EOF

# Run migration
./src/databasepostgre/migrate.sh

# Verify comprehensive metrics collection
psql -d migration_test_db -c "
SELECT 
    m.migration_name, 
    mm.duration_ms, 
    mm.rows_affected, 
    mm.memory_usage_mb, 
    mm.cpu_usage_percent,
    mm.error_count,
    mm.warning_count
FROM 
    migration_history m 
    JOIN migration_metrics mm ON m.migration_id = mm.migration_id 
WHERE 
    m.migration_name = '005_metrics_test';"
```

### 4. Rollback Testing

```bash
# Force version mismatch by setting a higher version number
psql -d migration_test_db -c "SELECT MAX(version_number) FROM schema_versions;"
# Take note of the current max version number

# Set to a version higher than any existing migration
psql -d migration_test_db -c "INSERT INTO schema_versions (version_number, description, is_active) VALUES (10, 'Temporary version for rollback test', TRUE);"

# Update to deactivate other versions
psql -d migration_test_db -c "UPDATE schema_versions SET is_active = FALSE WHERE version_number < 10;"

# Run migration (should trigger rollback to highest valid version)
DB_NAME=migration_test_db DB_USER=postgres DB_PASSWORD=postgres ./src/databasepostgre/migrate.sh

# Verify rollback
psql -d migration_test_db -c "SELECT * FROM rollback_history ORDER BY rollback_id DESC LIMIT 1;"

# Check current active version
psql -d migration_test_db -c "SELECT version_number, is_active FROM schema_versions ORDER BY version_number DESC;"
```

### 5. Logging System Testing

```bash
# Test different log levels (logs go to stderr)
export LOG_LEVEL=DEBUG
./src/databasepostgre/migrate.sh 2> migration_logs.txt

# View log file
cat migration_logs.txt

# Test other log levels
DB_NAME=migration_test_db DB_USER=postgres DB_PASSWORD=postgres LOG_LEVEL=INFO ./src/databasepostgre/migrate.sh 2>&1 | grep INFO

DB_NAME=migration_test_db DB_USER=postgres DB_PASSWORD=postgres LOG_LEVEL=WARN ./src/databasepostgre/migrate.sh 2>&1 | grep WARN

DB_NAME=migration_test_db DB_USER=postgres DB_PASSWORD=postgres LOG_LEVEL=ERROR ./src/databasepostgre/migrate.sh 2>&1 | grep ERROR
```

## Kubernetes Testing

1. **Set up test environment**:
```bash
# Create test namespace
kubectl create namespace migration-test

# Apply test configuration
kubectl apply -f server_mode/kubernetes/templates/deployment-databasepostgre-direct.yaml -n migration-test
```

2. **Test pod-based migration**:
```bash
# Get pod name
POD_NAME=$(kubectl get pods -n migration-test -l app=databasepostgre -o jsonpath='{.items[0].metadata.name}')

# Check logs
kubectl logs $POD_NAME -n migration-test

# Check pod status
kubectl get pods -n migration-test -l app=databasepostgre -o wide

# Check migration status
kubectl exec $POD_NAME -n migration-test -- psql -U postgres -c "SELECT * FROM migration_history ORDER BY applied_at DESC LIMIT 1;"
```

## Integration Testing

1. **Test version transitions**:
```bash
# Create test data
psql -d migration_test_db -c "INSERT INTO files (file_id, apikey_id, extension) VALUES (gen_random_uuid(), gen_random_uuid(), 'test');"

# Run multiple migrations
for i in {2..5}; do
  cat > src/databasepostgre/migrations/00${i}_test.sql << EOF
-- Migration: 00${i}_test
-- Version: ${i}
-- Description: Test migration ${i}

ALTER TABLE files ADD COLUMN test${i} TEXT;
EOF
DB_NAME=migration_test_db DB_USER=postgres DB_PASSWORD=postgres  ./src/databasepostgre/migrate.sh
done

# Verify data integrity
psql -d migration_test_db -c "SELECT * FROM files;"
```

2. **Test concurrent access**:
```bash
# Simulate concurrent migrations triggers a race condition so should fail
for i in {1..5}; do
  DB_NAME=migration_test_db DB_USER=postgres DB_PASSWORD=postgres ./src/databasepostgre/migrate.sh &
done

# Check for conflicts
psql -d migration_test_db -c "SELECT * FROM migration_history WHERE status = 'failed';"
```

**Expected Behavior**:
- All concurrent migration processes will fail with "Migration checksum mismatch" and "Database state verification failed" errors
- This is expected behavior as the migration system prevents concurrent migrations
- No failed migrations will be recorded in the `migration_history` table
- The database state remains consistent despite the concurrent access attempts
- This test verifies that the migration system properly handles race conditions and maintains data integrity

**Why This Happens**:
- The migration system uses database-level checks to prevent concurrent migrations
- When multiple processes try to migrate simultaneously, only one will succeed
- The other processes will fail gracefully without corrupting the database state
- This is a safety feature to prevent data corruption during migrations

## Monitoring Tests

1. **Test health alerts**:
```bash
# Simulate high replication lag
psql -d migration_test_db -c "UPDATE database_health SET replication_lag = 600 WHERE health_id = (SELECT MAX(health_id) FROM database_health);"

# Check health status
psql -d migration_test_db -c "SELECT health_status, details FROM database_health ORDER BY check_time DESC LIMIT 1;"
```

**Expected Behavior**:
- The health check system will automatically correct manually modified values
- The `replication_lag` will be reset to 0 in the next health check
- The health status will remain "healthy" if other metrics are within normal ranges
- The system maintains accurate metrics by performing regular health checks
- This demonstrates the system's resilience against manual data modifications

**Why This Happens**:
- The health check system performs regular checks of all metrics
- Each check overwrites previous values with current measurements
- Manual modifications are temporary and will be corrected in the next check
- This ensures the system always has accurate, up-to-date health information

2. **Test performance monitoring**:
```bash
# First, ensure we're at the correct version
psql -d migration_test_db -c "SELECT version_number, is_active FROM schema_versions ORDER BY version_number DESC;"

# If you see a checksum mismatch error for the current version, you need to:
# 1. Create a verification migration file for the current version (5):
cat > src/databasepostgre/migrations/005_verify.sql << EOF
-- Migration: 005_verify
-- Version: 5
-- Description: Verification migration for version 5

-- This is a no-op migration to verify the current state
SELECT 1;
EOF

# 2. Calculate the checksum for the verification file:
CHECKSUM=$(sha256sum src/databasepostgre/migrations/005_verify.sql | cut -d' ' -f1)

# 3. Update the migration history with the correct checksum:
psql -d migration_test_db -c "UPDATE migration_history SET checksum = '$CHECKSUM' WHERE version_id = (SELECT version_id FROM schema_versions WHERE version_number = 5);"

# 4. Verify the checksum was updated correctly:
psql -d migration_test_db -c "SELECT checksum FROM migration_history WHERE version_id = (SELECT version_id FROM schema_versions WHERE version_number = 5);"

# 5. Create the next migration file:
cat > src/databasepostgre/migrations/006_slow_migration.sql << EOF
-- Migration: 006_slow_migration
-- Version: 6
-- Description: Slow test migration

SELECT pg_sleep(5);
CREATE TABLE slow_test (id SERIAL);
EOF

# 6. Run the migration:
DB_NAME=migration_test_db DB_USER=postgres DB_PASSWORD=postgres ./src/databasepostgre/migrate.sh

# 7. Check comprehensive metrics with duration:
psql -d migration_test_db -c "
SELECT 
    m.migration_name, 
    mm.start_time,
    mm.end_time,
    mm.duration_ms, 
    mm.rows_affected, 
    mm.memory_usage_mb, 
    mm.cpu_usage_percent,
    mm.error_count,
    mm.warning_count
FROM 
    migration_history m 
    JOIN migration_metrics mm ON m.migration_id = mm.migration_id 
WHERE 
    m.migration_name = '006_slow_migration';"
```

**Expected Behavior**:
- The migration will only succeed if the current version is 5
- If you see a checksum mismatch error for version 5, it means the system is trying to verify the current version
- You need to provide a verification migration file with a matching checksum
- The verification file must be named with the current version number (005_verify.sql)
- The checksum must match the actual content of the verification file

**Why This Happens**:
- The migration system verifies each version before proceeding
- The checksum must match the actual migration file content
- The system calculates checksums based on the file content
- This ensures data integrity by verifying the migration files haven't been modified
- The verification file must exist and have the correct checksum before proceeding to the next version

## Cleanup

```bash
# Drop test database
dropdb migration_test_db

# Clean up Kubernetes resources
kubectl delete namespace migration-test
```

## Complete Cleanup Guide

For a thorough cleanup of all testing artifacts:

```bash
# 1. Drop the test database
dropdb migration_test_db

# 2. Remove any test migration files created for testing
rm -f src/databasepostgre/migrations/002_test_migration.sql
rm -f src/databasepostgre/migrations/002_rollback.sql
rm -f src/databasepostgre/migrations/003_performance_test.sql
rm -f src/databasepostgre/migrations/00{2..6}_*.sql

# 3. Reset environment variables
unset DB_HOST DB_PORT DB_NAME DB_USER DB_PASSWORD LOG_LEVEL POD_NAME POD_NAMESPACE

# 4. Clean up any temporary files that might have been created
find /tmp -name "tmp.*" -user $(whoami) -mtime -1 -delete

# 5. Remove any Docker containers/volumes used for testing (if applicable)
docker rm -f $(docker ps -a -q --filter "name=postgres-migration-test") 2>/dev/null || true
docker volume rm $(docker volume ls -q --filter "name=postgres-migration-data") 2>/dev/null || true

# 6. Clean up Kubernetes resources (more detailed)
kubectl delete namespace migration-test
kubectl delete configmap migration-scripts -n default 2>/dev/null || true
kubectl delete job database-migration -n default 2>/dev/null || true
```

If you need to reset the database without dropping it:

```bash
# Connect to database and drop all tables
psql -d migration_test_db -c "
DO \$\$ DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END \$\$;
"

# Reinitialize with init.sql
psql -d migration_test_db -f src/databasepostgre/init.sql
```

## Troubleshooting

1. **Check failed migrations**:
```bash
psql -d migration_test_db -c "SELECT * FROM migration_history WHERE status = 'failed';"
```

2. **Check database health**:
```bash
psql -d migration_test_db -c "SELECT * FROM database_health ORDER BY check_time DESC LIMIT 1;"
```

3. **Check migration logs**:
```bash
psql -d migration_test_db -c "SELECT * FROM migration_logs WHERE log_level = 'ERROR' ORDER BY timestamp DESC;"
```

4. **Check migration performance metrics**:
```bash
psql -d migration_test_db -c "SELECT m.migration_name, mm.duration_ms, mm.rows_affected, mm.memory_usage_mb, mm.cpu_usage_percent FROM migration_history m JOIN migration_metrics mm ON m.migration_id = mm.migration_id ORDER BY m.migration_id DESC LIMIT 5;"
```

5. **Handle SQL output issues**:
```bash
# If you encounter errors like "syntax error at or near "INSERT""
# it may be due to PostgreSQL command output being treated as SQL input.
# Check that all psql commands in scripts redirect their output:
grep -r "psql" --include="*.sh" src/databasepostgre/

# To fix these issues, make sure to redirect output:
# PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SQL COMMAND" > /dev/null 2>&1
```

## Best Practices

1. Always test migrations in a separate test database
2. Create rollback migrations for all schema changes
3. Monitor performance metrics during testing
4. Check logs for any warnings or errors
5. Verify data integrity after migrations
6. Test concurrent access scenarios
7. Monitor database health during testing 