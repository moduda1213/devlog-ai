from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import settings
from app.core.database import get_db
from app.services import github_service, user_service 

from app.core.security import create_access_token
from app.api.deps import get_current_user 
from app.models.user import User

router = APIRouter()
# cipher_suite 초기화 제거 (서비스 레이어로 이동)

@router.get("/github/login")
async def github_login():
    """GitHub 로그인 페이지로 리다이렉트"""
    logger.info("🚀 GitHub OAuth login initiated")
    
    base_url = "https://github.com/login/oauth/authorize"
    scope = "read:user repo"
    url = f"{base_url}?client_id={settings.GITHUB_CLIENT_ID}&scope={scope}"
    
    logger.debug(f"Redirecting to: {url}")
    return RedirectResponse(url)

@router.get("/github/callback")
async def github_callback(code: str, db: AsyncSession = Depends(get_db)):
    """GitHub 인증 콜백 처리"""
    logger.info(f"📥 OAuth callback received. Code: {code[:10]}...")
    
    try:
        # 1. GitHub API 통신 (Service)
        logger.debug("Requesting access token from GitHub...")
        access_token = await github_service.get_access_token(code)
        logger.debug(f"access_token: {access_token}")
        
        logger.debug("Fetching user profile from GitHub...")
        user_info = await github_service.get_user_info(access_token)
        logger.debug(f"👤 User authenticated: {user_info}")
        
        
        # 2. 비즈니스 로직 위임 (Service) ✅
        # Upsert 로직을 서비스 레이어로 위임하여 라우터를 간결하게 유지
        user = await user_service.get_or_create_user(
            db=db,
            github_id=user_info["id"],
            username=user_info["login"],
            access_token=access_token
        )
        
        logger.success(f"💾 User processed successfully. UUID: {user.id}")
        
        # ✅ JWT 토큰 발급
        access_token = create_access_token(subject=user.id)
        
        # 응답에 토큰 포함
        return {
            "message": "Login Successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "username": user.github_username
            }
        }
        
    except HTTPException as e:
        logger.error(f"❌ HTTP Error during auth: {e.detail}")
        raise e
    
    except Exception:
        logger.exception("🔥 Unexpected error during GitHub callback")
        raise HTTPException(status_code=500, detail="Internal Authentication Error")

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자 정보 반환"""
    return {
        "id": str(current_user.id),
        "username": current_user.github_username,
        "github_id": current_user.github_user_id,
        "created_at": current_user.created_at
    }