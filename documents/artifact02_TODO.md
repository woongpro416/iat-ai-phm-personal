# artifact02 TODO

작성일: 2026-06-05

목적: 오늘 진행한 작업 이후 다음 컨텍스트에서 바로 이어가기 위한 인수인계용 TODO.

## 1. 현재까지 완료된 내용

### 1-1. 문서화/시연 시나리오 고도화

완료.

- `docs/project-documentation-draft.md`에 실제 API 요청/응답 예시 추가
- DB 테이블 구조 및 Mermaid ERD 초안 추가
- 실제 시연 순서별 대본과 설명 멘트 추가
- Docker 실행, 시드 데이터 생성, 화면 확인 흐름 정리
- `docs/troubleshooting.md` 별도 작성
- `README.md`에 주요 문서 링크 추가

### 1-2. YOLO bbox 이미지 저장 고도화

완료.

- FastAPI 원본 이미지 저장 경로 분리
  - `ai-server/uploaded_images/original`
- FastAPI bbox 결과 이미지 저장 경로 분리
  - `ai-server/uploaded_images/results`
- OpenCV로 bbox와 class/confidence 라벨을 결과 이미지에 그림
- YOLO confidence를 정수 반올림하지 않고 소수점 4자리로 유지
- Spring Boot `SafetyEvent`에 `resultImagePath` 추가
- Spring Boot `SafetyEvent`에 `detectionSummary` 추가
- `SafetyEventResponseDto`에 `resultImageUrl`, `detectionSummary` 추가
- Vue `SafetyEventView`에서 원본/분석 이미지 썸네일 표시
- Vue `SafetyEventView` 상세 모달에서 detection class, confidence, bbox 좌표 표시

### 1-3. PHM 모델 고도화 1차

완료.

현재 단계는 실제 학습 모델이 아니라 설명 가능한 rule baseline 고도화.

- FastAPI PHM 모델을 `phm-rule-baseline-v1`로 버전화
- 입력 계약에 `deviceId`, `temperature`, `vibration`, `noise` 반영
- 응답 계약 추가
  - `modelVersion`
  - `predictionHorizon`
  - `contributionScores`
  - `thresholdViolations`
  - `recommendation`
- feature별 위험 기여도 계산
  - temperature
  - vibration
  - noise
- threshold 위반 코드 생성
  - `TEMPERATURE_WARNING`
  - `TEMPERATURE_DANGER`
  - `VIBRATION_WARNING`
  - `VIBRATION_DANGER`
  - `NOISE_WARNING`
  - `NOISE_DANGER`
- Spring Boot `DeviceStatusLog`에 PHM 분석 메타데이터 저장
- Vue `DeviceStatusView`에서 PHM 모델, 분석 근거, 권장 조치 표시
- Dashboard 최근 장비 상태 로그에 PHM 모델 버전과 권장 조치 표시

### 1-4. 화면/운영성 개선

완료.

- Safety Events 상세 모달 추가
- Alerts 상세 모달 추가
- Alerts 상세 모달에서 운영자용 메시지와 원본 메시지 구분 표시
- Alerts 상세 모달에서 확인 상태, 발생 시간, 확인 시간 표시
- Dashboard 최근 안전 이벤트에서 bbox 분석 결과 이미지 우선 표시
- `docs/dashboard-checklist.md`에 상세 모달 QA 항목 추가

### 1-5. 학습자료 작성

완료.

- `study/today_implementation_study_notes.md` 작성
- 오늘 구현한 주요 코드 흐름 정리
  - YOLO bbox 이미지 저장
  - PHM rule baseline
  - Spring Boot 저장 로직
  - Vue 상세 모달 패턴
  - 실무 관점 설계 포인트

## 2. 다음에 가장 먼저 해야 할 일

### 2-1. 사용자가 직접 build 및 실행 확인

사용자가 build를 직접 하기로 했으므로 Codex는 build를 실행하지 않았다.

다음 컨텍스트에서 사용자가 실행해야 할 확인:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

또는 변경된 서비스만 재빌드:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build ai-server backend frontend
```

확인 URL:

- Frontend: http://localhost:5173
- Dashboard: http://localhost:5173/dashboard
- Spring Swagger: http://localhost:8402/swagger-ui/index.html
- FastAPI Docs: http://localhost:8000/docs

### 2-2. 새 데이터로 smoke test

기존 DB 데이터에는 새 컬럼 값이 비어 있을 수 있다.

새로 생성한 데이터부터 다음 필드가 채워진다.

- `resultImagePath`
- `detectionSummary`
- `modelVersion`
- `predictionHorizon`
- `analysisMessage`
- `recommendation`
- `thresholdViolations`
- `temperatureScore`
- `vibrationScore`
- `noiseScore`

확인 순서:

1. 장비 상태 로그 새로 등록
2. `DeviceStatusView`에서 PHM 모델/분석 근거/권장 조치 표시 확인
3. 이미지 기반 안전 이벤트 새로 등록
4. `SafetyEventView`에서 원본/분석 이미지 표시 확인
5. Safety Events 상세 모달에서 detection 상세 표시 확인
6. Alerts 상세 모달에서 원본 메시지와 확인 시간 표시 확인
7. Dashboard 최근 이력에 분석 이미지/PHM 권장 조치 표시 확인

## 3. 다음 개발 TODO

### 3-1. PHM 실제 학습/평가 고도화

우선순위 높음.

현재는 rule baseline이므로, 다음 단계는 실제 데이터셋 기반 baseline 모델 실험이다.

해야 할 일:

- 학습 데이터 스키마 정의
  - `deviceId`
  - `sampledAt`
  - `temperature`
  - `vibration`
  - `noise`
  - rolling mean/std feature
  - label
- 라벨 정의
  - `NORMAL`
  - `WARNING`
  - `DANGER`
  - 또는 `failureWithinHorizon`
- 시간 순서 기반 train/validation/test split 설계
- scikit-learn 기반 baseline 모델 작성
  - LogisticRegression
  - RandomForest
  - GradientBoosting
  - 가능하면 XGBoost 또는 LightGBM 검토
- 평가 지표 작성
  - precision
  - recall
  - F1
  - ROC-AUC
  - PR-AUC
  - false alarm rate
  - lead time
  - confusion matrix
- 모델 artifact 저장 경로 설계
  - 예: `ai-server/model_artifacts/phm/phm_rf_v1.pkl`
- `modelVersion` 교체 절차 정리
- rule baseline과 ML baseline 비교표 작성

### 3-2. Safety Event detection 구조 정규화

중간 우선순위.

현재는 `detectionSummary` 문자열로 class/confidence/bbox를 저장한다.

추후 개선 방향:

- `safety_event_detections` 테이블 분리 검토
- 컬럼 후보
  - `detection_id`
  - `event_id`
  - `class_id`
  - `class_name`
  - `confidence`
  - `x1`
  - `y1`
  - `x2`
  - `y2`
- 장점
  - class별 통계 가능
  - confidence 분포 분석 가능
  - 오탐/미탐 개선 데이터셋 만들기 쉬움

### 3-3. DB 마이그레이션 전략 검토

중간 우선순위.

현재 Spring Boot 설정:

```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: update
```

개인 프로젝트 시연 단계에서는 괜찮지만, 포트폴리오 완성도를 높이려면 다음을 검토.

- Flyway 또는 Liquibase 도입 여부
- 최소한 `docs`에 변경 컬럼 목록 정리
- 운영 DB가 있다고 가정했을 때 nullable 컬럼 추가 전략 문서화

### 3-4. 시연 전 데이터 정리

중간 우선순위.

기존 DB에는 이전 구조로 생성된 데이터가 남아 있을 수 있다.

확인할 점:

- 이전 이미지 경로가 `uploaded_images/{filename}` 형태로 남아 있을 수 있음
- 새 이미지 경로는 `uploaded_images/original/{filename}` 형태
- 기존 안전 이벤트에는 `resultImagePath`, `detectionSummary`가 null일 수 있음
- 기존 장비 상태 로그에는 PHM 분석 메타데이터가 null일 수 있음

선택지:

1. 기존 DB 유지
   - 장점: 누적 데이터 유지
   - 단점: 새 필드가 비어 보일 수 있음
2. 시연용 DB 초기화 후 시드/수동 입력 재생성
   - 장점: 화면이 깔끔함
   - 단점: 기존 데이터 삭제

삭제/초기화는 사용자 확인 후 진행.

### 3-5. 운영 대시보드 추가 개선

낮음~중간 우선순위.

후보:

- 반복 알림 상위 장비 위젯
- 미처리 안전 이벤트 오래된 순 정렬
- 위험도 최근 5건 외 장비별 추이 조회
- PHM threshold 위반 유형별 카운트
- 알림 중요도별 카운트

## 4. 주의사항

### 4-1. build 미실행

사용자 요청에 따라 Codex는 build를 실행하지 않았다.

수행한 검증:

- Python 파일 `py_compile`
- PHM 예시 입력 직접 실행
- `git diff --check`

수행하지 않은 검증:

- Gradle build
- npm build
- Docker build
- 브라우저 수동 QA

### 4-2. 기존 데이터 null 처리

Vue 화면은 새 필드가 null이어도 `-` 또는 기본 문구를 표시하도록 작성되어 있다.

그래도 시연 품질을 위해서는 새 데이터 생성 후 확인하는 것이 좋다.

### 4-3. AI 서버 이미지 경로

현재 이미지 URL 생성 규칙:

```text
FastAPI static mount: /images
원본 이미지: uploaded_images/original/{filename}
분석 이미지: uploaded_images/results/{filename}_bbox.{ext}
Vue 표시 URL: http://localhost:8000/images/{relativePath}
```

### 4-4. PHM baseline 의미

`phm-rule-baseline-v1`은 학습 모델이 아니다.

현재 목적:

- API 계약 고정
- feature별 설명력 확보
- 모델 버전 저장 흐름 확보
- 추후 ML 모델 교체 준비

포트폴리오 설명 시 표현:

> 현재는 설명 가능한 rule-based PHM baseline을 구성하고, 모델 버전과 feature별 위험 기여도, threshold 위반 근거, 권장 조치를 운영 이력으로 저장하도록 만들었다. 이후 실제 시계열 데이터셋 기반 ML 모델로 교체할 수 있도록 API 계약을 먼저 고정했다.

## 5. 참고 문서

- `README.md`
- `docs/project-documentation-draft.md`
- `docs/dashboard-checklist.md`
- `docs/troubleshooting.md`
- `study/today_implementation_study_notes.md`
- `documents/artifact01_TODO.md`

## 6. 다음 컨텍스트 시작 추천 순서

1. 사용자가 build 및 실행 확인
2. 새 장비 상태 로그 생성 후 PHM 화면 확인
3. 새 이미지 안전 이벤트 생성 후 bbox 결과 이미지 확인
4. 상세 모달 QA
5. DB 기존 데이터 정리 여부 결정
6. PHM 실제 학습/평가 고도화 설계 시작
