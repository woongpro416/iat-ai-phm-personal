class PHMModel:
    """
    장비 상태 기반 위험도 분석 모델
    
    현재 버전:
        - 규칙 기반 위험도 계산
    
    향후 확장:
        -RandomForest
        -LSTM
        -AutoEncoder
        -1D CNN
    등의 모델로 교체 가능
    """
    def predict_risk_score(self, temperature: float, vibration: float, noise: float) -> float:
        temp_score = temperature * 0.8
        vibration_score = vibration * 40.0
        noise_score = noise * 0.3
        
        risk_score = temp_score + vibration_score + noise_score
        
        return min(100.0, round(risk_score, 1))