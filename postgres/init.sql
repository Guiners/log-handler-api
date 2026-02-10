CREATE TABLE application(
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    ingest_key VARCHAR(32) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TYPE error_lvl AS ENUM ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL');

CREATE TABLE event(
    id BIGSERIAL PRIMARY KEY,
    application_id BIGINT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    level error_lvl NOT NULL,
    message VARCHAR(255) NOT NULL,
    stack JSONB,
    tags JSONB,

    CONSTRAINT fk_event_application
        FOREIGN KEY (application_id) REFERENCES application(id) ON DELETE CASCADE
);

CREATE INDEX idx_event_application_id_received_at ON event(application_id, received_at DESC);
CREATE INDEX idx_event_application_id_occurred_at ON event(application_id, occurred_at);
