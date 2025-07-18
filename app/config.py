from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # 기본 설정
    PROJECT_NAME: str = "Faank"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "농축수산물 쇼핑몰 + STO 투자 플랫폼"

    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # DB 설정 (나중에 연결할 때 사용)
    DATABASE_URL: Optional[str] = None

    # JWT 토큰 설정
    SECRET_KEY: str = "your-secret-key" # secret key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 파일 업로드 설정
    UPLOAD_DIR: str = "static/uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024 # 10MB
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "gif", "webp"}

    # 이메일 설정
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # 외부 API 키 (나중에 연결)
    KAMIS_API_KEY: Optional[str] = None # 농산물 가격 정보
    WEATHER_API_KEY: Optional[str] = None # 기상청 API
    PAYMENT_API_KEY: Optional[str] = None # 결제 API

    # Redis 설정 (캐싱용)
    REDIS_URL: str = "redis://localhost:6379"

    # 개발/운영 환경 구분
    ENVIRONMENT: str = "development" # development, production

    class Config:
        env_file = ".env"
        case_sensitive = True

# 설정 인스턴스 생성
settings = Settings()

# 환경별 설정 오버라이드
if settings.ENVIRONMENT == "production":
    settings.DEBUG = False
    secret_key = os.getenv("SECRET_KEY")
    if secret_key:
        settings.SECRET_KEY = secret_key

elif settings.ENVIRONMENT == "development":
    settings.DEBUG = True
    # 개발 환경에서는 더 긴 토큰 만료 시간
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24