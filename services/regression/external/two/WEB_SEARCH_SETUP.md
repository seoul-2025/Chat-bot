# 웹 검색 기능 설정 가이드

## 🔧 환경변수 설정

### Lambda 환경변수 추가

다음 환경변수들을 Lambda 함수에 추가하세요:

```bash
# 웹 검색 기능 제어
ENABLE_NATIVE_WEB_SEARCH=true          # Anthropic 네이티브 웹 검색 활성화
ENABLE_WEB_SEARCH=false                # Perplexity 웹 검색 (폴백용)
ENABLE_CITATION_FORMATTING=true       # 출처 표시 기능 활성화

# Anthropic API 설정
ANTHROPIC_SECRET_NAME=regression-v1    # 이미 설정됨
ANTHROPIC_MODEL_ID=claude-opus-4-5-20251101

# 웹 검색 제한
MAX_WEB_SEARCH_USES=5                  # 최대 검색 횟수
```

### AWS Secrets Manager 설정

현재 설정된 Secrets Manager 시크릿(`regression-v1`)에 API 키가 다음 구조로 저장되어 있어야 합니다:

```json
{
  "api_key": "your-anthropic-api-key-here"
}
```

## 🚀 배포 방법

### 1. Lambda 환경변수 업데이트

```bash
aws lambda update-function-configuration \
  --function-name your-websocket-function \
  --environment Variables='{
    "ENABLE_NATIVE_WEB_SEARCH":"true",
    "ENABLE_CITATION_FORMATTING":"true",
    "ANTHROPIC_MODEL_ID":"claude-opus-4-5-20251101",
    "MAX_WEB_SEARCH_USES":"5"
  }'
```

### 2. 코드 배포

기존 배포 스크립트 사용:
```bash
./backend/deploy-fixed.sh
```

또는 특정 함수만 업데이트:
```bash
# WebSocket 메시지 핸들러 업데이트
zip -r websocket-update.zip \
  backend/lib/anthropic_client.py \
  backend/lib/citation_formatter.py \
  backend/services/websocket_service.py \
  backend/handlers/websocket/message.py

aws lambda update-function-code \
  --function-name your-websocket-function \
  --zip-file fileb://websocket-update.zip
```

## 📋 기능 설명

### 웹 검색 방식

1. **Anthropic Native (추천)**
   - `ENABLE_NATIVE_WEB_SEARCH=true`
   - Claude API의 `web_search_20250305` 도구 사용
   - Brave Search 엔진 기반
   - 자동 출처 인용 제공

2. **Perplexity 폴백**
   - `ENABLE_WEB_SEARCH=true`, `ENABLE_NATIVE_WEB_SEARCH=false`
   - 기존 Perplexity 클라이언트 사용
   - 네이티브 검색 실패 시 자동 폴백

### Citation 시스템

출처 표시 형식:
```
응답 텍스트... [1]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 **출처:**
[1] ✅ YTN - 뉴스 제목 - https://example.com
[2] 🏛️ 공공기관 - 정부 발표 - https://gov.kr
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 신뢰도 표시

- ✅ 신뢰할 수 있는 언론사 (YTN, 중앙일보, 조선일보 등)
- 🏛️ 정부/공공기관 (go.kr, korea.kr)
- ℹ️ 일반 웹사이트

## 🧪 테스트 방법

### 웹 검색 테스트

프론트엔드에서 다음과 같은 메시지로 테스트:

```
오늘 대한민국 최신 뉴스는?
현재 환율은 얼마야?
최근 정부 발표 내용 알려줘
```

### 로그 확인

CloudWatch Logs에서 다음 로그 확인:
```
✅ 웹 검색 기능이 활성화되었습니다
✅ Citation formatting applied
🔍 Performing web search via...
```

## ⚠️ 주의사항

1. **비용 관리**
   - `MAX_WEB_SEARCH_USES=5`로 검색 횟수 제한
   - 웹 검색은 추가 API 호출 비용 발생

2. **오류 처리**
   - 웹 검색 실패 시 일반 응답으로 폴백
   - Citation 오류 시 원본 응답 유지

3. **캐싱 호환성**
   - 동적 콘텐츠(검색 결과)는 캐싱되지 않음
   - 정적 시스템 프롬프트만 캐싱됨

## 📈 성능 최적화

### 검색 조건 최적화

현재 모든 요청에 웹 검색이 활성화되어 있습니다. 필요에 따라 특정 조건에만 검색을 활성화하려면:

```python
# websocket_service.py에서 조건부 웹 검색
def should_use_web_search(self, user_message: str) -> bool:
    # 실시간 정보가 필요한 키워드 체크
    keywords = ['최신', '오늘', '현재', '뉴스', '가격', '환율']
    return any(keyword in user_message for keyword in keywords)
```

이 기능은 필요 시 추가로 구현할 수 있습니다.