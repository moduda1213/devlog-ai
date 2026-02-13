import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1 import api_router
from app.services.github_service import GithubApiError
from loguru import logger
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

try:
    logger.debug(f"ALLOWED_ORIGINS (raw): {settings.ALLOWED_ORIGINS}")
    origins = json.loads(settings.ALLOWED_ORIGINS)
except json.JSONDecodeError:
    logger.warning("Failed to parse ALLOWED_ORIGINS as JSON. Fallback to comma-separated list.")
    # 쉼표로 분리하여 리스트 생성
    origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]

# 안전장치: 빈 리스트일 경우 로컬호스트 추가
if not origins:
    origins = ["http://localhost:3000", "http://localhost:4173"]

logger.info(f"✅ Loaded CORS Origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 허용할 출처 목록 (Frontend URL)
    allow_credentials=True,      # 쿠키(인증 정보) 포함 허용 (매우 중요!)
    allow_methods=["*"],         # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],         # 모든 헤더 허용
)

app.include_router(api_router, prefix="/api/v1")

@app.exception_handler(GithubApiError)
async def github_exception_handler(request: Request, exc: GithubApiError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

@app.get("/health")
def health_check():
    """서버 상태 확인"""
    return {
        "status": "ok",
        "env": settings.ENVIRONMENT,
        "version": settings.VERSION
    }

@app.get("/")
def root():
    return {"message": "Welcome to DevLog AI API"}
