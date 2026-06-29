BEGIN;

SET search_path TO iat_ai_safety;

WITH demo_devices AS (
    SELECT device_id
    FROM devices
    WHERE device_name IN (
        'Line A Robot Arm',
        'Packaging Conveyor',
        'Safety Gate Sensor',
        'A라인 로봇암',
        '포장 컨베이어',
        '안전 게이트 센서',
        '무인 셔틀 1호',
        '무인 셔틀 2호',
        '제2터미널 승강장 안전 게이트'
    )
)
DELETE FROM safety_events
WHERE device_id IN (SELECT device_id FROM demo_devices);

WITH demo_devices AS (
    SELECT device_id
    FROM devices
    WHERE device_name IN (
        'Line A Robot Arm',
        'Packaging Conveyor',
        'Safety Gate Sensor',
        'A라인 로봇암',
        '포장 컨베이어',
        '안전 게이트 센서',
        '무인 셔틀 1호',
        '무인 셔틀 2호',
        '제2터미널 승강장 안전 게이트'
    )
)
DELETE FROM alerts
WHERE device_id IN (SELECT device_id FROM demo_devices);

WITH demo_devices AS (
    SELECT device_id
    FROM devices
    WHERE device_name IN (
        'Line A Robot Arm',
        'Packaging Conveyor',
        'Safety Gate Sensor',
        'A라인 로봇암',
        '포장 컨베이어',
        '안전 게이트 센서',
        '무인 셔틀 1호',
        '무인 셔틀 2호',
        '제2터미널 승강장 안전 게이트'
    )
)
DELETE FROM device_status_logs
WHERE device_id IN (SELECT device_id FROM demo_devices);

DELETE FROM devices
WHERE device_name IN (
    'Line A Robot Arm',
    'Packaging Conveyor',
    'Safety Gate Sensor',
    'A라인 로봇암',
    '포장 컨베이어',
    '안전 게이트 센서',
    '무인 셔틀 1호',
    '무인 셔틀 2호',
    '제2터미널 승강장 안전 게이트'
);

INSERT INTO devices (device_name, device_type, location, status, created_at, updated_at)
VALUES
    ('무인 셔틀 1호', 'AUTONOMOUS_TRAIN', '제1터미널-탑승동 순환 노선', 'WARNING', CURRENT_TIMESTAMP - INTERVAL '3 days', CURRENT_TIMESTAMP - INTERVAL '10 minutes'),
    ('무인 셔틀 2호', 'AUTONOMOUS_TRAIN', '제2터미널 장기주차장 연결 노선', 'NORMAL', CURRENT_TIMESTAMP - INTERVAL '2 days', CURRENT_TIMESTAMP - INTERVAL '20 minutes'),
    ('제2터미널 승강장 안전 게이트', 'PLATFORM_GATE', '제2터미널 승강장 B구역', 'DANGER', CURRENT_TIMESTAMP - INTERVAL '1 day', CURRENT_TIMESTAMP - INTERVAL '5 minutes');

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
    'phm-train-baseline-v1',
    '24시간',
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
        ('무인 셔틀 1호', 68.5, 5.8, 69.0, 72.4, 'WARNING', '주행 중 차축 진동과 배터리 냉각 온도가 주의 기준을 초과했습니다.', '다음 회차 운행 전 차축 베어링과 배터리 냉각 계통을 점검하세요.', '배터리온도,차축진동', 66.0, 84.0, 45.0, INTERVAL '45 minutes'),
        ('무인 셔틀 1호', 65.2, 5.1, 66.5, 64.8, 'WARNING', '최근 운행 이후 진동 위험 점수가 계속 주의 구간에 머물고 있습니다.', '감속 운행으로 전환하고 진동 추이를 관제 대시보드에서 모니터링하세요.', '차축진동', 56.0, 76.0, 41.0, INTERVAL '2 hours'),
        ('무인 셔틀 2호', 49.4, 2.2, 55.0, 24.6, 'NORMAL', '구동 모터, 배터리 온도, 차내 소음이 정상 운행 범위 안에 있습니다.', '정상 운행을 계속 진행해도 됩니다.', '', 22.0, 18.0, 26.0, INTERVAL '3 hours'),
        ('제2터미널 승강장 안전 게이트', 77.1, 6.4, 74.3, 88.7, 'DANGER', '승강장 안전 게이트 주변에서 다중 임계값 초과와 접근 위험이 감지되었습니다.', '해당 승강장 출입을 제한하고 게이트 센서 정렬 상태를 즉시 점검하세요.', '센서온도,진동,소음', 82.0, 91.0, 78.0, INTERVAL '12 minutes'),
        ('제2터미널 승강장 안전 게이트', 74.8, 6.1, 71.9, 82.3, 'DANGER', '승강장 B구역의 위험 수준이 계속 높게 유지되고 있습니다.', '정비 확인 전까지 해당 승강장 구역을 통제 상태로 유지하세요.', '센서온도,진동', 79.0, 86.0, 69.0, INTERVAL '1 hour')
) AS v(device_name, temperature, vibration, noise, risk_score, status, analysis_message, recommendation, threshold_violations, temperature_score, vibration_score, noise_score, created_offset)
    ON d.device_name = v.device_name;

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
        ('무인 셔틀 1호', 'DEVICE_RISK', 'WARNING', '무인 셔틀 1호의 차축 진동 위험 점수가 주의 임계값을 초과했습니다.', FALSE, INTERVAL '40 minutes'),
        ('제2터미널 승강장 안전 게이트', 'DEVICE_RISK', 'CRITICAL', '승강장 안전 게이트 센서가 위험 상태로 전환되었습니다.', FALSE, INTERVAL '10 minutes'),
        ('무인 셔틀 2호', 'SYSTEM', 'INFO', '무인 셔틀 2호 정기 운행 점검이 정상적으로 완료되었습니다.', TRUE, INTERVAL '4 hours')
) AS v(device_name, alert_type, severity, message, checked, created_offset)
    ON d.device_name = v.device_name;

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
        ('제2터미널 승강장 안전 게이트', 'DANGER_ZONE_ACCESS', 0.93, NULL, NULL, '승객이 무인 셔틀 진입 전 제한 구역으로 접근했습니다.', '승강장 B구역의 위험 구역 안에서 승객 1명이 감지되었습니다.', FALSE, INTERVAL '8 minutes'),
        ('무인 셔틀 1호', 'OBSTACLE_DETECTED', 0.86, NULL, NULL, '무인 셔틀 1호 전방 선로 주변에서 장애물이 감지되었습니다.', '셔틀 전방 감시 영역 안쪽에서 미확인 물체가 감지되었습니다.', TRUE, INTERVAL '2 hours')
) AS v(device_name, event_type, confidence, image_path, result_image_path, message, detection_summary, resolved, created_offset)
    ON d.device_name = v.device_name;

COMMIT;
