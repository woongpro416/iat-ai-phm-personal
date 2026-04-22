from models.yolo_detector import YOLODetector


class SafetyDetectionService:
    """
    안전 이벤트 탐지 서비스
    """

    def __init__(self):
        self.detector = YOLODetector()

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

    def detect_safety_event_from_image(self, image_path: str) -> dict:
        detections = self.detector.detect(image_path)

        if not detections:
            return {
                "eventType": "OBSTACLE_DETECTED",
                "confidence": 0.0,
                "message": "탐지된 객체가 없습니다.",
                "imagePath": image_path,
                "detections": []
            }

        # confidence가 가장 높은 탐지 결과 선택
        top_detection = max(detections, key=lambda item: item["confidence"])

        class_name = top_detection["className"]
        confidence = top_detection["confidence"]

        # 1차 구현 규칙:
        # COCO 기본 모델에서 person이 감지되면 승객 관련 안전 이벤트로 변환
        if class_name == "person":
            event_type = "FALL_DETECTED"
            message = "사람 객체가 감지되었습니다. 승객 안전 이벤트 확인이 필요합니다."
        else:
            event_type = "OBSTACLE_DETECTED"
            message = f"{class_name} 객체가 감지되었습니다. 통행 구역 내 이물질 여부 확인이 필요합니다."

        return {
            "eventType": event_type,
            "confidence": confidence,
            "message": message,
            "imagePath": image_path,
            "detections": detections
        }