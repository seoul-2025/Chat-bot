# Nexus Architecture

## Overview
Nexus is a monorepo containing multiple AI-powered services for newsroom operations. The architecture follows a microservices pattern with shared libraries and infrastructure.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      API Gateway                         │
│                   (Single Entry Point)                   │
└────────────┬────────────────────────────────────────────┘
             │
             ├──────────────────────┬──────────────────────┐
             │                      │                      │
    ┌────────▼────────┐   ┌────────▼────────┐   ┌────────▼────────┐
    │  Title Service  │   │ Proofreading    │   │  Bodo Service   │
    │                 │   │    Service      │   │                 │
    └────────┬────────┘   └────────┬────────┘   └────────┬────────┘
             │                      │                      │
    ┌────────▼────────┐   ┌────────▼────────┐   ┌────────▼────────┐
    │ Foreign Service │   │ Regression      │   │  Buddy Service  │
    │                 │   │    Service      │   │                 │
    └────────┬────────┘   └────────┬────────┘   └────────┬────────┘
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                   │
                        ┌──────────▼──────────┐
                        │   Lambda Layers     │
                        │  - Core utilities   │
                        │  - AI libraries     │
                        │  - Nexus utils      │
                        └──────────┬──────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                │                  │                  │
       ┌────────▼────────┐ ┌──────▼──────┐ ┌────────▼────────┐
       │  AWS Bedrock    │ │  DynamoDB   │ │     S3 Storage  │
       │  (Claude API)   │ │  (Metadata) │ │     (Files)     │
       └─────────────────┘ └─────────────┘ └─────────────────┘
```

## Service Matrix

| Service | Internal | External | Card Options | Purpose |
|---------|----------|----------|--------------|---------|
| Title | ✓ | ✓ | 1, 2, 3 | Generate article titles |
| Proofreading | ✓ | ✓ | 1, 2 | Grammar and style checking |
| Bodo | ✓ | ✓ | 1, 2 | Press release processing |
| Foreign | ✓ | ✓ | 1, 2, 3 | Foreign news translation |
| Regression | ✓ | ✓ | 1 | Content regression testing |
| Buddy | ✓ | ✓ | 1, 2 | AI writing assistant |

## Technology Stack

### Runtime
- **Node.js 18.x**: Lambda runtime
- **Python 3.11**: Data processing scripts

### AWS Services
- **Lambda**: Serverless compute
- **API Gateway**: REST API management
- **DynamoDB**: NoSQL database
- **S3**: Object storage
- **Bedrock**: Claude AI integration
- **CloudWatch**: Logging and monitoring
- **X-Ray**: Distributed tracing

### Frameworks & Libraries
- **Serverless Framework**: Infrastructure as code
- **Express.js**: HTTP framework
- **AWS SDK v3**: AWS service integration
- **Jest**: Testing framework

## Data Flow

1. **Request Reception**
   - Client sends POST request to API Gateway
   - API Gateway validates API key
   - Request routed to appropriate Lambda

2. **Processing**
   - Lambda function receives request
   - Loads prompts from files
   - Calls Bedrock API with Claude model
   - Processes AI response

3. **Response**
   - Format response based on card count
   - Store metadata in DynamoDB
   - Return JSON response to client

## Security Architecture

### Authentication & Authorization
- API Key authentication for external clients
- IAM roles for service-to-service communication
- JWT tokens for user sessions

### Data Protection
- Encryption at rest (S3, DynamoDB)
- Encryption in transit (TLS 1.2+)
- VPC isolation for sensitive services

### Compliance
- GDPR compliant data handling
- PII data anonymization
- Audit logging for all operations

## Scalability

### Horizontal Scaling
- Lambda auto-scaling (up to 1000 concurrent)
- DynamoDB on-demand scaling
- S3 unlimited storage

### Performance Optimization
- Lambda provisioned concurrency
- API Gateway caching
- CloudFront CDN for static assets

## Monitoring & Observability

### Metrics
- Request count and latency
- Error rates (4xx, 5xx)
- Lambda cold starts
- Bedrock API usage

### Logging
- Structured JSON logging
- Centralized log aggregation
- Log retention: 30 days

### Alerting
- CloudWatch alarms
- SNS notifications
- PagerDuty integration

## Deployment Architecture

### Environments
- **Development**: Feature testing
- **Staging**: Integration testing
- **Production**: Live services

### CI/CD Pipeline
1. Code push to GitHub
2. GitHub Actions triggered
3. Run unit tests
4. Deploy to staging
5. Run integration tests
6. Deploy to production
7. Post-deployment validation

## Disaster Recovery

### Backup Strategy
- DynamoDB point-in-time recovery
- S3 versioning enabled
- Lambda function versioning

### RTO/RPO Targets
- Recovery Time Objective: 1 hour
- Recovery Point Objective: 15 minutes

## Cost Optimization

### Strategies
- Reserved capacity for predictable workloads
- Spot instances for batch processing
- S3 lifecycle policies
- Lambda right-sizing

### Monitoring
- AWS Cost Explorer integration
- Budget alerts
- Resource tagging for cost allocation