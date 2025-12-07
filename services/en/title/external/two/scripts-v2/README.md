# Demo-Two 배포 스크립트 가이드

## 📋 목차
1. [초기 배포](#초기-배포)
2. [빠른 재배포](#빠른-재배포)
3. [스크립트 설명](#스크립트-설명)
4. [문제 해결](#문제-해결)

---

## 🚀 초기 배포

### 전제 조건
- AWS CLI 설치 및 인증 완료
- Node.js 및 npm 설치
- Python 3.x 설치
- 적절한 AWS 권한 (Lambda, API Gateway, DynamoDB, S3, CloudFront 등)

### 배포 순서

#### 1단계: 초기 설정
```bash
./init.sh
```
- 서비스 이름, 리전, 카드 번호 등 설정
- `config.sh` 파일 생성

#### 2단계: DynamoDB 테이블 생성
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

#### 3단계: Lambda 함수 생성
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

#### 4단계: API Gateway 배포
```bash
./03-deploy-api-gateway-final.sh
```
생성 내용:
- **REST API**: 모든 HTTP 엔드포인트
  - `/conversations` (GET, POST, PUT, OPTIONS)
  - `/conversations/{id}` (GET, **PATCH**, PUT, DELETE, OPTIONS) ⭐
  - `/prompts` (GET, POST, OPTIONS)
  - `/prompts/{id}` (GET, POST, PUT, OPTIONS)
  - `/prompts/{id}/files` (GET, POST, OPTIONS)
  - `/prompts/{id}/files/{fileId}` (GET, PUT, DELETE, OPTIONS)
  - `/usage` (GET, POST, OPTIONS)
  - `/admin/*` (GET, PUT, OPTIONS)
- **WebSocket API**: 실시간 통신
  - $connect, $disconnect, $default

**주요 특징:**
- ✅ PATCH 메소드 지원 (대화 제목 수정용)
- ✅ 500 에러 CORS 지원
- ✅ OPTIONS Preflight 완벽 지원
- ✅ AWS_PROXY Integration
- ✅ tenant, transcribe 제외 (불필요)

배포 완료 시 출력:
```
REST API Endpoint:
  https://{API_ID}.execute-api.us-east-1.amazonaws.com/prod

WebSocket API Endpoint:
  wss://{WS_API_ID}.execute-api.us-east-1.amazonaws.com/prod
```

#### 5단계: 설정 업데이트
```bash
./04-update-config.sh
```
- API Gateway 엔드포인트를 `frontend/.env`에 자동 업데이트

#### 6단계: Lambda 코드 배포
```bash
./05-deploy-lambda-code.sh
```
- 백엔드 코드를 Lambda 함수에 배포

#### 7단계: 프론트엔드 배포
```bash
./06-deploy-frontend.sh
```
- S3 버킷 생성
- CloudFront 배포
- 프론트엔드 빌드 및 업로드

**배포 완료!** 🎉

---

## ⚡ 빠른 재배포

### 프론트엔드만 업데이트 (환경변수 변경, UI 수정 등)
```bash
./quick-deploy-frontend.sh
```
- 빌드 → S3 업로드 → CloudFront 캐시 무효화
- 약 1-2분 소요

### 백엔드만 업데이트 (Lambda 코드 수정)
```bash
./quick-deploy-backend.sh
```
- 배포 패키지 생성 → 모든 Lambda 함수 업데이트
- 약 1-2분 소요

---

## 📚 스크립트 설명

### `init.sh`
- 초기 설정 생성
- `config.sh` 파일 생성

### `config.sh`
모든 스크립트에서 사용하는 환경 변수:
```bash
STACK_NAME="demo-two"
SERVICE_NAME="demo"
CARD_COUNT="two"
REGION="us-east-1"
REST_API_NAME="${SERVICE_NAME}-rest-api-${CARD_COUNT}"
WEBSOCKET_API_NAME="${SERVICE_NAME}-websocket-api-${CARD_COUNT}"
S3_BUCKET="${SERVICE_NAME}-${CARD_COUNT}-frontend"
```

### `01-deploy-dynamodb.sh`
- 6개 DynamoDB 테이블 생성
- GSI (Global Secondary Index) 설정
- TTL 설정 (WebSocket connections)

### `02-deploy-lambda.sh`
- Lambda 실행 역할 생성
- 6개 Lambda 함수 생성
- 환경 변수 설정
- VPC 설정 (필요시)

### `03-deploy-api-gateway-final.sh` ⭐ 중요
**최종 수정 버전** - CORS 및 PATCH 완벽 지원

주요 함수:
```bash
create_lambda_method()  # Lambda 메소드 생성 (GET, POST, PUT, PATCH, DELETE)
create_options_method() # OPTIONS 메소드 생성 (Preflight)
```

CORS 설정:
- **Method Response**: 200, 500 상태 코드
- **Integration Response**: CORS 헤더 설정
  - `Access-Control-Allow-Origin: *`
  - `Access-Control-Allow-Methods: GET,POST,PUT,PATCH,DELETE,OPTIONS`
  - `Access-Control-Allow-Headers: Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
  - `Access-Control-Allow-Credentials: true`

### `04-update-config.sh`
- API Gateway 엔드포인트 조회
- `frontend/.env` 파일 업데이트

### `05-deploy-lambda-code.sh`
- 백엔드 의존성 설치
- 배포 패키지 생성
- Lambda 함수 코드 업데이트

### `06-deploy-frontend.sh`
- S3 버킷 생성 (없으면)
- CloudFront 배포 생성
- 프론트엔드 빌드
- S3 업로드
- CloudFront 캐시 무효화

### `quick-deploy-frontend.sh`
- 기존 인프라 사용
- 빌드 → S3 업로드 → 캐시 무효화만 수행
- **언제 사용**: UI 수정, 환경변수 변경, 버그 수정 등

### `quick-deploy-backend.sh`
- 기존 Lambda 함수 사용
- 코드 업데이트만 수행
- **언제 사용**: API 로직 수정, 버그 수정 등

---

## 🔧 문제 해결

### 1. CORS 오류
```
Access to fetch at '...' has been blocked by CORS policy
```

**원인**: API Gateway에 PATCH 메소드가 없거나 OPTIONS 설정 누락

**해결**:
```bash
# API Gateway 재배포
aws apigateway delete-rest-api --rest-api-id {API_ID} --region us-east-1
./03-deploy-api-gateway-final.sh
./04-update-config.sh
./quick-deploy-frontend.sh
```

### 2. 404 Not Found (프롬프트)
```
Error: HTTP error! status: 404
```

**원인**: DynamoDB에 프롬프트 데이터 없음

**해결**:
```bash
# 프롬프트 11 생성
aws dynamodb put-item \
  --table-name demo-prompts-two \
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
```
User is not authorized to perform: lambda:InvokeFunction
```

**원인**: API Gateway가 Lambda를 호출할 권한 없음

**해결**:
```bash
# 스크립트가 자동으로 권한 설정하므로 재실행
./03-deploy-api-gateway-final.sh
```

### 4. CloudFront 캐시 문제
```
변경사항이 반영되지 않음
```

**해결**:
```bash
# 수동 캐시 무효화
CLOUDFRONT_ID=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[?contains(Origins.Items[0].Id, 'demo-two-frontend')].Id | [0]" \
  --output text \
  --region us-east-1)

aws cloudfront create-invalidation \
  --distribution-id $CLOUDFRONT_ID \
  --paths "/*" \
  --region us-east-1
```

### 5. 빌드 캐시 문제
```
환경변수가 반영되지 않음
```

**해결**:
```bash
cd ../frontend
rm -rf dist node_modules/.vite
npm run build
cd ../scripts-v2
./quick-deploy-frontend.sh
```

---

## 📊 검증 방법

### API Gateway 테스트
```bash
# OPTIONS (Preflight)
curl -X OPTIONS https://{API_ID}.execute-api.us-east-1.amazonaws.com/prod/prompts/11 -v

# GET
curl https://{API_ID}.execute-api.us-east-1.amazonaws.com/prod/prompts/11

# PUT
curl -X PUT https://{API_ID}.execute-api.us-east-1.amazonaws.com/prod/prompts/11 \
  -H "Content-Type: application/json" \
  -d '{"description":"test"}'
```

### CORS 헤더 확인
```bash
curl -X OPTIONS https://{API_ID}.execute-api.us-east-1.amazonaws.com/prod/prompts/11 \
  -i | grep -i "access-control"
```

예상 출력:
```
access-control-allow-origin: *
access-control-allow-methods: GET,POST,PUT,PATCH,DELETE,OPTIONS
access-control-allow-headers: Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token
access-control-allow-credentials: true
```

---

## 🎯 베스트 프랙티스

### 1. 개발 워크플로우
```bash
# 코드 수정 후
./quick-deploy-backend.sh   # 백엔드 수정 시
./quick-deploy-frontend.sh  # 프론트엔드 수정 시
```

### 2. 전체 재배포 (인프라 변경 시)
```bash
# API Gateway 재배포 필요 시
./03-deploy-api-gateway-final.sh
./04-update-config.sh
./quick-deploy-frontend.sh
```

### 3. 환경변수 변경 시
```bash
# frontend/.env 수정 후
./quick-deploy-frontend.sh
```

### 4. 백업
```bash
# 중요: 배포 전 현재 API ID 백업
echo "Current REST API: $(aws apigateway get-rest-apis --query 'items[?name==`demo-rest-api-two`].id' --output text)"
```

---

## 📁 파일 구조

```
scripts-v2/
├── README.md                      # 이 파일
├── config.sh                      # 환경 변수
├── init.sh                        # 초기 설정
├── 01-deploy-dynamodb.sh         # DynamoDB 배포
├── 02-deploy-lambda.sh           # Lambda 생성
├── 03-deploy-api-gateway-final.sh # API Gateway 배포 ⭐
├── 04-update-config.sh           # 설정 업데이트
├── 05-deploy-lambda-code.sh      # Lambda 코드 배포
├── 06-deploy-frontend.sh         # 프론트엔드 배포
├── quick-deploy-backend.sh       # 백엔드 빠른 재배포
└── quick-deploy-frontend.sh      # 프론트엔드 빠른 재배포
```

---

## 🔗 참고

- **현재 배포 정보**: `deployment-info.txt` 참조
- **API 스펙**: `{SERVICE_NAME}-api-spec-final.json`
- **프론트엔드 환경변수**: `../frontend/.env`

---

## 📝 변경 이력

### v2.0 (2025-10-13)
- ✅ PATCH 메소드 추가 (`/conversations/{id}`)
- ✅ 500 에러 CORS 지원
- ✅ tenant, transcribe 리소스 제거
- ✅ 우수사례 (b1-rest-api) 반영

### v1.0 (2025-09-24)
- 초기 배포 스크립트
