-- Enable the necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS files (
    file_id UUID PRIMARY KEY NOT NULL,
    apikey_id UUID NOT NULL,
    extension VARCHAR(255) NOT NULL,
    data BYTEA DEFAULT ''::bytea,
    complete BOOLEAN NOT NULL DEFAULT FALSE,
    time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
