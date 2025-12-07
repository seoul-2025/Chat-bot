# Demo AI Chat Application - 배포 및 템플릿 작업 가이드

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [프로젝트 구조](#프로젝트-구조)
3. [배포 워크플로우](#배포-워크플로우)
4. [자주 발생하는 에러](#자주-발생하는-에러)
5. [템플릿 작업 가이드](#템플릿-작업-가이드)
6. [환경 설정](#환경-설정)

---

## 프로젝트 개요

이 프로젝트는 AWS 서버리스 아키텍처 기반의 AI 채팅 애플리케이션 템플릿입니다.

### 핵심 기술 스택

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Python Lambda Functions
- **Infrastructure**: AWS (API Gateway, DynamoDB, Lambda, S3, CloudFront)
- **Authentication**: AWS Cognito
- **AI Engine**: AWS Bedrock (Claude, GPT-4o 지원)

### 주요 기능

- AWS Cognito 기반 인증
- 실시간 WebSocket 채팅
- 다중 AI 엔진 지원
- 프롬프트 관리 및 파일 업로드
- 사용량 추적
- 대화 관리 (생성, 수정, 삭제)

---

## 프로젝트 구조

```
template_1/
├── frontend/                    # 프론트엔드 애플리케이션
│   ├── src/
│   │   ├── components/         # UI 컴포넌트
│   │   ├── contexts/          # React Context (인증, 상태 관리)
│   │   ├── services/          # API 및 WebSocket 서비스
│   │   ├── hooks/             # 커스텀 React Hooks
│   │   └── utils/             # 유틸리티 함수
│   ├── .env                   # 환경 변수 (API 엔드포인트, Cognito 설정)
│   ├── package.json           # 의존성 관리
│   └── vite.config.js         # Vite 빌드 설정
│
├── backend/                     # 백엔드 Lambda 함수
│   ├── handlers/               # Lambda 핸들러
│   │   ├── conversation_handler.py    # 대화 CRUD
│   │   ├── prompt_crud_handler.py     # 프롬프트 CRUD
│   │   ├── usage_handler.py           # 사용량 추적
│   │   ├── websocket_connect.py       # WebSocket 연결
│   │   ├── websocket_disconnect.py    # WebSocket 해제
│   │   └── websocket_message.py       # WebSocket 메시지 (AI 스트리밍)
│   ├── src/                    # 비즈니스 로직
│   ├── lib/                    # 외부 서비스 클라이언트
│   ├── utils/                  # 공통 유틸리티
│   └── requirements.txt        # Python 의존성
│
├── scripts-v2/                  # 배포 스크립트 (핵심)
│   ├── config.sh               # 환경 설정 파일
│   ├── init.sh                 # 초기 설정 스크립트
│   ├── 01-deploy-dynamodb.sh   # DynamoDB 테이블 생성
│   ├── 02-deploy-lambda.sh     # Lambda 함수 생성
│   ├── 03-deploy-api-gateway-final.sh  # API Gateway 배포 (CORS 설정 포함)
│   ├── 04-update-config.sh     # API 엔드포인트 자동 업데이트
│   ├── 05-deploy-lambda-code.sh # Lambda 코드 배포
│   ├── 06-deploy-frontend.sh   # 프론트엔드 배포 (S3 + CloudFront)
│   ├── quick-deploy-backend.sh  # 백엔드 빠른 재배포
│   ├── quick-deploy-frontend.sh # 프론트엔드 빠른 재배포
│   └── README.md               # 배포 스크립트 상세 가이드
│
└── .gitignore                   # Git 제외 파일 설정
```

### 각 디렉토리 역할

#### `frontend/`
- React 기반 SPA (Single Page Application)
- Vite로 빌드하여 S3에 정적 파일로 배포
- CloudFront를 통해 CDN으로 제공
- `.env` 파일에서 API Gateway 엔드포인트 및 Cognito 설정 관리

#### `backend/`
- Python 3.9 기반 Lambda 함수들
- 각 핸들러는 독립적인 Lambda 함수로 배포됨
- DynamoDB와 통신하여 데이터 처리
- AWS Bedrock을 통해 AI 응답 생성

#### `scripts-v2/`
- 전체 인프라 배포 자동화 스크립트
- `config.sh`에서 서비스명, 리전, 카드 번호 등 설정
- 순차적으로 실행하여 전체 인프라 구축
- 빠른 재배포 스크립트로 개발 속도 향상

---

## 배포 워크플로우

### 1. 초기 배포 (전체 인프라 구축)

#### 전제 조건
- AWS CLI 설치 및 인증 완료
- Node.js 및 npm 설치
- Python 3.x 설치
- 적절한 AWS 권한 (Lambda, API Gateway, DynamoDB, S3, CloudFront 등)

#### 배포 순서

**1단계: 초기 설정**
```bash
cd scripts-v2
./init.sh
```
- 서비스 이름, 리전, 카드 번호 입력
- `config.sh` 파일 자동 생성

**2단계: DynamoDB 테이블 생성**
```bash
./01-deploy-dynamodb.sh
```
생성되는 테이블:
- `{SERVICE_NAME}-conversations-{CARD_COUNT}`
- `{SERVICE_NAME}-messages-{CARD_COUNT}`
- `{SERVICE_NAME}-prompts-{CARD_COUNT}`
- `{SERVICE_NAME}-files-{CARD_COUNT}`
- `{SERVICE_NAME}-usage-{CARD_COUNT}`
- `{SERVICE_NAME}-websocket-connections-{CARD_COUNT}`

**3단계: Lambda 함수 생성**
```bash
./02-deploy-lambda.sh
```
생성되는 Lambda 함수:
- `{SERVICE_NAME}-websocket-connect-{CARD_COUNT}`
- `{SERVICE_NAME}-websocket-disconnect-{CARD_COUNT}`
- `{SERVICE_NAME}-websocket-message-{CARD_COUNT}`
- `{SERVICE_NAME}-conversation-api-{CARD_COUNT}`
- `{SERVICE_NAME}-prompt-crud-{CARD_COUNT}`
- `{SERVICE_NAME}-usage-handler-{CARD_COUNT}`

**4단계: API Gateway 배포**
```bash
./03-deploy-api-gateway-final.sh
```
생성 내용:
- **REST API**: 모든 HTTP 엔드포인트
  - `/conversations` (GET, POST, PUT, OPTIONS)
  - `/conversations/{id}` (GET, PATCH, PUT, DELETE, OPTIONS)
  - `/prompts` (GET, POST, OPTIONS)
  - `/prompts/{id}` (GET, POST, PUT, OPTIONS)
  - `/prompts/{id}/files` (GET, POST, OPTIONS)
  - `/prompts/{id}/files/{fileId}` (GET, PUT, DELETE, OPTIONS)
  - `/usage` (GET, POST, OPTIONS)
  - `/admin/*` (GET, PUT, OPTIONS)
- **WebSocket API**: 실시간 통신
  - $connect, $disconnect, $default

**5단계: 설정 업데이트**
```bash
./04-update-config.sh
```
- API Gateway 엔드포인트를 `frontend/.env`에 자동 업데이트

**6단계: Lambda 코드 배포**
```bash
./05-deploy-lambda-code.sh
```
- 백엔드 코드를 Lambda 함수에 배포

**7단계: 프론트엔드 배포**
```bash
./06-deploy-frontend.sh
```
- S3 버킷 생성
- CloudFront 배포
- 프론트엔드 빌드 및 업로드

### 2. 빠른 재배포 (코드 변경 시)

#### 프론트엔드만 업데이트
```bash
cd scripts-v2
./quick-deploy-frontend.sh
```
- 사용 시나리오: UI 수정, 환경변수 변경, 버그 수정
- 소요 시간: 약 1-2분
- 동작: 빌드 → S3 업로드 → CloudFront 캐시 무효화

#### 백엔드만 업데이트
```bash
cd scripts-v2
./quick-deploy-backend.sh
```
- 사용 시나리오: API 로직 수정, Lambda 코드 변경
- 소요 시간: 약 1-2분
- 동작: 배포 패키지 생성 → 모든 Lambda 함수 업데이트

### 3. API Gateway 재배포 (CORS 설정 변경 시)

```bash
cd scripts-v2
# 기존 API Gateway 삭제
aws apigateway delete-rest-api --rest-api-id {API_ID} --region us-east-1

# 재배포
./03-deploy-api-gateway-final.sh
./04-update-config.sh
./quick-deploy-frontend.sh
```

---

## 자주 발생하는 에러

### 1. CORS 에러

**증상**:
```
Access to fetch at '...' has been blocked by CORS policy
Method PATCH is not allowed by Access-Control-Allow-Methods in preflight response
```

**원인**:
- API Gateway에 특정 HTTP 메소드가 없음
- OPTIONS 메소드 설정 누락
- Integration Response의 CORS 헤더 미설정

**해결 방법**:
```bash
cd scripts-v2
# API Gateway 재배포
aws apigateway delete-rest-api --rest-api-id {API_ID} --region us-east-1
./03-deploy-api-gateway-final.sh
./04-update-config.sh
./quick-deploy-frontend.sh
```

**검증**:
```bash
# OPTIONS Preflight 확인
curl -X OPTIONS https://{API_ID}.execute-api.us-east-1.amazonaws.com/prod/conversations/1 -i

# 예상 응답 헤더
# access-control-allow-origin: *
# access-control-allow-methods: GET,POST,PUT,PATCH,DELETE,OPTIONS
# access-control-allow-headers: Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token
```

### 2. 404 Not Found (데이터 없음)

**증상**:
```
PUT https://{API_ID}.execute-api.us-east-1.amazonaws.com/prod/prompts/11 404 (Not Found)
Error: HTTP error! status: 404
```

**원인**: DynamoDB에 해당 리소스가 존재하지 않음 (API Gateway 문제 아님)

**해결 방법**:
```bash
# 예시: Prompt 11 생성
aws dynamodb put-item \
  --table-name {SERVICE_NAME}-prompts-{CARD_COUNT} \
  --item '{
    "promptId": {"S": "11"},
    "userId": {"S": "system"},
    "engineType": {"S": "11"},
    "promptName": {"S": "GPT-4o Prompt"},
    "description": {"S": "GPT-4o 엔진용 프롬프트"},
    "instruction": {"S": "당신은 유능한 AI 어시스턴트입니다."},
    "isPublic": {"BOOL": true},
    "createdAt": {"S": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"},
    "updatedAt": {"S": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}
  }' \
  --region us-east-1
```

### 3. Lambda 권한 오류

**증상**:
```
User is not authorized to perform: lambda:InvokeFunction
```

**원인**: API Gateway가 Lambda를 호출할 권한 없음

**해결 방법**:
```bash
cd scripts-v2
# 스크립트가 자동으로 권한 설정하므로 재실행
./03-deploy-api-gateway-final.sh
```

### 4. Cognito 인증 오류

**증상**:
```
User pool client YOUR_CLIENT_ID does not exist
```

**원인**: `frontend/.env` 파일의 Cognito 설정이 잘못됨

**해결 방법**:
```bash
# 1. AWS Cognito User Pool 및 Client 확인
aws cognito-idp list-user-pools --max-results 20 --region us-east-1
aws cognito-idp list-user-pool-clients --user-pool-id {USER_POOL_ID} --region us-east-1

# 2. frontend/.env 파일 수정
VITE_COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxx
VITE_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxx
VITE_AWS_REGION=us-east-1

# 3. 프론트엔드 재배포
cd scripts-v2
./quick-deploy-frontend.sh
```

### 5. CloudFront 캐시 문제

**증상**: 변경사항이 브라우저에 반영되지 않음

**해결 방법**:
```bash
# 1. CloudFront Distribution ID 확인
CLOUDFRONT_ID=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[?contains(Origins.Items[0].Id, '{SERVICE_NAME}-{CARD_COUNT}-frontend')].Id | [0]" \
  --output text \
  --region us-east-1)

# 2. 수동 캐시 무효화
aws cloudfront create-invalidation \
  --distribution-id $CLOUDFRONT_ID \
  --paths "/*" \
  --region us-east-1
```

### 6. 빌드 캐시 문제

**증상**: 환경변수 변경이 반영되지 않음

**해결 방법**:
```bash
cd frontend
rm -rf dist node_modules/.vite
npm run build
cd ../scripts-v2
./quick-deploy-frontend.sh
```

### 7. DynamoDB 테이블 생성 실패

**증상**:
```
❌ {TABLE_NAME} - 생성 실패
```

**원인**:
- 동일한 테이블명이 이미 존재
- AWS 권한 부족
- 리전 설정 오류

**해결 방법**:
```bash
# 1. 기존 테이블 확인
aws dynamodb list-tables --region us-east-1

# 2. 기존 테이블 삭제 (필요시)
aws dynamodb delete-table --table-name {TABLE_NAME} --region us-east-1

# 3. 스크립트 재실행
cd scripts-v2
./01-deploy-dynamodb.sh
```

---

## 템플릿 작업 가이드

이 섹션은 새로운 서비스를 만들기 위해 템플릿을 커스터마이징하는 작업자를 위한 가이드입니다.

### 1. 서비스 설정 변경

**작업 위치**: `scripts-v2/init.sh` 실행 또는 `scripts-v2/config.sh` 직접 수정

```bash
# config.sh 예시
STACK_NAME="my-service-one"
SERVICE_NAME="myservice"
CARD_COUNT="one"
REGION="us-east-1"
REST_API_NAME="${SERVICE_NAME}-rest-api-${CARD_COUNT}"
WEBSOCKET_API_NAME="${SERVICE_NAME}-websocket-api-${CARD_COUNT}"
S3_BUCKET="${SERVICE_NAME}-${CARD_COUNT}-frontend"
```

**주의사항**:
- `SERVICE_NAME`은 소문자와 하이픈만 사용
- `CARD_COUNT`는 각 서비스 인스턴스를 구분하는 식별자 (one, two, three 등)
- 리전은 Lambda, API Gateway, DynamoDB가 모두 지원하는 리전 선택

### 2. Cognito 설정

**작업 위치**: `frontend/.env`

```bash
VITE_COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxx
VITE_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxx
VITE_AWS_REGION=us-east-1
```

**Cognito 설정 방법**:
1. AWS 콘솔에서 Cognito User Pool 생성
2. App Client 생성 (Client Secret 없이)
3. User Pool ID와 Client ID를 `.env` 파일에 입력

### 3. AI 엔진 커스터마이징

**작업 위치**: `backend/handlers/websocket_message.py`

```python
# 모델 ID 변경
MODEL_CONFIGS = {
    "11": {  # engineType
        "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "max_tokens": 16384,
        "temperature": 0.81
    },
    "12": {
        "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "max_tokens": 8192,
        "temperature": 0.7
    }
}
```

**변경 후 배포**:
```bash
cd scripts-v2
./quick-deploy-backend.sh
```

### 4. 프론트엔드 UI 커스터마이징

**작업 위치**: `frontend/src/components/`

주요 커스터마이징 포인트:
- `frontend/src/App.jsx`: 라우팅 및 레이아웃
- `frontend/src/components/chat/`: 채팅 UI
- `frontend/src/components/settings/`: 설정 페이지
- `frontend/tailwind.config.js`: 테마 색상, 폰트

**변경 후 배포**:
```bash
cd scripts-v2
./quick-deploy-frontend.sh
```

### 5. 프롬프트 초기 데이터 설정

**작업 위치**: DynamoDB 직접 삽입

```bash
# 프롬프트 생성 스크립트 예시
aws dynamodb put-item \
  --table-name {SERVICE_NAME}-prompts-{CARD_COUNT} \
  --item '{
    "promptId": {"S": "11"},
    "userId": {"S": "system"},
    "engineType": {"S": "11"},
    "promptName": {"S": "기본 프롬프트"},
    "description": {"S": "서비스 기본 프롬프트"},
    "instruction": {"S": "당신은 유능한 AI 어시스턴트입니다. 사용자의 질문에 정확하고 친절하게 답변하세요."},
    "isPublic": {"BOOL": true},
    "createdAt": {"S": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"},
    "updatedAt": {"S": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}
  }' \
  --region us-east-1
```

### 6. API 엔드포인트 추가/수정

**작업 위치**: `scripts-v2/03-deploy-api-gateway-final.sh`

새로운 리소스 추가 예시:
```bash
# 1. 리소스 생성
ANALYTICS_ID=$(aws apigateway create-resource \
  --rest-api-id $REST_API_ID \
  --parent-id $ROOT_ID \
  --path-part "analytics" \
  --region $REGION \
  --query 'id' \
  --output text)

# 2. 메소드 추가
create_lambda_method $ANALYTICS_ID "GET" $LAMBDA_ANALYTICS "/analytics"
create_options_method $ANALYTICS_ID

# 3. Lambda 권한 부여
aws lambda add-permission \
  --function-name $LAMBDA_ANALYTICS \
  --statement-id apigateway-analytics-get \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${REST_API_ID}/*/*/*" \
  --region $REGION
```

### 7. 환경변수 관리

**프론트엔드 환경변수** (`frontend/.env`):
- `VITE_` 접두사 필수
- 빌드 시점에 코드에 포함됨
- 민감 정보 포함 금지

**백엔드 환경변수** (Lambda 환경변수):
- `scripts-v2/02-deploy-lambda.sh`에서 설정
- 런타임에 Lambda 함수에서 접근 가능

```bash
# Lambda 환경변수 설정 예시 (02-deploy-lambda.sh 내부)
--environment "Variables={
  CONVERSATIONS_TABLE=${CONVERSATIONS_TABLE},
  PROMPTS_TABLE=${PROMPTS_TABLE},
  BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
}"
```

### 8. 배포 전 체크리스트

**초기 배포 시**:
- [ ] `scripts-v2/config.sh` 설정 완료
- [ ] AWS 자격 증명 설정 완료 (`aws configure`)
- [ ] Cognito User Pool 생성 및 `.env` 설정
- [ ] 필요한 권한 확인 (Lambda, API Gateway, DynamoDB, S3, CloudFront)

**코드 변경 후 재배포 시**:
- [ ] 프론트엔드 변경: `quick-deploy-frontend.sh` 실행
- [ ] 백엔드 변경: `quick-deploy-backend.sh` 실행
- [ ] API Gateway 변경: `03-deploy-api-gateway-final.sh` → `04-update-config.sh` → `quick-deploy-frontend.sh`

**배포 후 검증**:
- [ ] API Gateway 엔드포인트 접근 확인
- [ ] CORS 헤더 확인 (`curl -X OPTIONS ...`)
- [ ] Cognito 로그인 테스트
- [ ] WebSocket 연결 테스트
- [ ] 프롬프트 데이터 존재 확인

---

## 환경 설정

### AWS CLI 설정

```bash
# AWS CLI 설치 (macOS)
brew install awscli

# AWS CLI 설치 (Linux)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# 자격 증명 설정
aws configure
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region name: us-east-1
# Default output format: json
```

### Node.js 설정

```bash
# Node.js 설치 (macOS)
brew install node

# Node.js 설치 (Linux)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 버전 확인
node --version  # v18 이상 권장
npm --version
```

### Python 설정

```bash
# Python 설치 (macOS)
brew install python@3.9

# Python 설치 (Linux)
sudo apt-get update
sudo apt-get install python3.9

# 버전 확인
python3 --version  # 3.9 이상 필요
```

### 프로젝트 의존성 설치

```bash
# 프론트엔드
cd frontend
npm install

# 백엔드
cd ../backend
pip install -r requirements.txt
```

---

## 참고 자료

### 배포 관련 문서
- `scripts-v2/README.md`: 배포 스크립트 상세 가이드
- `/tmp/api-gateway-setup-summary.md`: API Gateway 설정 완료 요약

### AWS 서비스 문서
- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [Amazon API Gateway](https://docs.aws.amazon.com/apigateway/)
- [Amazon DynamoDB](https://docs.aws.amazon.com/dynamodb/)
- [AWS Cognito](https://docs.aws.amazon.com/cognito/)
- [AWS Bedrock](https://docs.aws.amazon.com/bedrock/)

### 문제 해결
- CORS 에러 → `scripts-v2/03-deploy-api-gateway-final.sh` 재실행
- 환경변수 미반영 → `frontend/dist` 및 `.vite` 캐시 삭제 후 재빌드
- Lambda 권한 오류 → IAM 역할 및 실행 정책 확인

---

**프로젝트 버전**: 2.0
**최종 업데이트**: 2025-10-13
**템플릿 유지보수**: Backend Team
