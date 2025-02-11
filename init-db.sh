#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE moderation_db;
    GRANT ALL PRIVILEGES ON DATABASE moderation_db TO $POSTGRES_USER;
EOSQL
