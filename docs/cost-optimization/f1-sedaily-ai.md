# f1.sedaily.ai - Prompt Caching Cost Optimization

Last Updated: 2025-12-22 01:30 KST

## Overview

| Item | Value |
|------|-------|
| Service Name | Foreign (AI Foreign News Service) |
| URL | https://f1.sedaily.ai |
| Lambda Function | f1-websocket-message-two |
| Model | Claude Opus 4.5 (claude-opus-4-5-20251101) |
| Region | us-east-1 |
| Cache Status | Active |

---

## Cost Analysis (Before vs After)

### Per Request Cost

| Item | Before (No Cache) | After (Cached) | Savings |
|------|-------------------|----------------|---------|
| System Prompt | 63,409 tokens x $5.00/1M = $0.317 | 63,409 tokens x $0.50/1M = $0.032 | 90% |
| Input Tokens | 1,400 tokens x $5.00/1M = $0.007 | 1,400 tokens x $5.00/1M = $0.007 | - |
| Output Tokens | 1,000 tokens x $25.00/1M = $0.025 | 1,000 tokens x $25.00/1M = $0.025 | - |
| **Total** | **$0.349** | **$0.064** | **82%** |

### Monthly Estimate (1,000 requests)

| Scenario | Cost | Savings |
|----------|------|---------|
| Without Cache | $349 | - |
| With Cache | $64 | $285 |

---

## Test History

### 2025-12-22 00:00 KST (Latest)

| # | Time (UTC) | Cache | Input | Output | Cache Read | Cache Write |
|---|------------|-------|-------|--------|------------|-------------|
| 1 | 15:00:51 | MISS | 589 | 321 | 0 | 64,563 |
| 2 | 14:54:43 | HIT | 1,968 | 896 | 63,409 | 0 |
| 3 | 14:56:28 | HIT | 5,835 | 1,892 | 63,409 | 0 |

**Result**: 2/3 Cache HIT (67%) - MISS due to cold start

### 2025-12-21 19:49 KST

| # | Time (UTC) | Cache | Input | Output | Cache Read | Cost |
|---|------------|-------|-------|--------|------------|------|
| 1 | 10:49:54 | HIT | 2,740 | 411 | 63,409 | $0.064 |
| 2 | 10:50:31 | HIT | 3,227 | 1,600 | 63,409 | $0.072 |
| 3 | 10:50:46 | HIT | 4,893 | 301 | 63,409 | $0.064 |
| 4 | 10:51:12 | HIT | 5,267 | 485 | 63,409 | $0.067 |

**Result**: 4/4 Cache HIT (100%)

---

## Caching Architecture

```
System Prompt (Cached) - 63,409 tokens
├── Instruction
├── Description
└── Reference Files (from DynamoDB) - 8 files

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
| anthropic_client.py | /nexus/services/foreign/external/two/backend/lib/anthropic_client.py |
| websocket_service.py | /nexus/services/foreign/external/two/backend/services/websocket_service.py |

---

## Log Monitoring

```bash
aws logs tail /aws/lambda/f1-websocket-message-two --region us-east-1 --follow | grep -E "CACHE|HIT|MISS|Token"
```

| Log Pattern | Meaning |
|-------------|---------|
| PROMPT CACHE HIT | Cache hit (90% cost reduction) |
| PROMPT CACHE MISS | Cache miss (first request) |
| Token Usage | Token usage details |

---

## Deployment

```bash
cd /nexus/services/foreign/external/two
./upgrade-f1-anthropic.sh
```

---

## Changelog

### 2025-12-22: Lambda Timeout Fix
- Increased Lambda timeout: 120s → 180s (3 minutes)
- Issue: Long AI responses (foreign news translation) getting cut off
- All 6 Lambda functions updated
- Verified prompt loading from DynamoDB:
  - Instruction: 18,315 chars
  - Files: 8 reference files
  - Total system prompt: 108,977 chars

### 2025-12-21: Initial caching optimization
- Fixed logger: changed to setup_logger()
- Separated dynamic context from system prompt
- Added conversation_history parameter to stream_anthropic_response()
- Removed conversation_context from _build_system_prompt()
- Verified 100% cache HIT rate
