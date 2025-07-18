from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os


app = FastAPI(
    title="FAANK API",
    description="농축수산물 쇼핑몰 + STO 투자 플랫폼",
    version="1.0.0",
    docs_url="/docs", # Swagger UI
    redoc_url="/redoc", # ReDoc
)

# CORS 설정 (프론트엔드 통신용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], # Next.js 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (상품 이미지 등)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 라우터 import 및 등록
try:
    from app.routers import auth
    app.include_router(auth.roster, prefix="/api/auth", tags=["인증"])
    print("✅ Auth router registered successfully")
except ImportError as e:
    print(f"❌ Auth router import failed: {e}")
except Exception as e:
    print(f"❌ Auth router registration failed: {e}")

# 헬스 체크 엔드포인트
@app.get("/")
async def root():
    return {"message": "Faank API server is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version":"1.0.0"}

# 글로벌 예외 처리
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message":exc.detail, "stauts_code": exc.status_code}
    )

# 서버 실행 지정
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )