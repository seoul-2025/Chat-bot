# b1.sedaily.ai - Prompt Caching Cost Optimization

Last Updated: 2025-12-22 01:30 KST

## Overview

| Item | Value |
|------|-------|
| Service Name | Buddy (AI Assistant) |
| URL | https://b1.sedaily.ai |
| Lambda Function | p2-two-websocket-message-two |
| Model | Claude Opus 4.5 (claude-opus-4-5-20251101) |
| Region | us-east-1 |
| Cache Status | Active |

---

## Cost Analysis (Before vs After)

### Per Request Cost

| Item | Before (No Cache) | After (Cached) | Savings |
|------|-------------------|----------------|---------|
| System Prompt | 18,614 tokens x $5.00/1M = $0.093 | 18,614 tokens x $0.50/1M = $0.009 | 90% |
| Input Tokens | 1,000 tokens x $5.00/1M = $0.005 | 1,000 tokens x $5.00/1M = $0.005 | - |
| Output Tokens | 500 tokens x $25.00/1M = $0.013 | 500 tokens x $25.00/1M = $0.013 | - |
| **Total** | **$0.111** | **$0.027** | **76%** |

### Monthly Estimate (1,000 requests)

| Scenario | Cost | Savings |
|----------|------|---------|
| Without Cache | $111 | - |
| With Cache | $27 | $84 |

---

## Test History

### 2025-12-22 00:00 KST (Latest)

| # | Time (UTC) | Cache | Input | Output | Cache Read | Cost |
|---|------------|-------|-------|--------|------------|------|
| 1 | 14:46:02 | HIT | 933 | 2 | 19,343 | $0.0144 |
| 2 | 14:46:41 | HIT | 2,152 | 1 | 19,343 | $0.0205 |

**Result**: 2/2 Cache HIT (100%)

### 2025-12-21 20:00 KST

| # | Time (UTC) | Cache | Input | Output | Cache Read | Cost |
|---|------------|-------|-------|--------|------------|------|
| 1 | 10:59:07 | MISS | 925 | 2 | 0 | $0.099 |
| 2 | 10:59:16 | HIT | 1,230 | 1 | 18,614 | $0.015 |
| 3 | 11:00:15 | HIT | 4,470 | 82 | 18,614 | $0.032 |
| 4 | 11:04:48 | HIT | 1,434 | 110 | 18,614 | $0.017 |

**Result**: 4/4 Cache HIT (100% after first request)

---

## Caching Architecture

```
System Prompt (Cached) - 18,614 tokens
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
| anthropic_client.py | /nexus/services/buddy/external/two/backend/lib/anthropic_client.py |
| websocket_service.py | /nexus/services/buddy/external/two/backend/services/websocket_service.py |

---

## Log Monitoring

```bash
aws logs tail /aws/lambda/p2-two-websocket-message-two --region us-east-1 --follow | grep -E "CACHE|HIT|MISS|Token"
```

| Log Pattern | Meaning |
|-------------|---------|
| PROMPT CACHE HIT | Cache hit (90% cost reduction) |
| PROMPT CACHE MISS | Cache miss (first request) |
| Token Usage | Token usage details |

---

## Deployment

```bash
cd /nexus/services/buddy/external/two/w1-scripts
./deploy-backend.sh
```

---

## Changelog

### 2025-12-21: Initial caching optimization
- Added anthropic-beta header for prompt caching
- Enhanced dynamic context separation
- Added cache HIT/MISS tracking logs
- Verified 100% cache HIT rate after first request
