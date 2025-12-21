# One Service - AI Chat Application

React + AWS Serverless 기반 AI 채팅 애플리케이션

## 🏗️ 아키텍처

### Frontend
- **React 18** + **Vite** + **TailwindCSS**
- **Framer Motion** (애니메이션)
- **React Router** (라우팅)
- **WebSocket** (실시간 채팅)

### Backend (AWS Serverless)
- **Lambda Functions** (Python 3.9)
- **API Gateway** (REST + WebSocket)
- **DynamoDB** (데이터 저장)
- **S3** (프론트엔드 호스팅)
- **CloudFront** (CDN)

## 📁 프로젝트 구조

```
D:\one\
├── backend/                 # Python 백엔드
│   ├── handlers/           # Lambda 핸들러
│   │   ├── api/           # REST API
│   │   └── websocket/     # WebSocket
│   ├── src/
│   │   ├── models/        # 데이터 모델
│   │   ├── repositories/  # 데이터 액세스
│   │   └── services/      # 비즈니스 로직
│   └── utils/             # 유틸리티
├── scripts/                # 배포 스크립트
├── src/                    # React 프론트엔드
└── serverless.yml          # AWS 설정
```

## 🚀 배포 가이드

### 1. 사전 준비
```bash
# AWS CLI 설치 및 설정
aws configure

# Python 3.9+ 설치
python --version

# Node.js 18+ 설치
node --version
```

### 2. 설정 수정
`scripts/config.sh` 파일에서 다음 값들을 수정:
```bash
export AWS_ACCOUNT_ID="YOUR_ACCOUNT_ID"
export DOMAIN="your-domain.com"
```

### 3. 백엔드 배포
```bash
cd D:\one
chmod +x scripts/*.sh
./scripts/deploy-backend.sh
```

### 4. 프론트엔드 배포
```bash
./scripts/deploy-frontend.sh
```

## 🔧 로컬 개발

### 프론트엔드 실행
```bash
npm install
npm run dev
# http://localhost:3002
```

### 백엔드 테스트
```bash
cd backend
pip install -r requirements.txt
python -m pytest  # 테스트 실행 (추후 추가)
```

## 📋 AWS 리소스

### Lambda Functions
- `one-websocket-message` - WebSocket 메시지 처리
- `one-websocket-connect` - WebSocket 연결
- `one-websocket-disconnect` - WebSocket 해제
- `one-conversation-api` - 대화 관리 API
- `one-usage-handler` - 사용량 추적
- `one-prompt-crud` - 프롬프트 관리

### DynamoDB Tables
- `one-conversations` - 대화 저장
- `one-messages` - 메시지 저장
- `one-prompts` - 프롬프트 저장
- `one-usage` - 사용량 추적
- `one-connections` - WebSocket 연결

### S3 Bucket
- `one-frontend-bucket` - 프론트엔드 호스팅

## 🌐 엔드포인트

### REST API
- `GET /conversations` - 대화 목록
- `POST /conversations` - 대화 생성
- `PATCH /conversations/{id}` - 대화 수정
- `DELETE /conversations/{id}` - 대화 삭제

### WebSocket
- `wss://your-api-gateway-url/prod`

## 🔄 CI/CD

배포 스크립트를 통한 자동화:
1. 코드 패키징
2. Lambda 함수 업데이트
3. DynamoDB 테이블 생성
4. 프론트엔드 빌드 & S3 업로드

## 📝 라이센스

MIT License