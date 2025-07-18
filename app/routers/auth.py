# app/routers/auth.py
from typing import Optional

# FastAPI 관련 임포트 (한 줄씩 명시적으로)
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    SMSRequest, SMSVerifyRequest, UserRegisterRequest, UserLoginRequest,
    SMSResponse, SMSVerifyResponse, LoginResponse, UserResponse, ApiResponse
)
from app.services.auth_service import AuthService
from app.utils.auth import verify_token
from app.models import User

router = APIRouter()
security = HTTPBearer()

# 의존성: 현재 사용자 가져오기
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """JWT 토큰에서 현재 사용자 가져오기"""
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에서 사용자 정보를 찾을 수 없습니다"
        )
    
    auth_service = AuthService(db)
    user = auth_service.get_current_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다"
        )
    
    return user

# API 엔드포인트들
@router.post("/send-sms", response_model=SMSResponse)
def send_sms_verification(
    request: SMSRequest,
    db: Session = Depends(get_db)
):
    """SMS 인증번호 발송"""
    auth_service = AuthService(db)
    try:
        result = auth_service.send_sms_verification(request.phone_number)
        return SMSResponse(**result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 오류가 발생했습니다: {str(e)}"
        )

@router.post("/verify-sms", response_model=SMSVerifyResponse)
def verify_sms_code(
    request: SMSVerifyRequest,
    db: Session = Depends(get_db)
):
    """SMS 인증번호 확인"""
    auth_service = AuthService(db)
    try:
        result = auth_service.verify_sms_code(request.phone_number, request.verification_code)
        return SMSVerifyResponse(**result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 오류가 발생했습니다: {str(e)}"
        )

@router.post("/register", response_model=LoginResponse)
def register_user(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """회원가입"""
    auth_service = AuthService(db)
    try:
        result = auth_service.register_user(request)
        
        # LoginResponse 형태로 변환
        return LoginResponse(
            access_token=result["access_token"],
            token_type=result["token_type"],
            expires_in=30 * 60,  # 30분 (초 단위)
            user=UserResponse(**result["user"])
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 오류가 발생했습니다: {str(e)}"
        )

@router.post("/login", response_model=LoginResponse)
def login_user(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """로그인"""
    auth_service = AuthService(db)
    try:
        result = auth_service.login_user(request)
        
        # LoginResponse 형태로 변환
        return LoginResponse(
            access_token=result["access_token"],
            token_type=result["token_type"],
            expires_in=30 * 60,  # 30분 (초 단위)
            user=UserResponse(**result["user"])
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 오류가 발생했습니다: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """현재 사용자 정보 조회"""
    return UserResponse(**current_user.to_dict())

@router.post("/logout", response_model=ApiResponse)
def logout_user(
    current_user: User = Depends(get_current_user)
):
    """로그아웃 (클라이언트에서 토큰 삭제)"""
    return ApiResponse(
        success=True,
        message="로그아웃이 완료되었습니다"
    )

@router.get("/test", response_model=ApiResponse)
def test_auth():
    """인증 API 테스트"""
    return ApiResponse(
        success=True,
        message="인증 API가 정상 작동합니다",
        data={"timestamp": "2024-01-01 12:00:00"}
    )

# 관리자 권한 확인 의존성
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """관리자 권한 필요한 엔드포인트용"""
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    return current_user