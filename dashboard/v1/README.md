# Unified Monitoring Dashboard

AI Service Usage Monitoring Dashboard for Seoul Economic Daily

Last Updated: 2025-12-21

## Overview

A unified dashboard for real-time monitoring and analysis of 6 AI services (Title, Proofreading, News, Foreign, Revision, Buddy).

| Item | Info |
|------|------|
| Production URL | https://dashboard.sedaily.ai |
| API Endpoint | https://05oo6stfzk.execute-api.us-east-1.amazonaws.com/dev |
| Region | us-east-1 |
| Status | Production |

---

## Architecture

```
+------------------+     +-------------------+     +------------------+
|                  |     |                   |     |                  |
|   CloudFront     +---->+   S3 Bucket       |     |   Cognito        |
|   (CDN/HTTPS)    |     |   (Frontend)      |     |   (Auth)         |
|                  |     |                   |     |                  |
+--------+---------+     +-------------------+     +--------+---------+
         |                                                  |
         |  https://dashboard.sedaily.ai                    |
         v                                                  v
+------------------+     +-------------------+     +------------------+
|                  |     |                   |     |                  |
|   React App      +---->+   API Gateway     +---->+   Lambda (x10)   |
|   (Vite/Tailwind)|     |   (REST API)      |     |   (Node.js 20.x) |
|                  |     |                   |     |                  |
+------------------+     +-------------------+     +--------+---------+
                                                           |
                                                           v
                         +-------------------+     +------------------+
                         |                   |     |                  |
                         |   DynamoDB        +<----+   8 Usage Tables |
                         |   (NoSQL)         |     |   (per service)  |
                         |                   |     |                  |
                         +-------------------+     +------------------+
```

### Data Flow

```
User Request --> CloudFront --> S3 (React App)
                                    |
                                    v
                              API Gateway --> Lambda --> DynamoDB
                                    ^                        |
                                    |                        v
                              Cognito Auth           Usage Data (8 tables)
```

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Frontend | React 19, Vite, Tailwind CSS, Recharts |
| Backend | AWS Lambda (Node.js 20.x) |
| Database | DynamoDB |
| Auth | AWS Cognito |
| Hosting | CloudFront + S3 |
| IaC | Serverless Framework |

---

## AWS Resources

### Infrastructure

| Resource | ID/Name | Domain/Endpoint |
|----------|---------|-----------------|
| S3 Bucket | sed-dashboard-monitoring | sed-dashboard-monitoring.s3.us-east-1.amazonaws.com |
| CloudFront | ECRURESQSCGGQ | d16ixd4i1kne9s.cloudfront.net |
| Custom Domain | - | dashboard.sedaily.ai |
| API Gateway | 05oo6stfzk | 05oo6stfzk.execute-api.us-east-1.amazonaws.com/dev |
| Cognito Pool | us-east-1_ohLOswurY | User authentication |

### Lambda Functions (10)

| Function Name | Handler | Memory |
|---------------|---------|--------|
| unified-monitoring-getAllUsage-v2 | Get all usage | 256MB |
| unified-monitoring-getAllUsersUsage-v2 | Get all users usage | 256MB |
| unified-monitoring-getDailyTrend-v2 | Daily trend | 256MB |
| unified-monitoring-getMonthlyTrend-v2 | Monthly trend | 256MB |
| unified-monitoring-getSummary-v2 | Summary statistics | 256MB |
| unified-monitoring-getServiceUsage-v2 | Service usage | 256MB |
| unified-monitoring-getTopServices-v2 | Top services | 256MB |
| unified-monitoring-getTopEngines-v2 | Top engines | 256MB |
| unified-monitoring-getUserUsage-v2 | User usage | 256MB |
| unified-monitoring-getUserRegistrationTrend | Registration trend | 256MB |

### DynamoDB Tables (9)

| Service | Table Name | Key Structure | Type |
|---------|------------|---------------|------|
| Title (KR) | nx-tt-dev-ver3-usage-tracking | PK: user#userId, SK: engine#type#yearMonth | Daily |
| Proofreading | nx-wt-prf-usage | PK: userId, SK: yearMonth | Monthly |
| Proofreading (Daily) | nx-wt-prf-dev-v2-usage-tracking | PK: userId, SK: dateEngine | Daily |
| News | w1-usage | PK: userId, SK: yearMonth | Monthly |
| Foreign | f1-usage-two | PK: userId, SK: date | Daily |
| Revision (KR) | sedaily-column-usage | PK: userId, SK: usageDate#engineType | Daily |
| Buddy | p2-two-usage-two | PK: userId, SK: date | Daily |
| Title (EN) | tf1-usage-two | PK: userId, SK: date | Daily |
| Revision (EN) | er1-usage-two | PK: userId, SK: date | Daily |

---

## Features

- Service/Engine usage statistics
- User usage search and filtering
- Daily/Monthly usage trends
- Top services and engines ranking
- Date range filtering
- Korean/English service separation

---

## Service Mapping

| Service | ID | Table | Engine Label |
|---------|-----|-------|--------------|
| Title | title | nx-tt-dev-ver3-usage-tracking | t1-1, t1-2 |
| Proofreading | proofreading | nx-wt-prf-usage | p1-1, p1-2 |
| News | news | w1-usage | w1-1, w1-2 |
| Foreign | foreign | f1-usage-two | f1-1, f1-2 |
| Revision | revision | sedaily-column-usage | r1-1, r1-2 |
| Buddy | buddy | p2-two-usage-two | b1-1, b1-2 |
| Title (EN) | title_en | tf1-usage-two | - |
| Revision (EN) | revision_en | er1-usage-two | - |

---

## Deployment

### Frontend
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://sed-dashboard-monitoring/ --delete
aws cloudfront create-invalidation --distribution-id ECRURESQSCGGQ --paths "/*"
```

### Backend
```bash
cd backend
npm install
zip -r lambda-deployment.zip src/ node_modules/ package.json
aws lambda update-function-code --function-name <function-name> --zip-file fileb://lambda-deployment.zip --region us-east-1
```

---

## Change History

### Phase 8: Lambda Memory Optimization (2025-12-21)
- Reduced Lambda memory from 512MB to 256MB for all 10 functions
- Expected cost reduction: ~50% on Lambda costs
- Functions updated:
  - unified-monitoring-getDailyTrend-v2
  - unified-monitoring-getSummary-v2
  - unified-monitoring-getTopServices-v2
  - unified-monitoring-getMonthlyTrend-v2
  - unified-monitoring-getAllUsersUsage-v2
  - unified-monitoring-getUserRegistrationTrend
  - unified-monitoring-getAllUsage-v2
  - unified-monitoring-getUserUsage-v2
  - unified-monitoring-getServiceUsage-v2
  - unified-monitoring-getTopEngines-v2

### Phase 7: P1 Daily Tracking & All Services Filter Fix (2025-12-21)
- **P1 Daily Token Tracking**
  - Migrated 601 records from `nx-wt-prf-conversations` and `nx-wt-prf-conversations-v2` to daily tracking table
  - Added `nx-wt-prf-dev-v2-usage-tracking` table for daily usage
  - Modified P1 backend (`websocket_service.py`) to save daily tokens alongside monthly
  - Updated `aws.py` config to include `daily_usage` table
- **All Services Date Range Filtering**
  - Fixed bug: "전체 서비스" selection ignored date range filter
  - Now uses `dailyUsageTable` for each service when date range is specified
  - Modified: `dynamodbService.js` - `getAllUsersWithUsage` function
- **Default Sorting Change**
  - Changed default sorting from `totalTokens` to `messageCount` (descending)
  - Modified: `dynamodbService.js`, `UsersTable.jsx`
- **Files Modified**:
  - `backend/src/services/dynamodbService.js`
  - `backend/src/config/services.js` (added dailyUsageTable for proofreading)
  - `frontend/src/components/user/UsersTable.jsx`
  - `proofreading/external/two/backend/services/websocket_service.py`
  - `proofreading/external/two/backend/src/config/aws.py`
- **IAM Policy Updated**: Added `nx-wt-prf-dev-v2-usage-tracking` to Lambda role permissions

### Phase 6: User Filtering Fix (2025-12-21)
- Fixed `searchUserByEmail` to use Cognito instead of DynamoDB
- Fixed `getUserUsage` to support various key structures (user#userId, userId)
- Tested user filtering across all 6 services
- Modified: `backend/src/services/dynamodbService.js`
- Deployed: unified-monitoring-getUserUsage-v2

### Phase 5: Date Filtering Fix (2025-12-21)
- Added `updatedAt` field support to `extractDate` function
- Fixed proofreading (p1) service date filtering issue
- Tested date filtering for all 6 services
- Modified: `backend/src/services/dynamodbService.js`
- Deployed: unified-monitoring-getAllUsersUsage-v2, unified-monitoring-getDailyTrend-v2

### Phase 4: Data Overwrite Bug Fix (2025-12-13)
- Fixed data overwrite issue by including engine type in yearMonth key
- Cleaned up backend package dependencies
- Removed unused deployment files

### Phase 3: English Services & Monorepo Migration (2025-12-07)
- Migrated to Nexus monorepo structure
- Added English language services (title_en, revision_en)
- Added tf1-usage-two, er1-usage-two tables support
- Dashboard v2 folder structure added

### Phase 2: Code Quality Improvement (2025-11-05)
- Centralized constants management (`src/config/constants.js`)
- Input validation layer (`src/utils/validators.js`)
- Standardized error handling (`src/utils/errors.js`)
- CORS security enhancement (specific domains only)
- Environment variables support

### Phase 1: Initial Release (2025-11-06)
- 6 service monitoring (Title, Proofreading, News, Foreign, Revision, Buddy)
- User usage tracking and search
- Daily/Monthly trend analysis
- Cognito authentication integration
- CloudFront + S3 hosting
- 10 Lambda functions deployed

---

## Project Structure

```
dashboard/v1/
├── frontend/
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── contexts/       # React Context
│   │   ├── services/       # API services
│   │   ├── utils/          # Utilities (engineFormatter, etc.)
│   │   └── config/         # Service configuration
│   └── package.json
│
└── backend/
    ├── src/
    │   ├── handlers/       # Lambda handlers
    │   ├── services/       # dynamodbService
    │   ├── utils/          # Error handling
    │   └── config/         # Service/constants config
    ├── serverless.yml
    └── package.json
```

---

## Related Documents

- [Cost Optimization Report](../../services/cost-optimization/README.md) - Prompt Caching cost optimization

---

## Contact

Project inquiries: Development Team
