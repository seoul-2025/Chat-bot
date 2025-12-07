#!/bin/bash

# 빠른 프론트엔드 재배포 스크립트
set -e

# 설정 파일 확인
if [ ! -f "config.sh" ]; then
    echo "❌ config.sh 파일이 없습니다. 먼저 ./init.sh를 실행하세요."
    exit 1
fi

source config.sh

echo "========================================="
echo "   🚀 빠른 프론트엔드 재배포"
echo "   스택: ${STACK_NAME}"
echo "========================================="

# CloudFront Distribution ID 가져오기
CLOUDFRONT_ID=$(aws cloudfront list-distributions \
    --query "DistributionList.Items[?contains(Origins.Items[0].Id, '${S3_BUCKET}')].Id | [0]" \
    --output text \
    --region ${REGION})

if [ -z "$CLOUDFRONT_ID" ] || [ "$CLOUDFRONT_ID" == "None" ]; then
    echo "⚠️  CloudFront Distribution을 찾을 수 없습니다."
    echo "전체 배포 스크립트를 사용하세요: ./06-deploy-frontend.sh"
    exit 1
fi

echo "📋 배포 정보:"
echo "   S3 버킷: ${S3_BUCKET}"
echo "   CloudFront ID: ${CLOUDFRONT_ID}"
echo ""

# 프론트엔드 디렉토리로 이동
cd ../frontend

echo "🔨 [1/3] 프론트엔드 빌드 중..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ 빌드 실패"
    exit 1
fi

echo ""
echo "📤 [2/3] S3에 업로드 중..."
aws s3 sync dist/ s3://${S3_BUCKET} --delete --region ${REGION}

if [ $? -ne 0 ]; then
    echo "❌ S3 업로드 실패"
    exit 1
fi

echo ""
echo "🔄 [3/3] CloudFront 캐시 무효화 중..."
INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id ${CLOUDFRONT_ID} \
    --paths "/*" \
    --query 'Invalidation.Id' \
    --output text)

if [ $? -eq 0 ]; then
    echo "✅ 캐시 무효화 시작: ${INVALIDATION_ID}"
else
    echo "⚠️  캐시 무효화 실패 (수동으로 진행하세요)"
fi

# scripts-v2 디렉토리로 복귀
cd ../scripts-v2

echo ""
echo "========================================="
echo "✅ 프론트엔드 재배포 완료!"
echo "========================================="
echo ""
echo "🌐 CloudFront URL:"
CLOUDFRONT_DOMAIN=$(aws cloudfront get-distribution \
    --id ${CLOUDFRONT_ID} \
    --query 'Distribution.DomainName' \
    --output text)
echo "   https://${CLOUDFRONT_DOMAIN}"
echo ""
echo "⏳ 변경사항이 반영되기까지 1-2분 소요됩니다."
echo "========================================="
