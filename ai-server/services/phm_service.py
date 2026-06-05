from models.phm_model import PHMModel

class PHMService:
    def __init__(self):
        self.model = PHMModel()
        
    def analyze_device_status(self, temperature: float, vibration: float, noise: float) -> dict:
        prediction = self.model.predict(
            temperature=temperature,
            vibration=vibration,
            noise=noise
        )

        risk_score = prediction["riskScore"]
        status = self._decide_status(risk_score)
        message = self._create_message(status, prediction["thresholdViolations"])
        
        return {
            "riskScore": risk_score,
            "status": status,
            "message": message,
            "modelVersion": prediction["modelVersion"],
            "predictionHorizon": prediction["predictionHorizon"],
            "contributionScores": prediction["contributionScores"],
            "thresholdViolations": prediction["thresholdViolations"],
            "recommendation": self._create_recommendation(status, prediction["thresholdViolations"])
        }
        
    def _decide_status(self, risk_score: float) -> str:
        if risk_score >= 80:
            return "DANGER"

        if risk_score >= 50:
            return "WARNING"

        return "NORMAL"

    def _create_message(self, status: str, threshold_violations: list[str]) -> str:
        if threshold_violations:
            reason_text = ", ".join(threshold_violations)
        else:
            reason_text = "기준 초과 항목 없음"

        if status == "DANGER":
            return f"장비 고장 위험도가 높습니다. 즉시 점검이 필요합니다. 근거: {reason_text}"

        if status == "WARNING":
            return f"장비 이상 징후가 감지되었습니다. 점검이 권장됩니다. 근거: {reason_text}"

        return "장비 상태가 정상 범위입니다."

    def _create_recommendation(self, status: str, threshold_violations: list[str]) -> str:
        if status == "NORMAL":
            return "정상 운행을 유지하고 다음 정기 점검 시 센서 추이를 확인하세요."

        if any(violation.startswith("VIBRATION") for violation in threshold_violations):
            return "진동 증가 원인을 우선 확인하세요. 모터, 베어링, 체결부 점검이 필요합니다."

        if any(violation.startswith("TEMPERATURE") for violation in threshold_violations):
            return "온도 상승 원인을 우선 확인하세요. 냉각 상태와 배터리/구동부 부하를 점검하세요."

        if any(violation.startswith("NOISE") for violation in threshold_violations):
            return "소음 증가 원인을 우선 확인하세요. 구동부 마찰음과 외부 간섭 여부를 점검하세요."

        return "복합 이상 징후가 감지되었습니다. 최근 상태 로그와 현장 점검 결과를 함께 확인하세요."
