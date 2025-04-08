# Start from the official PostgreSQL image
FROM postgres:13@sha256:0b66ab08973087a4592632a719e6b83357bf63a5db4f92ae507cbe0037cbdd85

RUN apt-get update
RUN apt-get install -y postgresql-13-cron

# Expose the PostgreSQL port
EXPOSE 5432

# Copy the initialization script into the Docker entrypoint initialization directory
COPY init.sql /docker-entrypoint-initdb.d/

# Copy migration script and make it executable
COPY migrate.sh /app/
RUN chmod +x /app/migrate.sh

# Ensure pg_cron is loaded
RUN echo "shared_preload_libraries = 'pg_cron'" >> /usr/share/postgresql/postgresql.conf.sample
# Setting the cron database to default, it can also be the specific database you're using
RUN echo "cron.database_name = 'postgres'" >> /usr/share/postgresql/postgresql.conf.sample