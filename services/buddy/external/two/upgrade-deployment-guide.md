# 📦 B1.SEDAILY.AI 배포 가이드

> 빠른 배포 및 수정 가이드
> 최종 업데이트: 2024-12-14

## 🚀 Quick Start

### 1분 배포 (코드 수정 후)
```bash
# 백엔드 배포
./update-buddy-code.sh

# 프론트엔드 배포 (필요시)
./deploy-p2-frontend.sh
```

---

## 📝 일반적인 수정 작업

### upgrade-example-01: AI 응답 수정
```bash
# 1. 파일 수정
vim backend/lib/anthropic_client.py

# 2. 테스트
python3 test-api-direct.py

# 3. 배포
./update-buddy-code.sh

# 4. 확인 (30초 후)
python3 test-web-search.py
```

### upgrade-example-02: 시스템 프롬프트 수정
```bash
# 1. 프롬프트 파일 수정
vim backend/lib/bedrock_client_enhanced.py
# 또는
vim backend/services/websocket_service.py

# 2. 배포
./update-buddy-code.sh
```

### upgrade-example-03: 웹 검색 기능 토글
```bash
# 1. 환경변수 수정
vim update-buddy-code.sh

# ENABLE_NATIVE_WEB_SEARCH 값 변경
# "true" → "false" (비활성화)
# "false" → "true" (활성화)

# 2. 배포
./update-buddy-code.sh
```

### upgrade-example-04: 대화 저장 로직 수정
```bash
# 1. 대화 관리자 수정
vim backend/handlers/websocket/conversation_manager.py

# 2. API 핸들러 수정 (필요시)
vim backend/handlers/api/conversation.py

# 3. 배포
./update-buddy-code.sh

# 4. DynamoDB 확인
aws dynamodb scan \
    --table-name p2-two-conversations-two \
    --limit 1 \
    --region us-east-1
```

### upgrade-example-05: 새로운 API 엔드포인트 추가
```bash
# 1. 새 핸들러 생성
vim backend/handlers/api/new_endpoint.py

# 2. Lambda 함수 생성 (필요시)
aws lambda create-function \
    --function-name p2-two-new-handler-two \
    --runtime python3.9 \
    --handler handlers.api.new_endpoint.handler \
    --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
    --region us-east-1

# 3. API Gateway 라우트 추가
# REST API에 새 리소스와 메서드 추가

# 4. 배포
./update-buddy-code.sh
```

---

## 🔄 배포 프로세스 상세

### Phase 1: 준비
```bash
# 1. 현재 상태 백업
git add .
git commit -m "Before deployment"

# 2. 테스트 환경 확인
python3 --version  # Python 3.9+
aws --version      # AWS CLI 설치 확인
```

### Phase 2: 코드 수정
```bash
# 주요 파일 위치
backend/
├── lib/
│   ├── anthropic_client.py      # Anthropic API 클라이언트
│   ├── bedrock_client_enhanced.py # Bedrock 클라이언트
│   └── perplexity_client.py     # Perplexity 검색
├── handlers/
│   ├── websocket/
│   │   ├── message.py           # WebSocket 메시지 처리
│   │   └── conversation_manager.py # 대화 관리
│   └── api/
│       └── conversation.py      # REST API 핸들러
└── services/
    └── websocket_service.py     # WebSocket 서비스 로직
```

### Phase 3: 로컬 테스트
```bash
# API 직접 테스트
python3 test-api-direct.py

# WebSocket 테스트
python3 test-web-search.py

# 단위 테스트 (있는 경우)
python3 -m pytest tests/
```

### Phase 4: 배포
```bash
# update-buddy-code.sh 스크립트 동작
# 1. package/ 디렉토리 정리
# 2. 의존성 설치 (requirements.txt)
# 3. 소스 코드 복사
# 4. ZIP 파일 생성
# 5. 각 Lambda 함수 업데이트
# 6. 환경변수 설정

./update-buddy-code.sh
```

### Phase 5: 검증
```bash
# 1. Lambda 로그 확인
aws logs tail /aws/lambda/p2-two-websocket-message-two --follow

# 2. API 테스트
curl https://pisnqqgu75.execute-api.us-east-1.amazonaws.com/prod/health

# 3. WebSocket 테스트
wscat -c wss://dwc2m51as4.execute-api.us-east-1.amazonaws.com/prod

# 4. 브라우저 테스트
open https://b1.sedaily.ai
```

---

## 🛠️ 고급 배포 시나리오

### upgrade-advanced-01: 롤백
```bash
# Lambda 이전 버전으로 롤백
aws lambda update-function-code \
    --function-name p2-two-websocket-message-two \
    --s3-bucket YOUR_BACKUP_BUCKET \
    --s3-key backups/lambda-deployment-20241214.zip \
    --region us-east-1
```

### upgrade-advanced-02: Blue-Green 배포
```bash
# 1. 새 버전 발행
aws lambda publish-version \
    --function-name p2-two-websocket-message-two \
    --description "New version with feature X"

# 2. 별칭 업데이트
aws lambda update-alias \
    --function-name p2-two-websocket-message-two \
    --name PROD \
    --function-version 2

# 3. 트래픽 점진 이동
aws lambda update-alias \
    --function-name p2-two-websocket-message-two \
    --name PROD \
    --routing-config AdditionalVersionWeights={1=0.5}
```

### upgrade-advanced-03: 환경별 배포
```bash
# 개발 환경
ENVIRONMENT=dev ./update-buddy-code.sh

# 스테이징 환경
ENVIRONMENT=staging ./update-buddy-code.sh

# 프로덕션 환경
ENVIRONMENT=prod ./update-buddy-code.sh
```

---

## 📊 배포 체크리스트

### 배포 전
- [ ] 코드 리뷰 완료
- [ ] 로컬 테스트 통과
- [ ] Git 커밋 완료
- [ ] 환경변수 확인
- [ ] API 키 확인 (Secrets Manager)

### 배포 중
- [ ] update-buddy-code.sh 실행
- [ ] 에러 메시지 확인
- [ ] 모든 Lambda 함수 업데이트 성공

### 배포 후
- [ ] CloudWatch 로그 확인
- [ ] API 응답 테스트
- [ ] WebSocket 연결 테스트
- [ ] 브라우저 기능 테스트
- [ ] 성능 모니터링

---

## 🚨 일반적인 문제 해결

### 문제: Lambda 타임아웃
```bash
# 타임아웃 증가
aws lambda update-function-configuration \
    --function-name p2-two-websocket-message-two \
    --timeout 30
```

### 문제: 메모리 부족
```bash
# 메모리 증가
aws lambda update-function-configuration \
    --function-name p2-two-websocket-message-two \
    --memory-size 512
```

### 문제: 패키지 크기 초과
```bash
# 불필요한 파일 제거
cd backend
rm -rf __pycache__ *.pyc
rm -rf tests/ docs/
zip -r lambda-deployment.zip . -x "*.git*"
```

### 문제: 권한 오류
```bash
# IAM 역할 확인
aws lambda get-function-configuration \
    --function-name p2-two-websocket-message-two \
    --query Role

# 정책 추가
aws iam attach-role-policy \
    --role-name YOUR_LAMBDA_ROLE \
    --policy-arn arn:aws:iam::aws:policy/AWSLambdaExecute
```

---

## 📋 유용한 명령어

### 로그 조회
```bash
# 실시간 로그
aws logs tail /aws/lambda/p2-two-websocket-message-two --follow

# 특정 시간 로그
aws logs filter-log-events \
    --log-group-name /aws/lambda/p2-two-websocket-message-two \
    --start-time $(date -u -d '5 minutes ago' +%s)000
```

### Lambda 함수 정보
```bash
# 함수 설정 확인
aws lambda get-function-configuration \
    --function-name p2-two-websocket-message-two

# 환경변수만 확인
aws lambda get-function-configuration \
    --function-name p2-two-websocket-message-two \
    --query "Environment.Variables"
```

### DynamoDB 작업
```bash
# 항목 수 확인
aws dynamodb describe-table \
    --table-name p2-two-conversations-two \
    --query "Table.ItemCount"

# 최근 대화 확인
aws dynamodb scan \
    --table-name p2-two-conversations-two \
    --limit 5 \
    --scan-filter '{"updatedAt":{"ComparisonOperator":"GE","AttributeValueList":[{"S":"2024-12-14"}]}}'
```

---

## 🔗 관련 문서
- [AWS 리소스 구성](./upgrade-aws-resources.md)
- [API 문서](./api-documentation.md)
- [트러블슈팅 가이드](./troubleshooting.md)

---

최종 업데이트: 2024-12-14
작성자: Claude Assistant