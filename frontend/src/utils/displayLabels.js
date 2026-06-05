const deviceStatusLabels = {
  NORMAL: "정상",
  WARNING: "주의",
  DANGER: "위험",
  OFFLINE: "오프라인",
};

const severityLabels = {
  CRITICAL: "긴급",
  WARNING: "주의",
  INFO: "정보",
};

const eventTypeLabels = {
  FALL: "승객 쓰러짐",
  FALL_DETECTED: "승객 쓰러짐 감지",
  OBSTACLE: "장애물 감지",
  OBSTACLE_DETECTED: "장애물 감지",
  DOOR: "출입문 끼임 위험",
  DOOR_ENTRAPMENT: "출입문 끼임 위험",
  DOOR_RISK: "출입문 끼임 위험",
  DOOR_STUCK: "출입문 끼임 위험",
  DANGER_ZONE: "위험 구역 접근",
  DANGER_ZONE_ACCESS: "위험 구역 접근",
  SAFETY_OBJECT_DETECTED: "안전 객체 탐지",
};

const alertTypeLabels = {
  DEVICE_WARNING: "장비 주의 알림",
  DEVICE_DANGER: "장비 위험 알림",
  DEVICE_RISK: "장비 위험도 알림",
  DEVICE_OFFLINE: "장비 오프라인",
  SAFETY_EVENT: "안전 이벤트 알림",
  FALL: "승객 쓰러짐",
  FALL_DETECTED: "승객 쓰러짐 감지",
  OBSTACLE: "장애물 감지",
  OBSTACLE_DETECTED: "장애물 감지",
  DOOR: "출입문 끼임 위험",
  DOOR_ENTRAPMENT: "출입문 끼임 위험",
  DOOR_RISK: "출입문 끼임 위험",
  DOOR_STUCK: "출입문 끼임 위험",
  DANGER_ZONE: "위험 구역 접근",
  DANGER_ZONE_ACCESS: "위험 구역 접근",
};

const deviceTypeLabels = {
  AUTONOMOUS_SHUTTLE: "무인 셔틀",
};

const fallbackCodeLabel = (value) => {
  if (!value) return "-";

  return String(value)
    .toLowerCase()
    .split("_")
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

export const deviceStatusLabel = (status) => {
  return deviceStatusLabels[status] ?? fallbackCodeLabel(status);
};

export const severityLabel = (severity) => {
  return severityLabels[severity] ?? fallbackCodeLabel(severity);
};

export const eventTypeLabel = (eventType) => {
  return eventTypeLabels[eventType] ?? fallbackCodeLabel(eventType);
};

export const alertTypeLabel = (alertType) => {
  return alertTypeLabels[alertType] ?? fallbackCodeLabel(alertType);
};

export const deviceTypeLabel = (deviceType) => {
  return deviceTypeLabels[deviceType] ?? fallbackCodeLabel(deviceType);
};

export const readableSafetyEventMessage = (event) => {
  if (!event) return "-";

  const eventName = eventTypeLabel(event.eventType);
  const deviceName = event.deviceName || "선택 장비";

  return `${deviceName}에서 ${eventName} 이벤트가 감지되었습니다.`;
};

export const readableAlertMessage = (alert) => {
  if (!alert) return "-";

  const deviceName = alert.deviceName || "대상 장비";

  if (alert.alertType === "DEVICE_RISK") {
    return `${deviceName}의 장비 상태가 주의 또는 위험 수준으로 감지되었습니다. 장비 상태 로그를 확인하세요.`;
  }

  if (alert.alertType === "SAFETY_EVENT") {
    const knownEventType = Object.keys(eventTypeLabels).find((eventType) => {
      return alert.message?.includes(eventType);
    });

    const eventName = knownEventType ? eventTypeLabel(knownEventType) : "안전 위험";
    return `${deviceName}에서 ${eventName} 이벤트가 감지되었습니다. 안전 이벤트 목록을 확인하세요.`;
  }

  return String(alert.message || "-")
    .replaceAll("DEVICE_RISK", alertTypeLabel("DEVICE_RISK"))
    .replaceAll("SAFETY_EVENT", alertTypeLabel("SAFETY_EVENT"))
    .replaceAll("CRITICAL", severityLabel("CRITICAL"))
    .replaceAll("WARNING", severityLabel("WARNING"))
    .replaceAll("INFO", severityLabel("INFO"));
};
