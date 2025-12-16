#!/bin/bash

# w1.sedaily.ai 전체 배포 스크립트

source "$(dirname "$0")/00-config.sh"

log_info "w1.sedaily.ai 전체 배포 시작"
log_info "서비스명: w1"
log_info "도메인: w1.sedaily.ai"
log_info "리전: $REGION"

# 1. 프론트엔드 배포
log_info "=== 1단계: 프론트엔드 배포 ==="
./scripts/deploy-w1-frontend.sh
if [ $? -ne 0 ]; then
    log_error "프론트엔드 배포 실패"
    exit 1
fi

# 2. 백엔드 환경변수 업데이트
log_info "=== 2단계: 백엔드 환경변수 업데이트 ==="

# 기존 Lambda 함수들의 환경변수 업데이트
LAMBDA_FUNCTIONS=(
    "w1-websocket-connect"
    "w1-websocket-disconnect" 
    "w1-websocket-message"
    "w1-conversation-api"
    "w1-prompt-crud"
    "w1-usage-handler"
)

for func in "${LAMBDA_FUNCTIONS[@]}"; do
    log_info "Lambda 함수 환경변수 업데이트: $func"
    
    # 현재 환경변수 가져오기
    aws lambda get-function-configuration \
        --function-name "$func" \
        --region "$REGION" \
        --query 'Environment.Variables' > /tmp/current-env.json
    
    # w1 도메인 환경변수 추가
    jq '. + {
        "CUSTOM_DOMAIN": "w1.sedaily.ai",
        "API_DOMAIN": "api.w1.sedaily.ai", 
        "WS_DOMAIN": "ws.w1.sedaily.ai",
        "REST_API_URL": "https://api.w1.sedaily.ai",
        "WEBSOCKET_API_URL": "wss://ws.w1.sedaily.ai",
        "CORS_ORIGINS": "https://w1.sedaily.ai,https://api.w1.sedaily.ai"
    }' /tmp/current-env.json > /tmp/updated-env.json
    
    # 환경변수 업데이트
    aws lambda update-function-configuration \
        --function-name "$func" \
        --environment "Variables=$(cat /tmp/updated-env.json | jq -c .)" \
        --region "$REGION" >/dev/null
    
    if [ $? -eq 0 ]; then
        log_success "Lambda 함수 환경변수 업데이트 완료: $func"
    else
        log_warning "Lambda 함수 환경변수 업데이트 실패: $func"
    fi
done

# 3. API Gateway CORS 설정 업데이트
log_info "=== 3단계: API Gateway CORS 설정 업데이트 ==="

# REST API ID 가져오기
if [ -f "$API_IDS_FILE" ]; then
    source "$API_IDS_FILE"
fi

if [ -n "$REST_API_ID" ]; then
    log_info "REST API CORS 업데이트: $REST_API_ID"
    
    # 모든 리소스에 대해 CORS 헤더 업데이트
    RESOURCES=$(aws apigateway get-resources \
        --rest-api-id "$REST_API_ID" \
        --region "$REGION" \
        --query 'items[].id' \
        --output text)
    
    for resource_id in $RESOURCES; do
        # OPTIONS 메서드가 있는지 확인하고 CORS 헤더 업데이트
        aws apigateway get-method \
            --rest-api-id "$REST_API_ID" \
            --resource-id "$resource_id" \
            --http-method OPTIONS \
            --region "$REGION" >/dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            # 기존 OPTIONS 메서드 응답 헤더 업데이트
            aws apigateway put-method-response \
                --rest-api-id "$REST_API_ID" \
                --resource-id "$resource_id" \
                --http-method OPTIONS \
                --status-code 200 \
                --response-parameters \
                "method.response.header.Access-Control-Allow-Origin=false,method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false" \
                --region "$REGION" >/dev/null 2>&1
            
            aws apigateway put-integration-response \
                --rest-api-id "$REST_API_ID" \
                --resource-id "$resource_id" \
                --http-method OPTIONS \
                --status-code 200 \
                --response-parameters \
                "method.response.header.Access-Control-Allow-Origin='https://w1.sedaily.ai',method.response.header.Access-Control-Allow-Headers='Content-Type,Authorization,X-Requested-With',method.response.header.Access-Control-Allow-Methods='GET,POST,PUT,DELETE,OPTIONS'" \
                --region "$REGION" >/dev/null 2>&1
        fi
    done
    
    # API 배포
    aws apigateway create-deployment \
        --rest-api-id "$REST_API_ID" \
        --stage-name prod \
        --region "$REGION" >/dev/null
    
    log_success "REST API CORS 설정 업데이트 완료"
fi

# 4. 배포 상태 확인
log_info "=== 4단계: 배포 상태 확인 ==="

# CloudFront 배포 상태 확인
if [ -n "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
    CF_STATUS=$(aws cloudfront get-distribution \
        --id "$CLOUDFRONT_DISTRIBUTION_ID" \
        --query 'Distribution.Status' \
        --output text)
    log_info "CloudFront 배포 상태: $CF_STATUS"
fi

# Lambda 함수 상태 확인
log_info "Lambda 함수 상태 확인:"
for func in "${LAMBDA_FUNCTIONS[@]}"; do
    STATUS=$(aws lambda get-function \
        --function-name "$func" \
        --region "$REGION" \
        --query 'Configuration.State' \
        --output text 2>/dev/null)
    
    if [ "$STATUS" = "Active" ]; then
        log_success "✓ $func: Active"
    else
        log_warning "⚠ $func: $STATUS"
    fi
done

# 5. 최종 정보 출력
log_success "w1.sedaily.ai 배포 완료!"
log_info ""
log_info "=== 배포 정보 ==="
log_info "메인 도메인: https://w1.sedaily.ai"
log_info "API 도메인: https://api.w1.sedaily.ai"
log_info "WebSocket 도메인: wss://ws.w1.sedaily.ai"
log_info ""
log_info "=== 다음 단계 ==="
log_info "1. SSL 인증서 설정:"
log_info "   ./scripts/setup-w1-domain.sh"
log_info ""
log_info "2. DNS 레코드 설정 (Route 53 또는 도메인 관리자):"
log_info "   w1.sedaily.ai -> CloudFront 도메인 (CNAME)"
log_info "   api.w1.sedaily.ai -> API Gateway 도메인 (CNAME)"
log_info "   ws.w1.sedaily.ai -> WebSocket API 도메인 (CNAME)"
log_info ""
log_info "3. 설정 완료 후 테스트:"
log_info "   curl https://api.w1.sedaily.ai/health"
log_info "   브라우저에서 https://w1.sedaily.ai 접속"

# 정리
rm -f /tmp/current-env.json /tmp/updated-env.json