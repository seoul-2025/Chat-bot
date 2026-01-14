#!/bin/bash
# CloudFront 캐시 즉시 무효화 스크립트
# ====================================

set -e
source "$(dirname "$0")/config.sh"

echo "========================================="
echo "   CloudFront 캐시 무효화"
echo "========================================="

# 캐시 무효화 함수
invalidate_cache() {
    local distribution_id="$1"
    local site_name="$2"
    
    if [ -z "$distribution_id" ]; then
        log_warning "$site_name Distribution ID가 설정되지 않았습니다."
        return 1
    fi
    
    log_info "$site_name 캐시 무효화 중..."
    
    # 무효화 생성
    local invalidation_id=$(aws cloudfront create-invalidation \
        --distribution-id "$distribution_id" \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text)
    
    if [ $? -eq 0 ]; then
        log_info "$site_name 캐시 무효화 생성됨: $invalidation_id ✅"
        
        # 무효화 상태 확인
        log_info "무효화 진행 상태 확인 중..."
        aws cloudfront wait invalidation-completed \
            --distribution-id "$distribution_id" \
            --id "$invalidation_id" &
        
        local wait_pid=$!
        echo "무효화 완료 대기 중... (백그라운드 프로세스 PID: $wait_pid)"
        echo "일반적으로 1-3분 소요됩니다."
        
        return 0
    else
        log_error "$site_name 캐시 무효화 실패"
        return 1
    fi
}

# 메인 실행
main() {
    local main_success=false
    local chat_success=false
    
    echo "현재 설정된 Distribution ID:"
    echo "- Main Site: ${CLOUDFRONT_DISTRIBUTION_ID:-'설정되지 않음'}"
    echo "- Chat Site: ${CHAT_CLOUDFRONT_DISTRIBUTION_ID:-'설정되지 않음'}"
    echo ""
    
    # 메인 사이트 캐시 무효화
    if [ -n "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
        if invalidate_cache "$CLOUDFRONT_DISTRIBUTION_ID" "Main Site"; then
            main_success=true
        fi
        echo ""
    fi
    
    # 채팅 사이트 캐시 무효화
    if [ -n "$CHAT_CLOUDFRONT_DISTRIBUTION_ID" ]; then
        if invalidate_cache "$CHAT_CLOUDFRONT_DISTRIBUTION_ID" "Chat Site"; then
            chat_success=true
        fi
        echo ""
    fi
    
    # 결과 요약
    echo "========================================="
    echo "   무효화 결과"
    echo "========================================="
    
    if [ "$main_success" = true ]; then
        echo "✅ Main Site 캐시 무효화 완료"
    elif [ -n "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
        echo "❌ Main Site 캐시 무효화 실패"
    else
        echo "⚠️  Main Site Distribution ID 미설정"
    fi
    
    if [ "$chat_success" = true ]; then
        echo "✅ Chat Site 캐시 무효화 완료"
    elif [ -n "$CHAT_CLOUDFRONT_DISTRIBUTION_ID" ]; then
        echo "❌ Chat Site 캐시 무효화 실패"
    else
        echo "⚠️  Chat Site Distribution ID 미설정"
    fi
    
    echo ""
    
    # Distribution ID가 설정되지 않은 경우 안내
    if [ -z "$CLOUDFRONT_DISTRIBUTION_ID" ] && [ -z "$CHAT_CLOUDFRONT_DISTRIBUTION_ID" ]; then
        echo "💡 Distribution ID를 찾으려면 다음 명령을 실행하세요:"
        echo "   ./scripts/find-cloudfront-id.sh"
        echo ""
    fi
    
    echo "🔄 브라우저에서 강제 새로고침 (Ctrl+F5 또는 Cmd+Shift+R)을 해주세요."
}

# 스크립트 실행
main "$@"