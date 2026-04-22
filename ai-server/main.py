import os
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, File, UploadFile
from schemas.device_status_schema import DeviceStatusRequest, DeviceStatusResponse
from services.phm_service import PHMService
from schemas.safety_detection_schema import SafetyDetectionRequest, SafetyDetectionResponse, SafetyImageDetectionResponse
from services.safety_detection_service import SafetyDetectionService


safety_detection_service = SafetyDetectionService()

app = FastAPI(
    title="IAT AI Analysis Server",
    description="무인 셔틀 장비 상태 분석 및 위험도 예측 API",
    version="1.0.0"
)


UPLOAD_DIR = Path("uploaded_images")
UPLOAD_DIR.mkdir(exist_ok=True)

phm_service = PHMService()
safety_detection_service = SafetyDetectionService()


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

@app.post("/detect/safety/image", response_model=SafetyImageDetectionResponse)
async def detect_safety_event_from_image(file: UploadFile = File(...)):
    file_extension = os.path.splitext(file.filename)[1]
    saved_filename = f"{uuid4()}{file_extension}"
    saved_path = UPLOAD_DIR / saved_filename
    
    with open(saved_path, "wb") as buffer:
        buffer.write(await file.read())
        
    result = safety_detection_service.detect_safety_event_from_image(
        image_path=str(saved_path)
    )
    
    return result