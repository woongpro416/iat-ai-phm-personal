# PHM Rule Baseline vs ML Baseline

## 목적

이 문서는 현재 운영 API에 연결된 rule baseline과 학습 파이프라인으로 생성한
ML baseline의 역할 차이를 정리한다.

현재 FastAPI 운영 추론은 아직 `phm-rule-baseline-v1`을 사용한다.
`phm-rf-baseline-v1`은 포트폴리오용 학습/평가 파이프라인 검증 결과이며,
실제 운영 추론으로 교체하지 않았다.

## 비교 요약

| 구분 | Rule baseline | ML baseline |
| --- | --- | --- |
| 버전 | `phm-rule-baseline-v1` | `phm-rf-baseline-v1` |
| 위치 | `ai-server/models/phm_model.py` | `ai-server/model_artifacts/phm/phm_rf_v1.joblib` |
| 방식 | 센서별 threshold와 가중치 기반 점수 | `RandomForestClassifier` |
| 입력 | temperature, vibration, noise | 원본 센서값 + rolling mean/std |
| 라벨 | 없음 | `failureWithinHorizon` |
| 장점 | 설명이 쉽고 API 응답 근거를 바로 제공 | 시간 기반 split, 평가 지표, artifact 관리 가능 |
| 한계 | 실제 고장 라벨 기반 성능 평가가 아님 | 현재는 합성 샘플 데이터 기준이며 운영 API 미연결 |

## ML baseline 평가 결과

평가 리포트: [`docs/phm-baseline-report.md`](./phm-baseline-report.md)

테스트 split 기준:

| 지표 | 값 |
| --- | ---: |
| Precision | 1.000000 |
| Recall | 0.963636 |
| F1 | 0.981481 |
| ROC-AUC | 0.986460 |
| PR-AUC | 0.992724 |
| False alarm rate | 0.000000 |
| Confusion matrix | TN 47 / FP 0 / FN 2 / TP 53 |

위 결과는 `ai-server/datasets/phm/sample_phm_training.csv` 합성 샘플 데이터
기준이다. 실제 현장 성능으로 해석하지 않고, 학습 파이프라인과 평가 산출물
구현 여부를 보여주는 용도로 사용한다.

## 포트폴리오 설명 포인트

1. 먼저 rule baseline으로 운영 API 계약을 고정했다.
2. 이후 `deviceId + sampledAt` grain, `failureWithinHorizon` 라벨, 시간 순서 기반 split을 문서화했다.
3. rolling feature는 현재 행을 제외한 과거 행만 사용해 데이터 누수 위험을 줄였다.
4. ML baseline은 운영 추론 교체 전 단계로 artifact와 평가 리포트까지 생성했다.

## 다음 개선

- 실제 수집 데이터 또는 더 현실적인 시뮬레이션 데이터로 재학습
- validation split에서 threshold 조정 후 test split 1회 평가
- lead time 계산 추가
- FastAPI 추론 모델을 rule baseline과 ML baseline 중 선택할 수 있도록 구성
