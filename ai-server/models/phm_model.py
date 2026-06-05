class PHMModel:
    """
    장비 상태 기반 위험도 분석 baseline.

    현재 버전은 학습 모델이 아니라 설명 가능한 rule-based baseline이다.
    입력 feature, score 산식, threshold 코드를 명시해 추후 scikit-learn,
    XGBoost, ONNX 모델로 교체할 때 API 계약을 유지하기 쉽게 만든다.
    """

    MODEL_VERSION = "phm-rule-baseline-v1"
    PREDICTION_HORIZON = "IMMEDIATE_RISK"

    FEATURE_WEIGHTS = {
        "temperature": 35.0,
        "vibration": 40.0,
        "noise": 25.0,
    }

    FEATURE_RANGES = {
        "temperature": {"min": 25.0, "max": 75.0},
        "vibration": {"min": 0.05, "max": 1.20},
        "noise": {"min": 35.0, "max": 90.0},
    }

    THRESHOLDS = {
        "temperature": {"warning": 45.0, "danger": 60.0},
        "vibration": {"warning": 0.50, "danger": 0.90},
        "noise": {"warning": 60.0, "danger": 75.0},
    }

    def predict(self, temperature: float, vibration: float, noise: float) -> dict:
        contribution_scores = {
            "temperature": self._score_feature("temperature", temperature),
            "vibration": self._score_feature("vibration", vibration),
            "noise": self._score_feature("noise", noise),
        }

        risk_score = min(100.0, round(sum(contribution_scores.values()), 1))

        return {
            "riskScore": risk_score,
            "contributionScores": contribution_scores,
            "thresholdViolations": self._find_threshold_violations(
                temperature=temperature,
                vibration=vibration,
                noise=noise
            ),
            "modelVersion": self.MODEL_VERSION,
            "predictionHorizon": self.PREDICTION_HORIZON,
        }

    def _score_feature(self, feature_name: str, value: float) -> float:
        feature_range = self.FEATURE_RANGES[feature_name]
        weight = self.FEATURE_WEIGHTS[feature_name]

        normalized_value = (value - feature_range["min"]) / (feature_range["max"] - feature_range["min"])
        bounded_value = min(1.0, max(0.0, normalized_value))

        return round(bounded_value * weight, 1)

    def _find_threshold_violations(self, temperature: float, vibration: float, noise: float) -> list[str]:
        values = {
            "temperature": temperature,
            "vibration": vibration,
            "noise": noise,
        }

        violations = []

        for feature_name, value in values.items():
            thresholds = self.THRESHOLDS[feature_name]

            if value >= thresholds["danger"]:
                violations.append(f"{feature_name.upper()}_DANGER")
            elif value >= thresholds["warning"]:
                violations.append(f"{feature_name.upper()}_WARNING")

        return violations
