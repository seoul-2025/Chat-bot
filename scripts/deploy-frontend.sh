#!/bin/bash
# Deploy Frontend to S3 + CloudFront
# ===================================

set -e
source "$(dirname "$0")/config.sh"

echo "========================================="
echo "   Frontend Deployment"
echo "   Target: S3 + CloudFront"
echo "========================================="

# Step 1: Build frontend
build_frontend() {
    log_info "Building frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies
    log_info "Installing npm dependencies..."
    npm install --silent
    
    # Build for production
    log_info "Building for production..."
    npm run build
    
    log_info "Frontend build completed"
}

# Step 2: Create S3 bucket if it doesn't exist
create_s3_bucket() {
    log_info "Checking S3 bucket..."
    
    if aws s3api head-bucket --bucket "${FRONTEND_BUCKET}" --region "${AWS_REGION}" 2>/dev/null; then
        log_info "S3 bucket ${FRONTEND_BUCKET} exists ✓"
    else
        log_info "Creating S3 bucket ${FRONTEND_BUCKET}..."
        aws s3api create-bucket \
            --bucket "${FRONTEND_BUCKET}" \
            --region "${AWS_REGION}" \
            --create-bucket-configuration LocationConstraint="${AWS_REGION}"
        
        # Enable static website hosting
        aws s3 website "s3://${FRONTEND_BUCKET}" \
            --index-document index.html \
            --error-document index.html
        
        log_info "S3 bucket created and configured ✅"
    fi
}

# Step 3: Upload to S3
upload_to_s3() {
    log_info "Uploading to S3..."
    
    cd "$FRONTEND_DIR"
    
    # Sync dist folder to S3
    aws s3 sync dist/ "s3://${FRONTEND_BUCKET}/" \
        --delete \
        --region "${AWS_REGION}" \
        --cache-control "max-age=31536000" \
        --exclude "*.html" \
        --quiet
    
    # Upload HTML files with no cache
    aws s3 sync dist/ "s3://${FRONTEND_BUCKET}/" \
        --delete \
        --region "${AWS_REGION}" \
        --cache-control "no-cache" \
        --include "*.html" \
        --quiet
    
    log_info "Files uploaded to S3 ✅"
}

# Step 4: Create CloudFront distribution (optional)
create_cloudfront() {
    log_info "CloudFront distribution setup..."
    log_warning "CloudFront creation is manual - please configure in AWS Console"
    log_info "S3 Website URL: http://${FRONTEND_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com"
}

# Main execution
main() {
    # Check if in correct directory
    if [ ! -f "$FRONTEND_DIR/package.json" ]; then
        log_error "Frontend directory not found. Please run from project root."
        exit 1
    fi
    
    # Execute deployment steps
    build_frontend
    echo ""
    create_s3_bucket
    echo ""
    upload_to_s3
    echo ""
    create_cloudfront
    
    echo ""
    echo "========================================="
    echo "✅ Frontend Deployment Complete!"
    echo "========================================="
    echo ""
    echo "Website URL: http://${FRONTEND_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com"
}

main "$@"