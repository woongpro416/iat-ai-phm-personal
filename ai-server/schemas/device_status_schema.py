from pydantic import BaseModel
from typing import Literal
from typing import Optional

class DeviceStatusRequest(BaseModel):
    deviceId: Optional[int] = None
    temperature: float
    vibration: float
    noise: float


class DeviceStatusResponse(BaseModel):
    riskScore: float
    status: Literal["NORMAL", "WARNING", "DANGER"]
    message: str
    modelVersion: str
    predictionHorizon: str
    contributionScores: dict[str, float]
    thresholdViolations: list[str]
    recommendation: str
