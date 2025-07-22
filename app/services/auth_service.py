#app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional

from app.models import User, SMSVerification
from app.schemas import UserRegisterRequest, UserLoginRequest
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    generate_verification_code,
    send_sms,
    format_phone_number,
    mask_phone_number,
    create_verification_token
)

class AuthService:
    """인증 관련 비즈니스 로직"""

    def __init__(self, db: Session):
        self.db = db
    
    def send_sms_verification(self, phone_number: str) -> dict:
        """SMS 인증번호 발송"""
        phone_number = format_phone_number(phone_number)

        # 이미 가입된 사용자인지 확인
        existing_user = self.db.query(User).filter(User.phone_number == phone_number).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 가입된 핸드폰 번호입니다"
            )

        # 기존 인증번호 삭제 (같은 번호로 재발송시)
        self.db.query(SMSVerification).filter(
            SMSVerification.phone_number == phone_number
        ).delete()

        # 새 인증번호 생성
        verification_code = generate_verification_code()
        expires_at = datetime.now() + timedelta(minutes=5) # 5분 유효

        # DB에 저장
        sms_verification = SMSVerification(
            phone_number=phone_number,
            verification_code=verification_code,
            expires_at=expires_at
        )
        self.db.add(sms_verification)
        self.db.commit()

        # SMS 발송
        message = f"[Faank] 인증번호: {verification_code}"
        sms_success = send_sms(phone_number, message)

        if not sms_success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SMS 발송에 실패했습니다"
            )

        return {
            "success": True,
            "message": f"{mask_phone_number(phone_number)}로 인증번호를 발송했습니다"
        }

    def verify_sms_code(self, phone_number: str, verification_code: str) -> dict:
        """SMS 인증번호 확인"""
        phone_number = format_phone_number(phone_number)

        # 저장된 인증번호 조회
        sms_verification = self.db.query(SMSVerification).filter(
            SMSVerification.phone_number == phone_number,
            SMSVerification.is_verified == False
        ).order_by(SMSVerification.created_at.desc()).first()

        if not sms_verification:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="발송된 인증번호가 없습니다"
            )
        
        # 만료 확인
        if sms_verification.is_expired():
            self.db.delete(sms_verification)
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="인증번호가 만료되었습니다"
            )

        # 시도 횟수 확인
        if not sms_verification.is_valid_attempt():
            self.db.delete(sms_verification)
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="인증 시도 횟수를 초과했습니다"
            )

        # 인증번호 확인
        if sms_verification.verification_code != verification_code:
            sms_verification.attempts += 1
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="인증번호가 올바르지 않습니다"
            )
        
        # 인증 성공
        sms_verification = True
        self.db.commit()

        # 임시 검증 토큰 생성 (회원가입 진행용)
        verification_token = create_verification_token(phone_number)

        return {
            "success": True,
            "message": "핸드폰 번호 인증이 완료되었습니다",
            "verification": verification_token
        }

    def register_user(self, user_data: UserRegisterRequest) -> dict:
        """회원가입"""
        phone_number = format_phone_number(user_data.phone_number)

        # 중복 확인
        existing_user = self.db.query(User).filter(User.phone_number == phone_number).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 가입된 핸드폰 번호입니다"
            )
        
        # SMS 인증 완료 확인 (선택사항 - 더 엄격한 검증을 원할 경우)
        # verified_sms = self.db.query(SMSVerification).filter(
        #     SMSVerification.phone_number == phone_number,
        #     SMSVerification.is_verified == True
        # ).first()
        # if not verified_sms:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="핸드폰 번호 인증이 필요합니다"
        #     )

        # 사용자 생성
        hashed_password = hash_password(user_data.password)
        new_user = User(
            phone_number=phone_number,
            password_hash=hashed_password,
            user_name="김팽크",
            user_type="customer"
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        # 사용자 SMS 인증 데이터 삭제
        self.db.query(SMSVerification).filter(
            SMSVerification.phone_number == phone_number
        ).delete()
        self.db.commit()

        # JWT 토큰 생성
        access_token = create_access_token(
            data={"user_id": new_user.user_id, "phone_number": phone_number}
        )

        return {
            "success": True,
            "message": "회원가입이 완료되었습니다",
            "access_token": access_token,
            "token_type": "bearer",
            "user": new_user.to_dict()
        }

    def login_user(self, login_data: UserLoginRequest) -> dict:
        """로그인"""
        phone_number = format_phone_number(login_data.phone_number)

        # 사용자 조회
        user = self.db.query(User).filter(
            User.phone_number == phone_number,
            User.is_active == True
        ).first()

        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="핸드폰 번호 또는 비밀번호가 올바르지 않습니다"
            )

        # JWT 토큰 생성
        access_token = create_access_token(
            data={"user_id": user.user_id, "phone_number": phone_number}
        )

        return {
            "success": True,
            "message": "로그인이 완료되었습니다",
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }

    def get_current_user(self, user_id: int) -> Optional[User]:
        """현재 사용자 정보 조회"""
        return self.db.query(User).filter(
            User.user_id == user_id,
            User.is_active == True,
        ).first()

