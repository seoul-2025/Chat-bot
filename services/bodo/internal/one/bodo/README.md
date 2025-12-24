# BODO Internal Service

AI Press Release Service - Internal Version (No Login, No Sidebar)

Last Updated: 2025-12-24

## Overview

This is the **internal version** of the BODO AI press release service. It shares the same backend as `w1.sedaily.ai` but has a simplified frontend without login and sidebar functionality. Users are directed straight to the chat interface.

**Live URL:** https://d2emwatb21j743.cloudfront.net

## Comparison with w1.sedaily.ai

| Feature | external/two (w1.sedaily.ai) | internal/one (this service) |
|---------|------------------------------|------------------------------|
| Purpose | Public/External | Internal |
| Login | Required | Not required |
| Sidebar | Yes | No |
| Direct to Chat | No (via landing) | Yes |
| Domain | w1.sedaily.ai | d2emwatb21j743.cloudfront.net |
| S3 Bucket | w1-sedaily-frontend | bodo-frontend-20251204-230645dc |
| CloudFront | E10S6CKR5TLUBG (us-east-1) | EDF1H6DB796US (ap-northeast-2) |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Separate)                       │
├─────────────────────────────────────────────────────────────┤
│  internal/one                    external/two                │
│  ├─ S3: bodo-frontend-*          ├─ S3: w1-sedaily-frontend │
│  ├─ CloudFront: EDF1H6DB796US    ├─ CloudFront: E10S6CKR5TLUBG│
│  └─ Region: ap-northeast-2       └─ Region: us-east-1       │
│                                                              │
│  Features:                       Features:                   │
│  - No login                      - Login required            │
│  - No sidebar                    - Sidebar enabled           │
│  - Direct to /11 chat            - Landing page              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Shared)                          │
├─────────────────────────────────────────────────────────────┤
│  API Gateway (us-east-1)                                     │
│  ├─ REST API: 16ayefk5lc                                    │
│  └─ WebSocket: prsebeg7ub                                   │
│                                                              │
│  Lambda Functions (us-east-1)                                │
│  ├─ w1-websocket-message (Claude Opus 4.5 + Web Search)     │
│  ├─ w1-websocket-connect                                    │
│  ├─ w1-websocket-disconnect                                 │
│  ├─ w1-conversation-api                                     │
│  ├─ w1-prompt-crud                                          │
│  └─ w1-usage-handler                                        │
│                                                              │
│  DynamoDB Tables (us-east-1)                                 │
│  ├─ w1-conversations                                        │
│  ├─ w1-messages                                             │
│  ├─ w1-prompts                                              │
│  ├─ w1-usage                                                │
│  └─ w1-connections                                          │
│                                                              │
│  AI: Claude Opus 4.5 (Anthropic API)                        │
│  Secrets: bodo-v1 (Anthropic API Key)                       │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
.
├── README.md
├── backend/                    # Shared with w1.sedaily.ai
│   ├── handlers/
│   ├── lib/
│   ├── services/
│   └── requirements.txt
├── frontend/                   # Modified for internal use
│   ├── src/
│   │   ├── App.jsx            # No ProtectedRoute, sidebar disabled
│   │   └── ...
│   ├── .env
│   └── package.json
└── w1-scripts/
    ├── config.sh              # Frontend: ap-northeast-2
    ├── deploy-frontend.sh     # Deploy to internal CloudFront
    └── deploy-backend.sh      # Deploy to shared Lambda (us-east-1)
```

## Quick Start

### Prerequisites
- AWS CLI configured with appropriate credentials
- Node.js 18+
- Python 3.11+

### Frontend Deployment

```bash
cd w1-scripts

# Deploy frontend (builds, uploads to S3, invalidates CloudFront)
./deploy-frontend.sh

# Auto-confirm mode
./deploy-frontend.sh -y
```

### Backend Deployment

> **Note:** Backend is shared with w1.sedaily.ai. Deploy carefully.

```bash
cd w1-scripts
./deploy-backend.sh
```

### Log Monitoring

```bash
# Real-time Lambda logs
aws logs tail /aws/lambda/w1-websocket-message --follow --region us-east-1
```

## AWS Resources

### Frontend Resources (internal/one only)

| Resource | Value | Region |
|----------|-------|--------|
| S3 Bucket | bodo-frontend-20251204-230645dc | ap-northeast-2 |
| CloudFront | EDF1H6DB796US | ap-northeast-2 |
| Domain | d2emwatb21j743.cloudfront.net | - |

### Shared Backend Resources

| Resource | Value | Region |
|----------|-------|--------|
| REST API | 16ayefk5lc | us-east-1 |
| WebSocket API | prsebeg7ub | us-east-1 |
| Lambda Functions | w1-* | us-east-1 |
| DynamoDB Tables | w1-* | us-east-1 |
| Secrets Manager | bodo-v1 | us-east-1 |
| IAM Role | w1-lambda-execution-role | us-east-1 |

## AI Configuration

| Setting | Value |
|---------|-------|
| Provider | Anthropic API (Primary) |
| Model | claude-opus-4-5-20251101 |
| Max Tokens | 4096 |
| Temperature | 0.3 |
| Fallback | AWS Bedrock |
| Web Search | Enabled (web_search_20250305) |
| Prompt Caching | Enabled (90% cost reduction) |

## Frontend Modifications

The following changes were made to create the internal version:

1. **ProtectedRoute Removed** - `/11`, `/22`, `/11/chat/*`, `/22/chat/*` routes no longer require login
2. **Sidebar Disabled** - `showSidebar = false` in App.jsx
3. **Login Button Hidden** - Header shows no login button for logged-out users
4. **Direct Redirect** - `/` redirects directly to `/11` (no landing page)
5. **LandingPage Removed** - Unused import removed from App.jsx

## Change History

### Phase 1: Initial Setup & Sync (2025-12-24)

**Objective:** Create internal version by syncing with external/two and modifying frontend

**Tasks Completed:**
1. Synced codebase from `external/two` to `internal/one`
2. Removed unnecessary documentation files:
   - DEPLOYMENT.md
   - W1_SERVICE_MAPPING.md
   - infrastructure/
   - frontend/deploy/
3. Copied README.md and .gitignore from external/two
4. Updated backend code:
   - Added citation_formatter.py
   - Updated anthropic_client.py (Prompt Caching, Web Search)
   - Updated websocket_service.py (permanent cache)
   - Removed unused files (prompt.py, usage.py, etc.)

### Phase 2: Frontend Customization (2025-12-24)

**Objective:** Remove login/sidebar for internal use

**Tasks Completed:**
1. Removed ProtectedRoute from main routes:
   - `/11` - MainContent without auth check
   - `/22` - MainContent without auth check
   - `/11/chat/:conversationId?` - ChatPage without auth check
   - `/22/chat/:conversationId?` - ChatPage without auth check
2. Disabled sidebar: `showSidebar = false`
3. Hidden login button in Header for logged-out users
4. Removed unused LandingPage import
5. Updated route `/` to redirect directly to `/11`

### Phase 3: AWS Configuration (2025-12-24)

**Objective:** Configure separate frontend deployment

**Tasks Completed:**
1. Updated config.sh:
   - AWS_REGION: ap-northeast-2 (for frontend)
   - DOMAIN: d2emwatb21j743.cloudfront.net
   - FRONTEND_BUCKET: bodo-frontend-20251204-230645dc
   - CLOUDFRONT_ID: EDF1H6DB796US
   - Shared backend resources remain unchanged (us-east-1)
2. Updated .env:
   - VITE_CLOUDFRONT_DOMAIN: d2emwatb21j743.cloudfront.net

### Phase 4: Deployment Script Update (2025-12-24)

**Objective:** Fix MIME type issues and update scripts

**Tasks Completed:**
1. Updated deploy-frontend.sh:
   - Added correct MIME type for JavaScript files (application/javascript)
   - Separated JS file upload with proper content-type header
   - Updated header comments and output messages
2. Updated config.sh with clear documentation
3. Created this README.md with full change history

## Troubleshooting

### JavaScript MIME Type Error

If you see "Expected a JavaScript module script but the server responded with a MIME type of text/html":

1. Re-run deployment script which now sets correct MIME type
2. Verify S3 file content-type: `aws s3api head-object --bucket bodo-frontend-20251204-230645dc --key assets/index-xxx.js`
3. Invalidate CloudFront cache if needed

### Still Redirecting to Login

1. Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)
2. Try incognito mode
3. Verify latest code is deployed:
   ```bash
   curl -s https://d2emwatb21j743.cloudfront.net/ | grep "index-"
   ```

### CloudFront Cache Not Updating

```bash
aws cloudfront create-invalidation \
    --distribution-id EDF1H6DB796US \
    --paths "/*" \
    --region ap-northeast-2
```

## Security Notes

- **Backend is shared** - Changes to Lambda/DynamoDB affect both services
- **Frontend is separate** - S3/CloudFront changes only affect this service
- **No authentication** - This service has no login requirement (internal use only)
- **API Keys** - Managed via AWS Secrets Manager (bodo-v1)

## License

Proprietary - Seoul Economic Daily
