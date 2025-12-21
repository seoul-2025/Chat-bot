# r1.sedaily.ai - Prompt Caching Cost Optimization

Last Updated: 2025-12-22 01:30 KST

## Overview

| Item | Value |
|------|-------|
| Service Name | Column (AI Column Writing Service) |
| URL | https://r1.sedaily.ai |
| Lambda Function | sedaily-column-websocket-message |
| Model | Claude Opus 4.5 (claude-opus-4-5-20251101) |
| Region | us-east-1 |
| Cache Status | Active |

---

## Cost Analysis (Before vs After)

### Per Request Cost

| Item | Before (No Cache) | After (Cached) | Savings |
|------|-------------------|----------------|---------|
| System Prompt | 7,232 tokens x $5.00/1M = $0.036 | 7,232 tokens x $0.50/1M = $0.004 | 90% |
| Input Tokens | 2,500 tokens x $5.00/1M = $0.013 | 2,500 tokens x $5.00/1M = $0.013 | - |
| Output Tokens | 600 tokens x $25.00/1M = $0.015 | 600 tokens x $25.00/1M = $0.015 | - |
| **Total** | **$0.064** | **$0.032** | **50%** |

### Monthly Estimate (1,000 requests)

| Scenario | Cost | Savings |
|----------|------|---------|
| Without Cache | $64 | - |
| With Cache | $32 | $32 |

---

## Test History

### 2025-12-22 00:00 KST (Latest)

| # | Time (UTC) | Cache | Input | Output | Cache Read | Cache Write | Cost |
|---|------------|-------|-------|--------|------------|-------------|------|
| 1 | 14:43:03 | MISS | 22,911 | 2,319 | 0 | 9,393 | $0.2665 |
| 2 | 14:44:28 | HIT | 5,876 | 835 | 7,232 | 0 | $0.0539 |

**Result**: 1/2 Cache HIT (50%) - MISS due to cold start

### 2025-12-21 19:49 KST

| # | Time (UTC) | Cache | Input | Output | Cache Read | Cost |
|---|------------|-------|-------|--------|------------|------|
| 1 | 10:49:xx | MISS | 589 | 940 | 0 | $0.099 |
| 2 | 10:50:xx | HIT | 3,657 | 85 | 7,232 | $0.024 |
| 3 | 10:51:xx | HIT | 2,787 | 962 | 7,232 | $0.042 |
| 4 | 10:52:xx | HIT | 2,227 | 581 | 7,232 | $0.029 |

**Result**: 4/4 Cache HIT (100% after first request)

---

## Caching Architecture

```
System Prompt (Cached) - 7,232 tokens
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
| anthropic_client.py | /nexus/services/regression/external/two/backend/lib/anthropic_client.py |
| websocket_service.py | /nexus/services/regression/external/two/backend/services/websocket_service.py |

---

## Log Monitoring

```bash
aws logs tail /aws/lambda/sedaily-column-websocket-message --region us-east-1 --follow | grep -E "CACHE|HIT|MISS|Token"
```

| Log Pattern | Meaning |
|-------------|---------|
| PROMPT CACHE HIT | Cache hit (90% cost reduction) |
| PROMPT CACHE MISS | Cache miss (first request) |
| Token Usage | Token usage details |

---

## Deployment

```bash
cd /nexus/services/regression/external/two/backend/scripts
./05-deploy-lambda.sh
```

---

## Changelog

### 2025-12-21: Initial caching optimization
- Fixed logger: changed to setup_logger()
- Fixed cache_control: removed invalid ttl parameter
- Improved SSE parsing for cache usage extraction
- Separated conversation context from system prompt
- Verified 100% cache HIT rate after first request
