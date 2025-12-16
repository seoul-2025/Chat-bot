# 🚀 F1.sedaily.ai 배포 가이드

## 📋 현재 상태
- **운영 스택**: `f1-two`
- **서비스 URL**: https://f1.sedaily.ai
- **Lambda 함수**: 6개 (websocket, api, crud)

## 🔧 배포 방법

### ✅ 검증된 배포 스크립트들
```bash
# 백엔드 (Lambda 함수) 배포
./upgrade-f1-anthropic.sh

# 프론트엔드 (S3) 배포  
./upgrade-f1-frontend.sh
```

**이 스크립트가 하는 일:**
- f1-two 스택의 6개 Lambda 함수만 업데이트
- 웹 검색 기능 포함된 최신 코드 배포
- Anthropic Claude 4.5 Opus 설정 적용

### 📦 배포되는 Lambda 함수들
- `f1-conversation-api-two`
- `f1-prompt-crud-two` 
- `f1-usage-handler-two`
- `f1-websocket-connect-two`
- `f1-websocket-disconnect-two`
- `f1-websocket-message-two`

### 🔧 환경변수 설정
```bash
USE_ANTHROPIC_API=true
ANTHROPIC_MODEL_ID=claude-opus-4-5-20251101
AI_PROVIDER=anthropic_api
FALLBACK_TO_BEDROCK=true
ENABLE_NATIVE_WEB_SEARCH=true
WEB_SEARCH_MAX_USES=5
MAX_TOKENS=4096
TEMPERATURE=0.3
```

## 🆘 문제해결

### CloudWatch 로그 확인
```bash
aws logs tail /aws/lambda/f1-websocket-message-two --follow
```

### 함수 상태 확인
```bash
aws lambda get-function --function-name f1-websocket-message-two
```

## 📚 백업 정보
- **백업 위치**: `scripts-backup/20251214_224731/`
- **백업된 스크립트들**: 7개 (정리 전 모든 배포 스크립트)

## ⚠️ 주의사항
- 다른 배포 스크립트들은 안전을 위해 백업 폴더로 이동됨
- f1-two 스택만 대상으로 하는 스크립트만 사용
- 배포 전 항상 백업 확인

## 🧪 테스트 방법
배포 후 f1.sedaily.ai에서 다음 질문으로 웹 검색 기능 테스트:
- "오늘 한국 주요 뉴스는?"
- "최신 AI 기술 트렌드는?"
- "현재 코스피 상황은?"

웹 검색이 활성화되면 출처와 함께 실시간 정보가 제공됩니다.