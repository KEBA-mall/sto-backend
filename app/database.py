# app/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# PostgreSQL 연결 URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL, echo=True)  # echo=True로 SQL 쿼리 로그 출력

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 베이스 클래스 생성
Base = declarative_base()

# 데이터베이스 세션 의존성
def get_db():
    """FastAPI에서 사용할 DB 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 데이터베이스 연결 테스트
def test_connection():
    """데이터베이스 연결 테스트 함수"""
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        db.close()
        print(f"✅ Database connection successful!")
        print(f"📊 PostgreSQL version: {version}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

# 테이블 존재 확인
def check_tables():
    """생성된 테이블 확인"""
    try:
        db = SessionLocal()
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        db.close()
        
        print("📋 Found tables:")
        for table in tables:
            print(f"   - {table}")
        return tables
    except Exception as e:
        print(f"❌ Failed to check tables: {e}")
        return []