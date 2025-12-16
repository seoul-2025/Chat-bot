# AWS Stack Documentation for W1.SEDAILY.AI

## 📊 Current Stack Status (2025-12-14)

### Active Service: W1.SEDAILY.AI
- **Service Prefix**: w1
- **Domain**: w1.sedaily.ai
- **Region**: us-east-1
- **Status**: ✅ Production Active

---

## 🏗️ Infrastructure Architecture

### 1. Domain & Networking
```
w1.sedaily.ai → CloudFront (d9am5o27m55dc) → S3 Bucket (w1-sedaily-frontend-bucket)
api.w1.sedaily.ai → API Gateway REST (16ayefk5lc)
ws.w1.sedaily.ai → API Gateway WebSocket (prsebeg7ub)
```

### 2. API Gateway Configuration
```
REST API:
  ID: 16ayefk5lc
  Endpoint: https://16ayefk5lc.execute-api.us-east-1.amazonaws.com/prod
  
WebSocket API:
  ID: prsebeg7ub  
  Endpoint: wss://prsebeg7ub.execute-api.us-east-1.amazonaws.com/prod
```

### 3. Lambda Functions (6개)
```
w1-websocket-message      → WebSocket 메시지 처리 + 웹 검색 기능
w1-websocket-connect      → WebSocket 연결 처리  
w1-websocket-disconnect   → WebSocket 연결 해제
w1-conversation-api       → 대화 CRUD API
w1-usage-handler         → 사용량 추적
w1-prompt-crud           → 프롬프트 관리
```

### 4. DynamoDB Tables (5개)
```
w1-conversations         → 대화 세션 저장
w1-messages             → 개별 메시지 저장  
w1-prompts              → 시스템 프롬프트 관리
w1-usage                → 사용량 통계
w1-connections          → WebSocket 연결 관리
```

### 5. Security & Storage
```
Secrets Manager:
  - Secret Name: bodo-v1 (Anthropic API Key 저장)
  
IAM Role:
  - w1-lambda-execution-role
  
S3 Bucket:
  - w1-sedaily-frontend-bucket (React 앱 호스팅)
  
CloudFront:
  - Distribution ID: d9am5o27m55dc
```

---

## 🚀 Deployment Configuration

### Current Environment Variables
```bash
# API Configuration
USE_ANTHROPIC_API=true
ANTHROPIC_SECRET_NAME=bodo-v1
ANTHROPIC_MODEL_ID=claude-opus-4-5-20251101
AI_PROVIDER=anthropic_api

# Model Settings
MAX_TOKENS=4096
TEMPERATURE=0.3

# Feature Flags
ENABLE_NATIVE_WEB_SEARCH=true
USE_OPUS_MODEL=true
FALLBACK_TO_BEDROCK=true
```

### Web Search Implementation (NEW)
- **Tool**: web_search_20250305 (Anthropic Native)
- **Engine**: Brave Search
- **Max Uses**: 5 per request
- **Citation**: Automatic URL formatting with trust icons
- **Activation**: Automatically enabled for all requests

---

## 📂 File Structure

### Safe Scripts (b1(bodo)/w1-scripts/)
```
deploy-backend.sh       → Lambda 코드 배포
deploy-frontend.sh      → React 앱 S3 배포
config.sh              → 환경 설정
monitor-logs.sh         → CloudWatch 로그 모니터링
test-service.sh         → 전체 서비스 테스트
```

### Upgrade Scripts (b1(bodo)/upgrade-scripts/)
```
upgrade-deploy-w1-complete.sh     → 전체 서비스 배포
upgrade-deploy-lambda-improved.sh → Lambda 향상된 배포
upgrade-deploy-w1-frontend.sh     → 프론트엔드 전용 배포
```

---

## ⚠️ Important Notes

### 1. Security
- **절대 금지**: f1, p2, g2 등 다른 서비스 리소스 수정
- **안전한 접두사**: w1-* 만 사용
- **API Key**: Secrets Manager에서만 관리

### 2. Deployment
- **주 스크립트**: w1-scripts/deploy-backend.sh
- **환경변수**: config.sh에서 관리
- **테스트 필수**: test-service.sh로 검증

### 3. Monitoring
- **로그**: monitor-logs.sh 사용
- **에러 추적**: CloudWatch 로그 그룹
- **성능**: Lambda 메트릭 모니터링

---

## 🔄 Deployment History

### 2025-12-14: Web Search Feature
- Added Anthropic web_search_20250305 tool
- Implemented citation formatting
- Enhanced date handling
- All Lambda functions updated

### Previous Deployments
- 2024-11: Claude 4.5 Opus migration
- 2024-10: Initial w1 service setup
- 2024-09: Infrastructure provisioning

---

## 📞 Emergency Contacts

### AWS Resources
- Account ID: 887078546492
- Region: us-east-1
- Service: w1.sedaily.ai

### Key Commands
```bash
# Quick deploy
cd b1(bodo)/w1-scripts && ./deploy-backend.sh

# Check logs
./monitor-logs.sh websocket

# Test all
./test-service.sh
```