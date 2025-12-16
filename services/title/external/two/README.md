# t1.sedaily.ai - AI 대화 서비스

## 📋 개요
Claude Opus 4.5 기반 실시간 AI 대화 서비스  
웹 검색 기능이 통합된 최신 정보 제공 플랫폼

## 🏗️ 아키텍처
- **Frontend**: React + Vite (S3 + CloudFront)
- **Backend**: AWS Lambda (Python 3.11)
- **AI Provider**: Anthropic Claude Opus 4.5 with Web Search
- **Database**: DynamoDB + Aurora PostgreSQL (Vector DB)
- **Real-time**: WebSocket API (API Gateway)

## 📁 프로젝트 구조
```
.
├── frontend/           # React 애플리케이션
├── backend/           # Lambda 함수 코드
│   ├── handlers/      # WebSocket & REST 핸들러
│   └── lib/          # 공통 라이브러리
├── config/           # 환경 설정
│   └── t1-production.env  # 프로덕션 설정
├── upgrade-scripts/  # 아카이빙된 배포 스크립트
└── logs/            # 배포 로그
```

## 🚀 빠른 시작

### 배포
```bash
# 전체 배포
./deploy-main.sh

# 백엔드만 배포
./deploy-backend.sh

# 프론트엔드만 배포
./deploy-frontend.sh
```

## 📚 상세 문서

- **[AWS_STACK_DOCUMENTATION.md](./AWS_STACK_DOCUMENTATION.md)** - AWS 인프라 상세 문서
- **[RESOURCE_MAP.json](./RESOURCE_MAP.json)** - 구조화된 리소스 맵핑

## 🔧 주요 기능

### 웹 검색 통합
- Anthropic Claude의 네이티브 웹 검색 기능 활용
- 실시간 최신 정보 제공 (2025년 기준)
- 자동 출처 표시 및 신뢰도 표시

### 환경 설정
```bash
./deploy-main.sh
```
대화형 메뉴를 통해 배포 옵션 선택:
1. 전체 배포 (프론트엔드 + 백엔드)
2. 프론트엔드만 배포
3. 백엔드만 배포
4. Lambda 패키징만
5. Lambda 환경변수 업데이트
6. CloudFront 캐시 무효화

### 개별 배포 스크립트
```bash
./deploy-frontend.sh   # 프론트엔드만 배포
./deploy-backend.sh    # 백엔드만 배포  
./update-env.sh       # 환경변수만 업데이트
```

## 🔧 설정

### 환경 설정
`config/t1-production.env` 파일에서 모든 설정 관리

주요 설정:
- `CUSTOM_DOMAIN`: https://t1.sedaily.ai
- `S3_BUCKET`: nexus-title-hub-frontend
- `CLOUDFRONT_DISTRIBUTION_ID`: EIYU5SFVTHQMN
- `LAMBDA_WS_MESSAGE`: nx-tt-dev-ver3-websocket-message
- `ANTHROPIC_SECRET_NAME`: claude-opus-45-api-key

## 📝 유지보수 가이드

### 코드 업데이트 후 배포
```bash
# 프론트엔드 변경 시
./deploy-frontend.sh

# 백엔드 변경 시
./deploy-backend.sh

# 전체 배포
./deploy-main.sh
# 옵션 1 선택
```

### 환경변수 변경
1. `config/t1-production.env` 수정
2. `./update-env.sh` 실행

### 로그 확인
```bash
# Lambda 로그 실시간 확인
aws logs tail /aws/lambda/nx-tt-dev-ver3-websocket-message --follow

# 배포 로그 확인
ls -la logs/
```

## 🔍 모니터링

### CloudWatch 대시보드
- Lambda 함수 메트릭
- API Gateway 요청 수
- DynamoDB 읽기/쓰기 용량

### 비용 모니터링
- AWS Cost Explorer에서 `nx-tt-dev-ver3` 태그로 필터링

## ⚠️ 주의사항

1. **배포 전 확인**
   - AWS 계정 ID: 887078546492
   - Region: us-east-1
   - 올바른 AWS 프로필 사용 중인지 확인

2. **캐시 무효화**
   - 프론트엔드 배포 시 자동으로 CloudFront 캐시 무효화
   - 수동 무효화: `./deploy-main.sh` → 옵션 6

3. **Lambda 패키지 크기**
   - 최대 250MB (압축)
   - 현재 크기는 배포 시 표시됨

## 📞 지원
문제 발생 시 CloudWatch 로그 확인 후 담당자에게 연락