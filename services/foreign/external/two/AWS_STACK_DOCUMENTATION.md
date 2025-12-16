# 🏗️ AWS 스택 아키텍처 문서

## 📋 개요
f1.sedaily.ai 서비스의 AWS 인프라 구성과 배포 현황을 정리한 문서입니다.

---

## 🎯 운영 중인 서비스 스택들

### 1. **f1-two 스택** (메인 서비스)
- **서비스 URL**: https://f1.sedaily.ai
- **상태**: ✅ 활성 운영 중
- **마지막 배포**: 2025-12-14 (웹 검색 기능 포함)
- **코드 크기**: ~17MB

#### Lambda 함수들
| 함수명 | 역할 | 런타임 | 마지막 수정 |
|--------|------|---------|-------------|
| `f1-conversation-api-two` | 대화 관리 API | Python 3.9 | 2025-12-14 |
| `f1-prompt-crud-two` | 프롬프트 관리 | Python 3.9 | 2025-12-14 |
| `f1-usage-handler-two` | 사용량 추적 | Python 3.9 | 2025-12-14 |
| `f1-websocket-connect-two` | WebSocket 연결 | Python 3.9 | 2025-12-14 |
| `f1-websocket-disconnect-two` | WebSocket 연결 해제 | Python 3.9 | 2025-12-14 |
| `f1-websocket-message-two` | **WebSocket 메시지 처리** | Python 3.9 | 2025-12-14 |

#### DynamoDB 테이블들
| 테이블명 | 용도 |
|----------|------|
| `f1-conversations-two` | 대화 세션 저장 |
| `f1-messages-two` | 메시지 히스토리 |
| `f1-prompts-two` | 시스템 프롬프트 관리 |
| `f1-files-two` | 첨부 파일 메타데이터 |
| `f1-usage-two` | 사용량 통계 |
| `f1-websocket-connections-two` | WebSocket 연결 관리 |

---

### 2. **f1-nova 스택** (Nova 버전)
- **상태**: ✅ 별도 운영 중
- **마지막 배포**: 2025-11-30
- **코드 크기**: ~15MB

#### Lambda 함수들
| 함수명 | 마지막 수정 |
|--------|-------------|
| `f1-nova-websocket-connect-two` | 2025-11-03 |
| `f1-nova-websocket-message-two` | 2025-11-30 |
| `f1-nova-websocket-disconnect-two` | 2025-11-03 |
| `f1-nova-conversation-api-two` | 2025-11-30 |
| `f1-nova-prompt-crud-two` | 2025-11-03 |
| `f1-nova-usage-handler-two` | 2025-11-03 |

---

### 3. **tf1 스택** (TF1 서비스)
- **상태**: ✅ 별도 운영 중
- **마지막 배포**: 2025-12-10
- **코드 크기**: ~15MB

#### Lambda 함수들
| 함수명 | 마지막 수정 |
|--------|-------------|
| `tf1-websocket-connect-two` | 2025-12-09 |
| `tf1-websocket-message-two` | 2025-12-10 |
| `tf1-websocket-disconnect-two` | 2025-12-09 |
| `tf1-conversation-api-two` | 2025-12-09 |
| `tf1-prompt-crud-two` | 2025-12-09 |
| `tf1-usage-handler-two` | 2025-12-09 |

---

## 🔧 배포 스크립트들

### ✅ 검증된 배포 스크립트들
| 스크립트 | 대상 | 용도 | 상태 |
|----------|------|------|------|
| `upgrade-f1-anthropic.sh` | f1-two | 백엔드 Lambda 함수 배포 | ✅ 검증완료 |
| `upgrade-f1-frontend.sh` | f1-two | 프론트엔드 S3 배포 | ✅ 사용가능 |

### 🗂️ 백업된 스크립트들
**위치**: `scripts-backup/20251214_224731/`
- `deploy-anthropic.sh` - 전체 스택 배포 (주의 필요)
- `deploy-f1-backend.sh` - f1-two 백엔드만
- `deploy-github-version.sh` - GitHub 버전 배포
- `deploy-service.sh` - 범용 서비스 배포
- `deploy.sh` - 기본 배포 스크립트

---

## ⚙️ 현재 설정

### f1-websocket-message-two 환경변수
```bash
AI_PROVIDER=anthropic_api
ANTHROPIC_MODEL_ID=claude-opus-4-5-20251101
ANTHROPIC_SECRET_NAME=foreign-v1
ENABLE_NATIVE_WEB_SEARCH=true
FALLBACK_TO_BEDROCK=true
MAX_TOKENS=4096
TEMPERATURE=0.3
USE_ANTHROPIC_API=true
WEB_SEARCH_MAX_USES=5
```

### 주요 기능
- ✅ **Anthropic Claude 4.5 Opus** 사용
- ✅ **네이티브 웹 검색** 기능 (web_search_20250305)
- ✅ **자동 출처 표시** (Citation Formatter)
- ✅ **Bedrock 폴백** 지원
- ✅ **실시간 날짜 인식** (동적 컨텍스트)

---

## 🔍 모니터링 & 디버깅

### CloudWatch 로그
```bash
# 메인 웹소켓 핸들러 로그
aws logs tail /aws/lambda/f1-websocket-message-two --follow

# 대화 API 로그  
aws logs tail /aws/lambda/f1-conversation-api-two --follow

# 프롬프트 관리 로그
aws logs tail /aws/lambda/f1-prompt-crud-two --follow
```

### 함수 상태 확인
```bash
# 특정 함수 정보
aws lambda get-function --function-name f1-websocket-message-two

# 환경변수 확인
aws lambda get-function-configuration \
  --function-name f1-websocket-message-two \
  --query 'Environment.Variables'
```

### DynamoDB 테이블 상태
```bash
# 테이블 정보 확인
aws dynamodb describe-table --table-name f1-conversations-two

# 최근 항목 확인
aws dynamodb scan --table-name f1-conversations-two --max-items 5
```

---

## 📊 리소스 사용량

### Lambda 함수 크기 비교
- **f1-two**: ~17MB (최신 - 웹검색 포함)
- **f1-nova**: ~15MB 
- **tf1**: ~15MB
- **기존 f1**: ~581B (레거시)

### 배포 패키지 구성
- **의존성**: boto3, anthropic, requests 등
- **소스코드**: handlers, lib, services, utils
- **새기능**: citation_formatter.py (출처 표시)

---

## ⚠️ 주의사항

### 1. 스택 분리
- **절대 혼용 금지**: 각 스택별 독립적 운영
- **배포 스크립트 주의**: 반드시 해당 스택만 대상으로 설정

### 2. 환경변수 관리
- **Secrets Manager**: API 키는 foreign-v1에서 관리
- **수동 설정 필요**: 스크립트로 환경변수 설정 실패 시

### 3. 모니터링 필요 항목
- **API 호출량**: Anthropic API rate limit
- **오류율**: Bedrock 폴백 동작 확인
- **응답 시간**: 웹 검색 포함 시 지연 가능성

---

## 🚀 향후 계획

### 개선사항
- [ ] 환경변수 자동 설정 권한 문제 해결
- [ ] CloudFormation 템플릿 정리
- [ ] 모니터링 대시보드 구성
- [ ] 자동 백업/복구 프로세스 구축

### 확장 계획
- [ ] 다중 리전 배포 고려
- [ ] 캐싱 레이어 추가
- [ ] API Gateway 최적화
- [ ] 비용 최적화

---

**문서 작성일**: 2025-12-14  
**마지막 업데이트**: f1-two 스택 웹 검색 기능 배포 완료