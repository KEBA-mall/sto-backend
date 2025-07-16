from fastapi import APIRouter, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import jwt
from datetime import datetime, timedelta
import bcrypt

from app.config import settings

router = APIRouter()
security = HTTPBearer()

# Pydantic 모델 (요청/응답 스키마)
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    user_id: int
    email: str
    username: str
    user_type: str
    created_at: datetime

# 임시 사용자 저장소 (실제로는 DB 사용)
fake_users_db = {
    "admin@farmtoken.com": {
        "user_id": 1,
        "email": "admin@farmtoken.com",
        "username": "admin",
        "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "admin123"
        "user_type": "admin",
        "created_at": datetime.now()
    }
}

# 유틸리티 함수들
def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """JWT 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """JWT 토큰 검증"""
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# API 엔드포인트들
@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """회원가입"""
    if user_data.email in fake_users_db:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # 사용자 생성
    user_id = len(fake_users_db) + 1
    hashed_password = hash_password(user_data.password)

    new_user = {
        "user_id": user_id,
        "email": user_data.email,
        "username": user_data.username,
        "password_hash": hashed_password,
        "user_type": "customer",
        "created_at": datetime.now()
    }

    fake_users_db[user_data.email] = new_user

    return UserResponse(**new_user)

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """로그인"""
    user = fake_users_db.get(user_data.email)
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    # JWT 토큰 생성
    access_token = create_access_token(data= {"sub": user["email"], "user_id":user["user_id"]})

    return Token(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(token_data: dict = Depends(verify_token)):
    """현재 사용자 정보 조회"""
    user = fake_users_db(token_data["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(**user)

@router.post("/logout")
async def logout():
    """로그아웃 (클라이언트 토큰 삭제)"""
    return {"message": "Successfully logged out"}

# 관리자 권한 확인 의존성
async def require_admin(token_data: dict = Depends(verify_token)):
    """관리자 권한 필요"""
    user = fake_users_db.get(token_data["sub"])
    if not user or user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
