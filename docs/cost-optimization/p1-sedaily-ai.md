# p1.sedaily.ai - Prompt Caching Cost Optimization

Last Updated: 2025-12-22 01:30 KST

## Overview

| Item | Value |
|------|-------|
| Service Name | Proofreading (AI Proofreading Service) |
| URL | https://p1.sedaily.ai |
| Lambda Function | nx-wt-prf-websocket-message |
| Model | Claude Opus 4.5 (claude-opus-4-5-20251101) |
| Region | us-east-1 |
| Cache Status | Active |

---

## Cost Analysis (Before vs After)

### Per Request Cost

| Item | Before (No Cache) | After (Cached) | Savings |
|------|-------------------|----------------|---------|
| System Prompt | 65,153 tokens x $5.00/1M = $0.326 | 65,153 tokens x $0.50/1M = $0.033 | 90% |
| Input Tokens | 4,000 tokens x $5.00/1M = $0.020 | 4,000 tokens x $5.00/1M = $0.020 | - |
| Output Tokens | 150 tokens x $25.00/1M = $0.004 | 150 tokens x $25.00/1M = $0.004 | - |
| **Total** | **$0.350** | **$0.057** | **84%** |

### Monthly Estimate (1,000 requests)

| Scenario | Cost | Savings |
|----------|------|---------|
| Without Cache | $350 | - |
| With Cache | $57 | $293 |

---

## Test History

### 2025-12-22 00:00 KST (Latest)

| # | Time (UTC) | Cache | Input | Output | Cache Read | Cache Write | Cost |
|---|------------|-------|-------|--------|------------|-------------|------|
| 1 | 14:35:57 | MISS | 132 | 306 | 0 | 65,153 | $0.6598 |
| 2 | 14:37:08 | MISS | 2,755 | 648 | 0 | 67,043 | $0.7004 |
| 3 | 14:37:26 | HIT | 3,748 | 850 | 65,153 | 0 | $0.0726 |
| 4 | 14:38:12 | MISS | 2,132 | 859 | 0 | 70,416 | $0.7363 |

**Result**: 1/4 Cache HIT (25%) - Multiple engine types causing MISS

### 2025-12-21 19:56 KST

| # | Time (UTC) | Cache | Input | Output | Cache Read | Cost |
|---|------------|-------|-------|--------|------------|------|
| 1 | 10:56:xx | HIT | - | - | 65,153 | $0.084 |
| 2 | 10:57:xx | HIT | 5,669 | 238 | 65,153 | $0.067 |
| 3 | 10:58:xx | HIT | 4,014 | 169 | 65,153 | $0.057 |
| 4 | 10:59:xx | HIT | 3,354 | 104 | 65,153 | $0.052 |

**Result**: 4/4 Cache HIT (100%)

---

## Caching Architecture

```
System Prompt (Cached) - 65,153 tokens
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
| anthropic_client.py | /nexus/services/proofreading/external/two/backend/lib/anthropic_client.py |
| websocket_service.py | /nexus/services/proofreading/external/two/backend/services/websocket_service.py |

---

## Log Monitoring

```bash
aws logs tail /aws/lambda/nx-wt-prf-websocket-message --region us-east-1 --follow | grep -E "CACHE|HIT|MISS|Token"
```

| Log Pattern | Meaning |
|-------------|---------|
| PROMPT CACHE HIT | Cache hit (90% cost reduction) |
| PROMPT CACHE MISS | Cache miss (first request) |
| Token Usage | Token usage details |

---

## Deployment

```bash
cd /nexus/services/proofreading/external/two
./deploy-anthropic.sh
```

---

## Changelog

### 2025-12-21: Initial caching optimization
- Fixed cache_control: removed invalid ttl parameter
- Separated static/dynamic context
- Moved conversation context to user message
- Verified 100% cache HIT rate
