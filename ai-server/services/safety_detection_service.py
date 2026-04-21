class SafetyDetectionService:
    """
    안전 이벤트 탐지 서비스

    현재 버전:
    - 테스트용 시나리오 기반 결과 반환

    향후 확장:
    - YOLOv8 이미지/영상 객체탐지 결과로 대체
    """

    def detect_safety_event(self, scenario: str) -> dict:
        scenario = scenario.upper()

        if scenario == "FALL":
            return {
                "eventType": "FALL_DETECTED",
                "confidence": 0.91,
                "message": "승객 쓰러짐 위험이 감지되었습니다.",
                "imagePath": None
            }

        if scenario == "DOOR":
            return {
                "eventType": "DOOR_ENTRAPMENT",
                "confidence": 0.88,
                "message": "출입문 끼임 위험이 감지되었습니다.",
                "imagePath": None
            }

        if scenario == "OBSTACLE":
            return {
                "eventType": "OBSTACLE_DETECTED",
                "confidence": 0.86,
                "message": "통행 구역 내 이물질이 감지되었습니다.",
                "imagePath": None
            }

        return {
            "eventType": "DANGER_ZONE_ACCESS",
            "confidence": 0.82,
            "message": "위험 구역 접근이 감지되었습니다.",
            "imagePath": None
        }