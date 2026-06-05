다음 작업 TODO
완료된 내용
1. 상태별 장비 수 차트
완료
대시보드에 상태별 장비 수 차트 추가
정상/주의/위험/오프라인 장비 수 표시
한글 라벨 깨짐 수정
대시보드 레이아웃 및 자동 갱신 동작 점검 완료
2. 문서화/시연 시나리오
초안 완료
README.md 정리
docs/project-documentation-draft.md 작성
docs/dashboard-checklist.md 복구 및 정리
시연 흐름 초안 작성 완료
추가 완료된 내용
2. 문서화/시연 시나리오 고도화
완료
docs/project-documentation-draft.md에 실제 API 요청/응답 예시 추가
DB 테이블 구조 및 ERD 초안 추가
실제 시연 순서별 대본과 설명 멘트 추가
Docker 실행/시드 데이터 생성/화면 확인 흐름 정리
docs/troubleshooting.md 별도 작성
README.md에 트러블슈팅 문서 링크 추가
3. YOLO bbox 이미지 저장 고도화
완료
FastAPI에서 원본 이미지를 uploaded_images/original에 저장
FastAPI에서 bbox가 그려진 결과 이미지를 uploaded_images/results에 저장
Spring Boot SafetyEvent에 resultImagePath 필드 추가
SafetyEvent 응답에 resultImagePath/resultImageUrl 추가
Vue SafetyEventView에서 원본/분석 결과 이미지 썸네일 표시
4. PHM 모델 고도화
1차 완료
FastAPI PHM 로직을 phm-rule-baseline-v1 rule baseline으로 정리
입력 데이터 계약에 deviceId, temperature, vibration, noise 반영
응답 데이터 계약에 modelVersion, predictionHorizon, contributionScores, thresholdViolations, recommendation 추가
Spring Boot DeviceStatusLog에 모델 버전, feature별 위험 기여도, 분석 메시지, 권장 조치 저장
Vue DeviceStatusView에서 PHM 모델, 분석 근거, 권장 조치 표시
아직 못 한 내용
5. PHM 실제 학습/평가 고도화
미진행
실제 데이터셋 기반 train/validation/test split 미구현
precision, recall, F1, false alarm rate, lead time 평가 리포트 미작성
모델 artifact 저장 및 버전 교체 절차 미정리
다음 컨텍스트 TODO
1. PHM 실제 학습/평가 고도화
현재 rule baseline 기준으로 학습 데이터 스키마 설계
라벨 정의: 정상/주의/위험 또는 고장 위험도
시간 순서 기반 train/validation/test split 설계
기준선 모델 설계: scikit-learn 또는 XGBoost 기반
평가 지표 정리: precision, recall, F1, false alarm rate, lead time
모델 artifact 저장 경로와 modelVersion 교체 절차 정리
2. 화면/운영성 추가 개선
완료
Safety Events 상세 모달 추가
Safety Events 상세 모달에서 원본/분석 이미지, detection class/confidence/bbox 좌표 표시
Alerts 상세 모달 추가
대시보드 최근 안전 이벤트에서 bbox 분석 결과 이미지 우선 표시
대시보드 최근 장비 상태 로그에 PHM 모델 버전과 권장 조치 표시
Safety Events 테이블 처리 컬럼 폭 보정
운영자용 한글 라벨 SAFETY_OBJECT_DETECTED 추가
추후 검토
기존 DB에 남은 깨진 메시지 정리 필요 여부 검토
반복 장애/알림 통계 위젯 추가 여부 검토
