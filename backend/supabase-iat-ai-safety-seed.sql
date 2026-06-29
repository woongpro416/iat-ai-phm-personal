BEGIN;

SET search_path TO iat_ai_safety;

INSERT INTO devices (device_name, device_type, location, status, created_at, updated_at)
SELECT 'Line A Robot Arm', 'ROBOT_ARM', 'Production Line A', 'WARNING', CURRENT_TIMESTAMP - INTERVAL '3 days', CURRENT_TIMESTAMP - INTERVAL '10 minutes'
WHERE NOT EXISTS (
    SELECT 1 FROM devices WHERE device_name = 'Line A Robot Arm'
);

INSERT INTO devices (device_name, device_type, location, status, created_at, updated_at)
SELECT 'Packaging Conveyor', 'CONVEYOR', 'Packaging Zone', 'NORMAL', CURRENT_TIMESTAMP - INTERVAL '2 days', CURRENT_TIMESTAMP - INTERVAL '20 minutes'
WHERE NOT EXISTS (
    SELECT 1 FROM devices WHERE device_name = 'Packaging Conveyor'
);

INSERT INTO devices (device_name, device_type, location, status, created_at, updated_at)
SELECT 'Safety Gate Sensor', 'SENSOR', 'Safety Gate 2', 'DANGER', CURRENT_TIMESTAMP - INTERVAL '1 day', CURRENT_TIMESTAMP - INTERVAL '5 minutes'
WHERE NOT EXISTS (
    SELECT 1 FROM devices WHERE device_name = 'Safety Gate Sensor'
);

INSERT INTO device_status_logs (
    device_id,
    temperature,
    vibration,
    noise,
    risk_score,
    status,
    model_version,
    prediction_horizon,
    analysis_message,
    recommendation,
    threshold_violations,
    temperature_score,
    vibration_score,
    noise_score,
    created_at
)
SELECT
    d.device_id,
    v.temperature,
    v.vibration,
    v.noise,
    v.risk_score,
    v.status,
    'phm-baseline-v1',
    '24h',
    v.analysis_message,
    v.recommendation,
    v.threshold_violations,
    v.temperature_score,
    v.vibration_score,
    v.noise_score,
    CURRENT_TIMESTAMP - v.created_offset
FROM devices d
JOIN (
    VALUES
        ('Line A Robot Arm', 72.5, 5.8, 71.0, 72.4, 'WARNING', 'Vibration and temperature are above normal range.', 'Schedule bearing inspection and reduce load for the next cycle.', 'temperature,vibration', 68.0, 82.0, 46.0, INTERVAL '45 minutes'),
        ('Line A Robot Arm', 69.2, 5.1, 68.5, 64.8, 'WARNING', 'Risk score remains elevated after recent operation.', 'Monitor vibration trend and inspect lubrication state.', 'vibration', 58.0, 75.0, 42.0, INTERVAL '2 hours'),
        ('Packaging Conveyor', 51.4, 2.2, 58.0, 24.6, 'NORMAL', 'Device status is within expected operating range.', 'Continue normal operation.', '', 22.0, 18.0, 28.0, INTERVAL '3 hours'),
        ('Safety Gate Sensor', 80.1, 6.4, 76.3, 88.7, 'DANGER', 'Multiple threshold violations detected near safety gate.', 'Stop operation and inspect sensor alignment immediately.', 'temperature,vibration,noise', 84.0, 91.0, 79.0, INTERVAL '12 minutes'),
        ('Safety Gate Sensor', 77.8, 6.1, 73.9, 82.3, 'DANGER', 'Risk remains high in the safety gate area.', 'Keep area locked until maintenance confirmation.', 'temperature,vibration', 80.0, 86.0, 70.0, INTERVAL '1 hour')
) AS v(device_name, temperature, vibration, noise, risk_score, status, analysis_message, recommendation, threshold_violations, temperature_score, vibration_score, noise_score, created_offset)
    ON d.device_name = v.device_name
WHERE NOT EXISTS (
    SELECT 1
    FROM device_status_logs l
    WHERE l.device_id = d.device_id
      AND l.risk_score = v.risk_score
      AND l.model_version = 'phm-baseline-v1'
);

INSERT INTO alerts (device_id, alert_type, severity, message, checked, created_at, checked_at)
SELECT
    d.device_id,
    v.alert_type,
    v.severity,
    v.message,
    v.checked,
    CURRENT_TIMESTAMP - v.created_offset,
    CASE WHEN v.checked THEN CURRENT_TIMESTAMP - INTERVAL '30 minutes' ELSE NULL END
FROM devices d
JOIN (
    VALUES
        ('Line A Robot Arm', 'DEVICE_RISK', 'WARNING', 'Robot arm vibration risk score exceeded warning threshold.', FALSE, INTERVAL '40 minutes'),
        ('Safety Gate Sensor', 'DEVICE_RISK', 'CRITICAL', 'Safety gate sensor entered danger status.', FALSE, INTERVAL '10 minutes'),
        ('Packaging Conveyor', 'SYSTEM', 'INFO', 'Packaging conveyor completed normal periodic check.', TRUE, INTERVAL '4 hours')
) AS v(device_name, alert_type, severity, message, checked, created_offset)
    ON d.device_name = v.device_name
WHERE NOT EXISTS (
    SELECT 1
    FROM alerts a
    WHERE a.device_id = d.device_id
      AND a.alert_type = v.alert_type
      AND a.message = v.message
);

INSERT INTO safety_events (
    device_id,
    event_type,
    confidence,
    image_path,
    result_image_path,
    message,
    detection_summary,
    resolved,
    created_at,
    resolved_at
)
SELECT
    d.device_id,
    v.event_type,
    v.confidence,
    v.image_path,
    v.result_image_path,
    v.message,
    v.detection_summary,
    v.resolved,
    CURRENT_TIMESTAMP - v.created_offset,
    CASE WHEN v.resolved THEN CURRENT_TIMESTAMP - INTERVAL '20 minutes' ELSE NULL END
FROM devices d
JOIN (
    VALUES
        ('Safety Gate Sensor', 'DANGER_ZONE_ACCESS', 0.93, NULL, NULL, 'Worker entered restricted safety gate area.', 'Detected one person inside the configured danger zone.', FALSE, INTERVAL '8 minutes'),
        ('Line A Robot Arm', 'OBSTACLE_DETECTED', 0.86, NULL, NULL, 'Obstacle detected near robot arm operating radius.', 'Detected an object inside the robot arm motion boundary.', TRUE, INTERVAL '2 hours')
) AS v(device_name, event_type, confidence, image_path, result_image_path, message, detection_summary, resolved, created_offset)
    ON d.device_name = v.device_name
WHERE NOT EXISTS (
    SELECT 1
    FROM safety_events s
    WHERE s.device_id = d.device_id
      AND s.event_type = v.event_type
      AND s.message = v.message
);

COMMIT;
