from pathlib import Path

import cv2

from models.yolo_detector import YOLODetector


class SafetyDetectionService:
    """
    안전 이벤트 탐지 서비스

    - detect_safety_event(): 기존 시나리오 기반 테스트 API용
    - detect_safety_event_from_image(): 실제 YOLO 이미지 탐지 API용
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

    def detect_safety_event_from_image(self, image_path: str, result_dir: str) -> dict:
        detections = self.detector.detect(image_path)
        result_image_path = self._save_result_image(
            image_path=image_path,
            result_dir=result_dir,
            detections=detections
        )

        if not detections:
            return {
                "eventType": "SAFETY_OBJECT_DETECTED",
                "confidence": 0.0,
                "message": "탐지된 객체가 없습니다.",
                "imagePath": image_path,
                "resultImagePath": result_image_path,
                "detections": []
            }

        top_detection = max(detections, key=lambda item: item["confidence"])

        class_name = top_detection["className"]
        confidence = top_detection["confidence"]

        message = f"{class_name} 객체가 감지되었습니다. 안전 확인이 필요합니다."

        return {
            "eventType": "SAFETY_OBJECT_DETECTED",
            "confidence": confidence,
            "message": message,
            "imagePath": image_path,
            "resultImagePath": result_image_path,
            "detections": detections
        }

    def _save_result_image(self, image_path: str, result_dir: str, detections: list[dict]) -> str | None:
        image = cv2.imread(image_path)

        if image is None:
            return None

        for detection in detections:
            bbox = detection["bbox"]
            x1 = int(bbox["x1"])
            y1 = int(bbox["y1"])
            x2 = int(bbox["x2"])
            y2 = int(bbox["y2"])

            label = f'{detection["className"]} {detection["confidence"]:.2f}'

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 180, 255), 2)
            cv2.putText(
                image,
                label,
                (x1, max(y1 - 8, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 180, 255),
                2,
                cv2.LINE_AA
            )

        if not detections:
            cv2.putText(
                image,
                "No detections",
                (24, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 180, 255),
                2,
                cv2.LINE_AA
            )

        source_path = Path(image_path)
        result_path = Path(result_dir) / f"{source_path.stem}_bbox{source_path.suffix}"
        saved = cv2.imwrite(str(result_path), image)

        if not saved:
            return None

        return str(result_path)
