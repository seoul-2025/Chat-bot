# AWS Infrastructure Documentation - NX-WT-PRF Proofreading Service

## 📅 Last Updated: 2024-12-15

## 🏗️ Infrastructure Version: Production v3.1

---

## 🎯 Overview

이 문서는 서울경제신문 AI 교열 서비스(nx-wt-prf)의 AWS 인프라 구성을 상세히 문서화합니다.

### Service Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   CloudFront    │────▶│  S3 Bucket   │     │  API Gateway   │
│  (CDN)          │     │  (Frontend)  │     │  (WebSocket)   │
└─────────────────┘     └──────────────┘     └────────┬────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │  Lambda Functions│
                                              └────────┬────────┘
                                                       │
                                    ┌──────────────────┼──────────────────┐
                                    ▼                  ▼                  ▼
                            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
                            │  DynamoDB    │  │  Bedrock AI  │  │Anthropic API │
                            │  (Database)  │  │  (Fallback)  │  │(Primary AI)  │
                            └──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🔧 AWS Stack Components

### 1. Lambda Functions (19 Total)

#### Production Environment

| Function Name                    | Runtime     | Handler                               | Purpose                             | Memory | Timeout |
| -------------------------------- | ----------- | ------------------------------------- | ----------------------------------- | ------ | ------- |
| `nx-wt-prf-websocket-message`    | Python 3.11 | handlers.websocket.message.handler    | WebSocket 메시지 처리, AI 응답 생성 | 512MB  | 300s    |
| `nx-wt-prf-conversation-api`     | Python 3.11 | handlers.api.conversation.handler     | 대화 이력 관리 REST API             | 256MB  | 30s     |
| `nx-wt-prf-prompt-crud`          | Python 3.11 | handlers.api.prompt.handler           | 프롬프트 CRUD 작업                  | 256MB  | 30s     |
| `nx-wt-prf-usage-handler`        | Python 3.11 | handlers.api.usage.handler            | 사용량 추적 및 분석                 | 256MB  | 30s     |
| `nx-wt-prf-websocket-connect`    | Python 3.11 | handlers.websocket.connect.handler    | WebSocket 연결 처리                 | 128MB  | 30s     |
| `nx-wt-prf-websocket-disconnect` | Python 3.11 | handlers.websocket.disconnect.handler | WebSocket 연결 해제 처리            | 128MB  | 30s     |

#### Development Environments (v1 & v2)

- 각 환경별로 동일한 함수들이 `dev-v1`, `dev-v2` suffix와 함께 존재
- v1: Python 3.9 기반 (레거시)
- v2: Python 3.11 기반 (최신 기능 테스트)

### 2. DynamoDB Tables (20 Total)

#### Production Tables

| Table Name                        | Purpose              | Partition Key    | Sort Key                 | GSIs             |
| --------------------------------- | -------------------- | ---------------- | ------------------------ | ---------------- |
| `nx-wt-prf-conversations`         | 대화 이력 저장       | userId (S)       | conversationId (S)       | engineType-index |
| `nx-wt-prf-prompts`               | 시스템 프롬프트 관리 | id (S)           | -                        | -                |
| `nx-wt-prf-files`                 | 프롬프트 첨부 파일   | promptId (S)     | fileId (S)               | -                |
| `nx-wt-prf-usage`                 | 사용량 통계          | userId (S)       | yearMonth (S)            | -                |
| `nx-wt-prf-usage-tracking`        | 상세 사용 추적       | userId (S)       | usageDate#engineType (S) | -                |
| `nx-wt-prf-websocket-connections` | WebSocket 연결 관리  | connectionId (S) | -                        | -                |

### 3. API Gateway

#### REST APIs

| API Name                    | ID         | Endpoint                                               | Stage |
| --------------------------- | ---------- | ------------------------------------------------------ | ----- |
| `nx-wt-prf-api`             | wxwdb89w4m | https://wxwdb89w4m.execute-api.us-east-1.amazonaws.com | prod  |
| `nx-wt-prf-dev-v1-rest-api` | alxunm6tjc | https://alxunm6tjc.execute-api.us-east-1.amazonaws.com | dev   |
| `nx-wt-prf-dev-v2-rest-api` | 9tdv3tgpw5 | https://9tdv3tgpw5.execute-api.us-east-1.amazonaws.com | dev   |

#### WebSocket APIs

| API Name                         | ID         | Endpoint                                                  | Protocol  |
| -------------------------------- | ---------- | --------------------------------------------------------- | --------- |
| `nx-wt-prf-websocket-api`        | p062xh167h | wss://p062xh167h.execute-api.us-east-1.amazonaws.com/prod | WebSocket |
| `nx-wt-prf-dev-v1-websocket-api` | bqahvt0b22 | wss://bqahvt0b22.execute-api.us-east-1.amazonaws.com/dev  | WebSocket |
| `nx-wt-prf-dev-v2-websocket-api` | gisc7k1xag | wss://gisc7k1xag.execute-api.us-east-1.amazonaws.com/dev  | WebSocket |

### 4. S3 Buckets

| Bucket Name                     | Purpose              | Public Access                | Website Hosting |
| ------------------------------- | -------------------- | ---------------------------- | --------------- |
| `nx-wt-prf-frontend-prod`       | Production Frontend  | Restricted (CloudFront Only) | Enabled         |
| `nx-wt-prf-dev-ver2.sedaily.io` | Development Frontend | Restricted (CloudFront Only) | Enabled         |

### 5. CloudFront Distributions

| Distribution ID  | Domain Name                   | Origin                        | Comment                         |
| ---------------- | ----------------------------- | ----------------------------- | ------------------------------- |
| `E3E25OIRRG1ZR`  | d1ykmbuznjkj67.cloudfront.net | nx-wt-prf-frontend-prod       | Production Frontend             |
| `E3JAN9KZBNLM0O` | d1sp4xqbbrd61c.cloudfront.net | nx-wt-prf-dev-ver2.sedaily.io | Development Frontend            |
| `EY5UC9JRSD6RF`  | d3f2g4sqr31hs5.cloudfront.net | nx-wt-prf-frontend-prod       | Production Frontend (Secondary) |

### 6. Secrets Manager

| Secret Name            | Description                        | Usage                  |
| ---------------------- | ---------------------------------- | ---------------------- |
| `proof-v1`             | Anthropic API Key for Proofreading | Production AI Service  |
| `anthropic-api-key`    | General Anthropic API Key          | Development/Testing    |
| `q1-anthropic-api-key` | Q1 Service Anthropic API Key       | Q1 Service Integration |

---

## 🔐 IAM Roles and Policies

### Lambda Execution Role

- **Role Name**: `lambda-execution-role`
- **Attached Policies**:
  - `AWSLambdaBasicExecutionRole` - CloudWatch Logs
  - `AmazonAPIGatewayInvokeFullAccess` - API Gateway
  - `AmazonDynamoDBFullAccess` - DynamoDB
  - `AmazonS3FullAccess` - S3
  - `AmazonBedrockFullAccess` - Bedrock AI
  - `ProofreadingSecretsAccess` (Custom) - Secrets Manager for proof-v1

### Custom Policy: ProofreadingSecretsAccess

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "arn:aws:secretsmanager:us-east-1:887078546492:secret:proof-v1*"
    }
  ]
}
```

---

## 🚀 Environment Variables

### Lambda Environment Configuration

```json
{
  "USE_ANTHROPIC_API": "true",
  "ANTHROPIC_SECRET_NAME": "proof-v1",
  "ANTHROPIC_MODEL_ID": "claude-opus-4-5-20251101",
  "AI_PROVIDER": "anthropic_api",
  "FALLBACK_TO_BEDROCK": "true",
  "ENABLE_NATIVE_WEB_SEARCH": "true",
  "WEB_SEARCH_MAX_USES": "5",
  "ANTHROPIC_MAX_TOKENS": "4096",
  "ANTHROPIC_TEMPERATURE": "0.7"
}
```

---

## 🌐 Network Configuration

### Region

- **Primary Region**: us-east-1 (N. Virginia)
- **Reason**: Best performance for global access, all AWS services available

### Security Groups

- WebSocket connections allowed from all IPs (0.0.0.0/0)
- Lambda functions in default VPC
- DynamoDB accessed via AWS internal network

---

## 📊 Monitoring and Logging

### CloudWatch Log Groups

| Log Group                                 | Retention | Purpose                           |
| ----------------------------------------- | --------- | --------------------------------- |
| `/aws/lambda/nx-wt-prf-websocket-message` | 7 days    | WebSocket message processing logs |
| `/aws/lambda/nx-wt-prf-conversation-api`  | 7 days    | Conversation API logs             |
| `/aws/lambda/nx-wt-prf-prompt-crud`       | 7 days    | Prompt management logs            |
| `/aws/lambda/nx-wt-prf-usage-handler`     | 7 days    | Usage tracking logs               |

### Key Metrics to Monitor

- Lambda invocation count and errors
- DynamoDB read/write capacity consumption
- API Gateway 4xx/5xx errors
- WebSocket connection count
- Anthropic API success/failure rate

---

## 🔄 CI/CD Pipeline

### Current Deployment Process

1. **Code Update**: Local development and testing
2. **Package Creation**: `deploy-anthropic.sh` script
3. **Lambda Update**: AWS CLI commands
4. **Environment Update**: Configuration via AWS CLI
5. **Validation**: CloudWatch logs monitoring

### Deployment Scripts

- `deploy-anthropic.sh` - Deploy Lambda with Anthropic integration
- `deploy-frontend.sh` - Deploy frontend to S3/CloudFront
- `deploy.sh` - Legacy deployment script

---

## 💰 Cost Optimization

### Current Optimizations

1. **Lambda**:
   - Memory optimized per function (128MB-512MB)
   - Timeout settings appropriate to function
2. **DynamoDB**:
   - On-demand billing mode
   - No reserved capacity
3. **S3**:
   - CloudFront caching reduces S3 requests
4. **API Gateway**:
   - WebSocket for real-time communication (cost-effective)

### Cost Breakdown (Estimated Monthly)

- Lambda: ~$50-100 (based on usage)
- DynamoDB: ~$20-50 (on-demand)
- S3 & CloudFront: ~$10-20
- API Gateway: ~$10-30
- Secrets Manager: ~$1
- **Total**: ~$91-201/month

---

## 🚨 Disaster Recovery

### Backup Strategy

- **DynamoDB**: Point-in-time recovery enabled
- **Code**: Version controlled in Git
- **Secrets**: Manual backup recommended

### Recovery Time Objectives

- **RTO**: < 1 hour
- **RPO**: < 24 hours

---

## 📝 Maintenance Notes

### Regular Tasks

1. **Weekly**: Check CloudWatch logs for errors
2. **Monthly**: Review usage statistics and costs
3. **Quarterly**: Update dependencies and Lambda runtime
4. **Yearly**: Security audit and credential rotation

### Known Issues

1. Secrets Manager permissions need manual setup for new Lambda functions
2. WebSocket connections may timeout after 10 minutes of inactivity
3. Anthropic API fallback to Bedrock when rate limits hit

---

## 📞 Support Contacts

- **AWS Account ID**: 887078546492
- **Service Owner**: 서울경제신문 디지털뉴스팀
- **Technical Lead**: [Contact Information]
- **AWS Support Tier**: [Support Level]

---

## 🔄 Version History

| Date       | Version | Changes                               | Author           |
| ---------- | ------- | ------------------------------------- | ---------------- |
| 2024-12-15 | 1.0     | Initial documentation                 | AI Assistant     |
| 2024-12-14 | -       | Web search feature added              | Development Team |
| 2024-11-01 | -       | Anthropic Claude 4.5 Opus integration | Development Team |

---

## 📚 Related Documents

- [DEPLOYMENT_MANUAL.md](./backend/DEPLOYMENT_MANUAL.md) - Detailed deployment instructions
- [MAINTENANCE_GUIDE.md](./MAINTENANCE_GUIDE.md) - Maintenance procedures
- [README.md](./README.md) - Project overview
- [PROMPT_CACHING_IMPLEMENTATION.md](./PROMPT_CACHING_IMPLEMENTATION.md) - Caching strategy

---

_End of Document_
