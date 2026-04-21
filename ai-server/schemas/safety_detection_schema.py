from pydantic import BaseModel
from typing import Literal


class SafetyDetectionRequest(BaseModel):
    deviceId: int
    scenario: str


class SafetyDetectionResponse(BaseModel):
    eventType: Literal[
        "FALL_DETECTED",
        "DOOR_ENTRAPMENT",
        "OBSTACLE_DETECTED",
        "DANGER_ZONE_ACCESS"
    ]
    confidence: float
    message: str
    imagePath: str | None = None