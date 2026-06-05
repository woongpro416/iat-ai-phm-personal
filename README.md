# IAT AI Safety System

AI 기반 무인 셔틀 장비 상태 모니터링 및 실시간 안전 관제 웹 시스템입니다.

인천공항 무인 셔틀 운영 환경을 가정하여 장비 센서 데이터, AI 안전 이벤트, 알림 이력을 통합 관제하는 개인 프로젝트입니다.

## 문서

- [프로젝트 문서 초안](./docs/project-documentation-draft.md)
- [대시보드 점검 체크리스트](./docs/dashboard-checklist.md)
- [트러블슈팅 가이드](./docs/troubleshooting.md)
- [구현 학습 노트](./study/today_implementation_study_notes.md)

## 주요 실행 URL

- Frontend: http://localhost:5173
- Dashboard: http://localhost:5173/dashboard
- Spring Swagger: http://localhost:8402/swagger-ui/index.html
- FastAPI Docs: http://localhost:8000/docs

## 개발 실행

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

프론트 의존성 또는 Dockerfile 변경이 있을 때만 재빌드합니다.

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build frontend
```

## 시연 데이터 생성

```powershell
.\scripts\seed-dashboard-demo-data.ps1
```
