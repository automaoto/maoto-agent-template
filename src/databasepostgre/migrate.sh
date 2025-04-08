#!/bin/bash

# Migration manager script
# This script handles database migrations and version transitions

set -e

# Database connection parameters
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-postgres}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"
POD_NAME="${POD_NAME:-unknown}"
POD_NAMESPACE="${POD_NAMESPACE:-default}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"

# Function to execute SQL
execute_sql() {
    local command="$1"
    local need_result="$2"
    
    if [ "$need_result" = "true" ]; then
        # For commands that need to return a result (like SELECT)
        local result=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "$command")
        echo "$result"
    else
        # For commands that don't need a result (like INSERT, UPDATE, DELETE)
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "$command"
    fi
}

# Function to log messages
log_message() {
    local level="$1"
    local message="$2"
    local context="$3"
    local migration_id="$4"
    
    # Convert log level to uppercase for comparison
    local current_level=$(echo "$LOG_LEVEL" | tr '[:lower:]' '[:upper:]')
    local message_level=$(echo "$level" | tr '[:lower:]' '[:upper:]')
    
    # Define log level priorities
    local -A priorities=(
        ["DEBUG"]=0
        ["INFO"]=1
        ["WARN"]=2
        ["ERROR"]=3
    )
    
    # Only log if message level is >= current level
    if [ "${priorities[$message_level]}" -ge "${priorities[$current_level]}" ]; then
        local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        echo "[$timestamp] $level: $message" >&2
        
        # Store log in database if migration_id is provided
        if [ -n "$migration_id" ]; then
            local context_json=$(echo "$context" | jq -c . 2>/dev/null || echo "{}")
            execute_sql "INSERT INTO migration_logs (migration_id, log_level, message, context, pod_name, pod_namespace) 
                        VALUES ($migration_id, '$level', '$message', '$context_json', '$POD_NAME', '$POD_NAMESPACE');"
        fi
    fi
}

# Function to get database health
get_database_health() {
    log_message "DEBUG" "Starting database health check"
    
    # Check if we can connect to the database
    if ! PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
        log_message "ERROR" "Failed to connect to database"
        echo "unhealthy"
        return 1
    fi
    
    # Get active connections
    local active_connections=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM pg_stat_activity;")
    log_message "DEBUG" "Active connections: $active_connections"
    
    # Get transaction count
    local transaction_count=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active' AND query NOT LIKE '%pg_stat_activity%';")
    log_message "DEBUG" "Transaction count: $transaction_count"
    
    # Get dead tuples
    local dead_tuples=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT SUM(n_dead_tup) FROM pg_stat_user_tables;")
    log_message "DEBUG" "Dead tuples: $dead_tuples"
    
    # Get bloat ratio
    local relation_size=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT SUM(pg_relation_size(oid)) FROM pg_class WHERE relkind = 'r';")
    local total_size=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT SUM(pg_total_relation_size(oid)) FROM pg_class WHERE relkind = 'r';")
    local bloat_ratio=$(echo "scale=3; ($total_size - $relation_size) / $total_size" | bc)
    log_message "DEBUG" "Bloat ratio: $bloat_ratio"
    
    local bloat_status="normal"
    if (( $(echo "$bloat_ratio > 0.5" | bc -l) )); then
        bloat_status="high"
    fi
    log_message "DEBUG" "Bloat status: $bloat_status"
    
    # Get index usage ratio
    local index_scan=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COALESCE(SUM(idx_scan), 0) FROM pg_stat_user_indexes;")
    local seq_scan=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COALESCE(SUM(seq_scan), 0) FROM pg_stat_user_tables;")
    
    local index_usage_ratio=0
    if [ "$seq_scan" -gt 0 ]; then
        index_usage_ratio=$(echo "scale=10; $index_scan / ($index_scan + $seq_scan)" | bc)
    fi
    log_message "DEBUG" "Index usage ratio: $index_usage_ratio"
    
    # Get cache hit ratio
    local cache_hit_ratio=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT CASE WHEN sum(blks_hit) + sum(blks_read) = 0 THEN 0 ELSE sum(blks_hit) / (sum(blks_hit) + sum(blks_read)::float) END FROM pg_stat_database;")
    log_message "DEBUG" "Cache hit ratio: $cache_hit_ratio"
    
    # Get replication lag
    local replication_lag=0
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1 FROM pg_stat_replication LIMIT 1;" >/dev/null 2>&1; then
        replication_lag=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) FROM pg_stat_replication;")
        # Ensure replication_lag is a number
        if [ -z "$replication_lag" ] || ! [[ "$replication_lag" =~ ^[0-9]*\.?[0-9]+$ ]]; then
            replication_lag=0
        fi
    fi
    log_message "DEBUG" "Replication lag: $replication_lag"
    
    # Set health status
    local health_status="healthy"
    
    # Format numbers for JSON
    bloat_ratio=$(printf "%.6f" "$bloat_ratio")
    index_usage_ratio=$(printf "%.6f" "$index_usage_ratio")
    cache_hit_ratio=$(printf "%.6f" "$cache_hit_ratio")
    
    local details=$(cat << EOF
{
    "active_connections": $active_connections,
    "transaction_count": $transaction_count,
    "dead_tuples": $dead_tuples,
    "bloat_ratio": $bloat_ratio,
    "bloat_status": "$bloat_status",
    "index_usage_ratio": $index_usage_ratio,
    "cache_hit_ratio": $cache_hit_ratio,
    "replication_lag": $replication_lag
}
EOF
)
    
    # Insert health check record
    execute_sql "INSERT INTO database_health (check_time, active_connections, transaction_count, dead_tuples, bloat_ratio, index_usage_ratio, cache_hit_ratio, replication_lag, health_status, details) 
                VALUES (NOW(), $active_connections, $transaction_count, $dead_tuples, $bloat_ratio, $index_usage_ratio, $cache_hit_ratio, $replication_lag, '$health_status', '$details'::jsonb);"
    
    log_message "INFO" "Health status: $health_status"
    echo "$health_status"
}

# Function to start migration metrics collection
start_metrics_collection() {
    local migration_id="$1"
    local start_time=$(date +%s%N | cut -b1-13)
    local memory_usage=$(ps -o rss= -p $$ | awk '{print $1/1024}')
    local cpu_usage=$(ps -o pcpu= -p $$)
    
    execute_sql "INSERT INTO migration_metrics 
                 (migration_id, start_time, memory_usage_mb, cpu_usage_percent) 
                 VALUES 
                 ($migration_id, to_timestamp($start_time/1000.0), 
                  $memory_usage,
                  $cpu_usage);" "false"
    
    echo "$start_time"
}

# Function to update migration metrics
update_metrics() {
    local migration_id="$1"
    local start_time="$2"
    local rows_affected="$3"
    local end_time=$(date +%s%N | cut -b1-13)
    local duration_ms=$((end_time - start_time))
    local memory_usage=$(ps -o rss= -p $$ | awk '{print $1/1024}')
    local cpu_usage=$(ps -o pcpu= -p $$)
    
    execute_sql "UPDATE migration_metrics 
                 SET end_time = to_timestamp($end_time/1000.0),
                     duration_ms = $duration_ms,
                     rows_affected = $rows_affected,
                     memory_usage_mb = $memory_usage,
                     cpu_usage_percent = $cpu_usage,
                     lock_wait_time_ms = COALESCE(
                         (SELECT EXTRACT(EPOCH FROM (now() - query_start)) * 1000
                         FROM pg_stat_activity
                         WHERE pid = pg_backend_pid()),
                         0
                     )
                 WHERE migration_id = $migration_id;" "false"
}

# Function to calculate checksum of a file
calculate_checksum() {
    if [ -f "$1" ]; then
        sha256sum "$1" | cut -d' ' -f1
    else
        echo "0"
    fi
}

# Function to get current version
get_current_version() {
    local version=$(execute_sql "SELECT COALESCE(MAX(version_number)::integer, 0) FROM schema_versions WHERE is_active = TRUE;" "true")
    echo "$version" | tr -d '[:space:]'
}

# Function to check if a migration has already been applied
check_migration_applied() {
    local migration_name="$1"
    local version="$2"
    local status=$(execute_sql "SELECT COALESCE(status, '') FROM migration_history 
                              WHERE migration_name = '$migration_name' 
                              AND version_id = (SELECT version_id FROM schema_versions WHERE version_number = $version);" "true")
    echo "$status" | tr -d '[:space:]'
}

# Function to verify database state
verify_database_state() {
    local version="$1"
    local checksum="$2"
    
    # Check database health before proceeding
    health_status=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT 1;" >/dev/null 2>&1 && echo "healthy" || echo "unhealthy")
    log_message "DEBUG" "In verify_database_state: health_status=$health_status"
    
    if [ "$health_status" != "healthy" ]; then
        log_message "WARN" "Database health check failed" "{\"health_status\": \"$health_status\"}"
        return 1
    fi
    
    # Skip checksum verification for version 1 (initial schema)
    if [ "$version" -eq 1 ]; then
        return 0
    fi
    
    # Check if there are any failed migrations
    local failed_migrations=$(execute_sql "SELECT COALESCE(COUNT(*)::integer, 0) FROM migration_history WHERE status = 'failed';" "true")
    log_message "DEBUG" "Failed migrations: $failed_migrations"
    if [ "$failed_migrations" -gt 0 ]; then
        log_message "WARN" "There are failed migrations in the history" "{\"failed_count\": $failed_migrations}"
        return 1
    fi
    
    # If no migration history exists for current version, skip checksum verification
    local existing_migration=$(execute_sql "SELECT COUNT(*) FROM migration_history 
                                         WHERE version_id = (SELECT version_id FROM schema_versions WHERE version_number = $version);" "true")
    existing_migration=$(echo "$existing_migration" | tr -d '[:space:]')
    
    log_message "DEBUG" "Existing migration count for version $version: $existing_migration"
    if [ "$existing_migration" -eq 0 ]; then
        log_message "INFO" "No migration history found for version $version, skipping checksum verification"
        return 0
    fi
    
    # Check if the migration was successful
    local migration_status=$(execute_sql "SELECT status FROM migration_history 
                                        WHERE version_id = (SELECT version_id FROM schema_versions WHERE version_number = $version);" "true")
    migration_status=$(echo "$migration_status" | tr -d '[:space:]')
    
    if [ "$migration_status" != "success" ]; then
        log_message "WARN" "Migration for version $version was not successful" "{\"status\": \"$migration_status\"}"
        return 1
    fi
    
    # Verify migration checksums
    local stored_checksum=$(execute_sql "SELECT COALESCE(checksum, '0') FROM migration_history 
                                       WHERE version_id = (SELECT version_id FROM schema_versions WHERE version_number = $version);" "true")
    stored_checksum=$(echo "$stored_checksum" | tr -d '[:space:]')
    
    log_message "DEBUG" "Stored checksum: $stored_checksum, Calculated checksum: $checksum"
    if [ "$stored_checksum" != "$checksum" ]; then
        log_message "ERROR" "Migration checksum mismatch" "{\"stored\": \"$stored_checksum\", \"calculated\": \"$checksum\"}"
        return 1
    fi
    
    return 0
}

# Function to collect system metrics
collect_system_metrics() {
    local pid=$$
    
    # Get memory usage in KB and convert to MB
    local memory_kb=$(ps -o rss= -p $pid)
    local memory_mb=$(echo "scale=2; $memory_kb / 1024" | bc)
    
    # Get CPU usage percentage
    local cpu_percent=$(ps -o %cpu= -p $pid)
    
    # Return as JSON
    echo "{\"memory_mb\": $memory_mb, \"cpu_percent\": $cpu_percent}"
}

# Function to count affected rows from SQL output
count_affected_rows() {
    local output="$1"
    local count=0
    
    # Extract affected row counts from output
    while read -r line; do
        if [[ $line =~ INSERT\ ([0-9]+) ]]; then
            count=$((count + ${BASH_REMATCH[1]}))
        elif [[ $line =~ UPDATE\ ([0-9]+) ]]; then
            count=$((count + ${BASH_REMATCH[1]}))
        elif [[ $line =~ DELETE\ ([0-9]+) ]]; then
            count=$((count + ${BASH_REMATCH[1]}))
        elif [[ $line =~ CREATE\ TABLE ]]; then
            count=$((count + 1))
        elif [[ $line =~ CREATE\ INDEX ]]; then
            count=$((count + 1))
        elif [[ $line =~ ALTER\ TABLE ]]; then
            count=$((count + 1))
        fi
    done <<< "$output"
    
    echo "$count"
}

# Function to count errors and warnings from SQL output
count_errors_warnings() {
    local output="$1"
    local error_count=0
    local warning_count=0
    
    # Count errors and warnings
    while read -r line; do
        if [[ $line =~ ERROR|FATAL|PANIC ]]; then
            error_count=$((error_count + 1))
        elif [[ $line =~ WARNING|NOTICE ]]; then
            warning_count=$((warning_count + 1))
        fi
    done <<< "$output"
    
    echo "{\"errors\": $error_count, \"warnings\": $warning_count}"
}

# Function to execute migration SQL
execute_migration() {
    local version=$1
    local migration_name=$2
    local sql_file=$3
    local migration_type=$4  # 'migrate' or 'rollback'
    
    log_message "INFO" "Applying migration: $migration_name"
    
    # Generate migration ID (timestamp)
    local migration_id=$(date +%s)
    
    # Ensure schema version exists
    execute_sql "INSERT INTO schema_versions (version_number, description) 
                VALUES ($version, 'Migration $migration_name') 
                ON CONFLICT (version_number) DO NOTHING;"
    
    # Get version ID
    local version_id=$(execute_sql "SELECT version_id FROM schema_versions WHERE version_number = $version;" "true")
    version_id=$(echo "$version_id" | tr -d '[:space:]')
    
    # Calculate checksum
    local checksum=$(sha256sum "$sql_file" | cut -d' ' -f1)
    
    # Collect initial metrics
    local start_metrics=$(collect_system_metrics)
    local start_memory=$(echo "$start_metrics" | jq -r '.memory_mb')
    local start_cpu=$(echo "$start_metrics" | jq -r '.cpu_percent')
    
    # Start execution time
    local start_time=$(date +%s%N)
    local start_timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Execute the SQL file
    local output
    local exit_code
    
    # Execute SQL and store output and exit code
    output=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f "$sql_file" 2>&1)
    exit_code=$?
    
    # Print output for debugging
    echo "$output"
    
    # Collect end metrics
    local end_metrics=$(collect_system_metrics)
    local end_memory=$(echo "$end_metrics" | jq -r '.memory_mb')
    local end_cpu=$(echo "$end_metrics" | jq -r '.cpu_percent')
    
    # Use the end memory value directly rather than the differential
    local memory_usage="$end_memory"
    local cpu_usage=$(echo "scale=2; ($start_cpu + $end_cpu) / 2" | bc)
    
    # End execution time
    local end_time=$(date +%s%N)
    local end_timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Calculate duration in milliseconds
    local duration_ns=$((end_time - start_time))
    local duration_ms=$((duration_ns / 1000000))
    
    # Count affected rows
    local rows_affected=$(count_affected_rows "$output")
    
    # Count errors and warnings
    local error_counts=$(count_errors_warnings "$output")
    local error_count=$(echo "$error_counts" | jq -r '.errors')
    local warning_count=$(echo "$error_counts" | jq -r '.warnings')
    
    # Determine status based on exit code
    local status
    if [ $exit_code -eq 0 ]; then
        status="success"
    else
        status="failed"
        log_message "ERROR" "Migration failed: $output" "{\"migration_name\": \"$migration_name\"}"
    fi
    
    # Store migration record
    if [ "$migration_type" = "migrate" ]; then
        execute_sql "INSERT INTO migration_history (version_id, migration_name, status, checksum) 
                    VALUES ($version_id, '$migration_name', '$status', '$checksum');"
    elif [ "$migration_type" = "rollback" ]; then
        execute_sql "INSERT INTO rollback_history (from_version, to_version, status, initiated_by) 
                    VALUES ($version, $((version-1)), '$status', '$POD_NAME');"
    fi
    
    # Get migration_id from the inserted record
    if [ "$migration_type" = "migrate" ]; then
        local db_migration_id=$(execute_sql "SELECT migration_id FROM migration_history 
                                           WHERE version_id = $version_id 
                                           AND migration_name = '$migration_name';" "true")
        db_migration_id=$(echo "$db_migration_id" | tr -d '[:space:]')
        
        # Store complete metrics
        execute_sql "INSERT INTO migration_metrics (
                        migration_id, 
                        start_time, 
                        end_time, 
                        duration_ms, 
                        rows_affected, 
                        memory_usage_mb, 
                        cpu_usage_percent, 
                        error_count, 
                        warning_count
                    ) VALUES (
                        $db_migration_id, 
                        '$start_timestamp'::timestamptz, 
                        '$end_timestamp'::timestamptz, 
                        $duration_ms, 
                        $rows_affected, 
                        $memory_usage, 
                        $cpu_usage, 
                        $error_count, 
                        $warning_count
                    );"
    fi
    
    # Check if migration succeeded and update schema version
    if [ "$status" = "success" ] && [ "$migration_type" = "migrate" ]; then
        log_message "INFO" "Migration completed successfully"
        return 0
    else
        log_message "ERROR" "Migration failed with exit code $exit_code"
        return 1
    fi
}

# Function to apply a migration
apply_migration() {
    local migration_file="$1"
    local version="$2"
    local migration_name=$(basename "$migration_file" .sql)
    
    # Check if migration has already been applied
    local status=$(check_migration_applied "$migration_name" "$version")
    if [ "$status" = "success" ]; then
        log_message "INFO" "Migration $migration_name already applied, skipping"
        # Update active version anyway
        execute_sql "UPDATE schema_versions SET is_active = FALSE WHERE version_number != $version;"
        execute_sql "UPDATE schema_versions SET is_active = TRUE WHERE version_number = $version;"
        return 0
    fi
    
    # Execute the migration
    if execute_migration "$version" "$migration_name" "$migration_file" "migrate"; then
        # Update active version
        execute_sql "UPDATE schema_versions SET is_active = FALSE WHERE version_number != $version;"
        execute_sql "UPDATE schema_versions SET is_active = TRUE WHERE version_number = $version;"
        return 0
    else
        return 1
    fi
}

# Function to perform rollback
perform_rollback() {
    local from_version="$1"
    local to_version="$2"
    
    log_message "INFO" "Initiating rollback from version $from_version to $to_version" "{\"from\": $from_version, \"to\": $to_version}"
    
    # Insert rollback record
    execute_sql "INSERT INTO rollback_history (from_version, to_version, status, initiated_by)
                VALUES ($from_version, $to_version, 'running', COALESCE('$POD_NAME', 'migration_script'));"
    
    # Apply rollback migrations in reverse order
    for version in $(seq $((from_version)) -1 $((to_version + 1))); do
        rollback_file="src/databasepostgre/migrations/$(printf "%03d" $version)_rollback.sql"
        if [ -f "$rollback_file" ]; then
            local rollback_name=$(basename "$rollback_file" .sql)
            log_message "INFO" "Applying rollback migration: $rollback_name"
            execute_migration "$version" "$rollback_name" "$rollback_file" "rollback"
        fi
    done
    
    # Update active version - don't delete any versions due to foreign key constraints
    # Instead, mark all versions inactive except the target version
    execute_sql "UPDATE schema_versions SET is_active = FALSE WHERE version_number != $to_version;"
    execute_sql "UPDATE schema_versions SET is_active = TRUE WHERE version_number = $to_version;"
    
    # Also mark the source version as invalid to prevent future migrations from it
    execute_sql "UPDATE schema_versions 
                SET description = 'INVALID: ' || COALESCE(description, 'Rollback source') 
                WHERE version_number = $from_version;"
    
    # Update rollback status
    execute_sql "UPDATE rollback_history 
                SET status = 'completed', completed_at = NOW() 
                WHERE from_version = $from_version AND to_version = $to_version 
                AND status = 'running';"
    
    log_message "INFO" "Rollback completed successfully"
}

# Main migration logic
main() {
    local current_version=$(get_current_version)
    
    # Find highest available migration version
    local available_migrations=$(find src/databasepostgre/migrations -name "[0-9][0-9][0-9]_*.sql" ! -name "*rollback.sql" | sort)
    local target_version=1
    
    # If we have migrations, set target to the highest numbered one
    if [ -n "$available_migrations" ]; then
        local highest_migration=$(echo "$available_migrations" | tail -n 1)
        local version_pattern="^.*/([0-9][0-9][0-9])_.*\.sql$"
        if [[ "$highest_migration" =~ $version_pattern ]]; then
            target_version=$(echo "${BASH_REMATCH[1]}" | sed 's/^0*//')
        fi
    fi
    
    log_message "INFO" "Starting migration process" "{\"current_version\": $current_version, \"target_version\": $target_version}"
    
    # Run health check first - without redirecting output to see if it works
    log_message "INFO" "Running initial health check"
    local health_status=$(get_database_health)
    log_message "INFO" "Health status: $health_status"
    
    # Skip verification for initial state or if no migration file exists
    if [ "$current_version" -ne 1 ]; then
        local current_migration_file=$(find src/databasepostgre/migrations -name "$(printf "%03d" $current_version)_*.sql" ! -name "*rollback.sql" | head -n 1)
        
        if [ -n "$current_migration_file" ] && [ -f "$current_migration_file" ]; then
            log_message "INFO" "Verifying database state for version $current_version"
            local checksum=$(calculate_checksum "$current_migration_file")
            if ! verify_database_state "$current_version" "$checksum"; then
                log_message "ERROR" "Database state verification failed"
                exit 1
            fi
        else
            log_message "INFO" "No migration file found for version $current_version, skipping verification"
        fi
    else
        log_message "INFO" "At initial version, skipping verification"
    fi
    
    if [ "$current_version" -lt "$target_version" ]; then
        log_message "INFO" "Upgrading database schema"
        for version in $(seq $((current_version + 1)) $target_version); do
            migration_file=$(find src/databasepostgre/migrations -name "$(printf "%03d" $version)_*.sql" ! -name "*rollback.sql" | head -n 1)
            if [ -f "$migration_file" ]; then
                apply_migration "$migration_file" "$version"
            fi
        done
    elif [ "$current_version" -gt "$target_version" ]; then
        log_message "INFO" "Initiating rollback from version $current_version to $target_version"
        perform_rollback "$current_version" "$target_version"
    else
        log_message "INFO" "Database is already at target version"
    fi
    
    # Run final health check with more verbose logging
    log_message "INFO" "Running final health check"
    health_status=$(get_database_health)
    log_message "INFO" "Final health status: $health_status"
}

# Run main function
main 