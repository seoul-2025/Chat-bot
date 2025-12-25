#!/bin/bash

# f1.sedaily.ai 백엔드 배포 스크립트
set -e

# 색상 설정
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}   f1.sedaily.ai 백엔드 배포${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# 설정
REGION="us-east-1"
PREFIX="f1-two-backend-dev"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo -e "${YELLOW}Deploying Lambda functions for ${PREFIX}${NC}"
echo -e "${YELLOW}Backend directory: ${BACKEND_DIR}${NC}"
echo ""

# Lambda 함수 목록과 핸들러 매핑
FUNCTION_NAMES=(
    "${PREFIX}-conversation-api"
    "${PREFIX}-prompt-crud"
    "${PREFIX}-usage-handler"
    "${PREFIX}-websocket-message"
    "${PREFIX}-websocket-connect"
    "${PREFIX}-websocket-disconnect"
)

FUNCTION_HANDLERS=(
    "handlers.api.conversation.handler"
    "handlers.api.prompt.handler"
    "handlers.api.usage.handler"
    "handlers.websocket.message.handler"
    "handlers.websocket.connect.handler"
    "handlers.websocket.disconnect.handler"
)

# 임시 디렉토리 생성
TEMP_DIR="/tmp/lambda-deploy-${PREFIX}"
rm -rf $TEMP_DIR
mkdir -p $TEMP_DIR

# ====================================
# 배포 패키지 생성
# ====================================
echo -e "${BLUE}Creating deployment package...${NC}"

# 소스 코드 복사
cp -r "$BACKEND_DIR"/handlers "$TEMP_DIR"/
cp -r "$BACKEND_DIR"/src "$TEMP_DIR"/
cp -r "$BACKEND_DIR"/utils "$TEMP_DIR"/
cp -r "$BACKEND_DIR"/services "$TEMP_DIR"/ 2>/dev/null || true
cp -r "$BACKEND_DIR"/lib "$TEMP_DIR"/ 2>/dev/null || true

# requirements.txt 확인 및 의존성 설치
if [ -f "$BACKEND_DIR/requirements.txt" ]; then
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip install -r "$BACKEND_DIR"/requirements.txt -t "$TEMP_DIR" --upgrade --quiet
    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi

# 불필요한 파일 제거
find $TEMP_DIR -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find $TEMP_DIR -type f -name "*.pyc" -delete
find $TEMP_DIR -type d -name ".git" -exec rm -rf {} + 2>/dev/null
find $TEMP_DIR -type f -name ".DS_Store" -delete

# ZIP 파일 생성
cd $TEMP_DIR
zip -r deployment.zip . -q
PACKAGE_SIZE=$(du -h deployment.zip | cut -f1)
echo -e "${GREEN}✅ Deployment package created (${PACKAGE_SIZE})${NC}"

# ====================================
# Lambda 함수 업데이트/생성
# ====================================
echo ""
echo -e "${BLUE}Deploying Lambda functions...${NC}"

# 배포 함수
deploy_function() {
    local FUNCTION_NAME=$1
    local HANDLER=$2

    echo -e "${YELLOW}Deploying ${FUNCTION_NAME}...${NC}"

    # 함수 존재 확인
    if aws lambda get-function --function-name "$FUNCTION_NAME" --region $REGION >/dev/null 2>&1; then
        # 기존 함수 업데이트
        aws lambda update-function-code \
            --function-name "$FUNCTION_NAME" \
            --zip-file "fileb://$TEMP_DIR/deployment.zip" \
            --region $REGION \
            --output text >/dev/null 2>&1

        aws lambda update-function-configuration \
            --function-name "$FUNCTION_NAME" \
            --handler "$HANDLER" \
            --region $REGION \
            --output text >/dev/null 2>&1
    else
        # 새 함수 생성
        aws lambda create-function \
            --function-name "$FUNCTION_NAME" \
            --runtime python3.11 \
            --role "arn:aws:iam::887078546492:role/lambda-execution-role" \
            --handler "$HANDLER" \
            --zip-file "fileb://$TEMP_DIR/deployment.zip" \
            --timeout 30 \
            --memory-size 512 \
            --region $REGION \
            --output text >/dev/null 2>&1
    fi

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✓ ${FUNCTION_NAME} deployed${NC}"
        return 0
    else
        echo -e "${RED}  ✗ ${FUNCTION_NAME} deployment failed${NC}"
        return 1
    fi
}

# 배포 시작
TOTAL=${#FUNCTION_NAMES[@]}
CURRENT=0
SUCCESS=0
FAILED=0

for i in "${!FUNCTION_NAMES[@]}"; do
    FUNCTION_NAME="${FUNCTION_NAMES[$i]}"
    HANDLER="${FUNCTION_HANDLERS[$i]}"
    ((CURRENT++))
    echo -e "${BLUE}[${CURRENT}/${TOTAL}] ${FUNCTION_NAME}${NC}"

    if deploy_function "$FUNCTION_NAME" "$HANDLER"; then
        ((SUCCESS++))
    else
        ((FAILED++))
    fi
done

# 정리
rm -rf $TEMP_DIR

# ====================================
# 배포 결과
# ====================================
echo ""
echo -e "${GREEN}=================================${NC}"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
else
    echo -e "${YELLOW}⚠️  DEPLOYMENT COMPLETED WITH ISSUES${NC}"
fi
echo -e "${GREEN}=================================${NC}"
echo ""
echo -e "${BLUE}Deployment Summary:${NC}"
echo -e "  ${GREEN}✓ Successful:${NC} ${SUCCESS}"
if [ $FAILED -gt 0 ]; then
    echo -e "  ${RED}✗ Failed:${NC} ${FAILED}"
fi
echo ""