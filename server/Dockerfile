# ==========================================
# Stage 1: Builder (의존성 설치 및 가상환경 구성)
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# 시스템 의존성 설치 (git: 패키지 fetch용)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# UV 패키지 매니저 설치 (공식 이미지 활용)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 의존성 설정 파일 복사
COPY pyproject.toml uv.lock ./

# 가상환경 생성 및 의존성 설치
# --frozen: uv.lock 버전 준수
# --no-dev: 개발용 패키지 제외
# --no-install-project: 프로젝트 자체는 설치 제외 (소스 코드는 Runtime에서 복사)
# --compile: 바이트코드 컴파일
RUN uv sync --frozen --no-dev --no-install-project --compile

# ==========================================
# Stage 2: Runtime (실행 환경)
# ==========================================
FROM python:3.11-slim AS runtime

WORKDIR /app

# 헬스 체크용 도구 설치 (필요 시)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Builder에서 생성한 가상환경 복사
COPY --from=builder /app/.venv /app/.venv

# 환경 변수 설정
# PATH에 가상환경 bin을 추가하여 별도 activate 없이 실행
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# 소스 코드 복사
COPY . .

# 보안: 비루트 사용자 생성 및 권한 부여
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

# 사용자 전환
USER appuser

# 포트 노출
EXPOSE 8000

# 실행 명령
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]