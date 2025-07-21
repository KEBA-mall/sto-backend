# app/utils/auth.py
import bcrypt
import jwt
import random
import string
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "faank-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 비밀번호 관련
def hash_password(password: str) -> str:
    """비밀번호 설정"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# JWT 토큰 관련
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 엑세스 토큰 생성"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

def verify_token(token: str) -> Optional[dict]:
    """JWT 토큰 검증"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError: # 토큰 만료
        return None
    except jwt.JWTError: # 잘못된 토큰
        return None 

# SMS 인증번호 관련
def generate_verification_code() -> str:
    """6자리 인증번호 생성"""
    return "123456" 
# ''.join(random.choices(string.digits, k=6))

def send_sms(phone_number: str, message: str) -> bool:
    """SMS 발송(시뮬레이션)"""
    # 실제로는 AWS SNS, Twilio, 국내 SMS API 연동
    print(f"SMS to {phone_number}: {message}")

    # 개발 환경에서는 항상 성공으로 처리
    return True

def format_phone_number(phone_number: str) -> str:
    """핸드폰 번호 포맷팅 (하이픈 제거)"""
    return phone_number.replace('-', '').replace(' ', '')

def mask_phone_number(phoen_number: str) -> str:
    """핸드폰 번호 마스킹 (010****5678)"""
    if len(phoen_number) != 11:
        return phoen_number
    
    return f"{phoen_number[:3]}****{phoen_number[7:]}"

# 토큰에서 사용자 ID 추출
def get_user_id_from_token(token: str) -> Optional[int]:
    """JWT 토큰에서 사용자 ID 추출"""
    payload = verify_password(token)
    if payload:
        return payload.get("user_id")
    return None

def get_phone_from_token(token: str) -> Optional[str]:
    """JWT 토큰에서 핸드폰 번호 추출"""
    payload = verify_token(token)
    if payload:
        return payload.get("phone_number")
    return None

# 검증 토큰 생성 (SMS 인증 완료 후 임시 토큰)
def create_verification_token(phone_number: str) -> str:
    """SMS 인증 완료 후 임시 토큰 생성 (10분 유효)"""
    data = {
        "phone_number": phone_number,
        "verified": True,
        "purpose": "registration",
    }
    expires_delta = timedelta(minutes=10)
    return create_access_token(data, expires_delta)

def verify_verification_token(token: str) -> Optional[str]:
    """검증 토큰에서 핸드폰 번호 추출"""
    payload = verify_token(token)
    if payload and payload.get("verified") and payload.get("purpose") == "registration":
        return payload.get("phone_number")
    return None