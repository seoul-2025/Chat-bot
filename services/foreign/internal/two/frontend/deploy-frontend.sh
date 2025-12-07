#!/bin/bash

# 색상 코드 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Frontend 빌드 및 배포${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 환경 설정 파일 확인
if [ ! -f "deploy-config.env" ]; then
    echo -e "${RED}❌ deploy-config.env 파일을 찾을 수 없습니다.${NC}"
    echo -e "${YELLOW}먼저 ./deploy-new-s3-cloudfront.sh 를 실행하세요.${NC}"
    exit 1
fi

# 환경 변수 로드
source deploy-config.env

echo -e "${GREEN}✅ 환경 설정 로드 완료${NC}"
echo ""

# Node.js 및 npm 확인
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js가 설치되어 있지 않습니다.${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm이 설치되어 있지 않습니다.${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Node.js 버전: $(node -v)${NC}"
echo -e "${BLUE}📦 npm 버전: $(npm -v)${NC}"
echo ""

# 프로덕션 환경 변수 설정
echo -e "${YELLOW}🔧 프로덕션 환경 변수 확인 중...${NC}"

# .env.production 파일이 이미 올바르게 설정되어 있으므로 건너뜀
if [ -f ".env.production" ]; then
    echo -e "${GREEN}✅ 환경 변수 파일 존재 확인${NC}"
    echo -e "${BLUE}   API URL: $(grep VITE_API_URL .env.production | head -1 | cut -d'=' -f2)${NC}"
    echo -e "${BLUE}   WS URL: $(grep VITE_WS_URL .env.production | head -1 | cut -d'=' -f2)${NC}"
else
    echo -e "${RED}❌ .env.production 파일을 찾을 수 없습니다${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 환경 변수 설정 완료${NC}"
echo ""

# 기존 빌드 폴더 삭제
if [ -d "dist" ]; then
    echo -e "${YELLOW}🗑️  기존 빌드 폴더 삭제 중...${NC}"
    rm -rf dist
fi

# 의존성 설치
echo -e "${YELLOW}📦 의존성 설치 중...${NC}"
npm install --production=false

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 의존성 설치 실패${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 의존성 설치 완료${NC}"
echo ""

# 프로덕션 빌드
echo -e "${YELLOW}🔨 프로덕션 빌드 시작...${NC}"
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 빌드 실패${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 빌드 완료${NC}"
echo ""

# 빌드 결과 확인
if [ ! -d "dist" ]; then
    echo -e "${RED}❌ dist 폴더가 생성되지 않았습니다.${NC}"
    exit 1
fi

# 빌드 크기 확인
DIST_SIZE=$(du -sh dist | cut -f1)
echo -e "${BLUE}📊 빌드 크기: ${DIST_SIZE}${NC}"
echo ""

# S3 동기화
echo -e "${YELLOW}☁️  S3에 파일 업로드 중...${NC}"
echo -e "   버킷: ${S3_BUCKET}"

# 기존 파일 삭제 후 새 파일 업로드
aws s3 sync dist/ "s3://${S3_BUCKET}/" \
    --delete \
    --cache-control "public, max-age=31536000" \
    --exclude "index.html" \
    --exclude "*.map"

# index.html은 캐시하지 않도록 별도 업로드
aws s3 cp dist/index.html "s3://${S3_BUCKET}/index.html" \
    --cache-control "no-cache, no-store, must-revalidate" \
    --content-type "text/html"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ S3 업로드 실패${NC}"
    exit 1
fi

echo -e "${GREEN}✅ S3 업로드 완료${NC}"
echo ""

# CloudFront 캐시 무효화
echo -e "${YELLOW}🔄 CloudFront 캐시 무효화 중...${NC}"

INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id "${CLOUDFRONT_DISTRIBUTION_ID}" \
    --paths "/*" \
    --query 'Invalidation.Id' \
    --output text)

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ CloudFront 캐시 무효화 실패${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 캐시 무효화 요청 완료${NC}"
echo -e "   무효화 ID: ${INVALIDATION_ID}"
echo ""

# 배포 완료
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   🎉 배포 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}🌐 웹사이트 URL:${NC}"
echo -e "   ${GREEN}${CLOUDFRONT_DOMAIN}${NC}"
echo ""
echo -e "${YELLOW}⏱️  CloudFront 캐시 무효화가 진행 중입니다.${NC}"
echo -e "   완료까지 5-10분 정도 소요될 수 있습니다."
echo ""
echo -e "${BLUE}📊 배포 정보:${NC}"
echo -e "   S3 버킷: ${S3_BUCKET}"
echo -e "   CloudFront ID: ${CLOUDFRONT_DISTRIBUTION_ID}"
echo -e "   빌드 크기: ${DIST_SIZE}"
echo -e "   배포 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 배포 로그 저장
echo "$(date '+%Y-%m-%d %H:%M:%S') - 배포 완료: ${CLOUDFRONT_DOMAIN}" >> deploy.log