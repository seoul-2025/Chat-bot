# b1.sedaily.ai (Internal)
AI Press Release Assistant - Claude Opus 4.5 based real-time chat with web search

Last Updated: 2025-12-24

## Overview
NX-P2-BUDDY Internal is the development/internal version of the AI-powered press release writing assistant for Seoul Economic Daily. Built on Anthropic Claude Opus 4.5 with real-time WebSocket streaming, native web search, and prompt caching for cost optimization.

Production: https://b1.sedaily.ai

## Features
- Real-time Chat: WebSocket-based streaming responses
- Web Search: Anthropic's native web search integration (2025 data)
- Prompt Caching: 81% cost reduction with Anthropic ephemeral cache
- DynamoDB Caching: Permanent prompt cache in Lambda container
- Multiple AI Providers: Anthropic API primary, Bedrock fallback
- Dual Engine Support: Corporate (11) / Government (22) press release modes
- Press Release Generation: Structured 5-step article creation workflow

## Architecture
```
Frontend (React + Vite)
  |
CloudFront (CDN) -> b1.sedaily.ai
  |
S3 (Static Hosting)

WebSocket Flow:
User -> API Gateway WebSocket -> Lambda (message handler)
  |
Anthropic Claude Opus 4.5 (with web search)
  |
Streaming Response -> User

REST API Flow:
User -> API Gateway REST -> Lambda (conversation/prompt/usage)
  |
DynamoDB (conversations, prompts, usage tracking)
```

## Project Structure
```
.
├── README.md
├── deploy-p2-frontend.sh       # Frontend deployment script
├── backend/
│   ├── handlers/               # Lambda handlers (websocket)
│   ├── lib/                    # AI clients (anthropic, bedrock, perplexity)
│   ├── services/               # websocket_service
│   ├── src/                    # Core business logic
│   │   ├── models/
│   │   ├── repositories/
│   │   └── config/
│   ├── utils/                  # Logger utilities
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── features/           # auth, chat, dashboard, landing
    │   ├── shared/
    │   └── config.js
    └── package.json
```

## Quick Start

### Prerequisites
- AWS CLI configured
- Node.js 18+
- Python 3.11+
- AWS Account: 887078546492

### Deployment
```bash
# Frontend only (S3 + CloudFront)
./deploy-p2-frontend.sh
```

## Current Deployment
Status: Production Ready

Updated: 2025-12-24

## URLs
| Resource | URL |
|----------|-----|
| Primary Domain | https://b1.sedaily.ai |
| CloudFront | https://dxiownvrignup.cloudfront.net |
| REST API | https://pisnqqgu75.execute-api.us-east-1.amazonaws.com/prod |
| WebSocket API | wss://dwc2m51as4.execute-api.us-east-1.amazonaws.com/prod |

## AWS Resources (us-east-1)

### Lambda Functions
| Function | Purpose |
|----------|---------|
| p2-two-websocket-connect-two | WebSocket connection handler |
| p2-two-websocket-message-two | Main chat handler (Claude API) |
| p2-two-websocket-disconnect-two | WebSocket disconnect handler |
| p2-two-conversation-api-two | Conversation CRUD |
| p2-two-prompt-crud-two | Prompt management |
| p2-two-usage-handler-two | Usage tracking |

### DynamoDB Tables
| Table | Purpose |
|-------|---------|
| p2-two-conversations-two | Chat history |
| p2-two-messages-two | Message storage |
| p2-two-prompts-two | System prompts |
| p2-two-files-two | File metadata |
| p2-two-usage-two | Usage statistics |
| p2-two-websocket-connections-two | Active connections |

### Other Resources
| Resource | ID/Name |
|----------|---------|
| S3 Bucket | p2-two-frontend |
| CloudFront Distribution | E2WPOE6AL2G5DZ |
| Secrets Manager | buddy-v1 (Anthropic API key) |

## AI Configuration
| Setting | Value |
|---------|-------|
| Primary Provider | Anthropic API |
| Model | claude-opus-4-5-20251101 |
| Max Tokens | 4096 |
| Temperature | 0.3 |
| Fallback | AWS Bedrock |
| Web Search | Enabled (max 5 uses) |

## Environment Configuration
Lambda environment variables:
```json
{
  "USE_ANTHROPIC_API": "true",
  "ANTHROPIC_SECRET_NAME": "buddy-v1",
  "ANTHROPIC_MODEL_ID": "claude-opus-4-5-20251101",
  "SERVICE_NAME": "buddy",
  "AI_PROVIDER": "anthropic_api",
  "FALLBACK_TO_BEDROCK": "true",
  "ENABLE_NATIVE_WEB_SEARCH": "true",
  "MAX_TOKENS": "4096",
  "TEMPERATURE": "0.3"
}
```

## Log Monitoring
```bash
# Real-time Lambda logs
aws logs tail /aws/lambda/p2-two-websocket-message-two --follow --region us-east-1

# Check cache status
aws logs tail /aws/lambda/p2-two-websocket-message-two --since 5m --region us-east-1 | grep -E "cache|Cache"

# Check deployment
aws lambda get-function --function-name p2-two-websocket-message-two --query 'Configuration.LastModified'
```

## Cost Optimization

### Anthropic Prompt Caching (81% savings)
- System prompt (~27,925 tokens) cached with Anthropic ephemeral cache
- Cache TTL: 1 hour (Anthropic managed)
- Cache MISS: ~$0.155/request (first request creates cache)
- Cache HIT: ~$0.029/request (subsequent requests)

### Pricing (Claude Opus 4.5)
| Token Type | Price per 1M tokens |
|------------|---------------------|
| Input | $5.00 |
| Output | $25.00 |
| Cache Write | $10.00 |
| Cache Read | $0.50 (90% off) |

## Tech Stack

### Backend
- Python 3.11
- AWS Lambda
- Anthropic Claude Opus 4.5
- DynamoDB
- API Gateway (REST + WebSocket)
- Secrets Manager

### Frontend
- React 18.2
- Vite 4.4
- Tailwind CSS 3.3
- Framer Motion
- S3 + CloudFront

## Troubleshooting

### Common Issues

1. **WebSocket not connecting**
   - Check Lambda logs for errors
   - Verify API Gateway WebSocket stage is deployed
   ```bash
   wscat -c wss://dwc2m51as4.execute-api.us-east-1.amazonaws.com/prod
   ```

2. **AI responses not working**
   - Check Anthropic API key in Secrets Manager (`buddy-v1`)
   - Verify Lambda environment variables
   ```bash
   aws lambda get-function-configuration --function-name p2-two-websocket-message-two
   ```

3. **Frontend not updating**
   - Run CloudFront cache invalidation
   ```bash
   aws cloudfront create-invalidation --distribution-id E2WPOE6AL2G5DZ --paths "/*"
   ```

## Related
- Production version: `/buddy/external/two/`

## License
Proprietary - Seoul Economic Daily
