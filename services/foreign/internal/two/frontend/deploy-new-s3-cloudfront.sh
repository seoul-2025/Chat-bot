#!/bin/bash

# 색상 코드 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 타임스탬프 생성 (버킷명에 사용)
TIMESTAMP=$(date +%Y%m%d%H%M%S)

# AWS 설정
AWS_REGION="ap-northeast-2"
BUCKET_NAME="nexus-frontend-${TIMESTAMP}"
CLOUDFRONT_COMMENT="Nexus Frontend Distribution - ${TIMESTAMP}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   새로운 S3 + CloudFront 배포 시작${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# AWS CLI 설치 확인
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI가 설치되어 있지 않습니다.${NC}"
    echo "설치 방법: brew install awscli"
    exit 1
fi

# AWS 자격 증명 확인
echo -e "${YELLOW}📋 AWS 자격 증명 확인 중...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS 자격 증명이 설정되지 않았습니다.${NC}"
    echo "aws configure를 실행하여 설정하세요."
    exit 1
fi

echo -e "${GREEN}✅ AWS 자격 증명 확인 완료${NC}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "   계정 ID: ${ACCOUNT_ID}"
echo ""

# S3 버킷 생성
echo -e "${YELLOW}📦 S3 버킷 생성 중...${NC}"
echo -e "   버킷명: ${BUCKET_NAME}"

if aws s3api create-bucket \
    --bucket "${BUCKET_NAME}" \
    --region "${AWS_REGION}" \
    --create-bucket-configuration LocationConstraint="${AWS_REGION}" \
    2>/dev/null; then
    echo -e "${GREEN}✅ S3 버킷 생성 완료${NC}"
else
    echo -e "${RED}❌ S3 버킷 생성 실패${NC}"
    exit 1
fi

# 버킷 정책 설정 (CloudFront OAC용)
echo -e "${YELLOW}🔒 S3 버킷 정책 설정 중...${NC}"

# 버킷 퍼블릭 액세스 차단 설정
aws s3api put-public-access-block \
    --bucket "${BUCKET_NAME}" \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# 정적 웹사이트 호스팅 활성화
echo -e "${YELLOW}🌐 정적 웹사이트 호스팅 설정 중...${NC}"
aws s3 website "s3://${BUCKET_NAME}/" \
    --index-document index.html \
    --error-document index.html

echo -e "${GREEN}✅ S3 버킷 설정 완료${NC}"
echo ""

# CloudFront Origin Access Control (OAC) 생성
echo -e "${YELLOW}🔐 CloudFront OAC 생성 중...${NC}"
OAC_NAME="OAC-${BUCKET_NAME}"

OAC_CONFIG=$(cat <<EOF
{
    "Name": "${OAC_NAME}",
    "Description": "OAC for ${BUCKET_NAME}",
    "SigningProtocol": "sigv4",
    "SigningBehavior": "always",
    "OriginAccessControlOriginType": "s3"
}
EOF
)

OAC_ID=$(aws cloudfront create-origin-access-control \
    --origin-access-control-config "${OAC_CONFIG}" \
    --query 'OriginAccessControl.Id' \
    --output text 2>/dev/null) || true

if [ -z "$OAC_ID" ]; then
    echo -e "${YELLOW}⚠️  기존 OAC 사용 또는 생성 실패${NC}"
    # 기존 OAC 목록에서 첫 번째 것 사용
    OAC_ID=$(aws cloudfront list-origin-access-controls --query 'OriginAccessControlList.Items[0].Id' --output text 2>/dev/null)
fi

echo -e "${GREEN}✅ OAC 설정 완료: ${OAC_ID}${NC}"
echo ""

# CloudFront 배포 생성
echo -e "${YELLOW}☁️  CloudFront 배포 생성 중...${NC}"
echo -e "   이 작업은 15-20분 정도 소요될 수 있습니다.${NC}"

DISTRIBUTION_CONFIG=$(cat <<EOF
{
    "CallerReference": "${TIMESTAMP}",
    "Comment": "${CLOUDFRONT_COMMENT}",
    "Enabled": true,
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-${BUCKET_NAME}",
                "DomainName": "${BUCKET_NAME}.s3.${AWS_REGION}.amazonaws.com",
                "S3OriginConfig": {
                    "OriginAccessIdentity": ""
                },
                "OriginAccessControlId": "${OAC_ID}"
            }
        ]
    },
    "DefaultRootObject": "index.html",
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-${BUCKET_NAME}",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"],
            "CachedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            }
        },
        "Compress": true,
        "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
        "OriginRequestPolicyId": "88a5eaf4-2fd4-4709-b370-b4c650ea3fcf"
    },
    "CustomErrorResponses": {
        "Quantity": 2,
        "Items": [
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 10
            },
            {
                "ErrorCode": 403,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 10
            }
        ]
    },
    "PriceClass": "PriceClass_All"
}
EOF
)

# CloudFront 배포 생성
DISTRIBUTION_ID=$(aws cloudfront create-distribution \
    --distribution-config "${DISTRIBUTION_CONFIG}" \
    --query 'Distribution.Id' \
    --output text)

DISTRIBUTION_DOMAIN=$(aws cloudfront get-distribution \
    --id "${DISTRIBUTION_ID}" \
    --query 'Distribution.DomainName' \
    --output text)

echo -e "${GREEN}✅ CloudFront 배포 생성 완료${NC}"
echo -e "   배포 ID: ${DISTRIBUTION_ID}"
echo -e "   도메인: https://${DISTRIBUTION_DOMAIN}"
echo ""

# S3 버킷 정책 업데이트 (CloudFront OAC 액세스 허용)
echo -e "${YELLOW}📝 S3 버킷 정책 업데이트 중...${NC}"

BUCKET_POLICY=$(cat <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontServicePrincipal",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudfront.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${BUCKET_NAME}/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": "arn:aws:cloudfront::${ACCOUNT_ID}:distribution/${DISTRIBUTION_ID}"
                }
            }
        }
    ]
}
EOF
)

aws s3api put-bucket-policy \
    --bucket "${BUCKET_NAME}" \
    --policy "${BUCKET_POLICY}"

echo -e "${GREEN}✅ 버킷 정책 업데이트 완료${NC}"
echo ""

# 환경 설정 파일 생성
echo -e "${YELLOW}📄 환경 설정 파일 생성 중...${NC}"

cat > deploy-config.env <<EOF
# AWS S3 및 CloudFront 설정
export AWS_REGION="${AWS_REGION}"
export S3_BUCKET="${BUCKET_NAME}"
export CLOUDFRONT_DISTRIBUTION_ID="${DISTRIBUTION_ID}"
export CLOUDFRONT_DOMAIN="https://${DISTRIBUTION_DOMAIN}"
export CREATED_AT="${TIMESTAMP}"

# 배포 정보
echo "========================================="
echo "  배포 정보"
echo "========================================="
echo "S3 버킷: ${BUCKET_NAME}"
echo "CloudFront ID: ${DISTRIBUTION_ID}"
echo "CloudFront URL: https://${DISTRIBUTION_DOMAIN}"
echo "생성 시간: ${TIMESTAMP}"
echo "========================================="
EOF

echo -e "${GREEN}✅ 환경 설정 파일 생성 완료 (deploy-config.env)${NC}"
echo ""

# 배포 완료 메시지
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   🎉 배포 준비 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📋 배포 정보:${NC}"
echo -e "   S3 버킷: ${BUCKET_NAME}"
echo -e "   CloudFront ID: ${DISTRIBUTION_ID}"
echo -e "   CloudFront URL: ${GREEN}https://${DISTRIBUTION_DOMAIN}${NC}"
echo ""
echo -e "${YELLOW}⚠️  주의사항:${NC}"
echo -e "   1. CloudFront 배포가 완전히 활성화되는데 15-20분 소요됩니다."
echo -e "   2. 빌드 및 배포는 deploy-frontend.sh 스크립트를 사용하세요."
echo ""
echo -e "${BLUE}다음 단계:${NC}"
echo -e "   1. npm run build 로 프로덕션 빌드 생성"
echo -e "   2. ./deploy-frontend.sh 실행하여 S3에 업로드"
echo ""