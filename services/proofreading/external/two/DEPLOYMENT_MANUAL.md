# 📚 Unified Deployment Manual - NX-WT-PRF Service

## 📅 Last Updated: 2024-12-15
## 🎯 Purpose: 통합 배포 매뉴얼 (Backend + Frontend + Infrastructure)

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Backend Deployment](#backend-deployment)
3. [Frontend Deployment](#frontend-deployment)
4. [Infrastructure Setup](#infrastructure-setup)
5. [Quick Reference](#quick-reference)

---

## Overview

NX-WT-PRF 서비스는 서울경제신문의 AI 기반 교열 서비스입니다. 
이 문서는 전체 시스템의 배포 과정을 통합하여 설명합니다.

### Architecture
- **Backend**: Python 3.11 Lambda Functions + WebSocket/REST APIs
- **Frontend**: React 18 + Vite + TailwindCSS
- **Infrastructure**: AWS (Lambda, DynamoDB, API Gateway, S3, CloudFront)
- **AI Services**: Anthropic Claude 4.5 Opus (Primary) + AWS Bedrock (Fallback)

---

## Backend Deployment

### Prerequisites
- Python 3.11+
- AWS CLI configured
- Proper IAM permissions

### Quick Deploy
```bash
# Navigate to project root
cd /Users/yeong-gwang/nexus/services/proofreading/external/two

# Deploy with Anthropic integration
./deploy-anthropic.sh
```

### Manual Deployment Steps

#### 1. Package Dependencies
```bash
cd backend
pip install -r requirements.txt -t package/
```

#### 2. Copy Source Code
```bash
cp -r handlers lib services utils src package/
```

#### 3. Create Deployment Package
```bash
cd package
zip -r ../lambda-deployment.zip . -q
cd ..
```

#### 4. Update Lambda Functions
```bash
# List of Lambda functions
FUNCTIONS=(
    "nx-wt-prf-websocket-message"
    "nx-wt-prf-conversation-api"
    "nx-wt-prf-prompt-crud"
    "nx-wt-prf-usage-handler"
    "nx-wt-prf-websocket-connect"
    "nx-wt-prf-websocket-disconnect"
)

# Update each function
for func in "${FUNCTIONS[@]}"; do
    aws lambda update-function-code \
        --function-name $func \
        --zip-file fileb://lambda-deployment.zip \
        --region us-east-1
done
```

#### 5. Update Environment Variables
```bash
aws lambda update-function-configuration \
    --function-name nx-wt-prf-websocket-message \
    --environment Variables='{
        "USE_ANTHROPIC_API":"true",
        "ANTHROPIC_SECRET_NAME":"proof-v1",
        "ENABLE_NATIVE_WEB_SEARCH":"true",
        "WEB_SEARCH_MAX_USES":"5"
    }' \
    --region us-east-1
```

### Backend Structure
```
backend/
├── handlers/           # Lambda entry points
│   ├── api/           # REST API handlers
│   └── websocket/     # WebSocket handlers
├── lib/               # External integrations
│   ├── anthropic_client.py
│   ├── bedrock_client_enhanced.py
│   └── citation_formatter.py
├── services/          # Business logic
├── src/               # Core application code
│   ├── models/
│   ├── repositories/
│   └── services/
└── utils/             # Utilities
```

---

## Frontend Deployment

### Prerequisites
- Node.js 18+
- npm or yarn
- S3 bucket configured for static hosting
- CloudFront distribution

### Quick Deploy
```bash
# Deploy frontend
./deploy-frontend.sh
```

### Manual Deployment Steps

#### 1. Install Dependencies
```bash
cd frontend
npm install
```

#### 2. Build Production Bundle
```bash
npm run build
# Output: dist/ directory
```

#### 3. Upload to S3
```bash
# Production
aws s3 sync dist/ s3://nx-wt-prf-frontend-prod/ \
    --delete \
    --cache-control "public, max-age=31536000" \
    --exclude "index.html" \
    --exclude "*.json"

# Upload index.html with no-cache
aws s3 cp dist/index.html s3://nx-wt-prf-frontend-prod/ \
    --cache-control "no-cache, no-store, must-revalidate"
```

#### 4. Invalidate CloudFront
```bash
# Get distribution ID
DIST_ID="E3E25OIRRG1ZR"  # Production

# Create invalidation
aws cloudfront create-invalidation \
    --distribution-id $DIST_ID \
    --paths "/*"
```

### Frontend Structure
```
frontend/
├── src/
│   ├── features/      # Feature modules
│   │   ├── auth/
│   │   ├── chat/      # WebSocket chat UI
│   │   ├── dashboard/
│   │   └── landing/
│   ├── shared/        # Shared components
│   └── config.js      # Configuration
├── public/            # Static assets
└── dist/              # Build output
```

---

## Infrastructure Setup

### Initial Setup (One-time)

#### 1. DynamoDB Tables
```bash
# Run setup script
cd backend/scripts
./01-setup-dynamodb.sh
```

Tables Created:
- `nx-wt-prf-conversations`
- `nx-wt-prf-prompts`
- `nx-wt-prf-files`
- `nx-wt-prf-usage`
- `nx-wt-prf-usage-tracking`
- `nx-wt-prf-websocket-connections`

#### 2. API Gateway Setup
```bash
# REST API
./02-setup-api-gateway.sh

# WebSocket API
./03-setup-api-routes.sh
```

APIs Created:
- REST: `https://wxwdb89w4m.execute-api.us-east-1.amazonaws.com/prod`
- WebSocket: `wss://p062xh167h.execute-api.us-east-1.amazonaws.com/prod`

#### 3. S3 & CloudFront
```bash
cd frontend/scripts
./01-setup-cloudfront.sh
./02-setup-s3-policy.sh
```

#### 4. Secrets Manager
```bash
# Create secret for API key
aws secretsmanager create-secret \
    --name proof-v1 \
    --secret-string '{"api_key":"your-anthropic-api-key"}' \
    --region us-east-1
```

#### 5. IAM Permissions
```bash
# Create policy for Secrets Manager access
cat > /tmp/policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": ["secretsmanager:GetSecretValue"],
        "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:proof-v1*"
    }]
}
EOF

# Attach to Lambda role
aws iam put-role-policy \
    --role-name lambda-execution-role \
    --policy-name ProofreadingSecretsAccess \
    --policy-document file:///tmp/policy.json
```

---

## Quick Reference

### Deployment Commands
```bash
# Full deployment
./deploy-anthropic.sh && ./deploy-frontend.sh

# Backend only
./deploy-anthropic.sh

# Frontend only
./deploy-frontend.sh

# Infrastructure setup (first time)
cd backend/scripts && ./99-deploy-lambda.sh
```

### Environment Variables
```bash
# Production
USE_ANTHROPIC_API=true
ANTHROPIC_SECRET_NAME=proof-v1
ANTHROPIC_MODEL_ID=claude-opus-4-5-20251101
ENABLE_NATIVE_WEB_SEARCH=true
WEB_SEARCH_MAX_USES=5
FALLBACK_TO_BEDROCK=true
```

### Important URLs
- **Production Frontend**: https://d1ykmbuznjkj67.cloudfront.net
- **WebSocket API**: wss://p062xh167h.execute-api.us-east-1.amazonaws.com/prod
- **REST API**: https://wxwdb89w4m.execute-api.us-east-1.amazonaws.com/prod

### AWS Resources
- **Region**: us-east-1
- **Account ID**: 887078546492
- **Lambda Prefix**: nx-wt-prf-
- **DynamoDB Prefix**: nx-wt-prf-

### Monitoring
```bash
# View Lambda logs
aws logs tail /aws/lambda/nx-wt-prf-websocket-message --follow

# Check Lambda metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Errors \
    --dimensions Name=FunctionName,Value=nx-wt-prf-websocket-message \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Sum
```

### Troubleshooting
```bash
# Test WebSocket connection
wscat -c wss://p062xh167h.execute-api.us-east-1.amazonaws.com/prod

# Check API Gateway logs
aws logs filter-log-events \
    --log-group-name API-Gateway-Execution-Logs_p062xh167h/prod \
    --start-time $(date -d '1 hour ago' +%s)000

# Verify DynamoDB tables
aws dynamodb list-tables --query "TableNames[?contains(@, 'nx-wt-prf')]"
```

---

## Related Documents
- [AWS_INFRASTRUCTURE_DOCUMENTATION.md](./AWS_INFRASTRUCTURE_DOCUMENTATION.md) - Detailed infrastructure specs
- [UPGRADE_DEPLOYMENT_GUIDE.md](./UPGRADE_DEPLOYMENT_GUIDE.md) - Upgrade procedures
- [MAINTENANCE_GUIDE.md](./MAINTENANCE_GUIDE.md) - Maintenance procedures
- [README.md](./README.md) - Project overview

---

*End of Unified Deployment Manual*