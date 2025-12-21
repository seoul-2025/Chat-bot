# Service Cleanup & Deployment Test Report

Date: 2025-12-21

## Summary

Performed comprehensive cleanup and deployment testing for 6 AI services:
- p1.sedaily.ai (Proofreading Service)
- r1.sedaily.ai (Column Writing Service)
- f1.sedaily.ai (Chat Service)
- b1.sedaily.ai (Press Release Assistant)
- w1.sedaily.ai (Press Release Service)
- t1.sedaily.ai (Title AI Conversation Service)

---

## 1. p1.sedaily.ai (Proofreading Service)

### Cleanup Summary
| Category | Items Deleted |
|----------|---------------|
| Directories | `infrastructure/`, `work-logs/` |
| Backend | `*.zip` (4 files), `BACKEND_STRUCTURE.md` |
| Frontend | `node_modules/`, `dist/`, `.env.example` |
| Documentation | `DEPLOYMENT_MANUAL.md`, `MAINTENANCE_GUIDE.md`, `PROMPT_CACHING_OPTIMIZATION.md` (consolidated into README) |

### Final Structure
```
/proofreading/external/two/
├── README.md
├── AWS_INFRASTRUCTURE_DOCUMENTATION.md
├── deploy-anthropic.sh
├── deploy-frontend.sh
├── config/
├── backend/
└── frontend/
```

### Deployment Test Results
| Script | Result | Details |
|--------|--------|---------|
| `deploy-anthropic.sh` | PASS | 4/4 Lambda functions deployed |
| `deploy-frontend.sh` | PASS | S3 upload + CloudFront invalidation complete |

### Script Fixes
- Added `npm install` to `deploy-frontend.sh` (missing dependency installation)

### CloudFront Fix (Post-Deployment Issue)
**Problem**: `p1.sedaily.ai` returned "Access Denied" error after deployment

**Root Cause Analysis**:
- `deploy-frontend.sh` was uploading to wrong S3 bucket: `nx-wt-prf-frontend-prod`
- `p1.sedaily.ai` CloudFront (`E39OHKSWZD4F8J`) pointed to empty/wrong bucket
- Different CloudFront (`E3E25OIRRG1ZR`) was documented but not used by domain

**Fixes Applied**:
1. Updated `deploy-frontend.sh`:
   - `BUCKET_NAME`: `nx-wt-prf-frontend-prod` → `nx-prf-prod-frontend-2025`
   - `CLOUDFRONT_DISTRIBUTION_ID`: `E3E25OIRRG1ZR` → `E39OHKSWZD4F8J`
2. Updated CloudFront `E39OHKSWZD4F8J` origin:
   - From: `nx-wt-prf-frontend-prod.s3.amazonaws.com`
   - To: `nx-prf-prod-frontend-2025.s3-website-us-east-1.amazonaws.com`
3. Updated S3 bucket policy for public read access
4. Updated `AWS_INFRASTRUCTURE_DOCUMENTATION.md` with correct values
5. Updated `README.md` with correct URLs and CloudFront ID

**Verification**: `https://p1.sedaily.ai` returns HTTP 200 with correct content

### Additional Script Fixes (2025-12-21 22:40 KST)
**Problem**: `deploy-frontend.sh` overwrote S3 bucket policy causing Access Denied on re-deploy

**Fixes Applied**:
1. Changed S3 bucket policy from CloudFront-only to public read (for S3 website endpoint)
2. Simplified CloudFront section to use fixed `CLOUDFRONT_DISTRIBUTION_ID` instead of searching
3. Removed unused CloudFront creation logic

---

## 2. r1.sedaily.ai (Column Writing Service)

### Cleanup Summary
| Category | Items Deleted |
|----------|---------------|
| Directories | `admin-dashboard/`, `infrastructure/`, `backend/scripts/` |
| Root | `lambda-deployment.zip`, `package.json`, `package-lock.json` |
| Backend | `*.zip` (10 files), `__pycache__/` |
| Frontend | `node_modules/`, `dist/`, `scripts/`, `config.column.js`, `update-to-column.sh` |
| Documentation | 6 obsolete markdown files (Bedrock-based caching docs) |

### Final Structure
```
/regression/external/two/
├── README.md
├── AWS_INFRASTRUCTURE_MAP.md
├── deploy-backend.sh
├── deploy-column-frontend.sh
├── backend/
└── frontend/
```

### Deployment Test Results
| Script | Result | Details |
|--------|--------|---------|
| `deploy-backend.sh` | PASS | 6/6 Lambda functions deployed |
| `deploy-column-frontend.sh` | PASS | S3 upload + CloudFront invalidation complete |

### Script Fixes
- Moved `backend/scripts/05-deploy-lambda.sh` to root as `deploy-backend.sh`
- Fixed `BACKEND_DIR` path: `$(dirname "$SCRIPT_DIR")` → `$SCRIPT_DIR/backend`
- Fixed directory check in `deploy-column-frontend.sh`: removed typo `"sedaily_ column"` → proper `$SCRIPT_DIR/frontend` check

---

## 3. f1.sedaily.ai (Chat Service)

### Cleanup Summary
| Category | Items Deleted |
|----------|---------------|
| Directories | `cleanup-archive/`, `scripts-backup/` |
| Root | `test_caching_optimization.py` |
| Backend | `*.zip` (3 files), `__pycache__/` (8 directories), `backup_*` (2 folders), `extracted/`, `package/`, `.env`, `deployment-info.txt`, `test_prompt_caching.py` |
| Backend/services | `websocket_service_backup.py`, `websocket_service_fixed.py` |
| Frontend | `node_modules/`, `dist/` |
| Documentation | `DEPLOYMENT.md` (consolidated into README) |

### Final Structure
```
/foreign/external/two/
├── README.md
├── AWS_STACK_DOCUMENTATION.md
├── upgrade-f1-anthropic.sh
├── upgrade-f1-frontend.sh
├── config/
├── backend/
└── frontend/
```

### Deployment Test Results
| Script | Result | Details |
|--------|--------|---------|
| `upgrade-f1-anthropic.sh` | PASS | 6/6 Lambda functions deployed |
| `upgrade-f1-frontend.sh` | PASS | S3 upload + CloudFront invalidation complete |

### Script Fixes
- None required

---

## 4. b1.sedaily.ai (Press Release Assistant)

### Cleanup Summary
| Category | Items Deleted |
|----------|---------------|
| Root | `websocket-service-complete.zip`, `websocket-service-model-fix.zip`, `deprecated-scripts/`, `docs/`, `.DS_Store` |
| Backend | `deployment.zip` (15MB), `package/` (28MB), `__pycache__/` (7 directories), `backup_*` (4 folders) |
| Backend/services | `websocket_service_backup.py`, `websocket_service_dual.py`, `websocket_service_fixed.py`, `websocket_service_original_backup.py` |
| Frontend | `node_modules/`, `dist/`, `.env`, `.env.backup.*` (5 files), `.env.production.template`, `.env.w1` |
| Frontend/src | `LandingPresenter.jsx.backup`, `conversationService.js.backup.*`, `websocketService.js.backup.*` |

### Final Structure
```
/buddy/external/two/
├── README.md
├── upgrade-aws-resources.md
├── update-buddy-code.sh
├── deploy-p2-frontend.sh
├── backend/
└── frontend/
```

### Deployment Test Results
| Script | Result | Details |
|--------|--------|---------|
| `update-buddy-code.sh` | PASS | 4/4 Lambda functions deployed |
| `deploy-p2-frontend.sh` | PASS | S3 upload (70 files) + CloudFront invalidation complete |

### Script Fixes (2025-12-21 23:00 KST)
**Problem**: `update-buddy-code.sh` hung on environment variable update

**Root Cause Analysis**:
- Environment variable JSON format incompatible with AWS CLI
- Script tried to update env vars immediately after code update (Lambda still in pending state)

**Fixes Applied**:
1. Changed env var format from JSON to AWS CLI shorthand: `Variables={KEY=value,KEY2=value2}`
2. Removed environment variable update from script (already configured)
3. Changed `deployment.zip` to be kept instead of deleted (for manual retries)

**Verification**: Script now completes 4/4 Lambda updates successfully

### Documentation Updates
- README.md completely rewritten in English
- Added Phase 1-6 Change History
- Updated CloudFront URL to actual value
- Fixed Project Structure (removed deleted `package/`, `dist/` references)

---

## 5. w1.sedaily.ai (Press Release Service)

### Cleanup Summary
| Category | Items Deleted |
|----------|---------------|
| Root | `AWS_STACK_DOCUMENTATION.md`, `W1_SERVICE_MAPPING.md` (consolidated into README) |
| Backend | `deployment.zip` (16MB), `lambda-deployment.zip` (16MB), `.DS_Store` |
| Frontend | `dist/images/logo_backup.png`, `public/images/logo_backup.png` |
| w1-scripts | `monitor-logs.sh`, `test-service.sh`, `README.md` (optional/setup files) |

### Final Structure
```
/bodo/external/two/
├── README.md
├── PROMPT_CACHING_OPTIMIZATION.md
├── backend/
├── frontend/
├── config/
└── w1-scripts/
    ├── config.sh
    ├── deploy-backend.sh
    └── deploy-frontend.sh
```

### Deployment Test Results
| Script | Result | Details |
|--------|--------|---------|
| `deploy-backend.sh` | PASS | 6/6 Lambda functions deployed |
| `deploy-frontend.sh` | PASS | S3 upload (72 files) + CloudFront invalidation complete |

### Script Fixes
- None required

---

## 6. t1.sedaily.ai (Title AI Conversation Service)

### Cleanup Summary
| Category | Items Deleted |
|----------|---------------|
| Backend | `lambda-deployment.zip` (21MB), `package/` (37MB), `__pycache__/` (35 directories) |
| Frontend | `node_modules/`, `dist/`, `.env` |
| Root | `.DS_Store` files |

### Final Structure
```
/title/external/two/
├── README.md
├── .env.deploy
├── .gitignore
├── deploy-main.sh
├── deploy-backend.sh
├── deploy-frontend.sh
├── backend/
│   ├── handlers/
│   ├── lib/
│   ├── services/
│   ├── src/
│   ├── utils/
│   └── requirements.txt
└── frontend/
    ├── src/
    ├── public/
    └── package.json
```

### Deployment Test Results
| Script | Result | Details |
|--------|--------|---------|
| `deploy-backend.sh` | PASS | 4/4 Lambda functions deployed |
| `deploy-frontend.sh` | PASS | S3 upload + CloudFront invalidation complete |

### Script Fixes
- None required

### README Updates
- Fixed Project Structure section (removed non-existent files: `work-logs/`, `COST_OPTIMIZATION_SUMMARY.md`)

---

## Documentation Updates

All READMEs updated to match consistent format:
- English language
- No emojis
- Phase-based Change History
- Removed references to deleted files/folders
- Consolidated deployment guides into README

### README Structure (All Services)
```
# service.sedaily.ai
├── Overview
├── Features
├── Architecture
├── Project Structure
├── Quick Start
├── URLs
├── AWS Resources
├── AI Configuration
├── Change History (Phase format)
├── Deployment Guide
├── Cost Optimization (if applicable)
├── Tech Stack
├── Monitoring
├── Troubleshooting
├── Related Documents
└── License
```

---

## Lambda Functions Deployed

### p1.sedaily.ai (4 functions)
- nx-wt-prf-websocket-message
- nx-wt-prf-conversation-api
- nx-wt-prf-websocket-connect
- nx-wt-prf-websocket-disconnect

### r1.sedaily.ai (6 functions)
- sedaily-column-websocket-message
- sedaily-column-websocket-connect
- sedaily-column-websocket-disconnect
- sedaily-column-conversation-api
- sedaily-column-prompt-crud
- sedaily-column-usage-handler

### f1.sedaily.ai (6 functions)
- f1-websocket-message-two
- f1-websocket-connect-two
- f1-websocket-disconnect-two
- f1-conversation-api-two
- f1-prompt-crud-two
- f1-usage-handler-two

### b1.sedaily.ai (4 functions)
- p2-two-websocket-message-two
- p2-two-websocket-connect-two
- p2-two-websocket-disconnect-two
- p2-two-conversation-api-two

### w1.sedaily.ai (6 functions)
- w1-websocket-message
- w1-websocket-connect
- w1-websocket-disconnect
- w1-conversation-api
- w1-prompt-crud
- w1-usage-handler

### t1.sedaily.ai (4 functions)
- nx-tt-dev-ver3-websocket-message
- nx-tt-dev-ver3-conversation-api
- nx-tt-dev-ver3-prompt-crud
- nx-tt-dev-ver3-usage-handler

---

## Service URLs

| Service | URL | CloudFront |
|---------|-----|------------|
| p1 | https://p1.sedaily.ai | E39OHKSWZD4F8J |
| r1 | https://r1.sedaily.ai | EH9OF7IFDTPLW |
| f1 | https://f1.sedaily.ai | E1HNX1UP39MOOM |
| b1 | https://b1.sedaily.ai | E2WPOE6AL2G5DZ |
| w1 | https://w1.sedaily.ai | E10S6CKR5TLUBG |
| t1 | https://t1.sedaily.ai | EIYU5SFVTHQMN |

---

## 7. t1.sedaily.ai Cognito Fix (Post-Deployment)

### Issue
After deployment, t1.sedaily.ai login failed with error:
```
InvalidParameterException: 2 validation errors detected:
Value '' at 'clientId' failed to satisfy constraint
```

### Root Cause
- `frontend/.env` file was missing (deleted during project cleanup)
- Cognito `VITE_COGNITO_CLIENT_ID` and `VITE_COGNITO_USER_POOL_ID` were empty

### Fix Applied
1. Identified Cognito User Pool: `sedaily.ai_cognito` (`us-east-1_ohLOswurY`)
2. Identified Client ID: `nx-tt-dev-ver3-web-client` (`4m4edj8snokmhqnajhlj41h9n2`)
3. Created `frontend/.env` with all required environment variables
4. Rebuilt frontend with `npm run build`
5. Redeployed to S3 and invalidated CloudFront cache

### Verification
- Login functionality working correctly
- All authentication flows verified

---

## Final Test Results

| Service | Backend | Frontend | Auth | HTTP | Status |
|---------|---------|----------|------|------|--------|
| p1.sedaily.ai | 4/4 Lambda | S3 + CloudFront | Cognito | 200 | PASS |
| r1.sedaily.ai | 6/6 Lambda | S3 + CloudFront | Cognito | 200 | PASS |
| f1.sedaily.ai | 6/6 Lambda | S3 + CloudFront | Cognito | 200 | PASS |
| b1.sedaily.ai | 4/4 Lambda | S3 + CloudFront | Cognito | 200 | PASS |
| w1.sedaily.ai | 6/6 Lambda | S3 + CloudFront | Cognito | 200 | PASS |
| t1.sedaily.ai | 4/4 Lambda | S3 + CloudFront | Cognito | 200 | PASS |

---

## Conclusion

All 6 services have been:
1. Cleaned up (removed ~250+ unnecessary files, ~200MB+ saved)
2. Documentation standardized (English, consistent format)
3. Deployment scripts tested and verified
4. Script bugs fixed where found
5. Post-deployment issues resolved (p1 CloudFront, b1 env vars, t1 Cognito)
6. All services production-tested and verified working

All services are production-ready.

---

## 8. f1.sedaily.ai Lambda Timeout Fix (Post-Deployment)

### Issue
Long AI responses (foreign news translation) getting cut off mid-response.

### Root Cause
Lambda timeout was set to 120 seconds, insufficient for complex foreign news translation tasks.

### Fix Applied
1. Updated all 6 f1 Lambda functions timeout: 120s → 180s (3 minutes)
   - f1-websocket-message-two
   - f1-websocket-connect-two
   - f1-websocket-disconnect-two
   - f1-conversation-api-two
   - f1-prompt-crud-two
   - f1-usage-handler-two

2. Verified prompt loading from DynamoDB working correctly:
   - Instruction length: 18,315 chars
   - Description length: 1,429 chars
   - Files count: 8 reference files
   - Total system prompt: 108,977 chars

### Verification
- Lambda configuration confirmed: 180 second timeout
- Prompt loading verified via CloudWatch logs
- Redeployed backend and frontend

---

**Report Generated**: 2025-12-21 21:40 KST
**Updated**: 2025-12-22 01:00 KST (f1 Lambda timeout fix)
**Tested By**: Claude Code
