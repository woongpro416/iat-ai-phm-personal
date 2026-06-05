# Troubleshooting Guide

이 문서는 시연 또는 개발 중 자주 발생할 수 있는 문제를 빠르게 확인하기 위한 운영 메모다.

## 1. Docker 컨테이너가 정상 실행되지 않을 때

확인 명령:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml ps
```

확인 기준:

- `iat-ai-phm-postgres`: `running` 또는 `healthy`
- `iat-ai-server`: `running`
- `iat-backend`: `running`
- `iat-frontend`: `running`

로그 확인:

```powershell
docker logs iat-ai-phm-postgres
docker logs iat-ai-server
docker logs iat-backend
docker logs iat-frontend
```

주요 원인:

- PostgreSQL 포트 `5432`가 이미 사용 중이다.
- backend가 postgres healthcheck 완료 전에 DB에 접근했다.
- ai-server 의존성 설치 또는 Python 서버 실행에 실패했다.
- frontend 의존성 또는 Vite 실행에 실패했다.

## 2. 프론트 화면이 열리지 않을 때

접속 URL:

- http://localhost:5173
- http://localhost:5173/dashboard

확인 순서:

1. `iat-frontend` 컨테이너가 running인지 확인한다.
2. `docker logs iat-frontend`에서 Vite 실행 오류를 확인한다.
3. 브라우저 캐시 문제일 수 있으므로 새로고침한다.
4. 프론트 API 요청 실패가 보이면 backend URL `http://localhost:8402`가 열리는지 확인한다.

## 3. Swagger가 열리지 않을 때

접속 URL:

- http://localhost:8402/swagger-ui/index.html

확인 순서:

1. `iat-backend` 컨테이너가 running인지 확인한다.
2. `docker logs iat-backend`에서 DB 연결 오류를 확인한다.
3. PostgreSQL 컨테이너가 healthy인지 확인한다.
4. `AI_SERVER_URL` 환경변수가 `http://ai-server:8000`인지 확인한다.

관련 설정:

```yaml
AI_SERVER_URL: http://ai-server:8000
SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/iat-ai-phm-postgres
```

## 4. FastAPI Docs가 열리지 않을 때

접속 URL:

- http://localhost:8000/docs

확인 순서:

1. `iat-ai-server` 컨테이너가 running인지 확인한다.
2. `docker logs iat-ai-server`에서 import 오류 또는 패키지 설치 오류를 확인한다.
3. 이미지 업로드 테스트가 실패하면 `ai-server/uploaded_images` 디렉터리가 생성되었는지 확인한다.

## 5. 시드 데이터 생성이 실패할 때

실행 명령:

```powershell
.\scripts\seed-dashboard-demo-data.ps1
```

확인 순서:

1. backend가 `http://localhost:8402`에서 응답하는지 확인한다.
2. FastAPI가 `http://localhost:8000/docs`에서 응답하는지 확인한다.
3. PowerShell 실행 정책 문제라면 현재 세션에서만 허용한다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

4. 같은 스크립트를 여러 번 실행하면 장비명이 runId를 포함해 새로 생성된다. 기존 데이터가 누적되는 것은 정상이다.

## 6. 장비 상태 입력 시 502가 발생할 때

증상:

- `/api/device-status` 요청이 `502 Bad Gateway`를 반환한다.
- 응답 메시지: `AI 서버 호출 중 오류가 발생했습니다.`

원인:

- backend가 FastAPI `/predict/device-status`를 호출하지 못했다.
- ai-server 컨테이너가 중단되었거나 내부 오류가 발생했다.
- Docker 네트워크 내부 주소 `http://ai-server:8000` 연결에 실패했다.

확인 명령:

```powershell
docker logs iat-ai-server
docker logs iat-backend
```

## 7. 이미지 기반 안전 이벤트 생성이 실패할 때

확인 항목:

- 요청이 `multipart/form-data` 형식인지 확인한다.
- 필드명이 `deviceId`, `file`인지 확인한다.
- `deviceId`에 해당하는 장비가 DB에 존재하는지 확인한다.
- FastAPI 응답의 `eventType`이 Spring enum에 있는 값인지 확인한다.

지원 이벤트 타입:

```text
FALL_DETECTED
DOOR_ENTRAPMENT
OBSTACLE_DETECTED
DANGER_ZONE_ACCESS
SAFETY_OBJECT_DETECTED
```

이미지 URL 규칙:

```text
원본 저장 경로: uploaded_images/original/{filename}
bbox 결과 저장 경로: uploaded_images/results/{filename}_bbox.{ext}
원본 표시 URL: http://localhost:8000/images/original/{filename}
bbox 결과 표시 URL: http://localhost:8000/images/results/{filename}_bbox.{ext}
```

Spring Boot 안전 이벤트 응답에서 원본은 `imageUrl`, bbox 결과 이미지는 `resultImageUrl`로 내려간다.

## 8. 대시보드에 데이터가 비어 있을 때

확인 순서:

1. 시드 스크립트를 실행했는지 확인한다.
2. `/api/dashboard/summary` 응답의 카운트 값을 확인한다.
3. `/api/dashboard/recent` 응답 배열을 확인한다.
4. 데이터가 없을 때 차트와 목록에 빈 상태 문구가 표시되는지 확인한다.

직접 확인 URL:

- http://localhost:8402/api/dashboard/summary
- http://localhost:8402/api/dashboard/recent

## 9. 한글 라벨 또는 메시지가 깨질 때

확인 항목:

- 문서와 소스 파일을 UTF-8로 저장한다.
- DB에 이미 저장된 깨진 메시지는 프론트 라벨 수정만으로 복구되지 않는다.
- 새로 생성한 데이터에서도 깨진다면 backend 또는 ai-server 로그의 인코딩을 확인한다.

운영 판단:

- 시연용 DB에 깨진 기존 데이터가 많으면 볼륨 초기화 또는 신규 시드 생성 여부를 결정한다.
- 기존 사용자 데이터가 있는 환경에서는 임의 삭제하지 않는다.

## 10. 포트 충돌이 발생할 때

현재 사용 포트:

| 서비스 | 포트 |
| --- | ---: |
| Frontend | 5173 |
| Backend | 8402 |
| FastAPI | 8000 |
| PostgreSQL | 5432 |

확인 명령:

```powershell
netstat -ano | findstr :5173
netstat -ano | findstr :8402
netstat -ano | findstr :8000
netstat -ano | findstr :5432
```

포트가 이미 사용 중이면 해당 프로세스를 확인하고, 필요한 경우 compose 포트 매핑을 조정한다.

## 11. 시연 전 최종 점검

- [ ] Docker 컨테이너 4개가 running 상태다.
- [ ] http://localhost:5173/dashboard 접속 가능하다.
- [ ] http://localhost:8402/swagger-ui/index.html 접속 가능하다.
- [ ] http://localhost:8000/docs 접속 가능하다.
- [ ] 시드 데이터 생성이 완료되었다.
- [ ] 대시보드 요약 카드와 차트가 표시된다.
- [ ] Safety Events에서 이벤트 처리 완료가 동작한다.
- [ ] Alerts에서 알림 확인 처리가 동작한다.
