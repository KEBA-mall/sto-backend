# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(11), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_name = Column(String(100), nullable=True)
    user_type = Column(String(20), default="customer") # customer, admin, seller
    kyc_status = Column(String(20), default="pending") # pending, verified, rejected
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 관계 설정 (나중에 다른 테이블과 연결할 때 사용)
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, phone_number={self.phone_number}, user_type={self.user_type})>"

    def to_dict(self):
        """모델을 딕셔너리로 변환 (JSON 응답용)"""
        return {
            "user_id": self.user_id,
            "phone_number": self.phone_number,
            "user_name": self.user_name,
            "user_type": self.user_type,
            "kyc_status": self.kyc_status,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class SMSVerification(Base):
    """SMS 인증 모델"""
    __tablename__ = "sms_verifications"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(11), nullable=False, index=True)
    verification_code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    attempts = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<SMSVerification(phone_number={self.phone_number}, code={self.verification_code}, expires_at={self.expires_at})>"

    def is_expired(self):
        """인증번호 만료 여부 확인"""
        from datetime import datetime
        return datetime.now() > self.expires_at

    def is_valid_attempt(self):
        """시도 횟수 확인 (5회 제한)"""
        return self.attempts < 5

class UserSession(Base):
    """사용자 세션 모델 (JWT 토큰 관리)"""
    __tablename__ = "user_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    access_token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 관계 설정
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(session_id={self.session_id}, user_id={self.user_id}, expires_at={self.expires_at})>"

    def is_expired(self):
        """세션 만료 여부 확인"""
        from datetime import datetime
        return datetime.now() > self.expires_at