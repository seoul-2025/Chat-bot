# 환경변수 설정 가이드

이 문서는 백엔드 애플리케이션에 필요한 모든 환경변수를 정의합니다.

## 🔧 필수 환경변수

### AWS 설정
```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id
```

### DynamoDB 테이블
```bash
CONVERSATIONS_TABLE=your-conversations-table
PROMPTS_TABLE=your-prompts-table
FILES_TABLE=your-files-table
USAGE_TABLE=your-usage-table
WEBSOCKET_TABLE=your-websocket-connections-table
```

### Bedrock 설정
```bash
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
BEDROCK_OPUS_MODEL_ID=us.anthropic.claude-opus-4-1-20250805-v1:0
BEDROCK_MAX_TOKENS=16384
BEDROCK_TEMPERATURE=0.81
BEDROCK_TOP_P=0.9
BEDROCK_TOP_K=50
ANTHROPIC_VERSION=bedrock-2023-05-31
```

## 🚀 엔진 설정 (핵심)

### 기본 엔진 설정
```bash
# 사용 가능한 엔진 목록 (쉼표로 구분)
AVAILABLE_ENGINES=one,two,three

# 기본 엔진
DEFAULT_ENGINE_TYPE=one
```

### 엔진별 상세 설정

#### 엔진 ONE
```bash
ENGINE_ONE_NAME=기업 보도자료
ENGINE_ONE_DESC=기업 보도자료 전문 엔진
ENGINE_ONE_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
ENGINE_ONE_INPUT_COST=0.003
ENGINE_ONE_OUTPUT_COST=0.015
```

#### 엔진 TWO
```bash
ENGINE_TWO_NAME=정부/공공 보도자료
ENGINE_TWO_DESC=정부/공공 보도자료 전문 엔진
ENGINE_TWO_MODEL_ID=us.anthropic.claude-opus-4-1-20250805-v1:0
ENGINE_TWO_INPUT_COST=0.015
ENGINE_TWO_OUTPUT_COST=0.075
```

#### 엔진 THREE (선택)
```bash
ENGINE_THREE_NAME=지역 뉴스
ENGINE_THREE_DESC=지역 뉴스 전문 엔진
ENGINE_THREE_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
ENGINE_THREE_INPUT_COST=0.003
ENGINE_THREE_OUTPUT_COST=0.015
```

### 🔐 보안 설정

```bash
# 관리자 이메일 (쉼표로 구분)
ADMIN_EMAILS=ai@sedaily.com,admin@sedaily.com
```

### 📊 사용량 제한

```bash
# Free Tier
FREE_TIER_TOKENS=10000
FREE_TIER_REQUESTS=100
FREE_TIER_MAX_TOKENS=1000

# Basic Tier
BASIC_TIER_TOKENS=100000
BASIC_TIER_REQUESTS=1000
BASIC_TIER_MAX_TOKENS=5000

# Premium Tier
PREMIUM_TIER_TOKENS=500000
PREMIUM_TIER_REQUESTS=10000
PREMIUM_TIER_MAX_TOKENS=10000
```

### 💬 대화 설정

```bash
MAX_CONVERSATION_MESSAGES=50
DEFAULT_HISTORY_LIMIT=20
MAX_MERGED_MESSAGES=30
MAX_BEDROCK_CONTEXT=10
```

### 🔢 토큰 추정

```bash
KOREAN_CHARS_PER_TOKEN=2.5
ENGLISH_CHARS_PER_TOKEN=4
NUMBERS_CHARS_PER_TOKEN=3.5
SPACES_CHARS_PER_TOKEN=4
SPECIAL_CHARS_PER_TOKEN=3
```

### 🌐 WebSocket 설정

```bash
WS_MESSAGE_TIMEOUT=300
WS_MAX_MESSAGE_SIZE=1048576
WS_CONNECTION_TIMEOUT=3600
WS_CONNECTION_TTL=86400
```

### 🗄️ 데이터베이스 설정

```bash
DB_MAX_RETRIES=3
DB_TIMEOUT=10
DB_MAX_POOL_CONNECTIONS=50
DB_BATCH_WRITE_SIZE=25
MAX_CONVERSATIONS_QUERY=1000
DEFAULT_PUBLIC_PROMPTS_LIMIT=50
MAX_USAGE_HISTORY_DAYS=90
```

### 📝 텍스트 처리

```bash
MAX_TITLE_LENGTH=50
DEFAULT_CONVERSATION_TITLE=New Conversation
```

### 🌏 시스템 프롬프트 기본값

```bash
DEFAULT_USER_LOCATION=대한민국
DEFAULT_TIMEZONE=Asia/Seoul (KST)
DEFAULT_TIMEZONE_OFFSET=9
SESSION_ID_LENGTH=8
KNOWLEDGE_CUTOFF_DATE=2025년 1월 31일
```

### 📈 사용량 제한 기본값

```bash
DAILY_DEFAULT_REQUESTS=1000
DAILY_DEFAULT_TOKENS=1000000
DAILY_DEFAULT_COST=100.00
MONTHLY_DEFAULT_REQUESTS=30000
MONTHLY_DEFAULT_TOKENS=30000000
MONTHLY_DEFAULT_COST=3000.00
```

## 🔄 데이터 마이그레이션 가이드

기존에 `'11'`, `'22'` 같은 숫자 ID를 사용했다면 다음과 같이 마이그레이션하세요:

### DynamoDB 데이터 업데이트
```python
# 예시 스크립트
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('your-conversations-table')

# 기존 '11' -> 'one', '22' -> 'two' 변환
mapping = {
    '11': 'one',
    '22': 'two',
    '33': 'three'
}

# Scan & Update
response = table.scan()
for item in response['Items']:
    old_engine = item.get('engineType')
    if old_engine in mapping:
        table.update_item(
            Key={'conversationId': item['conversationId']},
            UpdateExpression='SET engineType = :new_engine',
            ExpressionAttributeValues={':new_engine': mapping[old_engine]}
        )
```

### 프롬프트 테이블 업데이트
```python
# promptId가 엔진 ID와 연결되어 있다면
prompts_table = dynamodb.Table('your-prompts-table')

for old_id, new_id in mapping.items():
    # 기존 프롬프트 가져오기
    old_prompt = prompts_table.get_item(Key={'promptId': old_id})
    if 'Item' in old_prompt:
        item = old_prompt['Item']
        item['promptId'] = new_id
        item['engineType'] = new_id

        # 새 ID로 저장
        prompts_table.put_item(Item=item)

        # 기존 ID 삭제 (선택)
        # prompts_table.delete_item(Key={'promptId': old_id})
```

## 📌 주의사항

1. **환경변수 우선순위**: 환경변수가 설정되지 않으면 기본값이 사용됩니다.
2. **필수 변수**: `CONVERSATIONS_TABLE`, `PROMPTS_TABLE` 등 테이블 관련 변수는 반드시 설정해야 합니다.
3. **엔진 추가**: 새 엔진을 추가하려면 `AVAILABLE_ENGINES`에 추가하고 해당 엔진의 환경변수를 설정하세요.
4. **비용 설정**: `ENGINE_*_INPUT_COST`, `ENGINE_*_OUTPUT_COST`는 USD 기준입니다.

## 🧪 테스트

환경변수가 제대로 설정되었는지 확인:

```python
from src.config.business import ENGINE_TYPES, DEFAULT_ENGINE_TYPE

print(f"Default Engine: {DEFAULT_ENGINE_TYPE}")
print(f"Available Engines: {list(ENGINE_TYPES.keys())}")

for engine_id, config in ENGINE_TYPES.items():
    print(f"\nEngine: {engine_id}")
    print(f"  Name: {config['name']}")
    print(f"  Model: {config['model_id']}")
    print(f"  Input Cost: ${config['input_cost_per_1k']}/1K")
    print(f"  Output Cost: ${config['output_cost_per_1k']}/1K")
```
