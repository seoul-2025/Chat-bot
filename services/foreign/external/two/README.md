# 🤖 F1.sedaily.ai - AI Chat Service

[![AWS](https://img.shields.io/badge/AWS-Lambda-orange)](https://aws.amazon.com/lambda/)
[![Python](https://img.shields.io/badge/Python-3.9-blue)](https://www.python.org/)
[![Claude](https://img.shields.io/badge/Claude-4.5%20Opus-purple)](https://www.anthropic.com/)
[![WebSearch](https://img.shields.io/badge/WebSearch-Enabled-green)](https://docs.anthropic.com/)

한국 경제 전문 AI 채팅 서비스입니다. 실시간 웹 검색과 출처 표시 기능을 제공합니다.

## 🌐 서비스 정보

- **서비스 URL**: https://f1.sedaily.ai
- **AI 모델**: Claude 4.5 Opus (claude-opus-4-5-20251101)
- **주요 기능**: 실시간 웹 검색, 자동 출처 표시, 한국어 경제 전문 상담

## 🚀 주요 기능

### ✨ AI 채팅

- **Claude 4.5 Opus** 모델 기반 고품질 응답
- **실시간 대화** WebSocket 지원
- **대화 히스토리** 관리

### 🔍 웹 검색 기능

- **자동 활성화**: "오늘", "최신", "뉴스" 키워드 감지
- **Brave Search**: Claude 네이티브 웹 검색 도구
- **최대 5회 검색**: 한 대화당 제한

### 📚 출처 표시

- **자동 Citation**: URL 감지 및 각주 번호 변환
- **신뢰도 표시**:
  - ✅ 공식 언론사 (YTN, 연합뉴스 등)
  - 🏛️ 정부/공공기관 (.gov.kr, .go.kr)
  - ℹ️ 일반 웹사이트

## 🏗️ 아키텍처

### AWS 스택 (f1-two)

```
├── Lambda Functions (6개)
│   ├── f1-websocket-message-two     # 메시지 처리 (메인)
│   ├── f1-websocket-connect-two     # 연결 관리
│   ├── f1-websocket-disconnect-two  # 연결 해제
│   ├── f1-conversation-api-two      # 대화 API
│   ├── f1-prompt-crud-two          # 프롬프트 관리
│   └── f1-usage-handler-two        # 사용량 추적
│
├── DynamoDB Tables (6개)
│   ├── f1-conversations-two        # 대화 세션
│   ├── f1-messages-two            # 메시지 히스토리
│   ├── f1-prompts-two             # 시스템 프롬프트
│   ├── f1-files-two               # 파일 메타데이터
│   ├── f1-usage-two               # 사용량 통계
│   └── f1-websocket-connections-two # 연결 관리
│
└── Frontend (React + Vite)
    └── S3 + CloudFront 배포
```

## 🔧 개발 환경

### 배포

```bash
# 백엔드 Lambda 함수 배포
./upgrade-f1-anthropic.sh

# 프론트엔드 S3 배포
./upgrade-f1-frontend.sh
```

### 환경 설정

```bash
# 환경변수 확인
aws lambda get-function-configuration \
  --function-name f1-websocket-message-two \
  --query 'Environment.Variables'

# 로그 모니터링
aws logs tail /aws/lambda/f1-websocket-message-two --follow
```

## 📊 모니터링

### 핵심 지표

- **응답 시간**: WebSocket 메시지 처리 속도
- **에러율**: Lambda 함수 실행 실패율
- **웹 검색 사용량**: 일일 검색 요청 수
- **사용자 활동**: 대화 세션 수

### CloudWatch 대시보드

```bash
# Lambda 메트릭 확인
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=f1-websocket-message-two \
  --start-time 2025-12-14T00:00:00Z \
  --end-time 2025-12-14T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

## 🛠️ 개발 가이드

### 프로젝트 구조

```
├── backend/                 # Lambda 함수 소스
│   ├── handlers/            # API & WebSocket 핸들러
│   ├── lib/                 # AI 클라이언트 라이브러리
│   ├── services/            # 비즈니스 로직
│   └── utils/               # 공통 유틸리티
│
├── frontend/                # React 프론트엔드
│   ├── src/                 # 소스 코드
│   └── public/              # 정적 파일
│
├── config/                  # 환경 설정
└── docs/                    # 문서
    ├── DEPLOYMENT.md        # 배포 가이드
    └── AWS_STACK_DOCUMENTATION.md  # AWS 구조
```

### 코드 품질

- **Python 3.9**: Lambda 런타임
- **Type Hints**: 타입 안정성
- **Error Handling**: 포괄적 예외 처리
- **Logging**: 구조화된 로그

## 📚 참고 문서

- [배포 가이드](./DEPLOYMENT.md)
- [AWS 스택 문서](./AWS_STACK_DOCUMENTATION.md)
- [백업 및 복구](./scripts-backup/)

## 🔐 보안

- **API 키**: AWS Secrets Manager (foreign-v1)
- **IAM 역할**: 최소 권한 원칙
- **VPC**: 필요시 네트워크 격리
- **암호화**: 저장/전송 중 데이터 암호화

## 📞 지원

- **로그 확인**: CloudWatch Logs
- **모니터링**: AWS X-Ray
- **알람**: CloudWatch Alarms
- **백업**: scripts-backup/ 폴더

---

**마지막 업데이트**: 2025-12-14 (웹 검색 기능 추가)  
**라이센스**: Private  
**관리자**: Seoul Economic Daily AI Team
