from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# from app.routers import auth, products, orders, cart, admin
# from app.core.middleware import LoggingMiddleware

app = FastAPI(
    title="FAANK API",
    # description="농축수산물 쇼핑몰 + STO 투자 플랫폼",
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

# 커스텀 미들웨어 추가
# app.add_middleware(LoggingMiddleware)

# 정적 파일 서빙 (상품 이미지 등)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# API 라우터 등록
# app.include_router(auth.router, prefix="/api/auth", tags=["인증"])
# app.include_router(products.router, prefix="/api/products", tags=["상품"])
# app.include_router(orders.router, prefix="/api/orders", tags=["주문"])
# app.include_router(cart.router, prefix="/api/cart", tags=["장바구니"])
# app.include_router(admin.router, prefix="/api/admin", tags=["관리자"])

# 헬스 체크 엔드포인트
@app.get("/")
async def root():
    return {"message": "Faank Backend API server is running!"}

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