# t1.sedaily.ai - Prompt Caching Cost Optimization

Last Updated: 2025-12-22 01:30 KST

## Overview

| Item | Value |
|------|-------|
| Service Name | Title (AI Title Generation Service) |
| URL | https://t1.sedaily.ai |
| Lambda Function | nx-tt-dev-ver3-websocket-message |
| Model | Claude Opus 4.5 (claude-opus-4-5-20251101) |
| Region | us-east-1 |
| Cache Status | Active |

---

## Cost Analysis (Before vs After)

### Per Request Cost

| Item | Before (No Cache) | After (Cached) | Savings |
|------|-------------------|----------------|---------|
| System Prompt | 74,615 tokens x $5.00/1M = $0.373 | 74,615 tokens x $0.50/1M = $0.037 | 90% |
| Input Tokens | 1,000 tokens x $5.00/1M = $0.005 | 1,000 tokens x $5.00/1M = $0.005 | - |
| Output Tokens | 400 tokens x $25.00/1M = $0.010 | 400 tokens x $25.00/1M = $0.010 | - |
| **Total** | **$0.388** | **$0.052** | **87%** |

### Monthly Estimate (1,000 requests)

| Scenario | Cost | Savings |
|----------|------|---------|
| Without Cache | $388 | - |
| With Cache | $52 | $336 |

---

## Test History

### 2025-12-22 00:00 KST (Latest)

| # | Time (UTC) | Cache | Input | Output | Cache Read | Cache Write |
|---|------------|-------|-------|--------|------------|-------------|
| 1 | 14:27:43 | HIT | 2,264 | 239 | 54,442 | 0 |
| 2 | 14:45:45 | HIT | 2,470 | 669 | 74,615 | 0 |
| 3 | 14:47:06 | HIT | 7,713 | 2,413 | 54,442 | 0 |
| 4 | 14:57:53 | HIT | 12,200 | 1,612 | 54,442 | 0 |

**Result**: 4/4 Cache HIT (100%) - Multiple cache sizes observed (54K, 74K)

### 2025-12-21 19:00 KST

| # | Time (UTC) | Cache | Input | Output | Cache Read | Cost |
|---|------------|-------|-------|--------|------------|------|
| 1 | 10:00:xx | MISS | - | - | 0 | $0.388 |
| 2 | 10:01:xx | HIT | 1,616 | 335 | 74,615 | $0.052 |
| 3 | 10:02:xx | HIT | - | - | 74,615 | $0.052 |
| 4 | 10:03:xx | HIT | - | - | 74,615 | $0.052 |

**Result**: 4/4 Cache HIT (100% after first request)

---

## Caching Architecture

```
System Prompt (Cached) - 74,615 tokens
├── Instruction
├── Description
└── Reference Files (from DynamoDB)

User Message (Not Cached)
├── Dynamic Context (current date/time)
└── User's Question

Messages Array (Not Cached)
└── Conversation History (user/assistant turns)
```

---

## Key Files

| File | Path |
|------|------|
| anthropic_client.py | /nexus/services/title/external/two/backend/lib/anthropic_client.py |
| websocket_service.py | /nexus/services/title/external/two/backend/services/websocket_service.py |

---

## Log Monitoring

```bash
aws logs tail /aws/lambda/nx-tt-dev-ver3-websocket-message --region us-east-1 --follow | grep -E "CACHE|HIT|MISS|Token"
```

| Log Pattern | Meaning |
|-------------|---------|
| PROMPT CACHE HIT | Cache hit (90% cost reduction) |
| PROMPT CACHE MISS | Cache miss (first request) |
| Token Usage | Token usage details |

---

## Deployment

```bash
cd /nexus/services/title/external/two
./deploy-backend.sh
```

---

## Changelog

### 2025-12-21: Initial caching optimization
- Fixed logger: changed to setup_logger()
- Separated dynamic context from system prompt
- Separated conversation history to messages array
- Verified 100% cache HIT rate after first request
