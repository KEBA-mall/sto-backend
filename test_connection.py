# test_connection.py
# 데이터베이스 연결 테스트용 스크립트

from app.database import test_connection, check_tables

def main():
    print("🔍 Testing database connection...")
    print("=" * 50)
    
    # 1. 연결 테스트
    if test_connection():
        print()
        # 2. 테이블 확인
        print("🔍 Checking tables...")
        tables = check_tables()
        
        if tables:
            print(f"\n✅ Found {len(tables)} tables in faank_db")
            
            # 기대하는 테이블들
            expected_tables = ['users', 'sms_verifications', 'user_sessions']
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                print(f"⚠️  Missing tables: {missing_tables}")
                print("   Please run the SQL schema creation script in pgAdmin")
            else:
                print("🎉 All required tables found!")
        else:
            print("❌ No tables found. Please create tables first.")
    else:
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if PostgreSQL is running")
        print("2. Verify DATABASE_URL in .env file")
        print("3. Check username/password")
        print("4. Ensure faank_db database exists")

if __name__ == "__main__":
    main()