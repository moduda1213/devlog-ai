# server/Dockerfile
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필수 패키지 설치 (git은 uv 등에서 필요할 수 있음)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# UV 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 의존성 파일 복사
COPY pyproject.toml uv.lock ./

# 의존성 설치 (System Python에 설치하여 가상환경 없이 실행)
RUN uv pip install --system -r pyproject.toml

# 소스 코드 복사
COPY . .

# 실행 명령 (개발 모드)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]