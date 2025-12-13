#!/bin/bash

# 색상 설정
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Lambda 함수 배포 (의존성 포함)${NC}"
echo -e "${BLUE}=================================${NC}"

# 스크립트 디렉토리
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

# 기존 패키지 디렉토리 삭제
echo -e "\n${BLUE}1. 기존 패키지 정리 중...${NC}"
rm -rf package lambda_deploy_with_deps.zip

# requests 라이브러리 설치
echo -e "\n${BLUE}2. 의존성 설치 중...${NC}"
pip install requests -t package --quiet

# 배포 패키지 생성
echo -e "\n${BLUE}3. 배포 패키지 생성 중...${NC}"

# 먼저 package 디렉토리의 내용을 압축
cd package
zip -r ../lambda_deploy_with_deps.zip . -x "*.pyc" -x "*__pycache__*" -x ".*" > /dev/null 2>&1
cd ..

# 그 다음 소스 코드 추가
zip -r lambda_deploy_with_deps.zip handlers services utils lib src -x "*.pyc" -x "*__pycache__*" -x ".*" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ZIP 파일 생성 실패${NC}"
    exit 1
fi

# 파일 크기 확인
FILE_SIZE=$(ls -lh lambda_deploy_with_deps.zip | awk '{print $5}')
echo -e "${GREEN}✅ ZIP 파일 생성 완료 (크기: ${FILE_SIZE})${NC}"

# Lambda 함수 목록
FUNCTIONS=(
    "nx-wt-prf-conversation-api"
    "nx-wt-prf-prompt-crud"
    "nx-wt-prf-usage-handler"
    "nx-wt-prf-websocket-connect"
    "nx-wt-prf-websocket-disconnect"
    "nx-wt-prf-websocket-message"
)

# 핸들러 매핑
get_handler_for_function() {
    case "$1" in
        "nx-wt-prf-conversation-api")
            echo "handlers.api.conversation.handler"
            ;;
        "nx-wt-prf-prompt-crud")
            echo "handlers.api.prompt.handler"
            ;;
        "nx-wt-prf-usage-handler")
            echo "handlers.api.usage.handler"
            ;;
        "nx-wt-prf-websocket-connect")
            echo "handlers.websocket.connect.handler"
            ;;
        "nx-wt-prf-websocket-disconnect")
            echo "handlers.websocket.disconnect.handler"
            ;;
        "nx-wt-prf-websocket-message")
            echo "handlers.websocket.message.handler"
            ;;
        *)
            echo ""
            ;;
    esac
}

# 각 함수 업데이트
echo -e "\n${BLUE}4. Lambda 함수 업데이트 중...${NC}"
for func in "${FUNCTIONS[@]}"; do
    echo -e "\n${YELLOW}처리 중: $func${NC}"
    
    # 코드 업데이트
    echo -e "  코드 업데이트..."
    aws lambda update-function-code \
        --function-name $func \
        --zip-file fileb://lambda_deploy_with_deps.zip \
        --region us-east-1 > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✅ 코드 업데이트 성공${NC}"
    else
        echo -e "  ${RED}❌ 코드 업데이트 실패${NC}"
        continue
    fi
    
    # 핸들러 업데이트
    HANDLER=$(get_handler_for_function "$func")
    if [ -n "$HANDLER" ]; then
        echo -e "  핸들러 설정..."
        aws lambda update-function-configuration \
            --function-name $func \
            --handler "$HANDLER" \
            --region us-east-1 > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✅ 핸들러 설정 성공 ($HANDLER)${NC}"
        else
            echo -e "  ${YELLOW}⚠ 핸들러 이미 설정됨${NC}"
        fi
    fi
    
    # 함수가 준비될 때까지 대기
    echo -e "  함수 준비 대기..."
    aws lambda wait function-active \
        --function-name $func \
        --region us-east-1 2>/dev/null
    
    echo -e "  ${GREEN}✅ $func 업데이트 완료${NC}"
done

# 정리
rm -rf package lambda_deploy_with_deps.zip

echo -e "\n${BLUE}=================================${NC}"
echo -e "${GREEN}✅ 배포 완료!${NC}"
echo -e "${BLUE}=================================${NC}"

# 배포 결과 확인
echo -e "\n${BLUE}5. 배포 상태 확인${NC}"
for func in "${FUNCTIONS[@]}"; do
    STATE=$(aws lambda get-function --function-name $func --region us-east-1 --query 'Configuration.State' --output text 2>/dev/null)
    LAST_MODIFIED=$(aws lambda get-function --function-name $func --region us-east-1 --query 'Configuration.LastModified' --output text 2>/dev/null)
    
    if [ "$STATE" = "Active" ]; then
        echo -e "  ${GREEN}✓${NC} $func: $STATE (최종 수정: $LAST_MODIFIED)"
    else
        echo -e "  ${RED}✗${NC} $func: $STATE"
    fi
done

echo -e "\n${YELLOW}다음 단계:${NC}"
echo -e "  1. CloudWatch 로그에서 에러 확인"
echo -e "  2. API Gateway에서 테스트 실행"
echo -e "  3. 필요시 롤백: git checkout -- ."