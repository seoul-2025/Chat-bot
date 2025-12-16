# 🚀 Claude 웹 검색 빠른 적용 가이드

> 5분 만에 다른 서비스에 적용하기
> 작성일: 2024-12-14

## ✅ 체크리스트

다른 서비스에 적용하기 전 확인사항:

- [ ] AWS 계정 접근 권한
- [ ] Anthropic API Key
- [ ] Python 3.9+ Lambda 런타임
- [ ] 기존 WebSocket 또는 REST API 구조

---

## 📦 Step 1: 필수 파일 복사 (1분)

```bash
# 대상 프로젝트 경로로 이동
cd YOUR_PROJECT_PATH

# 필수 파일 복사
cp /path/to/two/backend/lib/anthropic_client.py backend/lib/
cp /path/to/two/backend/lib/citation_formatter.py backend/lib/

# 테스트 스크립트 복사 (선택)
cp /path/to/two/test-*.py .
```

---

## 🔑 Step 2: API Key 설정 (2분)

### Option A: AWS Secrets Manager 사용 (권장)

```bash
aws secretsmanager create-secret \
    --name buddy-v1 \
    --secret-string '{"api_key":"sk-ant-api03-YOUR_KEY"}' \
    --region us-east-1
```

### Option B: 환경변수 직접 설정

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-YOUR_KEY"
```

---

## ⚙️ Step 3: Lambda 환경변수 설정 (1분)

### AWS Console에서:

1. Lambda 함수 선택
2. Configuration → Environment variables
3. 다음 변수 추가:

```json
{
  "ANTHROPIC_SECRET_NAME": "buddy-v1",
  "USE_ANTHROPIC_API": "true",
  "ANTHROPIC_MODEL_ID": "claude-opus-4-5-20251101",
  "ENABLE_NATIVE_WEB_SEARCH": "true",
  "AI_PROVIDER": "anthropic_api",
  "MAX_TOKENS": "4096",
  "TEMPERATURE": "0.3"
}
```

### AWS CLI 사용:

```bash
aws lambda update-function-configuration \
    --function-name YOUR_FUNCTION_NAME \
    --environment Variables='{
        "ANTHROPIC_SECRET_NAME":"buddy-v1",
        "USE_ANTHROPIC_API":"true",
        "ANTHROPIC_MODEL_ID":"claude-opus-4-5-20251101",
        "ENABLE_NATIVE_WEB_SEARCH":"true"
    }' \
    --region us-east-1
```

---

## 💻 Step 4: 코드 통합 (1분)

### 기존 핸들러 수정

#### WebSocket 핸들러의 경우:

```python
# 기존 코드
from your_ai_client import YourAIClient

# 변경 후
from lib.anthropic_client import AnthropicClient
from lib.citation_formatter import CitationFormatter

# AI 응답 생성 부분
ai_client = AnthropicClient()
formatter = CitationFormatter()

# 스트리밍 응답
total_response = ""
for chunk in ai_client.stream_response(
    user_message=user_message,
    system_prompt="당신은 도움이 되는 AI 어시스턴트입니다.",
    enable_web_search=True  # 웹 검색 활성화
):
    total_response += chunk
    # 청크 전송 로직

# 출처 포맷팅 적용
if "http" in total_response:
    total_response = formatter.format_response_with_citations(total_response)
```

#### REST API 핸들러의 경우:

```python
from lib.anthropic_client import AnthropicClient

def handler(event, context):
    client = AnthropicClient()
    user_message = event['body']['message']

    response = ""
    for chunk in client.stream_response(
        user_message=user_message,
        system_prompt="시스템 프롬프트",
        enable_web_search=True
    ):
        response += chunk

    return {
        'statusCode': 200,
        'body': json.dumps({'response': response})
    }
```

---

## 🧪 Step 5: 테스트 (30초)

### 빠른 테스트:

```python
# test_quick.py
from lib.anthropic_client import AnthropicClient

client = AnthropicClient()
for chunk in client.stream_response(
    user_message="오늘 대한민국 주요 뉴스 1개만 알려줘",
    system_prompt="간단히 답변하세요",
    enable_web_search=True
):
    print(chunk, end='', flush=True)
```

실행:

```bash
python3 test_quick.py
```

---

## 🔨 문제 해결

### 문제 1: ImportError

```bash
pip install requests boto3
```

### 문제 2: API Key 오류

```bash
# Secret 확인
aws secretsmanager get-secret-value --secret-id buddy-v1 --region us-east-1
```

### 문제 3: 타임아웃

```bash
# Lambda 타임아웃 증가
aws lambda update-function-configuration \
    --function-name YOUR_FUNCTION \
    --timeout 300
```

---

## 📝 최소 요구사항 요약

### 필수 파일 (2개)

1. `anthropic_client.py` - API 클라이언트
2. `citation_formatter.py` - 출처 포맷터

### 필수 환경변수 (3개)

1. `ANTHROPIC_SECRET_NAME` 또는 `ANTHROPIC_API_KEY`
2. `USE_ANTHROPIC_API=true`
3. `ENABLE_NATIVE_WEB_SEARCH=true`

### 코드 변경 (3줄)

```python
from lib.anthropic_client import AnthropicClient  # Import
client = AnthropicClient()  # 초기화
# 기존 AI 호출을 client.stream_response()로 교체
```

---

## ⚡ 원클릭 배포 스크립트

`quick-deploy.sh` 생성:

```bash
#!/bin/bash
FUNCTION_NAME="your-lambda-function"
REGION="us-east-1"

# 1. 파일 복사
cp anthropic_client.py backend/lib/
cp citation_formatter.py backend/lib/

# 2. 패키징
cd backend
zip -r ../deployment.zip .

# 3. Lambda 업데이트
aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://../deployment.zip \
    --region $REGION

# 4. 환경변수 설정
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --environment Variables='{
        "USE_ANTHROPIC_API":"true",
        "ENABLE_NATIVE_WEB_SEARCH":"true"
    }' \
    --region $REGION

echo "✅ 배포 완료!"
```

실행:

```bash
chmod +x quick-deploy.sh
./quick-deploy.sh
```

---

## 🎉 완료!

이제 서비스에서:

- ✅ Claude Opus 4.5 모델 사용
- ✅ 실시간 웹 검색 가능
- ✅ 자동 출처 표시

문의: 2024-12-14 작업 문서 참조
