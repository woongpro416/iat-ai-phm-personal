package com.example.demo.domain.enums;

public enum SafetyEventType {
    FALL_DETECTED,
    DOOR_ENTRAPMENT,
    OBSTACLE_DETECTED,
    DANGER_ZONE_ACCESS,

    // YOLO 기본 모델 기반 객체 탐지 이벤트
    SAFETY_OBJECT_DETECTED
}
