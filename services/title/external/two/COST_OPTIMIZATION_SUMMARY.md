# 비용 최적화 구현 요약

## 적용된 최적화 내역

### 1. `backend/lib/anthropic_client.py` 변경사항

#### 1.1 Prompt Caching 구현
- **시스템 프롬프트 캐싱**: 1시간 TTL (ephemeral cache)
- **API 요청 시 cache_control 추가**
```python
"system": [
    {
        "type": "text",
        "text": static_prompt,
        "cache_control": {"type": "ephemeral", "ttl": "1h"}
    }
]
```

#### 1.2 비용 계산 함수 추가
- Claude Opus 4.5 기준 비용 상수 정의
- `calculate_cost()` 함수로 실시간 비용 추적
- 토큰별 세분화된 비용 계산 (input, output, cache_read, cache_write)

#### 1.3 Usage 추적 및 로깅
- 스트리밍 응답 중 usage 정보 수집
- 상세한 비용 로그 출력 (💰 API Cost)
- `get_last_usage()` 메서드로 마지막 사용량 조회 가능

#### 1.4 동적/정적 컨텍스트 분리
- **정적 컨텍스트**: `replace_template_variables()` - 캐싱 가능
  - 사용자 위치: 대한민국
  - 타임존: Asia/Seoul (KST)
  
- **동적 컨텍스트**: `create_dynamic_context()` - user_message에 추가
  - 현재 시간
  - 세션 ID

### 2. `backend/services/websocket_service.py` 변경사항

#### 2.1 영구 캐시 구현
- **Before**: 5분 TTL 캐시 (`CACHE_TTL = 300`)
- **After**: 영구 캐시 (TTL 제거)
- Lambda 컨테이너 수명 동안 DB 조회 0회

#### 2.2 캐시 로직 간소화
```python
# Before
PROMPT_CACHE: Dict[str, Tuple[Dict[str, Any], float]] = {}

# After  
PROMPT_CACHE: Dict[str, Dict[str, Any]] = {}
```
- 타임스탬프 관리 불필요
- 만료 체크 로직 제거

#### 2.3 Anthropic API 호출 시 캐싱 활성화
```python
enable_caching=True  # 프롬프트 캐싱 활성화
```

## 성능 개선 효과

### 비용 절감
1. **프롬프트 캐싱**: 
   - 캐시 히트 시 $0.50/1M tokens (vs $5.00/1M tokens)
   - **90% 비용 절감**

2. **DB 조회 감소**:
   - 5분마다 조회 → 컨테이너 재시작 시에만
   - DynamoDB 읽기 비용 대폭 감소

### 응답 속도 개선
- 캐시된 프롬프트 사용 시 초기 처리 시간 단축
- DB 조회 지연 제거

## 환경 변수 설정

```bash
# Anthropic API 사용 활성화
USE_ANTHROPIC_API=true

# 웹 검색 기능 활성화
ENABLE_NATIVE_WEB_SEARCH=true

# Secrets Manager 설정
ANTHROPIC_SECRET_NAME=title-v1
```

## 모니터링 포인트

### 로그 확인 사항
1. **캐시 히트율**: 
   - `✅ Cache HIT for {engine_type}`
   - `❌ Cache MISS for {engine_type}`

2. **비용 추적**:
   - `💰 API Cost: ${cost}`
   - 각 요청별 토큰 사용량

3. **캐싱 효과**:
   - `cache_read` vs `cache_write` 비율
   - 전체 비용 절감률

## 추가 최적화 제안

1. **배치 처리**: 여러 요청을 모아서 처리
2. **응답 길이 최적화**: MAX_TOKENS 조정
3. **프롬프트 압축**: 불필요한 지침 제거
4. **캐시 워밍**: Lambda 초기화 시 프롬프트 사전 로드

## 롤백 방법

변경사항을 되돌리려면:
```bash
git checkout main
```

또는 특정 파일만:
```bash
git checkout main -- backend/lib/anthropic_client.py
git checkout main -- backend/services/websocket_service.py
```