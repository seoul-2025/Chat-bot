#!/bin/bash
# Deploy Chat-Only to separate S3 + CloudFront
# ============================================

set -e
source "$(dirname "$0")/config.sh"

# Chat-only specific config
CHAT_BUCKET="one-chat-only-bucket-${RANDOM}"
CHAT_DOMAIN="chat.sedaily.ai"  # 원하는 도메인으로 변경

echo "========================================="
echo "   Chat-Only Deployment"
echo "   Target: ${CHAT_BUCKET}"
echo "========================================="

# Step 1: Build chat-only
build_chat() {
    log_info "Building chat-only app..."
    
    cd "$FRONTEND_DIR"
    npm run build:chat
    
    log_info "Chat build completed ✅"
}

# Step 2: Create separate S3 bucket
create_chat_bucket() {
    log_info "Creating chat S3 bucket..."
    
    aws s3api create-bucket \
        --bucket "${CHAT_BUCKET}" \
        --region "${AWS_REGION}" \
        --create-bucket-configuration LocationConstraint="${AWS_REGION}"
    
    # Enable static website hosting
    aws s3 website "s3://${CHAT_BUCKET}" \
        --index-document chat-only.html \
        --error-document chat-only.html
    
    # Set public read policy
    cat > /tmp/chat-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${CHAT_BUCKET}/*"
    }
  ]
}
EOF
    
    aws s3api put-bucket-policy \
        --bucket "${CHAT_BUCKET}" \
        --policy file:///tmp/chat-policy.json
    
    log_info "Chat S3 bucket created ✅"
}

# Step 3: Upload chat files
upload_chat() {
    log_info "Uploading chat files..."
    
    cd "$FRONTEND_DIR"
    
    aws s3 sync dist-chat/ "s3://${CHAT_BUCKET}/" \
        --delete \
        --region "${AWS_REGION}" \
        --cache-control "no-cache"
    
    log_info "Chat files uploaded ✅"
}

# Step 4: Create CloudFront for chat
create_chat_cloudfront() {
    log_info "Creating CloudFront distribution for chat..."
    
    ORIGIN_DOMAIN="${CHAT_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com"
    
    cat > /tmp/chat-cf-config.json << EOF
{
  "CallerReference": "chat-$(date +%s)",
  "Comment": "Chat-only distribution",
  "DefaultRootObject": "chat-only.html",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "chat-origin",
        "DomainName": "${ORIGIN_DOMAIN}",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "http-only"
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "chat-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "MinTTL": 0
  },
  "CustomErrorResponses": {
    "Quantity": 2,
    "Items": [
      {
        "ErrorCode": 403,
        "ResponsePagePath": "/chat-only.html",
        "ResponseCode": "200",
        "ErrorCachingMinTTL": 300
      },
      {
        "ErrorCode": 404,
        "ResponsePagePath": "/chat-only.html",
        "ResponseCode": "200",
        "ErrorCachingMinTTL": 300
      }
    ]
  },
  "Enabled": true,
  "PriceClass": "PriceClass_100"
}
EOF
    
    DISTRIBUTION_ID=$(aws cloudfront create-distribution \
        --distribution-config file:///tmp/chat-cf-config.json \
        --query 'Distribution.Id' \
        --output text)
    
    CHAT_CLOUDFRONT_DOMAIN=$(aws cloudfront get-distribution \
        --id "${DISTRIBUTION_ID}" \
        --query 'Distribution.DomainName' \
        --output text)
    
    log_info "CloudFront created: ${CHAT_CLOUDFRONT_DOMAIN} ✅"
    
    echo ""
    echo "========================================="
    echo "✅ Chat-Only Deployment Complete!"
    echo "========================================="
    echo ""
    echo "S3 Website: http://${ORIGIN_DOMAIN}"
    echo "CloudFront: https://${CHAT_CLOUDFRONT_DOMAIN}"
    echo "Distribution ID: ${DISTRIBUTION_ID}"
    echo ""
    echo "💡 Custom domain setup:"
    echo "   1. Add CNAME: ${CHAT_DOMAIN} → ${CHAT_CLOUDFRONT_DOMAIN}"
    echo "   2. Add SSL certificate in CloudFront console"
}

# Main execution
main() {
    build_chat
    echo ""
    create_chat_bucket
    echo ""
    upload_chat
    echo ""
    create_chat_cloudfront
}

main "$@"