# 🚀 Upgrade Deployment Guide - NX-WT-PRF Service

## 📅 Document Version: 1.0 (2024-12-15)
## 🎯 Purpose: 웹 검색 기능 및 Anthropic API 통합 업그레이드 가이드

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Deployment Steps](#detailed-deployment-steps)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Rollback Procedure](#rollback-procedure)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools
```bash
# Check AWS CLI
aws --version  # Should be 2.x or higher

# Check Python
python3 --version  # Should be 3.11 or higher

# Check Node.js (for frontend)
node --version  # Should be 18.x or higher
```

### AWS Credentials
```bash
# Configure AWS credentials
aws configure
# Region: us-east-1
# Output: json
```

### Required Permissions
- Lambda full access
- DynamoDB full access
- API Gateway full access
- Secrets Manager read access
- IAM policy management
- CloudWatch logs read access

---

## Quick Start

### 🎯 One-Command Deployment
```bash
# Complete deployment (backend + frontend)
./deploy-anthropic.sh && ./deploy-frontend.sh
```

### ⚡ Backend Only
```bash
# Deploy Lambda functions with Anthropic integration
./deploy-anthropic.sh
```

### 🎨 Frontend Only
```bash
# Deploy React frontend to S3/CloudFront
./deploy-frontend.sh
```

---

## Detailed Deployment Steps

### Step 1: Prepare Environment
```bash
# 1. Navigate to project root
cd /Users/yeong-gwang/nexus/services/proofreading/external/two

# 2. Set environment variables
export AWS_REGION=us-east-1
export ANTHROPIC_SECRET_NAME=proof-v1
export USE_ANTHROPIC_API=true
export ENABLE_NATIVE_WEB_SEARCH=true
```

### Step 2: Update Secrets (if needed)
```bash
# Check if secret exists
aws secretsmanager describe-secret --secret-id proof-v1 --region us-east-1

# Update secret if needed (replace YOUR_API_KEY)
aws secretsmanager put-secret-value \
  --secret-id proof-v1 \
  --secret-string '{"api_key":"YOUR_API_KEY"}' \
  --region us-east-1
```

### Step 3: Deploy Backend
```bash
# Run deployment script
./deploy-anthropic.sh

# Expected output:
# ✅ 패키지 설치 완료
# ✅ 소스 코드 복사 완료
# ✅ 배포 패키지 생성 완료
# ✅ Lambda 함수 업데이트 완료
# ✅ 환경 변수 업데이트 완료
# ✅ IAM 권한 설정 완료
```

### Step 4: Update IAM Permissions
```bash
# The deploy script handles this automatically, but to verify:
aws iam get-role-policy \
  --role-name lambda-execution-role \
  --policy-name ProofreadingSecretsAccess \
  --region us-east-1
```

### Step 5: Deploy Frontend (Optional)
```bash
# Build and deploy frontend
cd frontend
npm install
npm run build
cd ..
./deploy-frontend.sh

# Verify deployment
aws s3 ls s3://nx-wt-prf-frontend-prod/
```

### Step 6: Invalidate CloudFront Cache
```bash
# Get distribution ID
DIST_ID=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[?Comment=='nx-wt-prf-frontend-prod'].Id" \
  --output text)

# Create invalidation
aws cloudfront create-invalidation \
  --distribution-id $DIST_ID \
  --paths "/*"
```

---

## Configuration

### Lambda Environment Variables
```json
{
  "USE_ANTHROPIC_API": "true",           // Enable Anthropic API
  "ANTHROPIC_SECRET_NAME": "proof-v1",   // Secrets Manager key name
  "ANTHROPIC_MODEL_ID": "claude-opus-4-5-20251101",  // Model version
  "AI_PROVIDER": "anthropic_api",        // Primary AI provider
  "FALLBACK_TO_BEDROCK": "true",        // Enable fallback
  "ENABLE_NATIVE_WEB_SEARCH": "true",   // Enable web search
  "WEB_SEARCH_MAX_USES": "5",           // Max web searches per request
  "ANTHROPIC_MAX_TOKENS": "4096",       // Max response tokens
  "ANTHROPIC_TEMPERATURE": "0.7"        // Response creativity (0-1)
}
```

### Engine Types
| Engine | Purpose | System Prompt Location |
|--------|---------|------------------------|
| `Basic` | General proofreading | DynamoDB: nx-wt-prf-prompts |
| `T5` | Title generation | DynamoDB: nx-wt-prf-prompts |
| `H8` | Headline creation | DynamoDB: nx-wt-prf-prompts |

---

## Testing

### 1. Test WebSocket Connection
```python
# Save as test_connection.py
import asyncio
import websockets
import json
from datetime import datetime, timezone

async def test():
    uri = 'wss://p062xh167h.execute-api.us-east-1.amazonaws.com/prod'
    async with websockets.connect(uri) as ws:
        msg = {
            'action': 'sendMessage',
            'message': 'Hello',
            'engineType': 'Basic',
            'userId': 'test@example.com',
            'conversationHistory': [],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        await ws.send(json.dumps(msg))
        response = await ws.recv()
        print(json.loads(response))

asyncio.run(test())
```

### 2. Test Web Search
```python
# Test web search functionality
python3 test_web_search.py
```

### 3. Check Logs
```bash
# View recent logs
aws logs tail /aws/lambda/nx-wt-prf-websocket-message --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/nx-wt-prf-websocket-message \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000
```

---

## Rollback Procedure

### Quick Rollback
```bash
# 1. Restore previous Lambda code
cd upgrade-archive
aws lambda update-function-code \
  --function-name nx-wt-prf-websocket-message \
  --zip-file fileb://websocket-deployment.zip \
  --region us-east-1

# 2. Restore environment variables
aws lambda update-function-configuration \
  --function-name nx-wt-prf-websocket-message \
  --environment Variables='{
    "USE_ANTHROPIC_API":"false",
    "FALLBACK_TO_BEDROCK":"true"
  }' \
  --region us-east-1
```

### Full Rollback
```bash
# Use archived scripts
cd upgrade-archive
./upgrade-20241215-deploy.sh
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. "No module named 'requests'" Error
```bash
# Solution: Deploy with dependencies
cd backend
pip install -r requirements.txt -t package/
cp -r handlers lib services utils src package/
cd package && zip -r ../lambda-deployment.zip . -q
aws lambda update-function-code \
  --function-name nx-wt-prf-websocket-message \
  --zip-file fileb://../lambda-deployment.zip
```

#### 2. "Secret not found" Error
```bash
# Check secret exists
aws secretsmanager describe-secret --secret-id proof-v1

# Check Lambda IAM role
aws iam list-attached-role-policies --role-name lambda-execution-role
```

#### 3. Web Search Not Working
```bash
# Check environment variables
aws lambda get-function-configuration \
  --function-name nx-wt-prf-websocket-message \
  --query 'Environment.Variables'

# Ensure these are set:
# ENABLE_NATIVE_WEB_SEARCH=true
# USE_ANTHROPIC_API=true
# ANTHROPIC_SECRET_NAME=proof-v1
```

#### 4. Anthropic API Fallback to Bedrock
```bash
# Check CloudWatch logs for reason
aws logs filter-log-events \
  --log-group-name /aws/lambda/nx-wt-prf-websocket-message \
  --filter-pattern "Anthropic API failed"

# Common causes:
# - Invalid API key
# - Rate limiting
# - Network issues
```

---

## Monitoring

### Key Metrics to Watch
```bash
# Lambda invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=nx-wt-prf-websocket-message \
  --start-time 2024-12-14T00:00:00Z \
  --end-time 2024-12-15T00:00:00Z \
  --period 3600 \
  --statistics Sum

# Lambda errors
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=nx-wt-prf-websocket-message \
  --start-time 2024-12-14T00:00:00Z \
  --end-time 2024-12-15T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

### Set Up Alarms
```bash
# Create error alarm
aws cloudwatch put-metric-alarm \
  --alarm-name nx-wt-prf-high-error-rate \
  --alarm-description "Alert when Lambda errors are high" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --dimensions Name=FunctionName,Value=nx-wt-prf-websocket-message \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

---

## Best Practices

### 1. Pre-Deployment
- ✅ Always backup current configuration
- ✅ Test in development environment first
- ✅ Review CloudWatch logs for existing issues
- ✅ Ensure API keys are valid and have sufficient quota

### 2. During Deployment
- ✅ Deploy during low-traffic periods
- ✅ Monitor logs in real-time
- ✅ Test immediately after deployment
- ✅ Keep rollback scripts ready

### 3. Post-Deployment
- ✅ Verify all features work as expected
- ✅ Check error rates in CloudWatch
- ✅ Monitor API usage and costs
- ✅ Document any issues or changes

---

## Cost Considerations

### Anthropic API Costs
- **Input**: $15 per million tokens
- **Output**: $75 per million tokens
- **Web Search**: Included in API usage

### AWS Costs (Monthly Estimate)
- Lambda: ~$50-100
- DynamoDB: ~$20-50
- API Gateway: ~$10-30
- Secrets Manager: ~$0.40 per secret
- CloudWatch: ~$5-10

### Cost Optimization Tips
1. Enable prompt caching to reduce token usage
2. Use appropriate MAX_TOKENS setting
3. Implement request throttling if needed
4. Monitor usage with CloudWatch metrics

---

## Support and Resources

### Internal Resources
- Project Repository: `/nexus/services/proofreading/external/two`
- Documentation: `AWS_INFRASTRUCTURE_DOCUMENTATION.md`
- Logs: CloudWatch Log Groups

### External Resources
- [Anthropic API Documentation](https://docs.anthropic.com)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [WebSocket API Gateway Guide](https://docs.aws.amazon.com/apigateway/latest/developerguide/websocket-api.html)

### Contact
- Service Owner: 서울경제신문 디지털뉴스팀
- AWS Account: 887078546492
- Region: us-east-1

---

## Appendix

### A. File Structure
```
/nexus/services/proofreading/external/two/
├── deploy-anthropic.sh          # Main deployment script
├── deploy-frontend.sh           # Frontend deployment
├── backend/
│   ├── handlers/               # Lambda handlers
│   ├── lib/                   # Libraries (anthropic_client.py, etc.)
│   ├── services/              # Business logic
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React application
├── upgrade-archive/           # Backup scripts with upgrade- prefix
└── test_web_search.py        # Web search test script
```

### B. Version History
| Date | Version | Changes |
|------|---------|---------|
| 2024-12-15 | 1.0 | Initial upgrade guide with web search |
| 2024-12-14 | - | Web search feature implementation |

---

*End of Deployment Guide*