from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import settings
from app.core.database import get_db
from app.services import github_service, user_service, auth_service

from app.core.security import create_access_token
from app.api.deps import get_current_user 
from app.models.user import User

router = APIRouter()
# cipher_suite 초기화 제거 (서비스 레이어로 이동)

@router.get("/github/login")
async def github_login() -> RedirectResponse:
    """GitHub 로그인 페이지로 리다이렉트"""
    logger.info("🚀 GitHub OAuth login initiated")
    
    base_url = "https://github.com/login/oauth/authorize"
    scope = "read:user repo"
    url = f"{base_url}?client_id={settings.GITHUB_CLIENT_ID}&scope={scope}"
    
    logger.debug(f"Redirecting to: {url}")
    return RedirectResponse(url)

@router.get("/github/callback")
async def github_callback(
    code: str, 
    db: AsyncSession = Depends(get_db)) -> RedirectResponse:
    
    """GitHub 인증 콜백 처리"""
    logger.info(f"📥 OAuth callback received. Code: {code[:10]}...")
    
    try:
        # 1. GitHub API 통신 (Service)
        logger.debug("Requesting access token from GitHub...")
        access_token = await github_service.get_access_token(code)
        logger.debug(f"access_token: {access_token}")
        
        logger.debug("Fetching user profile from GitHub...")
        user_info = await github_service.get_user_info(access_token)
        logger.debug(f"👤 User authenticated: {user_info.get('login')}")
        
        
        # 2. 비즈니스 로직 위임 (Service) ✅
        # Upsert 로직을 서비스 레이어로 위임하여 라우터를 간결하게 유지
        user = await user_service.get_or_create_user(
            db=db,
            github_id=user_info["id"],
            username=user_info["login"],
            access_token=access_token,
            avatar_url=user_info.get("avatar_url")
        )
        
        logger.success(f"💾 User processed successfully. UUID: {user.id}")
        
        # ✅ JWT 토큰 발급
        access_token = create_access_token(subject=user.id)
        
        refresh_token = await auth_service.create_refresh_token(db, user.id)
            
        # 프론트엔드로 리다이렉트
        response = RedirectResponse(
            url = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
        )
        
        # Refresh Token 쿠키 설정
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, # 초 단위 변환
            samesite="none" if settings.ENVIRONMENT == "production" else "lax",
            secure=settings.ENVIRONMENT == "production",
            path="/api/v1/auth/refresh" # Refresh 요청 때만 전송되도록 제한
        )
        
        return response
        
    except HTTPException as e:
        logger.error(f"❌ HTTP Error during auth: {e.detail}")
        raise e
    
    except Exception:
        logger.exception("🔥 Unexpected error during GitHub callback")
        raise HTTPException(status_code=500, detail="Internal Authentication Error")

@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(None),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """로그아웃: Refresh Token 폐기 및 쿠키 삭제"""

    # DB에서 토큰 삭제 (유효한 경우만)
    if refresh_token:
        await auth_service.revoke_token(db, refresh_token)

    # 쿠키 삭제
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth/refresh",
        httponly=True,
        samesite="none" if settings.ENVIRONMENT == "production" else "lax",
        secure=settings.ENVIRONMENT == "production"
    )

    # (선택) Access Token 쿠키가 혹시 남아있다면 같이 삭제
    response.delete_cookie("access_token")

    return {"message": "Successfully logged out"}

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)) -> dict:
    """현재 로그인한 사용자 정보 반환"""
    return {
        "id": str(current_user.id),
        "username": current_user.github_username,
        "avatar_url": current_user.avatar_url,
        "github_id": current_user.github_user_id,
        "created_at": current_user.created_at,
        "selected_repo_id": str(current_user.selected_repo_id) if current_user.selected_repo_id else None
    }
    
@router.post("/refresh")
async def refresh_access_token(
    response: Response,
    refresh_token: str | None = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Access Token 재발급 (Silent Refresh)
    - HttpOnly 쿠키의 Refresh Token을 사용
    - 성공 시 새 Access Token(Body)과 새 Refresh Token(Cookie) 발급 (RTR)
    """
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        # ✅ [수정] verify 호출 없이 바로 rotate 호출 (여기서 검증, 삭제, 생성 다 함)
        new_refresh_token_val, user_id = await auth_service.rotate_refresh_token(db, refresh_token)

        # 2. 새 Access Token 생성
        new_access_token = create_access_token(subject=user_id)

        # 3. 쿠키 갱신
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token_val,
            httponly=True,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            samesite="none" if settings.ENVIRONMENT == "production" else "lax",
            secure=settings.ENVIRONMENT == "production",
            path="/api/v1/auth/refresh"
        )

        return {"access_token": new_access_token, "token_type": "bearer"}

    except ValueError:
        # 토큰 검증 실패 또는 만료 시 쿠키 삭제
        response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")