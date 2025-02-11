Running migrations offline with URL: postgresql+psycopg://postgres:postgres123@content_moderation_db:5432/moderation_db
BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 690ed9b651cc

CREATE TABLE moderation_results (
    id SERIAL NOT NULL, 
    text VARCHAR, 
    task_id VARCHAR, 
    status VARCHAR, 
    results JSON, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_moderation_results_id ON moderation_results (id);

CREATE UNIQUE INDEX ix_moderation_results_text ON moderation_results (text);

INSERT INTO alembic_version (version_num) VALUES ('690ed9b651cc') RETURNING alembic_version.version_num;

COMMIT;

