BEGIN;

CREATE SCHEMA IF NOT EXISTS iat_ai_safety;
SET search_path TO iat_ai_safety;

CREATE TABLE IF NOT EXISTS devices (
    device_id BIGSERIAL PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    location VARCHAR(150) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'NORMAL',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    CONSTRAINT ck_iat_devices_status
        CHECK (status IN ('NORMAL', 'WARNING', 'DANGER', 'OFFLINE'))
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id BIGSERIAL PRIMARY KEY,
    device_id BIGINT,
    alert_type VARCHAR(30) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message VARCHAR(500) NOT NULL,
    checked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    checked_at TIMESTAMP,
    CONSTRAINT fk_iat_alerts_device
        FOREIGN KEY (device_id) REFERENCES devices(device_id),
    CONSTRAINT ck_iat_alerts_type
        CHECK (alert_type IN ('DEVICE_RISK', 'SAFETY_EVENT', 'SYSTEM')),
    CONSTRAINT ck_iat_alerts_severity
        CHECK (severity IN ('INFO', 'WARNING', 'CRITICAL'))
);

CREATE TABLE IF NOT EXISTS device_status_logs (
    status_log_id BIGSERIAL PRIMARY KEY,
    device_id BIGINT NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    vibration DOUBLE PRECISION NOT NULL,
    noise DOUBLE PRECISION NOT NULL,
    risk_score DOUBLE PRECISION NOT NULL,
    status VARCHAR(20) NOT NULL,
    model_version VARCHAR(80),
    prediction_horizon VARCHAR(50),
    analysis_message VARCHAR(700),
    recommendation VARCHAR(700),
    threshold_violations VARCHAR(500),
    temperature_score DOUBLE PRECISION,
    vibration_score DOUBLE PRECISION,
    noise_score DOUBLE PRECISION,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_iat_device_status_logs_device
        FOREIGN KEY (device_id) REFERENCES devices(device_id),
    CONSTRAINT ck_iat_device_status_logs_status
        CHECK (status IN ('NORMAL', 'WARNING', 'DANGER', 'OFFLINE'))
);

CREATE TABLE IF NOT EXISTS safety_events (
    event_id BIGSERIAL PRIMARY KEY,
    device_id BIGINT NOT NULL,
    event_type VARCHAR(40) NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    image_path VARCHAR(500),
    result_image_path VARCHAR(500),
    message VARCHAR(500) NOT NULL,
    detection_summary VARCHAR(2000),
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    CONSTRAINT fk_iat_safety_events_device
        FOREIGN KEY (device_id) REFERENCES devices(device_id),
    CONSTRAINT ck_iat_safety_events_type
        CHECK (event_type IN (
            'FALL_DETECTED',
            'DOOR_ENTRAPMENT',
            'OBSTACLE_DETECTED',
            'DANGER_ZONE_ACCESS',
            'SAFETY_OBJECT_DETECTED'
        )),
    CONSTRAINT ck_iat_safety_events_confidence
        CHECK (confidence >= 0 AND confidence <= 1)
);

CREATE INDEX IF NOT EXISTS idx_iat_devices_status
    ON devices(status);
CREATE INDEX IF NOT EXISTS idx_iat_devices_created_at
    ON devices(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_iat_alerts_device_id
    ON alerts(device_id);
CREATE INDEX IF NOT EXISTS idx_iat_alerts_checked
    ON alerts(checked);
CREATE INDEX IF NOT EXISTS idx_iat_alerts_created_at
    ON alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_iat_device_status_logs_device_id
    ON device_status_logs(device_id);
CREATE INDEX IF NOT EXISTS idx_iat_device_status_logs_created_at
    ON device_status_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_iat_safety_events_device_id
    ON safety_events(device_id);
CREATE INDEX IF NOT EXISTS idx_iat_safety_events_resolved
    ON safety_events(resolved);
CREATE INDEX IF NOT EXISTS idx_iat_safety_events_created_at
    ON safety_events(created_at DESC);

COMMIT;
