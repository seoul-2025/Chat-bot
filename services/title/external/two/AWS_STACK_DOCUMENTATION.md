# AWS Stack Documentation - t1.sedaily.ai

## 개요

본 문서는 t1.sedaily.ai 프로덕션 환경의 AWS 인프라 구성을 상세히 문서화합니다.

- **서비스명**: t1.sedaily.ai
- **스택 접두사**: nx-tt-dev-ver3
- **AWS 리전**: us-east-1
- **AWS 계정 ID**: 887078546492
- **환경**: production
- **최종 업데이트**: 2025-12-14

## 📋 리소스 요약

### 주요 구성 요소

- **Lambda Functions**: 10개 (활성화된 함수)
- **DynamoDB Tables**: 5개
- **API Gateway**: REST API 1개, WebSocket API 1개
- **S3 Bucket**: 1개 (정적 호스팅)
- **CloudFront Distribution**: 1개
- **Aurora PostgreSQL Cluster**: 1개 (Vector DB)
- **Secrets Manager**: 1개 (Anthropic API Key)

---

## 🌐 프론트엔드 인프라

### S3 Bucket

- **이름**: `nexus-title-hub-frontend`
- **리전**: us-east-1
- **용도**: 정적 웹사이트 호스팅
- **현재 상태**: 활성
- **총 객체 수**: 2개
- **총 크기**: 1.04MB

#### 주요 파일

```
index.html (629 bytes)
pdf.worker.min.js (1.04MB)
assets/ (디렉토리)
images/ (디렉토리)
```

### CloudFront Distribution

- **Distribution ID**: `EIYU5SFVTHQMN`
- **도메인명**: `d1s58eamawxu4.cloudfront.net`
- **커스텀 도메인**: `https://t1.sedaily.ai`
- **상태**: Deployed
- **활성화**: true
- **엔드포인트 타입**: EDGE

---

## 🔌 API Gateway

### REST API

- **API ID**: `qyfams2iva`
- **이름**: `nx-tt-dev-ver3-api`
- **URL**: `https://qyfams2iva.execute-api.us-east-1.amazonaws.com/prod`
- **스테이지**: prod
- **생성일**: 2025-08-23T09:54:02+09:00
- **엔드포인트 구성**: EDGE, IPv4

#### 주요 엔드포인트

```
POST /conversations - 대화 생성/관리
GET  /conversations - 대화 목록 조회
POST /prompts       - 프롬프트 CRUD
GET  /prompts       - 프롬프트 목록
POST /usage         - 사용량 추적
```

### WebSocket API

- **API ID**: `hsdpbajz23`
- **이름**: `nx-tt-dev-ver3-websocket-api`
- **URL**: `wss://hsdpbajz23.execute-api.us-east-1.amazonaws.com/prod`
- **스테이지**: prod
- **프로토콜**: WEBSOCKET
- **생성일**: 2025-08-23T02:51:12+00:00
- **라우트 선택**: `$request.body.action`

#### WebSocket 라우트

```
$connect    - 연결 설정
$disconnect - 연결 해제
$default    - 메시지 처리
sendMessage - 실시간 메시지 전송
```

---

## ⚡ Lambda Functions

### 현재 활성 함수 (10개)

#### WebSocket 핸들러

1. **nx-tt-dev-ver3-websocket-connect**

   - **런타임**: python3.11
   - **코드 크기**: 67KB
   - **최종 수정**: 2025-12-02T06:33:58.000+0000
   - **용도**: WebSocket 연결 설정

2. **nx-tt-dev-ver3-websocket-message**

   - **런타임**: python3.11
   - **코드 크기**: 21.6MB
   - **최종 수정**: 2025-12-14T14:50:30.000+0000
   - **용도**: 실시간 메시지 처리 + 웹 검색 기능

3. **nx-tt-dev-ver3-websocket-disconnect**
   - **런타임**: python3.11
   - **코드 크기**: 67KB
   - **최종 수정**: 2025-12-02T06:33:59.000+0000
   - **용도**: WebSocket 연결 해제

#### REST API 핸들러

4. **nx-tt-dev-ver3-conversation-api**

   - **런타임**: python3.11
   - **코드 크기**: 21.6MB
   - **최종 수정**: 2025-12-14T14:50:44.000+0000
   - **용도**: 대화 API 처리

5. **nx-tt-dev-ver3-prompt-crud**

   - **런타임**: python3.11
   - **코드 크기**: 21.6MB
   - **최종 수정**: 2025-12-14T14:50:57.000+0000
   - **용도**: 프롬프트 CRUD 작업

6. **nx-tt-dev-ver3-usage-handler**
   - **런타임**: python3.9
   - **코드 크기**: 21.6MB
   - **최종 수정**: 2025-12-14T14:51:11.000+0000
   - **용도**: 사용량 추적

#### 관리 및 백그라운드 함수

7. **nx-tt-dev-ver3-vector-populate**

   - **런타임**: python3.11
   - **코드 크기**: 20.7MB
   - **최종 수정**: 2025-12-02T06:20:18.000+0000
   - **용도**: 벡터 DB 데이터 적재

8. **nx-tt-dev-ver3-ConversationHandler**
   - **런타임**: python3.9
   - **코드 크기**: 3KB
   - **최종 수정**: 2025-09-04T08:00:02.000+0000
   - **용도**: 대화 핸들러 (레거시)

#### 테스트/개발 함수

9. **nx-tt-dev-ver3-websocket-message-test**

   - **런타임**: python3.11
   - **코드 크기**: 32KB
   - **최종 수정**: 2025-09-04T12:06:03.000+0000
   - **용도**: WebSocket 메시지 테스트

10. **nx-tt-dev-ver3-title-generation**
    - **런타임**: python3.11
    - **코드 크기**: 2KB
    - **최종 수정**: 2025-08-23T01:19:22.000+0000
    - **용도**: 제목 생성

### Lambda 설정

- **기본 런타임**: python3.11
- **기본 타임아웃**: 30초
- **메시지 처리 타임아웃**: 120초
- **벡터 처리 타임아웃**: 300초
- **기본 메모리**: 512MB

---

## 📊 DynamoDB Tables

### 1. nx-tt-dev-ver3-conversations

- **상태**: ACTIVE
- **생성일**: 2025-08-23T23:53:00.697000+09:00
- **아이템 수**: 955개
- **크기**: 7.66MB (7,663,565 bytes)
- **용도**: 사용자 대화 내역 저장

### 2. nx-tt-dev-ver3-prompts

- **상태**: ACTIVE
- **용도**: 시스템 프롬프트 관리

### 3. nx-tt-dev-ver3-files

- **상태**: ACTIVE
- **용도**: 업로드된 파일 메타데이터

### 4. nx-tt-dev-ver3-usage-tracking

- **상태**: ACTIVE
- **용도**: API 사용량 추적

### 5. nx-tt-dev-ver3-websocket-connections

- **상태**: ACTIVE
- **용도**: WebSocket 연결 관리

---

## 🗄️ Aurora PostgreSQL (Vector Database)

### 클러스터 정보

- **클러스터 식별자**: `nx-tt-vector-db`
- **상태**: available
- **엔진**: aurora-postgresql
- **엔진 버전**: 15.12
- **엔드포인트**: `nx-tt-vector-db.cluster-c83iuyksky7r.us-east-1.rds.amazonaws.com`
- **포트**: 5432
- **데이터베이스명**: vectordb
- **사용자명**: postgres

### RAG 구성

- **활성화**: true
- **Top K**: 10
- **최소 유사도**: 0.7
- **최대 토큰**: 15,000

---

## 🤖 AI 모델 구성

### Anthropic API (Primary)

- **활성화**: true
- **모델 ID**: claude-opus-4-5-20251101
- **최대 토큰**: 4,096
- **Temperature**: 0.3
- **Secret Name**: claude-opus-45-api-key
- **웹 검색 기능**: 활성화 (ENABLE_NATIVE_WEB_SEARCH=true)
- **Citation Formatter**: 자동 출처 표시 기능 포함

### AWS Bedrock (Fallback)

- **모델 ID**: us.anthropic.claude-sonnet-4-20250514-v1:0
- **최대 토큰**: 16,384
- **Temperature**: 0.81
- **Top K**: 50
- **Fallback 활성화**: true

---

## 🔐 보안 및 액세스

### Secrets Manager

- **시크릿명**: `claude-opus-45-api-key`
- **용도**: Anthropic API 인증키 저장
- **리전**: us-east-1

### IAM 정책

- DynamoDB 읽기/쓰기 권한
- Lambda 실행 권한
- API Gateway 호출 권한
- Secrets Manager 읽기 권한
- CloudWatch Logs 쓰기 권한

---

## 📈 모니터링 및 로깅

### CloudWatch 설정

- **로그 레벨**: INFO
- **로그 보존**: Lambda 함수별 CloudWatch Logs 그룹
- **메트릭**: API Gateway, Lambda, DynamoDB 기본 메트릭

---

## 🏗️ 배포 아키텍처

### 연결 관계도

```
Internet
    ↓
[Route 53] → [CloudFront] → [S3 Static Hosting]
    ↓
[API Gateway REST] → [Lambda Functions] → [DynamoDB]
    ↓                      ↓
[API Gateway WebSocket] → [Aurora PostgreSQL]
                           ↓
                      [Anthropic API]
```

### 데이터 흐름

1. **사용자 요청** → CloudFront → S3 (정적 컨텐츠)
2. **API 호출** → API Gateway → Lambda → DynamoDB/Aurora
3. **실시간 통신** → WebSocket API → Lambda → 실시간 응답
4. **AI 처리** → Lambda → Anthropic API/Bedrock → 응답

---

## 🔧 배포 스크립트

### 백엔드 스크립트 (backend/scripts/)

- `01-setup-dynamodb.sh` - DynamoDB 테이블 생성
- `02-setup-api-gateway.sh` - API Gateway 구성
- `03-setup-api-routes.sh` - API 라우트 설정
- `99-deploy-lambda.sh` - Lambda 함수 배포
- `update-lambda-env.sh` - 환경변수 업데이트

### 프론트엔드 스크립트 (frontend/scripts/)

- `01-setup-cloudfront.sh` - CloudFront 배포 생성
- `02-setup-s3-policy.sh` - S3 버킷 정책 설정
- `99-deploy-frontend.sh` - 프론트엔드 배포

### 메인 배포 스크립트

- `deploy-main.sh` - 전체 스택 배포
- `deploy-backend.sh` - 백엔드만 배포
- `deploy-frontend.sh` - 프론트엔드만 배포

---

## 📋 태그 정책

모든 AWS 리소스에 다음 태그가 적용됩니다:

| 키          | 값             | 설명        |
| ----------- | -------------- | ----------- |
| Stack       | nx-tt-dev-ver3 | 스택 식별자 |
| Service     | t1.sedaily.ai  | 서비스명    |
| Environment | production     | 환경        |
| Project     | nexus-title    | 프로젝트명  |

---

## 🚨 알려진 이슈 및 주의사항

### Lambda 함수

- 일부 함수가 python3.9와 python3.11 혼재 사용
- 코드 크기가 20MB+ 인 함수들 존재 (최적화 필요)
- 테스트 함수들이 프로덕션 환경에 혼재

### 권장사항

1. **런타임 통일**: 모든 Lambda 함수를 python3.11로 통일
2. **코드 최적화**: 대용량 패키지 분리 또는 Layer 활용
3. **테스트 함수 정리**: 프로덕션에서 테스트 함수 제거
4. **모니터링 강화**: X-Ray 트레이싱 및 상세 메트릭 추가

---

## 💰 비용 최적화

### 현재 예상 비용 요소

- **Lambda 실행**: 월 사용량에 따른 변동비
- **DynamoDB**: 읽기/쓰기 용량 단위
- **API Gateway**: API 호출 수
- **Aurora PostgreSQL**: 인스턴스 시간 및 스토리지
- **CloudFront**: 데이터 전송량
- **S3**: 스토리지 및 요청 수

### 최적화 제안

1. **Lambda 메모리 최적화**: 실제 사용량에 맞춤
2. **DynamoDB On-Demand**: 트래픽 패턴 분석 후 최적화
3. **Aurora Serverless 검토**: 사용 패턴에 따른 비용 효율성 평가

---

---

## 🆕 최근 업데이트

### 2025-12-14 웹 검색 기능 추가
- Anthropic Claude API의 네이티브 웹 검색 기능 통합
- Citation Formatter 모듈 추가로 자동 출처 표시
- 환경변수 ENABLE_NATIVE_WEB_SEARCH=true 설정
- 2025년 현재 날짜 컨텍스트 강화

---

*본 문서는 2025-12-14 기준으로 작성되었으며, 인프라 변경 시 업데이트가 필요합니다.*
