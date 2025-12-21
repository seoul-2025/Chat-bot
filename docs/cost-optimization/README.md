# Anthropic Prompt Caching - Cost Optimization Report

Last Updated: 2025-12-22 01:00 KST

## Executive Summary

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Monthly Cost (6 services, 1K req each) | $1,389 | $262 | **$1,127 (81%)** |
| Cache HIT Rate | 0% | 100% | - |
| Services Optimized | 0 | 6 | - |

---

## Service Overview

| Service | URL | Document | Cache Status | Test Result |
|---------|-----|----------|--------------|-------------|
| b1 (Buddy) | https://b1.sedaily.ai | [b1-sedaily-ai.md](./b1-sedaily-ai.md) | Active | 4/4 HIT |
| p1 (Proofreading) | https://p1.sedaily.ai | [p1-sedaily-ai.md](./p1-sedaily-ai.md) | Active | 4/4 HIT |
| r1 (Column) | https://r1.sedaily.ai | [r1-sedaily-ai.md](./r1-sedaily-ai.md) | Active | 4/4 HIT |
| w1 (Bodo) | https://w1.sedaily.ai | [w1-sedaily-ai.md](./w1-sedaily-ai.md) | Active | 4/4 HIT |
| t1 (Title) | https://t1.sedaily.ai | [t1-sedaily-ai.md](./t1-sedaily-ai.md) | Active | 4/4 HIT |
| f1 (Foreign) | https://f1.sedaily.ai | [f1-sedaily-ai.md](./f1-sedaily-ai.md) | Active | 4/4 HIT |

---

## Cost Comparison (Before vs After)

### Per Request Cost

| Service | Cached Tokens | Before | After | Savings |
|---------|---------------|--------|-------|---------|
| b1 | 18,614 | $0.111 | $0.027 | 76% |
| p1 | 65,153 | $0.350 | $0.057 | 84% |
| r1 | 7,232 | $0.064 | $0.032 | 50% |
| w1 | 19,476 | $0.117 | $0.030 | 74% |
| t1 | 74,615 | $0.388 | $0.052 | 87% |
| f1 | 63,409 | $0.349 | $0.064 | 82% |

### Monthly Estimate (1,000 requests per service)

| Service | Before | After | Savings |
|---------|--------|-------|---------|
| b1 | $111 | $27 | $84 |
| p1 | $350 | $57 | $293 |
| r1 | $64 | $32 | $32 |
| w1 | $117 | $30 | $87 |
| t1 | $388 | $52 | $336 |
| f1 | $349 | $64 | $285 |
| **Total** | **$1,379** | **$262** | **$1,117** |

---

## Anthropic Pricing Reference (Claude Opus 4.5)

| Token Type | Price (per 1M tokens) |
|------------|----------------------|
| Input Tokens | $5.00 |
| Output Tokens | $25.00 |
| Cache Read | $0.50 (90% discount) |
| Cache Write | $10.00 |

---

## Caching Architecture

```
+----------------------------------------------------------+
|                 System Prompt (Cached)                    |
|  +-------------+ +-------------+ +---------------------+  |
|  | Instruction | | Description | | Files (DynamoDB)    |  |
|  +-------------+ +-------------+ +---------------------+  |
|  cache_control: { "type": "ephemeral" }                   |
+----------------------------------------------------------+
                            |
                            v
+----------------------------------------------------------+
|                 User Message (Not Cached)                 |
|  +------------------------+ +---------------------------+ |
|  | Dynamic Context        | | User's Actual Question    | |
|  | (current date/time)    | |                           | |
|  +------------------------+ +---------------------------+ |
+----------------------------------------------------------+
                            |
                            v
+----------------------------------------------------------+
|                 Messages Array (Not Cached)               |
|  +------------------------------------------------------+ |
|  | Conversation History (user/assistant turns)          | |
|  +------------------------------------------------------+ |
+----------------------------------------------------------+
```

---

## Key Principles

### 1. Static/Dynamic Separation
- Static content -> system_prompt (cached)
- Dynamic content -> user_message (not cached)

### 2. Conversation History Separation
- Do NOT include in system_prompt
- Pass as messages array

### 3. Cache Efficiency
- Same system_prompt = Same cache key
- Cache persists even as conversation grows

---

## Log Monitoring Commands

```bash
# b1 (buddy)
aws logs tail /aws/lambda/p2-two-websocket-message-two --region us-east-1 --follow | grep -E "CACHE|HIT|MISS|Token"

# p1 (proofreading)
aws logs tail /aws/lambda/nx-wt-prf-websocket-message --region us-east-1 --follow | grep -E "CACHE|HIT|MISS|Token"

# r1 (column)
aws logs tail /aws/lambda/sedaily-column-websocket-message --region us-east-1 --follow | grep -E "CACHE|HIT|MISS|Token"

# w1 (bodo)
aws logs tail /aws/lambda/w1-websocket-message --region us-east-1 --follow | grep -E "CACHE|HIT|MISS|Token"

# t1 (title)
aws logs tail /aws/lambda/nx-tt-dev-ver3-websocket-message --region us-east-1 --follow | grep -E "CACHE|HIT|MISS|Token"

# f1 (foreign)
aws logs tail /aws/lambda/f1-websocket-message-two --region us-east-1 --follow | grep -E "CACHE|HIT|MISS|Token"
```

---

## Log Patterns

| Log Pattern | Meaning |
|-------------|---------|
| PROMPT CACHE MISS | First request, cache created |
| PROMPT CACHE HIT | Cache hit (90% cost reduction) |
| Token Usage | Token usage details |
| cache_read > 0 | Cache hit |
| cache_write > 0 | New cache created |

---

## Test History

### 2025-12-21

| Service | Time (KST) | Result | Cache Tokens |
|---------|------------|--------|--------------|
| b1 | 20:00 | 4/4 HIT | 18,614 |
| p1 | 19:56 | 4/4 HIT | 65,153 |
| r1 | 19:49 | 4/4 HIT | 7,232 |
| w1 | 20:14 | 4/4 HIT | 19,476 |
| t1 | 19:00 | 4/4 HIT | 74,615 |
| f1 | 19:49 | 4/4 HIT | 63,409 |

---

## Changelog

### 2025-12-22: f1 Lambda Timeout Fix
- Issue: Long AI responses (foreign news translation) getting cut off mid-response
- Root cause: Lambda timeout was 120 seconds (insufficient for complex translations)
- Fix: Updated all 6 f1 Lambda functions timeout: 120s → 180s (3 minutes)
- Verified prompt loading from DynamoDB working correctly

### 2025-12-21: All 6 services optimized

#### w1 (Bodo) - 20:15 KST
- Fixed: conversation_context included in system_prompt (cache invalidation)
- Solution: Separated conversation_history to messages array
- Fixed cache_control: removed invalid ttl parameter
- Result: 100% cache HIT after first request

#### b1 (Buddy) - 20:00 KST
- Added anthropic-beta header for prompt caching
- Enhanced dynamic context separation
- Added cache HIT/MISS tracking logs
- Result: 100% cache HIT after first request

#### p1, r1, t1, f1 - 19:00~19:56 KST
- Fixed logger: changed to setup_logger()
- Fixed cache_control: removed invalid ttl parameter
- Separated dynamic context from system prompt
- Separated conversation history to messages array
- Result: 100% cache HIT after first request
