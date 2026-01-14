#!/bin/bash
# Deploy Chat-Only to separate S3 + CloudFront
# ============================================

set -e
source "$(dirname "$0")/config.sh"

# Chat-only specific config
# CHAT_BUCKET은 config.sh에서 가져옴
CHAT_DOMAIN="d1jjxbf1f82fxa.cloudfront.net"

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

# Step 2: Check S3 bucket exists
check_chat_bucket() {
    log_info "Checking chat S3 bucket..."
    
    if aws s3api head-bucket --bucket "${CHAT_BUCKET}" --region "${AWS_REGION}" 2>/dev/null; then
        log_info "S3 bucket ${CHAT_BUCKET} exists ✓"
    else
        log_error "S3 bucket ${CHAT_BUCKET} does not exist!"
        exit 1
    fi
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

# Step 4: Invalidate chat CloudFront cache
invalidate_chat_cloudfront() {
    log_info "Invalidating chat CloudFront cache..."
    
    # Chat CloudFront Distribution ID
    CHAT_CLOUDFRONT_DISTRIBUTION_ID="${CHAT_CLOUDFRONT_DISTRIBUTION_ID:-}"
    
    if [ -z "$CHAT_CLOUDFRONT_DISTRIBUTION_ID" ]; then
        log_warning "CHAT_CLOUDFRONT_DISTRIBUTION_ID not set in config.sh"
        log_info "Skipping chat CloudFront invalidation"
        return 0
    fi
    
    # Create invalidation for all files
    INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --distribution-id "$CHAT_CLOUDFRONT_DISTRIBUTION_ID" \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text)
    
    if [ $? -eq 0 ]; then
        log_info "Chat CloudFront invalidation created: $INVALIDATION_ID ✅"
        log_info "Cache will be cleared in 1-3 minutes"
    else
        log_error "Failed to create chat CloudFront invalidation"
    fi
}

# Step 5: Show deployment info
show_deployment_info() {
    log_info "Deployment information..."
    
    echo ""
    echo "========================================="
    echo "✅ Chat-Only Deployment Complete!"
    echo "========================================="
    echo ""
    echo "S3 Bucket: ${CHAT_BUCKET}"
    echo "CloudFront: https://${CHAT_DOMAIN}"
    echo "Distribution ID: ${CHAT_CLOUDFRONT_DISTRIBUTION_ID}"
    echo ""
    echo "🌐 Access URL: https://${CHAT_DOMAIN}/11"
    echo ""
}

# Main execution
main() {
    build_chat
    echo ""
    check_chat_bucket
    echo ""
    upload_chat
    echo ""
    invalidate_chat_cloudfront
    echo ""
    show_deployment_info
}

main "$@"