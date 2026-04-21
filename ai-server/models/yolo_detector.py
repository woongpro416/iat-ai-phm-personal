from pathlib import Path
from ultralytics import YOLO

class YOLODetector:
    """
    YOLO 기반 안전 이벤트 탐지 모델
    
    현재 버전:
        - COCO 사전학습 모델(yolov8n.pt) 사용
        - person 또는 일반 객체 감지 결과를 안전 이벤트로 변환
        
    향후 확장:
        - 직접 라벨링한 FALL / DOOR_ENTRAPMENT / OBSTACLE 데이터셋으로 custom model 학습
        - best.pt 로 교체
    """
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        self.model = YOLO(model_path)
        
    def detect(self, image_path: str) -> list[dict]:
        results = self.model(image_path)
        result = results[0]