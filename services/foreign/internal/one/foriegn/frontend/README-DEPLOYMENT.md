# 🚀 새로운 S3 + CloudFront 배포 가이드

## 📋 개요
이 가이드는 새로운 AWS S3 버킷과 CloudFront 배포를 생성하고 프론트엔드를 배포하는 방법을 설명합니다.

## 🔧 사전 요구사항

1. **AWS CLI 설치**
   ```bash
   brew install awscli
   ```

2. **AWS 자격 증명 설정**
   ```bash
   aws configure
   ```
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region: ap-northeast-2
   - Default output format: json

3. **Node.js & npm 설치**
   - Node.js 16.x 이상 권장

## 📦 배포 스크립트

### 1️⃣ `deploy-new-s3-cloudfront.sh`
새로운 S3 버킷과 CloudFront 배포를 생성합니다.

**기능:**
- 타임스탬프 기반 고유 S3 버킷 생성
- CloudFront Origin Access Control (OAC) 설정
- CloudFront 배포 생성
- S3 버킷 정책 자동 설정
- 환경 설정 파일 생성 (`deploy-config.env`)

### 2️⃣ `deploy-frontend.sh`
프론트엔드를 빌드하고 S3에 배포합니다.

**기능:**
- 프로덕션 환경 변수 설정
- npm 빌드 실행
- S3에 빌드 파일 업로드
- CloudFront 캐시 무효화

## 🚀 배포 단계

### Step 1: 인프라 생성
```bash
# 실행 권한 부여
chmod +x deploy-new-s3-cloudfront.sh

# 스크립트 실행
./deploy-new-s3-cloudfront.sh
```

**예상 결과:**
- 새로운 S3 버킷 생성
- CloudFront 배포 생성 (15-20분 소요)
- `deploy-config.env` 파일 생성

### Step 2: 프론트엔드 배포
```bash
# 실행 권한 부여
chmod +x deploy-frontend.sh

# 스크립트 실행
./deploy-frontend.sh
```

**예상 결과:**
- 프로덕션 빌드 생성
- S3에 파일 업로드
- CloudFront 캐시 무효화

## 📊 배포 정보 확인

배포 완료 후 `deploy-config.env` 파일에서 확인:
```bash
source deploy-config.env
```

주요 정보:
- **S3 버킷명**: `nexus-frontend-YYYYMMDDHHMMSS`
- **CloudFront URL**: `https://dxxxxxxxxx.cloudfront.net`
- **Distribution ID**: CloudFront 배포 ID

## 🔄 업데이트 배포

코드 변경 후 재배포:
```bash
./deploy-frontend.sh
```

## 🛠️ 문제 해결

### AWS 자격 증명 오류
```bash
aws sts get-caller-identity
```
위 명령어로 자격 증명 확인

### 빌드 실패
```bash
# node_modules 재설치
rm -rf node_modules package-lock.json
npm install
```

### CloudFront 접근 오류
- CloudFront 배포가 완전히 활성화될 때까지 15-20분 대기
- S3 버킷 정책 확인

## 📝 환경 변수 설정

`.env.production` 파일에서 설정 가능:
```env
VITE_APP_ENV=production
VITE_API_URL=https://api.example.com
VITE_WS_URL=wss://api.example.com
VITE_ENABLE_AUTH=false
VITE_ENABLE_SIDEBAR=false
VITE_ENABLE_DASHBOARD=false
```

## 🔒 보안 고려사항

1. S3 버킷은 퍼블릭 액세스 차단 설정됨
2. CloudFront OAC를 통해서만 접근 가능
3. HTTPS 강제 리다이렉션 설정됨

## 📈 모니터링

AWS Console에서 확인:
- CloudFront > Distributions > 모니터링
- S3 > 버킷 > 메트릭스
- CloudWatch > 대시보드

## 🗑️ 리소스 정리

더 이상 필요없을 때:
```bash
# CloudFront 배포 비활성화
aws cloudfront update-distribution --id $CLOUDFRONT_DISTRIBUTION_ID --distribution-config ...

# S3 버킷 삭제
aws s3 rm s3://$S3_BUCKET --recursive
aws s3api delete-bucket --bucket $S3_BUCKET
```

## 📞 지원

문제 발생 시 다음 정보와 함께 문의:
- `deploy-config.env` 파일 내용
- 에러 메시지
- AWS 리전 정보