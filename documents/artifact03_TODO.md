# artifact03 TODO

작성일: 2026-06-24

목적: 오전 작업 이후 오후에 바로 이어서 마감 QA를 진행하기 위한 TODO.

## 1. 오전 작업 완료 내용

### 1-1. 작은 품질 보정

완료.

- `DeviceStatusCreateRequestDto` 진동 validation 메시지 수정
- Spring Boot 이미지 업로드 빈 파일/비이미지 방어 추가
- FastAPI 이미지 업로드 빈 파일/비이미지 방어 추가
- `SafetyEventView` 파일 선택 단계에서 비이미지/빈 파일 안내
- `DeviceStatusView`에서 백엔드 `fieldErrors` 상세 메시지 표시
- 빈 센서 입력값이 `0`으로 바뀌지 않도록 `null` 전송 처리

### 1-2. PHM ML baseline 학습/평가 파이프라인

완료.

- `ai-server/training/phm_model_input.py` 추가
- `ai-server/training/phm_baseline_trainer.py` 추가
- `ai-server/training/phm_sample_dataset_generator.py` 추가
- `ai-server/tests/test_phm_model_input.py` 추가
- `ai-server/tests/test_phm_baseline_trainer.py` 추가
- `scikit-learn`, `joblib` requirements 추가
- 샘플 학습 CSV 생성
  - `ai-server/datasets/phm/sample_phm_training.csv`
- RandomForest baseline artifact 생성
  - `ai-server/model_artifacts/phm/phm_rf_v1.joblib`
- 평가 리포트 생성
  - `docs/phm-baseline-report.md`
- rule baseline vs ML baseline 비교 문서 생성
  - `docs/phm-baseline-comparison.md`

### 1-3. 문서화

완료.

- `README.md` 포트폴리오 소개용으로 정리
- `docs/phm-training-data-contract.md` 최신 구현 상태로 업데이트
- `study/work-log-2026-06-24.md` 작업일지 작성

### 1-4. UI 마감 보정

완료.

- `/` Home 화면 추가
- `AppNavbar` 브랜드 링크를 Home으로 변경
- 전역 CSS import 활성화
- Bootstrap 기본 스타일 위에 앱 전용 디자인 레이어 적용
- 카드, 버튼, 테이블, 네비게이션, 배경 톤 정리
- Tailwind/Emotion 전면 도입 대신 기존 Vue + Bootstrap 코드와 호환되는 커스텀 CSS 방식 선택
- Home 셔틀 운행 관제 그래프를 최근 위험도 추이 형태로 정리
- Safety Events / Alerts 목록의 장비명, 발생 시간, 처리 버튼 가독성 보정
- 네비게이션 브랜드 마크와 맞춘 프로젝트 favicon 적용

### 1-5. 최종 마감 정리

완료.

- `frontend/public/favicon.svg`를 브랜드 마크 형태로 교체
- `frontend/index.html`의 favicon, lang, title 정리
- README에 Home, favicon, 마감 기준 반영
- 작업일지에 UI 가독성 보정과 파비콘 적용 내용 추가

## 2. 오후에 가장 먼저 할 일

### 2-1. Docker build 및 실행 확인

Codex는 build를 실행하지 않았다. 사용자가 직접 실행한다.

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build ai-server backend frontend
```

상태 확인:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml ps
```

확인 URL:

- Frontend: http://localhost:5173
- Dashboard: http://localhost:5173/dashboard
- Spring Swagger: http://localhost:8402/swagger-ui/index.html
- FastAPI Docs: http://localhost:8000/docs

### 2-2. Build 후 smoke test

확인 순서:

1. `/dashboard` 접속 확인
2. `/` 접속 시 Home 화면 표시 확인
3. 브라우저 탭 title과 favicon 표시 확인
4. Home 화면 진입 카드로 각 화면 이동 확인
5. `/device-status`에서 장비 목록 로딩 확인
6. 장비 상태 로그 정상 등록 확인
7. 진동 `-1` 입력 시 `진동 값은 0 이상이어야 합니다.` 표시 확인
8. 소음 `-1` 입력 시 `소음 값은 0 이상이어야 합니다.` 표시 확인
9. 온도/진동/소음 빈 값 입력 시 필수 메시지 표시 확인
10. `/safety-events`에서 정상 이미지 업로드 확인
11. 비이미지 파일 업로드 시 안내 메시지 확인
12. 빈 파일 업로드 시 안내 메시지 확인
13. Safety Events 상세 모달에서 원본/분석 이미지와 detection 상세 확인
14. 여러 객체가 탐지된 이미지에서 bbox와 라벨 색상이 객체별로 구분되는지 확인
15. `/alerts`에서 알림 확인 처리 확인
16. `/dashboard` 최근 이력에 새 상태 로그/이벤트 반영 확인

## 3. 시연 데이터 정리

기존 DB에 이전 구조 데이터가 남아 있을 수 있다.

확인할 점:

- 기존 안전 이벤트의 `resultImagePath`, `detectionSummary`가 null일 수 있음
- 기존 장비 상태 로그의 `modelVersion`, `recommendation`, feature score가 null일 수 있음
- 기존 깨진 한글 메시지가 남아 있을 수 있음

오후 선택지:

1. 기존 DB 유지
   - 장점: 누적 데이터 유지
   - 단점: 일부 행에 새 필드가 비어 보일 수 있음
2. 시연용 DB 초기화 후 seed 재생성
   - 장점: 화면이 깔끔함
   - 단점: 기존 데이터 삭제

삭제/초기화는 사용자 판단 후 진행한다.

## 4. 포트폴리오 마감 TODO

### 우선순위 높음

- build 후 smoke test 결과 기록
- README 실행 명령이 실제로 맞는지 확인
- Swagger/FastAPI Docs 접속 확인
- 주요 화면 캡처 저장 여부 결정
- 시연 순서 최종 확정
- 시드 데이터 재생성 전 DB 정리 여부 결정

### 우선순위 중간

- `docs/project-documentation-draft.md`의 `남은 고도화 과제` 섹션이 최신 상태와 맞지 않는 부분 정리
- `docs/dashboard-checklist.md` 기준으로 화면 QA 체크
- `docs/troubleshooting.md`에 이미지 업로드 400 오류 대응 항목 보강

### 우선순위 낮음

- Flyway 도입 검토
- `safety_event_detections` 테이블 분리 검토
- FastAPI 운영 추론을 `phm-rf-baseline-v1`로 교체하는 옵션 검토
- 실제 데이터 기반 PHM 성능 재평가

## 5. 더 이상 크게 고도화하지 않을 항목

개인 포트폴리오 마감 기준으로는 아래 작업은 보류한다.

- XGBoost/LightGBM 추가 실험
- ONNX 변환
- 실시간 WebSocket 관제
- 권한/로그인
- Flyway 전체 도입
- detection box 별도 테이블 정규화
- 운영 배포 자동화

현재 목표는 새 기능 추가가 아니라 안정적인 시연과 설명 가능한 문서화다.

## 6. 오후 시작 추천 순서

1. Docker build 실행
2. 컨테이너 상태 확인
3. 화면 smoke test
4. validation/이미지 업로드 방어 확인
5. 시드 데이터 재생성 여부 결정
6. `docs/project-documentation-draft.md` 최신화 여부 결정
7. 최종 README와 문서 링크 점검
