#!/bin/bash
# CloudFront Distribution ID 자동 찾기 스크립트
# ===============================================

set -e
source "$(dirname "$0")/config.sh"

echo "========================================="
echo "   CloudFront Distribution ID 찾기"
echo "========================================="

# S3 버킷 기반으로 CloudFront Distribution 찾기
find_distribution_by_bucket() {
    local bucket_name="$1"
    local description="$2"
    
    log_info "Finding CloudFront distribution for $bucket_name..."
    
    # S3 website endpoint 생성
    local s3_website_domain="${bucket_name}.s3-website-${AWS_REGION}.amazonaws.com"
    
    # CloudFront distributions 조회
    local distribution_id=$(aws cloudfront list-distributions \
        --query "DistributionList.Items[?Origins.Items[0].DomainName=='${s3_website_domain}'].Id" \
        --output text)
    
    if [ -n "$distribution_id" ] && [ "$distribution_id" != "None" ]; then
        log_info "$description Distribution ID: $distribution_id ✅"
        echo "$distribution_id"
    else
        log_warning "$description Distribution not found for bucket: $bucket_name"
        echo ""
    fi
}

# 메인 사이트 Distribution ID 찾기
main_distribution_id=$(find_distribution_by_bucket "$FRONTEND_BUCKET" "Main site")

# 채팅 사이트 Distribution ID 찾기 (패턴 매칭)
chat_distribution_id=""
chat_buckets=$(aws s3api list-buckets --query 'Buckets[?starts_with(Name, `one-chat-only-bucket`)].Name' --output text)

if [ -n "$chat_buckets" ]; then
    for bucket in $chat_buckets; do
        chat_distribution_id=$(find_distribution_by_bucket "$bucket" "Chat site")
        if [ -n "$chat_distribution_id" ]; then
            break
        fi
    done
fi

echo ""
echo "========================================="
echo "   결과 요약"
echo "========================================="

if [ -n "$main_distribution_id" ]; then
    echo "Main Site Distribution ID: $main_distribution_id"
    echo "config.sh에 추가할 내용:"
    echo "export CLOUDFRONT_DISTRIBUTION_ID=\"$main_distribution_id\""
else
    echo "Main Site Distribution: Not found"
fi

echo ""

if [ -n "$chat_distribution_id" ]; then
    echo "Chat Site Distribution ID: $chat_distribution_id"
    echo "config.sh에 추가할 내용:"
    echo "export CHAT_CLOUDFRONT_DISTRIBUTION_ID=\"$chat_distribution_id\""
else
    echo "Chat Site Distribution: Not found"
fi

echo ""
echo "========================================="
echo "   자동 업데이트 옵션"
echo "========================================="

# config.sh 자동 업데이트 제안
if [ -n "$main_distribution_id" ] || [ -n "$chat_distribution_id" ]; then
    echo ""
    read -p "config.sh 파일을 자동으로 업데이트하시겠습니까? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        config_file="$(dirname "$0")/config.sh"
        
        if [ -n "$main_distribution_id" ]; then
            sed -i "s/export CLOUDFRONT_DISTRIBUTION_ID=\".*\"/export CLOUDFRONT_DISTRIBUTION_ID=\"$main_distribution_id\"/" "$config_file"
            log_info "Main Distribution ID updated in config.sh ✅"
        fi
        
        if [ -n "$chat_distribution_id" ]; then
            sed -i "s/export CHAT_CLOUDFRONT_DISTRIBUTION_ID=\".*\"/export CHAT_CLOUDFRONT_DISTRIBUTION_ID=\"$chat_distribution_id\"/" "$config_file"
            log_info "Chat Distribution ID updated in config.sh ✅"
        fi
        
        echo ""
        log_info "config.sh 파일이 업데이트되었습니다!"
    else
        echo ""
        log_info "수동으로 config.sh 파일을 업데이트해주세요."
    fi
fi