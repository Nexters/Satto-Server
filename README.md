# Satto Server

사주 기반 운세 및 로또 추천 서비스 백엔드

## 아키텍처

이 프로젝트는 **Clean Architecture** 패턴을 따릅니다.

### 레이어 구조

각 모듈(`users`, `lotto`, `fortune` 등)은 다음과 같은 레이어 구조를 가집니다:

```
{module}/
├── api/                    # API 레이어 (프레젠테이션)
│   ├── router.py          # FastAPI 라우터 (엔드포인트 정의)
│   └── schemas.py         # 요청/응답 스키마 (Pydantic 모델)
│
├── application/            # 애플리케이션 레이어 (Use Case)
│   └── service.py         # 비즈니스 로직 구현, 도메인 조합
│
├── domain/                 # 도메인 레이어 (비즈니스 규칙)
│   ├── entities/          # 도메인 엔티티
│   │   ├── models.py      # SQLAlchemy 모델
│   │   └── enums.py       # 도메인 Enum
│   └── interfaces.py      # 리포지토리 인터페이스 (Protocol)
│
└── infrastructure/         # 인프라 레이어 (구현)
    └── repository.py      # 리포지토리 구현 (데이터베이스 접근)
```

#### 각 레이어의 역할

> **API Layer (`api/`)**
- HTTP 요청/응답 처리
- FastAPI 라우터를 통한 엔드포인트 정의
- 요청 검증 및 응답 직렬화
- 예: `@router.get("/users/{user_id}")` 엔드포인트 정의

> **Application Layer (`application/`)**
- Use Case 구현
- 도메인 로직 조합 및 오케스트레이션
- 트랜잭션 관리
- 예: `UserService.create_user()` - 사용자 생성 Use Case

> **Domain Layer (`domain/`)**
- 비즈니스 규칙 및 도메인 모델
- 외부 의존성 없음 (순수 비즈니스 로직)
- 인터페이스 정의 (의존성 역전 원칙)
- 예: `IUserRepository` 인터페이스, `User` 엔티티

> **Infrastructure Layer (`infrastructure/`)**
- 외부 시스템과의 통신 구현
- 데이터베이스 접근 구현
- 외부 API 클라이언트
- 예: `UserRepository` - MySQL 접근 구현

### 의존성 방향

```
API → Application → Domain ← Infrastructure
```

- **Domain**: 가장 안쪽 레이어, 외부 의존성 없음
- **Application**: Domain을 사용하여 비즈니스 로직 구현
- **Infrastructure**: Domain 인터페이스를 구현
- **API**: Application을 호출하여 HTTP 요청 처리

## 주요 모듈

### `users`
사용자 관리 모듈
- 사용자 생성/조회/수정
- 사주 정보 저장 및 조회

### `four_pillars`
사주 계산 모듈
- 생년월일 기반 사주 계산
- 오행, 십신 분석
- HCX API를 통한 사주 설명 생성

### `fortune`
운세 모듈
- 일일 운세 제공
- 사주 기반 운세 분석

### `lotto`
로또 추천 모듈
- 사주 기반 로또 번호 추천
- 로또 통계 및 당첨 확인

## 시작하기

### 요구사항
- Python 3.13+
- MySQL
- uv (패키지 관리자)

### 설치

```bash
# 의존성 설치
uv sync

# 환경 변수 설정
cp .env.example .env
```

### 실행

```bash
# 개발 서버 실행
uvicorn src.main:app --reload

# 프로덕션 실행
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 전체 프로젝트 구조

```
Satto-Server/
├── src/
│   ├── users/          # 사용자 모듈
│   ├── four_pillars/   # 사주 계산 모듈
│   ├── fortune/        # 운세 모듈
│   ├── lotto/          # 로또 추천 모듈
│   ├── hcx_client/     # HCX API 클라이언트
│   ├── config/         # 설정
│   └── common/         # 공통 유틸리티
├── migrations/          # 데이터베이스 마이그레이션
├── nginx/              # Nginx 설정
└── pyproject.toml      # 프로젝트 설정
```

## 기술 스택

- **Framework**: FastAPI
- **Database**: MySQL (SQLAlchemy)
- **Migration**: Alembic
- **Package Manager**: uv
- **Code Quality**: ruff, mypy


## 개발

### 코드 포맷팅
```bash
ruff format .
ruff check .
```

### 타입 체크
```bash
mypy src/
```

### 데이터베이스 마이그레이션
```bash
# 마이그레이션 생성
alembic revision --autogenerate -m "description"

# 마이그레이션 적용
alembic upgrade head
```

