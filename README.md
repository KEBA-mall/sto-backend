# mall-backend

## 🚀 프로젝트 소개

**증권형 토큰(STO) 투자 플랫폼** </br>
안정적이고 확장 가능한 아키텍처 설계를 통해, 현재는 MVP(Minimum Viable Product) 개발을 위한 프로토타입 단계에 있으며, 향후 실제 증권사 연동 및 강화된 보안 시스템 구축을 목표로 합니다.

## ✨ 현재 개발 계획 (MVP/프로토타입)

현재 개발 단계에서는 **프로토타입 제품 출시**에 중점을 둡니다.

- **실시간 데이터베이스**: **Firebase Realtime Database**를 활용하여 데이터 저장 및 관리를 진행합니다.
- **사용자 인증**: 핸드폰을 통한 **실명인증 기능**을 구현합니다.
- **계좌 연결**: **더미 데이터 기반**으로 계좌 연결 기능을 구현하여 기본적인 사용자 흐름을 테스트합니다.
- **핵심 비즈니스 로직**: STO 투자 상품 정보 조회, 간단한 투자 시뮬레이션 등 핵심 비즈니스 로직을 구현합니다.

## 🚀 확장성 고려 사항 (향후 계획)

프로젝트의 장기적인 성공과 **증권형 토큰 플랫폼으로서의 신뢰성 확보**를 위해 다음과 같은 확장 계획을 고려하고 있습니다.

- **증권사 연동**: 실제 증권사 시스템(API)과 연동하여 **실제 계좌 관리, 자산 이체, 증권형 토큰 발행 및 유통** 등의 기능을 구현합니다. (키움증권, 신한증권 등)
- **강화된 보안 시스템**:
  - **암호화**: 모든 민감 데이터(개인정보, 금융 정보)에 대한 강력한 암호화 적용.
  - **접근 제어**: 역할 기반 접근 제어(RBAC) 및 최소 권한 원칙 적용.
  - **보안 프로토콜**: HTTPS, OAuth 2.0 등 표준 보안 프로토콜 준수.
  - **이상 거래 탐지**: 금융 사기 및 이상 거래 탐지를 위한 시스템 도입.
  - **정기적인 보안 감사**: 외부 전문가를 통한 보안 취약점 점검 및 개선.
- **분산원장기술(DLT) 통합**: 블록체인 기반의 STO 발행 및 관리를 위한 핵심 DLT 기술 스택 확정 및 통합.
- **확장 가능한 데이터베이스**: 트랜잭션 처리량 및 데이터 안정성을 고려한 관계형 DB (PostgreSQL) 도입 검토.
- **마이크로서비스 아키텍처**: 기능별 분리를 통한 독립적인 개발, 배포, 확장을 위한 아키텍처 전환 검토.
- **클라우드 인프라**: AWS, GCP, Azure 등 클라우드 플랫폼의 관리형 서비스를 활용한 안정적이고 확장 가능한 인프라 구축.

## 🛠️ 기술 스택 (MVP/프로토타입 기준)

현재 프로토타입 개발에 사용될 주요 기술 스택입니다.

- **[백엔드 프레임워크]**: Node.js (Express.js, NestJS), Python (Django, Flask), Java (Spring Boot)
- **[데이터베이스]**: Firebase Realtime Database
- **[인증]**: Firebase Authentication 또는 자체 구현 (더미)
- **[배포]**: Firebase Hosting

# 여기부터는 확장을 고려한 설계입니다.

# FarmToken Backend

농축수산물 쇼핑몰 + STO 투자 플랫폼 백엔드 API

## 🚀 기술 스택

- **FastAPI**: 고성능 웹 API 프레임워크
- **Python 3.10+**: 백엔드 언어
- **PostgreSQL**: 메인 데이터베이스 (예정)
- **Redis**: 캐싱 및 세션 관리 (예정)
- **JWT**: 사용자 인증

## 📦 설치 및 실행

### 1. 가상환경 생성

```bash
python -m venv faank
source faank/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

```bash
cp .env.example .env
# .env 파일을 수정하여 필요한 설정값 입력
```

### 4. 서버 실행

```bash
uvicorn app.main:app --reload
```

## 📖 API 문서

서버 실행 후 다음 URL에서 API 문서 확인:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🏗️ 프로젝트 구조

```
farmtoken-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config.py              # 환경변수, 설정
│   ├── database.py            # DB 연결 설정
│   ├── dependencies.py        # 공통 의존성 (인증 등)
│   │
│   ├── models/                # SQLAlchemy 모델 (DB 테이블)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── review.py
│   │
│   ├── schemas/               # Pydantic 스키마 (API 요청/응답)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── auth.py
│   │
│   ├── routers/               # API 라우터 (엔드포인트)
│   │   ├── __init__.py
│   │   ├── auth.py           # 로그인, 회원가입
│   │   ├── products.py       # 상품 CRUD
│   │   ├── orders.py         # 주문 관리
│   │   ├── cart.py           # 장바구니
│   │   └── admin.py          # 관리자 기능
│   │
│   ├── services/              # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   └── payment_service.py
│   │
│   ├── utils/                 # 유틸리티 함수
│   │   ├── __init__.py
│   │   ├── security.py       # 비밀번호 해싱, JWT
│   │   ├── email.py          # 이메일 발송
│   │   └── file_handler.py   # 파일 업로드
│   │
│   └── core/                  # 핵심 설정
│       ├── __init__.py
│       ├── security.py
│       └── middleware.py
│
├── tests/                     # 테스트 코드
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_products.py
│   └── test_orders.py
│
├── requirements.txt           # 패키지 의존성
├── .env                      # 환경변수
├── .gitignore
└── README.md
```

## 🔧 개발 단계

### 1단계: 기초 인프라 구축 (현재)

- [ ] FastAPI 기본 구조
- [ ] 사용자 인증 시스템
- [ ] 상품 관리 API
- [ ] 주문 시스템
- [ ] 관리자 페이지

### 2단계: STO 토큰 연동 (예정)

- [ ] 토큰 발행 로직
- [ ] 지갑 연동
- [ ] 증권사 API 연결

### 3단계: AI 시세 예측 (예정)

- [ ] 가격 예측 모델
- [ ] 리스크 분석
- [ ] 투자 추천 시스템

## 🔑 주요 API 엔드포인트

### 인증

- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인
- `GET /api/auth/me` - 현재 사용자 정보

### 상품 (예정)

- `GET /api/products` - 상품 목록
- `POST /api/products` - 상품 등록 (관리자)
- `GET /api/products/{id}` - 상품 상세

## 🧪 테스트

```bash
pytest
```

## 📄 라이선스

MIT License
