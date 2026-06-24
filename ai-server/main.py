import os
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles

from schemas.device_status_schema import DeviceStatusRequest, DeviceStatusResponse
from schemas.safety_detection_schema import (
    SafetyDetectionRequest,
    SafetyDetectionResponse,
    SafetyImageDetectionResponse
)
from services.phm_service import PHMService
from services.safety_detection_service import SafetyDetectionService


app = FastAPI(
    title="IAT AI Analysis Server",
    description="무인 셔틀 장비 상태 분석 및 YOLO 안전 이벤트 탐지 API",
    version="1.0.0"
)

UPLOAD_DIR = Path("uploaded_images")
ORIGINAL_IMAGE_DIR = UPLOAD_DIR / "original"
RESULT_IMAGE_DIR = UPLOAD_DIR / "results"
UPLOAD_DIR.mkdir(exist_ok=True)
ORIGINAL_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
RESULT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/images", StaticFiles(directory="uploaded_images"), name="images")

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
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="빈 이미지 파일은 업로드할 수 없습니다.")

    file_extension = os.path.splitext(file.filename or "")[1] or ".jpg"
    saved_filename = f"{uuid4()}{file_extension}"
    saved_path = ORIGINAL_IMAGE_DIR / saved_filename

    with open(saved_path, "wb") as buffer:
        buffer.write(file_bytes)

    result = safety_detection_service.detect_safety_event_from_image(
        image_path=str(saved_path),
        result_dir=str(RESULT_IMAGE_DIR)
    )

    return result
