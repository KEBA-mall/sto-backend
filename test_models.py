# test_models.py
# SQLAlchemy 모델이 제대로 작동하는지 테스트

from app.database import SessionLocal, engine
from app.models import User, SMSVerification, UserSession
from app.schemas import UserRegisterRequest
from sqlalchemy import text
import bcrypt

def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def test_user_model():
    """User 모델 테스트"""
    print("👤 Testing User model...")
    
    db = SessionLocal()
    try:
        # 테스트 사용자 생성
        test_user = User(
            phone_number="01012345678",
            password_hash=hash_password("123456"),
            user_name="테스트 사용자",
            user_type="customer"
        )
        
        # 데이터베이스에 저장
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ User created: {test_user}")
        print(f"   User dict: {test_user.to_dict()}")
        
        # 사용자 조회
        found_user = db.query(User).filter(User.phone_number == "01012345678").first()
        if found_user:
            print(f"✅ User found: {found_user.user_name}")
        
        # 테스트 데이터 삭제
        db.delete(test_user)
        db.commit()
        print("🗑️ Test user deleted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def test_sms_model():
    """SMSVerification 모델 테스트"""
    print("\n📱 Testing SMSVerification model...")
    
    db = SessionLocal()
    try:
        from datetime import datetime, timedelta
        
        # SMS 인증 데이터 생성
        sms_verification = SMSVerification(
            phone_number="01087654321",
            verification_code="123456",
            expires_at=datetime.now() + timedelta(minutes=5)
        )
        
        db.add(sms_verification)
        db.commit()
        db.refresh(sms_verification)
        
        print(f"✅ SMS verification created: {sms_verification}")
        print(f"   Is expired: {sms_verification.is_expired()}")
        print(f"   Is valid attempt: {sms_verification.is_valid_attempt()}")
        
        # 테스트 데이터 삭제
        db.delete(sms_verification)
        db.commit()
        print("🗑️ Test SMS verification deleted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def test_schema_validation():
    """Pydantic 스키마 검증 테스트"""
    print("\n🔍 Testing Pydantic schemas...")
    
    try:
        # 올바른 데이터
        valid_request = UserRegisterRequest(
            phone_number="010-1234-5678",  # 하이픈 포함
            password="123456",
            user_name="홍길동"
        )
        print(f"✅ Valid request: {valid_request}")
        print(f"   Cleaned phone: {valid_request.phone_number}")
        
        # 잘못된 데이터 테스트
        try:
            invalid_request = UserRegisterRequest(
                phone_number="010-123-456",  # 짧은 번호
                password="12345",  # 5자리
                user_name="홍길동"
            )
        except Exception as e:
            print(f"✅ Validation error caught: {e}")
        
    except Exception as e:
        print(f"❌ Schema test error: {e}")

def main():
    print("🧪 Testing SQLAlchemy models and Pydantic schemas")
    print("=" * 60)
    
    # 테이블 존재 확인
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        count = result.fetchone()[0]
        print(f"📊 Current users in database: {count}")
    except Exception as e:
        print(f"❌ Cannot access users table: {e}")
        print("   Please make sure tables are created!")
        return
    finally:
        db.close()
    
    # 모델 테스트 실행
    test_user_model()
    test_sms_model()
    test_schema_validation()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()