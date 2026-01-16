from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
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
