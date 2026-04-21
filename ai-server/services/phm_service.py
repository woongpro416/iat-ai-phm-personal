from models.phm_model import PHMModel

class PHMService:
    def __init__(self):
        self.model = PHMModel()
        
    def analyze_device_status(self, temperature: float, vibration: float, noise: float) -> dict:
        risk_score = self.model.predict_risk_score(
            temperature= temperature,
            vibration= vibration,
            noise= noise
        )
        
        status = self._decide_status(risk_score)
        message = self._create_message(status)
        
        return {
            "riskScore" : risk_score,
            "status" : status,
            "message" : message
        }
        
    def _decide_status(self, risk_score: float) -> str:
        if risk_score >= 80:
            return "DANGER"

        if risk_score >= 50:
            return "WARNING"

        return "NORMAL"

    def _create_message(self, status: str) -> str:
        if status == "DANGER":
            return "장비 고장 위험도가 높습니다. 즉시 점검이 필요합니다."

        if status == "WARNING":
            return "장비 이상 징후가 감지되었습니다. 점검이 권장됩니다."

        return "장비 상태가 정상 범위입니다."