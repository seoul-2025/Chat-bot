# Nexus Project Structure

## Directory Organization

### Root Structure
```
Nexus-main/
├── .amazonq/rules/memory-bank/     # AI assistant memory bank
├── dashboard/v1/                   # Management dashboard
├── docs/                          # Project documentation
├── infra/                         # Infrastructure components
├── libs/                          # Shared libraries
└── services/                      # AI services (main application)
```

## Core Components

### Services Directory (`/services/`)
The main application containing 6 AI-powered services:

```
services/
├── proofreading/external/two/     # p1.sedaily.ai - Article proofreading
├── regression/external/two/       # r1.sedaily.ai - Column writing
├── foreign/external/two/          # f1.sedaily.ai - General chat
├── buddy/external/two/            # b1.sedaily.ai - Press release assistant
├── bodo/external/two/             # w1.sedaily.ai - Press release service
├── title/external/two/            # t1.sedaily.ai - Title AI conversation
└── README.md                      # Services overview
```

### Service Structure Pattern
Each service follows consistent organization:
```
{service}/external/two/
├── backend/                       # Python Lambda functions
│   ├── src/                      # Source code
│   │   ├── anthropic_client.py   # AI client
│   │   ├── lambda_function.py    # Main handler
│   │   └── utils/                # Utilities
│   ├── requirements.txt          # Dependencies
│   └── serverless.yml           # Infrastructure config
├── frontend/                     # React application
│   ├── src/                     # Source code
│   │   ├── components/          # UI components
│   │   ├── features/            # Feature modules
│   │   └── utils/               # Utilities
│   ├── package.json             # Dependencies
│   └── vite.config.js          # Build config
├── deploy-*.sh                  # Deployment scripts
└── README.md                    # Service documentation
```

### Shared Libraries (`/libs/`)
Reusable components across services:
```
libs/
├── auth-utils/                   # Authentication utilities
├── bedrock-client/              # AWS Bedrock integration
├── dynamo-utils/                # DynamoDB operations
├── prompt-engine/               # Prompt management
└── s3-utils/                    # S3 operations
```

### Infrastructure (`/infra/`)
Infrastructure as code and deployment tools:
```
infra/
├── api-gateway/                 # API Gateway configurations
├── deployment-scripts/          # Deployment automation
└── lambda-layer/               # Lambda layer definitions
```

### Documentation (`/docs/`)
Comprehensive project documentation:
```
docs/
├── cost-optimization/           # Cost analysis per service
├── reports/                    # Implementation reports
├── architecture.md             # System architecture
├── conventions.md              # Development standards
└── service-guidelines.md       # Service development guide
```

### Dashboard (`/dashboard/v1/`)
Management interface:
```
dashboard/v1/
├── backend/                    # Dashboard API
├── frontend/                   # Dashboard UI
└── README.md                   # Dashboard documentation
```

## Architectural Patterns

### Microservices Architecture
- **Service Isolation**: Each AI service operates independently
- **Shared Libraries**: Common functionality extracted to `/libs/`
- **Consistent Structure**: Standardized organization across services
- **Independent Deployment**: Each service can be deployed separately

### Serverless Pattern
- **Lambda Functions**: Event-driven compute for each service
- **API Gateway**: REST and WebSocket endpoints
- **DynamoDB**: NoSQL database for conversations and metadata
- **S3**: Static hosting and file storage
- **CloudFront**: Global CDN for performance

### Frontend Architecture
- **React + Vite**: Modern build tooling and hot reload
- **Tailwind CSS**: Utility-first styling framework
- **Component-based**: Reusable UI components
- **Feature Modules**: Organized by business functionality

### Backend Architecture
- **Python 3.11**: Lambda runtime environment
- **Anthropic API**: Primary AI provider
- **AWS Bedrock**: Fallback AI provider
- **WebSocket Streaming**: Real-time AI responses
- **Prompt Caching**: Cost optimization through intelligent caching

## Component Relationships

### Service Dependencies
```
Frontend (React) → API Gateway → Lambda Functions
                                      ↓
                              Anthropic API / AWS Bedrock
                                      ↓
                              DynamoDB (conversations)
                                      ↓
                              S3 (static assets)
```

### Shared Library Usage
- **auth-utils**: User authentication across all services
- **dynamo-utils**: Database operations for conversations and prompts
- **prompt-engine**: AI prompt management and optimization
- **bedrock-client**: Fallback AI provider integration
- **s3-utils**: File storage and retrieval operations

### Cross-Service Communication
- **Independent Operation**: Services don't directly communicate
- **Shared Data Layer**: Common DynamoDB tables for user data
- **Unified Authentication**: Single Cognito user pool
- **Consistent API Patterns**: Standardized request/response formats

## Deployment Architecture

### Environment Structure
- **Development**: Local development and testing
- **Staging**: Integration testing environment
- **Production**: Live services (*.sedaily.ai domains)

### Infrastructure as Code
- **Serverless Framework**: Service-level infrastructure
- **AWS CloudFormation**: Underlying resource management
- **GitHub Actions**: CI/CD pipeline automation
- **Deployment Scripts**: Service-specific deployment automation

## Scalability Design

### Horizontal Scaling
- **Lambda Auto-scaling**: Up to 1000 concurrent executions
- **API Gateway**: Unlimited request handling
- **DynamoDB On-demand**: Automatic capacity scaling
- **CloudFront**: Global edge locations

### Performance Optimization
- **Prompt Caching**: 67-92% cost reduction
- **Connection Pooling**: Efficient database connections
- **Static Asset CDN**: Fast global content delivery
- **Lambda Provisioned Concurrency**: Reduced cold starts