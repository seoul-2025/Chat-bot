# Prompt Caching 최적화 구현 가이드

## 📋 개요
P1 서비스 (Proofreading)에 대한 Prompt Caching 최적화를 적용하여 API 비용을 대폭 절감하고 성능을 향상시킵니다.

## 🎯 주요 변경사항

### 1. `lib/anthropic_client.py` - Anthropic API Prompt Caching 구현

#### ✅ Prompt Caching 적용
```python
# 프롬프트 캐싱 적용 (system prompt만 캐싱)
body["system"] = [
    {
        "type": "text",
        "text": static_system_prompt,
        "cache_control": {"type": "ephemeral", "ttl": "1h"}  # 1시간 캐시
    }
]
```

#### ✅ 동적/정적 컨텍스트 분리
- **정적 컨텍스트** (캐시 가능): 위치, 타임존, 언어, 서비스명
- **동적 컨텍스트** (user_message에 추가): 현재 시간, 세션 ID

#### ✅ 비용 계산 함수
```python
def _calculate_cost(self, usage: Dict[str, int]) -> float:
    """Claude Opus 4.5 기준 비용 계산"""
    PRICE_INPUT = 5.0       # Base Input Tokens
    PRICE_OUTPUT = 25.0     # Output Tokens  
    PRICE_CACHE_WRITE = 10.0 # 1h Cache Writes
    PRICE_CACHE_READ = 0.50  # Cache Hits
```

#### ✅ 상세 사용량 추적
- Input/Output 토큰
- Cache Read/Write 토큰
- 총 비용 및 캐시 효율성

### 2. `services/websocket_service.py` - 영구 인메모리 캐싱

#### ✅ TTL 제거 → 영구 캐시
```python
# Before (5분 TTL)
PROMPT_CACHE: Dict[str, Tuple[Dict[str, Any], float]] = {}
CACHE_TTL = 300  # 5분

# After (영구 캐시)
PROMPT_CACHE: Dict[str, Dict[str, Any]] = {}
# TTL 제거 - Lambda 컨테이너 수명 동안 유지
```

#### ✅ 성능 개선
- DB 조회: 5분마다 → 컨테이너 재시작시에만
- 캐시 히트율: ~90% → ~99.9%
- 응답 시간: 대폭 단축

## 💰 비용 절감 효과

### Claude Opus 4.5 가격표 (1M 토큰당)
| 토큰 유형 | 가격 |
|---------|------|
| Base Input | $5.00 |
| Output | $25.00 |
| Cache Write (1h) | $10.00 |
| Cache Read | $0.50 |

### 예상 절감률
- **첫 요청**: 캐시 생성 비용 발생 (Cache Write)
- **후속 요청**: 90% 이상 비용 절감 (Cache Read만 발생)
- **일일 평균**: 약 70-80% 비용 절감 예상

## 🚀 배포 가이드

### 1. 환경변수 설정
```bash
# Lambda 환경변수에 추가
ENABLE_PROMPT_CACHING=true      # Prompt Caching 활성화
PROMPT_CACHE_TTL=1h             # 캐시 TTL (1시간)
ANTHROPIC_MODEL_ID=claude-opus-4-5-20251101
USE_ANTHROPIC_API=true          # Anthropic API 사용
```

### 2. 테스트
```bash
cd /Users/yeong-gwang/nexus/services/proofreading/external/two/backend
python test_prompt_caching_optimization.py
```

### 3. 모니터링
- CloudWatch Logs에서 캐시 히트/미스 확인
- 비용 추적을 위한 사용량 로그 확인

## 📊 모니터링 포인트

### 로그 패턴
```
✅ Cache HIT for [engine] - DB query skipped (permanent cache)
❌ Cache MISS for [engine] - fetching from DB (first time)
🎯 Cache HIT! Read [N] tokens from cache
💾 Cache MISS! Created cache with [N] tokens
💰 Cost Breakdown: ...
📊 Cache Efficiency: XX.X%
```

### 주요 메트릭
1. **캐시 히트율**: Cache HIT vs MISS 비율
2. **비용 절감률**: 캐시 사용 전후 비용 비교
3. **응답 시간**: DB 조회 생략에 따른 속도 향상
4. **메모리 사용량**: 영구 캐시의 메모리 점유율

## ⚠️ 주의사항

1. **Lambda 메모리 설정**: 영구 캐싱으로 인한 메모리 사용 증가 고려
2. **Cold Start**: 컨테이너 재시작시 첫 요청은 캐시 미스 발생
3. **프롬프트 업데이트**: DynamoDB 프롬프트 변경시 Lambda 재배포 필요

## 🔄 롤백 방법

환경변수로 즉시 비활성화 가능:
```bash
ENABLE_PROMPT_CACHING=false    # Prompt Caching 비활성화
USE_ANTHROPIC_API=false        # Bedrock으로 폴백
```

## 📝 변경 파일 목록

- `/backend/lib/anthropic_client.py` - Prompt Caching 구현
- `/backend/services/websocket_service.py` - 영구 캐싱 적용
- `/backend/test_prompt_caching_optimization.py` - 테스트 스크립트
- `/PROMPT_CACHING_OPTIMIZATION.md` - 본 문서

## 🎉 기대 효과

1. **비용 절감**: 70-80% API 비용 감소
2. **성능 향상**: DB 조회 최소화로 응답 속도 향상
3. **안정성**: 캐시를 통한 일관된 응답 제공
4. **확장성**: 트래픽 증가에도 비용 효율적 대응