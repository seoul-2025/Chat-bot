```python
# 주요 설정
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
OPUS_MODEL = "claude-opus-4-5-20251101"
MAX_TOKENS = 4096
TEMPERATURE = 0.3

# 웹 검색 도구 설정
if enable_web_search:
    body["tools"] = [
        {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5  # 최대 5번까지 웹 검색 허용
        }
    ]
```

#### B. 환경변수 설정

```bash
ENVIRONMENT_VARS='{
    "ANTHROPIC_SECRET_NAME":"",
    "USE_ANTHROPIC_API":"true",
    "USE_OPUS_MODEL":"true",
    "ANTHROPIC_MODEL_ID":"claude-opus-4-5-20251101",
    "SERVICE_NAME":"",
    "AI_PROVIDER":"anthropic_api",
    "MAX_TOKENS":"4096",
    "TEMPERATURE":"0.3",
    "FALLBACK_TO_BEDROCK":"true",
    "ENABLE_NATIVE_WEB_SEARCH":"true"
}'
```

### 2. 웹 검색 기능 활성화

#### A. 네이티브 웹 검색 활성화

Claude API의 `web_search_20250305` 도구를 사용하여 실시간 웹 정보 검색:

```python
# API 요청 시 tools 파라미터 추가
body["tools"] = [
    {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 5
    }
]
```

#### B. 웹 검색 결과 특징

- Brave Search 엔진 사용
- 자동 출처 인용 제공
- Citation 필드는 토큰 비용에 포함되지 않음
- 암호화된 검색 결과 제공

### 3. 출처 표시 기능 구현

#### A. Citation Formatter 모듈

**파일**: `backend/lib/citation_formatter.py`

주요 기능:

- URL 자동 감지 및 각주 변환
- 도메인별 신뢰도 표시
- 마크다운 포맷팅 지원

```python
class CitationFormatter:
    @staticmethod
    def format_response_with_citations(text: str) -> str:
        """AI 응답에서 출처 정보를 추출하고 포맷팅"""

    @staticmethod
    def _extract_domain(url: str) -> str:
        """URL에서 도메인 추출 및 분류"""
        # ✅ 공식 언론사
        # 🏛️ 정부/공공기관
        # ℹ️ 일반 웹사이트
```

#### B. 시스템 프롬프트 개선

**파일**: `backend/lib/bedrock_client_enhanced.py`

```python
### 📚 웹 검색 출처 표시 (필수)
웹 검색 결과 사용 시 반드시:
1. **인라인 각주**: 정보 제공 시 [1], [2] 형식으로 번호 표시
2. **출처 섹션**: 응답 마지막에 다음 형식으로 출처 명시
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📚 출처:
   [1] 언론사/사이트명 - 제목 (URL)
   [2] 언론사/사이트명 - 제목 (URL)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. **신뢰도 표시**:
   - 공식 언론사: ✅
   - 정부/공공기관: 🏛️
   - 일반 웹사이트: ℹ️
```

#### C. WebSocket 메시지 핸들러 수정

**파일**: `backend/handlers/websocket/message.py`

```python
# 웹 검색 출처 포맷팅 적용
from lib.citation_formatter import CitationFormatter
formatter = CitationFormatter()

if "📚 출처:" not in total_response and "http" in total_response:
    formatted_response = formatter.format_response_with_citations(total_response)
```

### 5. 날짜 정보 동적 처리

#### 문제

하드코딩된 날짜로 인한 오래된 정보 제공

#### 해결

**파일**: `backend/lib/anthropic_client.py`

```python
# 동적 날짜 생성
from datetime import datetime, timezone, timedelta

kst = timezone(timedelta(hours=9))
current_time = datetime.now(kst)

context_info = f"""[현재 세션 정보]
현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S KST')}
사용자 위치: 대한민국
타임존: Asia/Seoul (KST)
"""
```

---

## 🚀 배포 방법

### 1. 코드 배포

```bash
# 백엔드 Lambda 함수 배포
./update-buddy-code.sh

# 프론트엔드 배포 (필요시)
./deploy-p2-frontend.sh
```

### 2. 테스트 스크립트

```bash
# API 직접 테스트
python3 test-api-direct.py

# WebSocket 테스트
python3 test-web-search.py

# Citation 테스트
python3 test-citation.py
```

---

## 📊 테스트 결과

### 웹 검색 테스트

```
요청: "오늘 2025년 12월 14일 대한민국 최신 뉴스"
결과:
- ✅ 실시간 뉴스 제공
- ✅ 출처 자동 표시 (YTN, 서울신문 등)
- ✅ 2025년 현재 날짜 정확히 인식
```
