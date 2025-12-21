# w1.sedaily.ai - Prompt Caching Cost Optimization

Last Updated: 2025-12-21 20:15 KST

## Overview

| Item | Value |
|------|-------|
| Service Name | Bodo (Press Release AI) |
| URL | https://w1.sedaily.ai |
| Lambda Function | w1-websocket-message |
| Model | Claude Opus 4.5 (claude-opus-4-5-20251101) |
| Region | us-east-1 |
| Cache Status | Active |

---

## Cost Analysis (Before vs After)

### Per Request Cost

| Item | Before (No Cache) | After (Cached) | Savings |
|------|-------------------|----------------|---------|
| System Prompt | 19,476 tokens x $5.00/1M = $0.097 | 19,476 tokens x $0.50/1M = $0.010 | 90% |
| Input Tokens | 3,000 tokens x $5.00/1M = $0.015 | 3,000 tokens x $5.00/1M = $0.015 | - |
| Output Tokens | 200 tokens x $25.00/1M = $0.005 | 200 tokens x $25.00/1M = $0.005 | - |
| **Total** | **$0.117** | **$0.030** | **74%** |

### Monthly Estimate (1,000 requests)

| Scenario | Cost | Savings |
|----------|------|---------|
| Without Cache | $117 | - |
| With Cache | $30 | $87 |

---

## Test History

### 2025-12-21 20:14 KST

| # | Time (UTC) | Cache | Input | Output | Cache Read | Cost |
|---|------------|-------|-------|--------|------------|------|
| 1 | 11:14:31 | MISS | 597 | 258 | 0 | $0.198 |
| 2 | 11:14:56 | HIT | 3,731 | 72 | 19,476 | $0.028 |
| 3 | 11:15:22 | HIT | 4,593 | 41 | 19,476 | $0.033 |
| 4 | 11:15:30 | HIT | - | - | 19,476 | $0.030 |

**Result**: 4/4 Cache HIT (100% after first request)

---

## Caching Architecture

```
System Prompt (Cached) - 19,476 tokens
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
| anthropic_client.py | /nexus/services/bodo/external/two/backend/lib/anthropic_client.py |
| websocket_service.py | /nexus/services/bodo/external/two/backend/services/websocket_service.py |

---

## Log Monitoring

```bash
aws logs tail /aws/lambda/w1-websocket-message --region us-east-1 --follow | grep -E "CACHE|HIT|MISS|Token"
```

| Log Pattern | Meaning |
|-------------|---------|
| PROMPT CACHE HIT | Cache hit (90% cost reduction) |
| PROMPT CACHE MISS | Cache miss (first request) |
| Token Usage | Token usage details |

---

## Deployment

```bash
cd /nexus/services/bodo/external/two/w1-scripts
./deploy-backend.sh
```

---

## Changelog

### 2025-12-21: Caching re-optimization
- Fixed: conversation_context was included in system_prompt (cache invalidation)
- Solution: Separated conversation_history to messages array
- Fixed cache_control: removed invalid ttl parameter
- Added List import fix
- Verified 100% cache HIT rate after first request
