# Start from the official PostgreSQL image
FROM postgres:13@sha256:0b66ab08973087a4592632a719e6b83357bf63a5db4f92ae507cbe0037cbdd85

RUN apt-get update

# Expose the PostgreSQL port
EXPOSE 5432

# Set environment variables for database name, username, and password
ENV POSTGRES_DB=mydatabase
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword

# Copy the initialization script into the Docker entrypoint initialization directory
COPY init.sql /docker-entrypoint-initdb.d/