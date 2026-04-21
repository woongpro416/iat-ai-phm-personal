from pydantic import BaseModel
from typing import Literal

class DeviceStatusRequest(BaseModel):
    temperature: float
    vibration: float
    noise: float


class DeviceStatusResponse(BaseModel):
    riskScore: float
    status: Literal["NORMAL", "WARNING", "DANGER"]
    message: str