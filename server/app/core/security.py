from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt, JWTError
from cryptography.fernet import Fernet
from app.core.config import settings

def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """JWT Access Token 생성"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
        
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def decode_token(token: str) -> dict[str, Any] | None:
    """JWT 토큰 해독"""
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_token if decoded_token["exp"] >= datetime.now(timezone.utc).timestamp() else None
    
    except JWTError:
        return None

def encrypt_token(token: str) -> str:
    """토큰 암호화 (DB 저장용)"""
    f = Fernet(settings.ENCRYPTION_KEY.encode()) # 가정: 설정에 키가 있다고 전제
    return f.encrypt(token.encode()).decode()

def decrypt_token(token_encrypted: str) -> str:
    """토큰 복호화 (API 호출용)"""
    f = Fernet(settings.ENCRYPTION_KEY.encode())
    return f.decrypt(token_encrypted.encode()).decode()