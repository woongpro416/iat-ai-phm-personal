from fastapi import FastAPI

from schemas.device_status_schema import DeviceStatusRequest, DeviceStatusResponse
from services.phm_service import PHMService
from schemas.safety_detection_schema import SafetyDetectionRequest, SafetyDetectionResponse
from services.safety_detection_service import SafetyDetectionService


safety_detection_service = SafetyDetectionService()

app = FastAPI(
    title="IAT AI Analysis Server",
    description="무인 셔틀 장비 상태 분석 및 위험도 예측 API",
    version="1.0.0"
)

phm_service = PHMService()


@app.get("/")
def root():
    return {
        "message": "IAT AI Analysis Server is running"
    }


@app.post("/predict/device-status", response_model=DeviceStatusResponse)
def predict_device_status(request: DeviceStatusRequest):
    result = phm_service.analyze_device_status(
        temperature=request.temperature,
        vibration=request.vibration,
        noise=request.noise
    )

    return result

@app.post("/detect/safety", response_model=SafetyDetectionResponse)
def detect_safety_event(request: SafetyDetectionRequest):
    result = safety_detection_service.detect_safety_event(
        scenario=request.scenario
    )

    return result
