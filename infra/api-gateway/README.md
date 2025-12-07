# API Gateway Configuration

## Purpose
Centralized API Gateway configuration for all Nexus services.

## Architecture
- Single API Gateway for all services
- Path-based routing to Lambda functions
- CORS enabled for all endpoints
- API key authentication
- Rate limiting and throttling

## Endpoints Structure
```
/api/v1/
├── /title
│   ├── /internal
│   │   ├── /one   [POST]
│   │   ├── /two   [POST]
│   │   └── /three [POST]
│   └── /external
│       ├── /one   [POST]
│       ├── /two   [POST]
│       └── /three [POST]
├── /proofreading
│   ├── /internal
│   │   └── /one   [POST]
│   └── /external
│       ├── /one   [POST]
│       └── /two   [POST]
├── /bodo
│   ├── /internal
│   │   └── /one   [POST]
│   └── /external
│       ├── /one   [POST]
│       └── /two   [POST]
├── /foreign
│   ├── /internal
│   │   └── /one   [POST]
│   └── /external
│       ├── /one   [POST]
│       ├── /two   [POST]
│       └── /three [POST]
├── /regression
│   ├── /internal
│   │   └── /one   [POST]
│   └── /external
│       └── /one   [POST]
└── /buddy
    ├── /internal
    │   └── /one   [POST]
    └── /external
        ├── /one   [POST]
        └── /two   [POST]
```

## Security
- API Key required for all endpoints
- Rate limiting: 1000 requests per minute
- Request size limit: 10MB
- Response caching: 5 minutes for GET requests

## Deployment
```bash
# Deploy API Gateway
aws apigateway create-rest-api --name nexus-api

# Deploy with Serverless Framework
serverless deploy --stage prod
```

## Monitoring
- CloudWatch Logs enabled
- X-Ray tracing enabled
- Custom metrics for each service
- Alarm on 4xx/5xx errors

## CORS Configuration
```json
{
  "AllowOrigins": ["*"],
  "AllowMethods": ["GET", "POST", "OPTIONS"],
  "AllowHeaders": ["Content-Type", "X-Api-Key", "Authorization"],
  "MaxAge": 3600
}
```