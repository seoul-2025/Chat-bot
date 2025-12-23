# API Gateway Lambda 함수 연결 완료

## 추가된 엔드포인트

### 1. Claude API 프록시
- **POST** `/api/claude/chat` - Claude API 프록시
- **OPTIONS** `/api/claude/chat` - CORS 지원

### 2. 프롬프트 관리
- **GET** `/prompts/{engineType}` - 프롬프트 조회
- **GET** `/prompts/{engineType}/files` - 프롬프트 파일 목록
- **OPTIONS** `/prompts/{engineType}` - CORS 지원

### 3. 사용량 관리 (업데이트됨)
- **GET** `/usage/{user_id}/{conversation_id}` - 사용량 조회
- **POST** `/usage/update` - 사용량 업데이트

## 배포 방법

```bash
# 백엔드 배포
cd d:\sedaily\Project\external_one
serverless deploy

# 또는 기존 스크립트 사용
./scripts/deploy-backend.sh
```

## API Gateway 구성

배포 후 다음 리소스가 자동으로 생성됩니다:

1. **REST API Gateway**
   - Claude API 프록시 엔드포인트
   - 프롬프트 관리 엔드포인트
   - 사용량 관리 엔드포인트

2. **Lambda 함수**
   - `one-service-prod-claude-api-proxy`
   - `one-service-prod-prompt-handler`
   - `one-service-prod-usage-handler` (업데이트됨)

3. **CORS 설정**
   - 모든 엔드포인트에 CORS 자동 적용
   - OPTIONS 메서드 지원

## 환경 변수

Lambda 함수에서 사용하는 환경 변수:
- `CLAUDE_API_KEY` - Claude API 키 (필수)

## 테스트

배포 완료 후 API Gateway 콘솔에서 확인:
1. AWS 콘솔 → API Gateway
2. `one-service-prod` API 선택
3. 새로 추가된 리소스/메서드 확인
4. 테스트 실행