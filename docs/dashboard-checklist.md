# Dashboard QA Checklist

## 실행 확인

- [ ] Docker Compose에서 postgres, ai-server, backend, frontend가 모두 running 상태인지 확인
- [ ] Vue 접속: http://localhost:5173/dashboard
- [ ] Spring Swagger 접속: http://localhost:8402/swagger-ui/index.html
- [ ] FastAPI Docs 접속: http://localhost:8000/docs

## 대시보드 데이터 확인

- [ ] 전체 장비 수 표시
- [ ] 주의 장비 수 표시
- [ ] 위험 장비 수 표시
- [ ] 미확인 알림 수 표시
- [ ] 최근 위험도 표시
- [ ] 전체 안전 이벤트 수 표시
- [ ] 미처리 안전 이벤트 수 표시

## 차트 확인

- [ ] 최근 위험도 변화 차트 표시
- [ ] 상태별 장비 수 차트 표시
- [ ] 데이터가 없을 때 빈 상태 문구 표시
- [ ] 차트 라벨이 한글로 표시

## 버튼 동작 확인

- [ ] 새로고침 버튼 동작
- [ ] 자동 갱신 카운트 감소
- [ ] 0초 도달 시 "갱신중" 표시
- [ ] 자동 갱신 후 스크롤 위치 유지
- [ ] 최근 알림 확인 버튼 동작
- [ ] 최근 안전 이벤트 처리 완료 버튼 동작
- [ ] Safety Events 상세 버튼 동작
- [ ] Alerts 상세 버튼 동작

## 화면 확인

- [ ] DashboardView 레이아웃 깨짐 없음
- [ ] SafetyEventView 테이블 헤더/버튼 줄바꿈 없음
- [ ] AlertView 미확인/확인 완료 탭 표시
- [ ] DeviceStatusView 단위 표시 확인
- [ ] Safety Events 상세 모달에서 원본/분석 이미지 표시
- [ ] Safety Events 상세 모달에서 detection class/confidence/bbox 표시
- [ ] Alerts 상세 모달에서 원본 메시지와 확인 시간 표시
- [ ] DeviceStatusView에서 PHM 모델 버전, 분석 근거, 권장 조치 표시
