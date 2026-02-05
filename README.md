# 📝 DevLog AI (Development Journal)

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7.0-DC382D?logo=redis&logoColor=white)
![Upstash](https://img.shields.io/badge/Upstash-Serverless-00E599?logo=upstash&logoColor=black)
![CloudType](https://img.shields.io/badge/CloudType-Deploy-000000?logo=cloudtype&logoColor=white)

**DevLog AI**는 개발자의 GitHub 커밋 활동을 자동으로 수집하고, Gemini AI를 활용해 의미 있는 **개발 일지(회고록)**를 생성해주는 서비스입니다.

---

## 🚀 주요 기능

- **GitHub OAuth 로그인**: 별도 가입 없이 GitHub 계정으로 간편 로그인
- **커밋 자동 수집**: 선택한 저장소의 당일 커밋 내역(메시지, 변경 파일 등) 수집
- **AI 회고록 생성**: Gemini 2.5 Flash 모델이 커밋을 분석하여 '오늘의 작업', '배운 점', '기술적 도전' 요약
- **Markdown 에디터**: 생성된 일지를 자유롭게 수정 및 저장
- **개발 통계**: 주간/월간 커밋 수 및 활동 추이 시각화 (준비 중)

---

## 🛠️ 실행 방법 (로컬 개발)

### 1. 환경 설정
```bash
# 저장소 복제
git clone https://github.com/csjh1/DevLogAI.git
cd DevLogAI

# 환경변수 파일 생성
cp env.example .env
# .env 파일을 열어 GitHub Client ID/Secret, Gemini API Key 등을 입력하세요.
```

### 2. 실행 (Docker Compose)
가장 간편한 실행 방법입니다. DB와 Redis가 자동으로 설정됩니다.

```bash
docker-compose up --build
```
- 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs

### 3. 실행 (수동)
```bash
# 가상환경 생성 및 패키지 설치
cd server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# DB 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload
```

### 4. 실행 (uv 사용 - 권장)
`uv`는 Rust로 작성된 초고속 Python 패키지 매니저입니다.

```bash
# uv 설치 (없을 경우)
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Mac/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

cd server

# 의존성 설치 및 가상환경 생성 (한 번에 처리)
uv sync

# DB 마이그레이션 실행
uv run alembic upgrade head

# 서버 실행
uv run uvicorn app.main:app --reload
```

---

## ☁️ 배포 (Deployment)

이 프로젝트는 **CloudType** (PaaS) 및 **Upstash** (Serverless Redis) 환경에 최적화되어 있습니다.

자세한 배포 방법은 [CloudType 배포 가이드](docs/guidelines/cloudtype-deploy.md)를 참고하세요.

---

## 📚 기술 스택

| 구분 | 스택 | 설명 |
|---|---|---|
| **Backend** | FastAPI, Python 3.11 | 비동기 처리, 높은 성능 |
| **DB** | PostgreSQL, SQLAlchemy (Async) | 데이터 영속성, ORM |
| **Cache** | Redis (Upstash) | 일지 조회 캐싱, 세션 관리 |
| **AI** | Google Gemini 2.5 Flash | 커밋 분석 및 텍스트 생성 |
| **Deploy** | Docker, CloudType | 컨테이너 기반 배포 |

---

## 📅 개발 현황 (TDS)

> **Current Phase**: Phase 10 - 문서화 및 최종 점검 (Backend Core Completed)

- [x] Phase 1: 프로젝트 셋업 & 기술 스택 선정
- [x] Phase 2: DB 설계 및 ERD 작성
- [x] Phase 3: 인증 (GitHub OAuth + JWT)
- [x] Phase 4: GitHub API 연동
- [x] Phase 5: Gemini AI 연동
- [x] Phase 6: 일지 CRUD 구현
- [x] Phase 7: 통계 서비스 (백엔드 로직 완료)
- [x] Phase 8: 테스트 코드 작성
- [x] Phase 9: 배포 (CloudType + CI/CD)
- [x] Phase 10: 백엔드 최종 검증 및 문서화 완료

---

## 📄 라이선스

MIT License
