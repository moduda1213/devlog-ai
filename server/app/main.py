from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1 import api_router
from app.services.github_service import GithubApiError

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
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
