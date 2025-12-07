#!/bin/bash

# f1.sedaily.ai 백엔드 배포 스크립트 (GitHub 버전)
set -e

# 색상 설정
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# 설정 - f1-two 스택
STACK_NAME="f1-two"
SERVICE_NAME="f1"
REGION="us-east-1"

# Lambda 함수 목록
LAMBDA_FUNCTIONS=(
  "f1-conversation-api-two"
  "f1-prompt-crud-two"
  "f1-usage-handler-two"
  "f1-websocket-connect-two"
  "f1-websocket-disconnect-two"
  "f1-websocket-message-two"
)

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   f1.sedaily.ai 백엔드 배포 (GitHub 버전)${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo -e "스택: ${CYAN}${STACK_NAME}${NC}"
echo -e "Lambda 함수 개수: ${CYAN}${#LAMBDA_FUNCTIONS[@]}${NC}"
echo ""

# 프로젝트 루트로 이동
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

# 1. Backend 디렉토리로 이동
echo -e "${YELLOW}📂 Backend 디렉토리로 이동...${NC}"
cd "${PROJECT_ROOT}/backend"

# 2. 임시 패키지 디렉토리 생성
echo -e "${YELLOW}📦 배포 패키지 생성 중...${NC}"
rm -rf deployment_package
mkdir -p deployment_package

# 3. 의존성 설치
echo -e "${YELLOW}📥 의존성 설치 중...${NC}"
pip install -r requirements.txt -t deployment_package/ --upgrade --quiet

# 4. 소스 코드 복사
echo -e "${YELLOW}📋 소스 코드 복사 중...${NC}"
cp -r handlers deployment_package/
cp -r lib deployment_package/
cp -r services deployment_package/
cp -r utils deployment_package/
cp -r src deployment_package/

# 5. ZIP 파일 생성
echo -e "${YELLOW}🗜️ ZIP 파일 생성 중...${NC}"
cd deployment_package
zip -r ../f1-lambda-deployment.zip . -q
cd ..

# 패키지 크기 확인
PACKAGE_SIZE=$(ls -lh f1-lambda-deployment.zip | awk '{print $5}')
echo -e "${GREEN}✅ 배포 패키지 생성 완료 (크기: ${PACKAGE_SIZE})${NC}"

# 6. Lambda 함수 업데이트
echo ""
echo -e "${BLUE}🚀 Lambda 함수 업데이트 시작${NC}"
echo ""

UPDATED=0
FAILED=0

for func in "${LAMBDA_FUNCTIONS[@]}"; do
    echo -e "${YELLOW}→ ${func} 업데이트 중...${NC}"
    
    # 함수 존재 확인
    if aws lambda get-function --function-name $func --region $REGION &>/dev/null; then
        # 코드 업데이트
        if aws lambda update-function-code \
            --function-name $func \
            --zip-file fileb://f1-lambda-deployment.zip \
            --region $REGION \
            --output json > /dev/null 2>&1; then
            
            echo -e "  ${GREEN}✅ ${func} 업데이트 성공${NC}"
            ((UPDATED++))
        else
            echo -e "  ${RED}❌ ${func} 업데이트 실패${NC}"
            ((FAILED++))
        fi
    else
        echo -e "  ${YELLOW}⚠️ ${func} 함수를 찾을 수 없습니다${NC}"
        ((FAILED++))
    fi
done

# 7. 정리
echo ""
echo -e "${YELLOW}🧹 정리 중...${NC}"
rm -rf deployment_package
rm -f f1-lambda-deployment.zip

# 8. 결과 출력
echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   📊 배포 결과${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "성공: ${GREEN}${UPDATED}${NC} / 실패: ${RED}${FAILED}${NC}"
echo ""

if [ $UPDATED -eq ${#LAMBDA_FUNCTIONS[@]} ]; then
    echo -e "${GREEN}✅ 모든 Lambda 함수가 성공적으로 업데이트되었습니다!${NC}"
else
    echo -e "${YELLOW}⚠️ 일부 Lambda 함수 업데이트에 실패했습니다.${NC}"
    echo "  CloudWatch Logs를 확인하세요."
fi

echo ""
echo -e "${BLUE}다음 단계:${NC}"
echo "  1. CloudWatch Logs에서 함수 동작 확인"
echo "  2. f1.sedaily.ai에서 기능 테스트"
echo ""