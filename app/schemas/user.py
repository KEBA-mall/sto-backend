# app/schemas/user.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

# 요청 스키마 (입력)
class SMSRequest(BaseModel):
    """SMS 인증번호 발송 요청"""
    phone_number: str

    @validator('phone_number')
    def validate_phone_number(cls, v):
        # 하이픈 제거
        phone = v.replace('-', '').replace(' ', '')
        
        # 한국 핸드폰 번호 형식 확인
        if not phone.startswith('010') or len(phone) != 11:
            raise ValueError('올바른 핸드폰 번호 형식이 아닙니다 (010xxxxxxxx)')
        
        if not phone.isdigit():
            raise ValueError('핸드폰 번호는 숫자만 입력 가능합니다')
        
        return phone

class SMSVerifyRequest(BaseModel):
    """SMS 인증번호 확인 요청"""
    phone_number: str
    verification_code: str

    @validator('phone_number')
    def validate_phone_number(cls, v):
        phone = v.replace('-', '').replace(' ', '')
        if not phone.startswith('010') or len(phone) != 11:
            raise ValueError('올바른 핸드폰 번호 형식이 아닙니다')
        return phone

    @validator('verification_code')
    def validate_verification_code(cls, v):
        if len(v) != 6 or not v.isdigit():
            raise ValueError('인증번호는 6자리 숫자여야 합니다')
        return v

class UserRegisterRequest(BaseModel):
    """회원가입 요청"""
    phone_number: str
    password: str
    user_name: Optional[str] = None

    @validator('phone_number')
    def validate_phone_number(cls, v):
        phone = v.replace('-', '').replace(' ', '')
        if not phone.startswith('010') or len(phone) != 11:
            raise ValueError('올바른 핸드폰 번호 형식이 아닙니다')
        return phone

    @validator('password')
    def validate_password(cls, v):
        if len(v) != 6 or not v.isdigit():
            raise ValueError('비밀번호는 6자리 숫자여야 합니다')
        return v

class UserLoginRequest(BaseModel):
    """로그인 요청"""
    phone_number: str
    password: str

    @validator('phone_number')
    def validate_phone_number(cls, v):
        phone = v.replace('-', '').replace(' ', '')
        if not phone.startswith('010') or len(phone) != 11:
            raise ValueError('올바른 핸드폰 번호 형식이 아닙니다')
        return phone

    @validator('password')
    def validate_password(cls, v):
        if len(v) != 6 or not v.isdigit():
            raise ValueError('비밀번호는 6자리 숫자여야 합니다')
        return v

# 응답 스키마 (출력)
class UserResponse(BaseModel):
    """사용자 정보 응답"""
    user_id: int
    phone_number: str
    user_name: Optional[str] = None
    user_type: str
    kyc_status: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy 모델에서 데이터 가져오기

class LoginResponse(BaseModel):
    """로그인 응답"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class SMSResponse(BaseModel):
    """SMS 발송 응답"""
    success: bool
    message: str

class SMSVerifyResponse(BaseModel):
    """SMS 인증 응답"""
    success: bool
    message: str
    verification_token: Optional[str] = None

class ApiResponse(BaseModel):
    """일반 API 응답"""
    success: bool
    message: str
    data: Optional[dict] = None