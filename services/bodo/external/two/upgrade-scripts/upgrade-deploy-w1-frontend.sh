#!/bin/bash

# w1.sedaily.ai 프론트엔드 배포 스크립트

source "$(dirname "$0")/00-config.sh"

CUSTOM_DOMAIN="w1.sedaily.ai"
S3_BUCKET="w1-sedaily-frontend"

log_info "w1.sedaily.ai 프론트엔드 배포 시작"

# 1. S3 버킷 생성 (존재하지 않는 경우)
if ! aws s3 ls "s3://$S3_BUCKET" >/dev/null 2>&1; then
    log_info "S3 버킷 생성 중: $S3_BUCKET"
    aws s3 mb "s3://$S3_BUCKET" --region "$REGION"
    
    # 정적 웹사이트 호스팅 설정
    aws s3 website "s3://$S3_BUCKET" \
        --index-document index.html \
        --error-document index.html
else
    log_info "S3 버킷이 이미 존재합니다: $S3_BUCKET"
fi

# 2. 프론트엔드 빌드
log_info "프론트엔드 빌드 중..."
cd "$FRONTEND_DIR"

# w1 환경변수 사용
cp .env.w1 .env

# 의존성 설치 및 빌드
npm install
npm run build

if [ $? -ne 0 ]; then
    log_error "프론트엔드 빌드 실패"
    exit 1
fi

log_success "프론트엔드 빌드 완료"

# 3. S3에 업로드
log_info "S3에 파일 업로드 중..."
aws s3 sync dist/ "s3://$S3_BUCKET" --delete

# 4. CloudFront 배포 생성
log_info "CloudFront 배포 생성 중..."

# Origin Access Identity 생성
OAI_ID=$(aws cloudfront create-cloud-front-origin-access-identity \
    --cloud-front-origin-access-identity-config \
    CallerReference="w1-sedaily-$(date +%s)",Comment="W1 Sedaily OAI" \
    --query 'CloudFrontOriginAccessIdentity.Id' \
    --output text)

log_info "Origin Access Identity 생성됨: $OAI_ID"

# CloudFront 배포 설정 파일 생성
cat > /tmp/cloudfront-config.json << EOF
{
    "CallerReference": "w1-sedaily-$(date +%s)",
    "Comment": "W1 Sedaily AI Assistant Distribution",
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$S3_BUCKET",
        "ViewerProtocolPolicy": "redirect-to-https",
        "MinTTL": 0,
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        }
    },
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$S3_BUCKET",
                "DomainName": "$S3_BUCKET.s3.amazonaws.com",
                "S3OriginConfig": {
                    "OriginAccessIdentity": "origin-access-identity/cloudfront/$OAI_ID"
                }
            }
        ]
    },
    "Enabled": true,
    "DefaultRootObject": "index.html",
    "CustomErrorResponses": {
        "Quantity": 1,
        "Items": [
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 300
            }
        ]
    },
    "PriceClass": "PriceClass_100"
}
EOF

# CloudFront 배포 생성
DISTRIBUTION_ID=$(aws cloudfront create-distribution \
    --distribution-config file:///tmp/cloudfront-config.json \
    --query 'Distribution.Id' \
    --output text)

if [ $? -eq 0 ]; then
    log_success "CloudFront 배포 생성됨: $DISTRIBUTION_ID"
else
    log_error "CloudFront 배포 생성 실패"
    exit 1
fi

# 5. S3 버킷 정책 업데이트
log_info "S3 버킷 정책 업데이트 중..."

cat > /tmp/bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity $OAI_ID"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$S3_BUCKET/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket "$S3_BUCKET" \
    --policy file:///tmp/bucket-policy.json

# 6. 배포 정보 저장
CLOUDFRONT_DOMAIN=$(aws cloudfront get-distribution \
    --id "$DISTRIBUTION_ID" \
    --query 'Distribution.DomainName' \
    --output text)

cat >> "$PROJECT_ROOT/endpoints.txt" << EOF

# w1.sedaily.ai 프론트엔드 배포 정보
S3_BUCKET=$S3_BUCKET
CLOUDFRONT_DISTRIBUTION_ID=$DISTRIBUTION_ID
CLOUDFRONT_DOMAIN=$CLOUDFRONT_DOMAIN
ORIGIN_ACCESS_IDENTITY=$OAI_ID
EOF

# 환경변수 파일에 추가
echo "CLOUDFRONT_DISTRIBUTION_ID=$DISTRIBUTION_ID" >> "$BACKEND_DIR/.env.w1"
echo "VITE_CLOUDFRONT_DOMAIN=$CLOUDFRONT_DOMAIN" >> "$FRONTEND_DIR/.env.w1"

log_success "w1.sedaily.ai 프론트엔드 배포 완료!"
log_info ""
log_info "배포 정보:"
log_info "- S3 버킷: $S3_BUCKET"
log_info "- CloudFront 배포 ID: $DISTRIBUTION_ID"
log_info "- CloudFront 도메인: $CLOUDFRONT_DOMAIN"
log_info "- 임시 접속 URL: https://$CLOUDFRONT_DOMAIN"
log_info ""
log_info "다음 단계:"
log_info "1. SSL 인증서 설정 (setup-w1-domain.sh 실행)"
log_info "2. DNS 레코드 설정"
log_info "3. 최종 접속: https://$CUSTOM_DOMAIN"

# 정리
rm -f /tmp/cloudfront-config.json /tmp/bucket-policy.json

cd "$PROJECT_ROOT"