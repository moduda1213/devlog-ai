from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- Project Info ---
    PROJECT_NAME: str = "DevLog AI"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # --- Database & Redis ---
    # App에서 사용하는 연결 문자열
    DATABASE_URL: str
    REDIS_URL: str
    REDIS_MAX_MEMORY: str = "50mb"

    # Docker Init용 변수 (App 코드에서는 안 쓸 수도 있음)
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_PORT: int = 5432
    REDIS_PORT: int = 6379

    # --- Security ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: str

    # --- External APIs ---
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/github/callback"

    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    GEMINI_MAX_TOKENS: int = 1000
    GEMINI_TEMPERATURE: float = 0.7

    # --- Utils ---
    ALLOWED_ORIGINS: str = '["http://localhost:3000"]'
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # --- Pydantic V2 Config ---
    model_config = SettingsConfigDict(
        env_file="../.env",  # server 폴더 기준 상위 경로
        env_file_encoding="utf-8",
        extra="ignore"  # 정의되지 않은 변수 무시
    )

settings = Settings()